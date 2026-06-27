"""数据管道模块测试"""

from __future__ import annotations

import pandas as pd
import pytest

from modules.data_pipeline import DataPipeline, PipelineConfig, PipelineStats


class TestDataPipelineLoad:
    """数据加载测试"""

    def test_load_data(self, small_df):
        """load_data 加载数据"""
        pipeline = DataPipeline()
        result = pipeline.load_data(small_df)
        assert result is pipeline  # 链式调用
        assert pipeline.stats.input_rows == 5

    def test_load_data_none(self):
        """加载 None 数据"""
        pipeline = DataPipeline()
        pipeline.load_data(None)
        assert pipeline.stats.input_rows == 0

    def test_load_detection_result(self, tmp_path):
        """load 从 DetectionResult 加载文件"""
        from modules.data_source_detector import AccessProtocol, DataSourceInfo, DetectionResult

        csv_path = tmp_path / "test.csv"
        csv_path.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")

        detection = DetectionResult(
            primary_source=DataSourceInfo(
                source_type=None,
                access_protocol=AccessProtocol.LOCAL_FILE,
                location=str(csv_path),
            )
        )

        pipeline = DataPipeline()
        pipeline.load(detection)
        data = pipeline.execute()
        assert len(data) == 2
        assert list(data.columns) == ["a", "b"]

    def test_load_nonexistent_file(self):
        """加载不存在的文件应抛出异常"""
        from modules.data_source_detector import AccessProtocol, DataSourceInfo, DetectionResult

        detection = DetectionResult(
            primary_source=DataSourceInfo(
                source_type=None,
                access_protocol=AccessProtocol.LOCAL_FILE,
                location="/nonexistent/file.csv",
            )
        )

        pipeline = DataPipeline()
        with pytest.raises(FileNotFoundError):
            pipeline.load(detection)


class TestDataPipelineClean:
    """数据清洗测试"""

    def test_clean_basic(self, small_df):
        """基本清洗流程"""
        pipeline = DataPipeline()
        pipeline.clean(small_df)
        data = pipeline.execute()
        assert len(data) == 5

    def test_clean_with_missing_values(self):
        """含缺失值的清洗"""
        df = pd.DataFrame({"a": [1, None, 3, 4, 5], "b": [10, 20, None, 40, 50]})
        pipeline = DataPipeline(PipelineConfig(fill_missing_strategy="mean"))
        pipeline.clean(df)
        data = pipeline.execute()
        assert data.isnull().sum().sum() == 0

    def test_clean_dedup(self):
        """去重清洗"""
        df = pd.DataFrame({"a": [1, 1, 2, 3], "b": [10, 10, 20, 30]})
        pipeline = DataPipeline()
        pipeline.clean(df)
        data = pipeline.execute()
        assert len(data) == 3

    def test_clean_chaining(self, small_df):
        """链式调用"""
        pipeline = DataPipeline()
        result = pipeline.clean(small_df)
        assert result is pipeline


class TestDataPipelineTransform:
    """数据转换测试"""

    def test_transform_returns_data(self, small_df):
        """transform 返回 DataFrame"""
        pipeline = DataPipeline()
        pipeline.load_data(small_df)
        result = pipeline.transform()
        assert isinstance(result, pd.DataFrame)

    def test_transform_with_data(self, small_df):
        """传入数据的 transform"""
        pipeline = DataPipeline()
        result = pipeline.transform(data=small_df)
        assert len(result) == 5

    def test_transform_none(self):
        """无数据时 transform 返回 None"""
        pipeline = DataPipeline()
        result = pipeline.transform()
        assert result is None


class TestDataPipelineOperations:
    """其他管道操作测试"""

    def test_handle_missing_strategies(self):
        """不同缺失值处理策略"""
        df = pd.DataFrame({"a": [1, None, 3], "b": [4, 5, None]})

        for strategy in ("mean", "median", "forward", "drop"):
            pipeline = DataPipeline(PipelineConfig(fill_missing_strategy=strategy))
            pipeline.load_data(df.copy())
            pipeline.handle_missing()
            result = pipeline.execute()
            assert result is not None

    def test_normalize_minmax(self):
        """MinMax 归一化"""
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        pipeline = DataPipeline(PipelineConfig(normalization_method="minmax"))
        pipeline.load_data(df)
        pipeline.normalize()
        data = pipeline.execute()
        assert data["x"].min() == 0.0
        assert data["x"].max() == 1.0

    def test_normalize_zscore(self):
        """Z-score 归一化"""
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        pipeline = DataPipeline(PipelineConfig(normalization_method="zscore"))
        pipeline.load_data(df)
        pipeline.normalize()
        data = pipeline.execute()
        assert abs(data["x"].mean()) < 1e-10

    def test_detect_anomalies(self):
        """异常值检测"""
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5, 100]})
        pipeline = DataPipeline()
        pipeline.load_data(df)
        anomalies = pipeline.detect_anomalies(columns=["x"])
        assert isinstance(anomalies, dict)

    def test_clip_anomalies(self):
        """异常值截断"""
        df = pd.DataFrame({"x": [1, 2, 3, 4, 5, 100]})
        pipeline = DataPipeline()
        pipeline.load_data(df)
        pipeline._clip_anomalies()
        data = pipeline.execute()
        # 100 应被截断到合理范围
        assert data["x"].max() < 100

    def test_get_stats(self, small_df):
        """统计信息获取"""
        pipeline = DataPipeline()
        pipeline.clean(small_df)
        stats = pipeline.get_stats()
        assert isinstance(stats, PipelineStats)
        assert stats.input_rows == 5

    def test_reset(self, small_df):
        """管道重置"""
        pipeline = DataPipeline()
        pipeline.load_data(small_df)
        pipeline.reset()
        assert pipeline._current_data is None
        assert pipeline.stats.input_rows == 0

    def test_pipeline_log(self, small_df):
        """管道日志"""
        pipeline = DataPipeline()
        pipeline.clean(small_df)
        log = pipeline.pipeline_log
        assert len(log) > 0
        assert any("加载" in entry for entry in log)
