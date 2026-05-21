"""数据处理管道模块 - 数据清洗、转换与合并"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass
class PipelineStats:
    """管道执行统计"""
    input_rows: int = 0
    output_rows: int = 0
    rows_dropped: int = 0
    duplicates_removed: int = 0
    missing_filled: int = 0
    anomalies_detected: int = 0
    transformations_applied: int = 0


@dataclass
class PipelineConfig:
    """管道配置"""
    fill_missing_strategy: str = "mean"  # mean, median, mode, forward, drop
    duplicate_strategy: str = "first"  # first, last, drop
    normalization_method: str | None = None  # minmax, zscore, robust
    anomaly_detection_method: str = "iqr"  # iqr, zscore, isolation_forest
    anomaly_threshold: float = 1.5
    merge_strategy: str = "inner"  # inner, outer, left, right


@dataclass
class FieldMapping:
    """字段映射"""
    source_field: str
    target_field: str
    transform: Callable[[Any], Any] | None = None


@dataclass
class TimeAlignmentSpec:
    """时间对齐规格"""
    target_frequency: str  # D, W, M, Q, Y
    method: str = "ffill"  # ffill, bfill, interpolate
    fill_value: Any | None = None


class DataPipeline:
    """数据处理管道"""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self.stats = PipelineStats()
        self._current_data: Any = None
        self._pipeline_log: list[str] = []

    @property
    def pipeline_log(self) -> list[str]:
        """获取管道执行日志"""
        return list(self._pipeline_log)

    def load_data(self, data: Any) -> DataPipeline:
        """
        加载输入数据

        Args:
            data: 数据源（DataFrame 兼容对象）

        Returns:
            self（支持链式调用）
        """
        self._current_data = data
        self.stats.input_rows = len(data) if data is not None else 0
        self._log(f"加载数据: {self.stats.input_rows} 行")
        return self

    def handle_missing(self) -> DataPipeline:
        """处理缺失值"""
        if self._current_data is None:
            self._log("跳过缺失值处理: 无数据")
            return self

        strategy = self.config.fill_missing_strategy

        if strategy == "drop":
            before = len(self._current_data)
            self._current_data = self._current_data.dropna()
            dropped = before - len(self._current_data)
            self.stats.rows_dropped += dropped
            self._log(f"删除含缺失值行: {dropped}")
            return self

        missing_count = self._current_data.isnull().sum().sum()
        if missing_count == 0:
            self._log("无缺失值，跳过处理")
            return self

        numeric_cols = self._current_data.select_dtypes(include="number").columns
        object_cols = self._current_data.select_dtypes(include="object").columns

        if strategy == "mean":
            for col in numeric_cols:
                self._current_data[col].fillna(
                    self._current_data[col].mean(), inplace=True
                )
        elif strategy == "median":
            for col in numeric_cols:
                self._current_data[col].fillna(
                    self._current_data[col].median(), inplace=True
                )
        elif strategy == "mode":
            for col in numeric_cols:
                self._current_data[col].fillna(
                    self._current_data[col].mode().iloc[0], inplace=True
                )
        elif strategy == "forward":
            self._current_data.fillna(method="ffill", inplace=True)
            self._current_data.fillna(method="bfill", inplace=True)

        self.stats.missing_filled += int(missing_count)
        self._log(f"填充缺失值: {missing_count} 个 (策略: {strategy})")
        return self

    def deduplicate(self) -> DataPipeline:
        """去除重复数据"""
        if self._current_data is None:
            return self

        before = len(self._current_data)
        keep_map = {"first": "first", "last": "last", "drop": False}
        keep = keep_map.get(self.config.duplicate_strategy, "first")

        if keep is False:
            self._current_data = self._current_data.drop_duplicates(keep=False)
        else:
            self._current_data = self._current_data.drop_duplicates(keep=keep)

        removed = before - len(self._current_data)
        self.stats.duplicates_removed += removed
        self._log(f"去重: 移除 {removed} 条")
        return self

    def normalize(self, columns: list[str] | None = None) -> DataPipeline:
        """
        数据归一化

        Args:
            columns: 需要归一化的列，None 表示所有数值列
        """
        if self._current_data is None:
            return self

        method = self.config.normalization_method
        if method is None:
            self._log("跳过归一化: 未指定方法")
            return self

        target_cols = columns or list(
            self._current_data.select_dtypes(include="number").columns
        )

        for col in target_cols:
            if col not in self._current_data.columns:
                continue

            data_col = self._current_data[col]
            if method == "minmax":
                min_val, max_val = data_col.min(), data_col.max()
                if max_val != min_val:
                    self._current_data[col] = (data_col - min_val) / (max_val - min_val)
            elif method == "zscore":
                mean, std = data_col.mean(), data_col.std()
                if std > 0:
                    self._current_data[col] = (data_col - mean) / std
            elif method == "robust":
                median = data_col.median()
                iqr = data_col.quantile(0.75) - data_col.quantile(0.25)
                if iqr > 0:
                    self._current_data[col] = (data_col - median) / iqr

        self.stats.transformations_applied += len(target_cols)
        self._log(f"归一化: {len(target_cols)} 列 (方法: {method})")
        return self

    def detect_anomalies(
        self, columns: list[str] | None = None
    ) -> dict[str, list[int]]:
        """
        异常值检测

        Args:
            columns: 检测的列

        Returns:
            {列名: 异常值行索引}
        """
        if self._current_data is None:
            return {}

        method = self.config.anomaly_detection_method
        threshold = self.config.anomaly_threshold
        target_cols = columns or list(
            self._current_data.select_dtypes(include="number").columns
        )

        anomalies: dict[str, list[int]] = {}

        for col in target_cols:
            if col not in self._current_data.columns:
                continue

            data_col = self._current_data[col]
            indices: list[int] = []

            if method == "iqr":
                q1, q3 = data_col.quantile(0.25), data_col.quantile(0.75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
                indices = list(
                    self._current_data[
                        (data_col < lower) | (data_col > upper)
                    ].index
                )
            elif method == "zscore":
                mean, std = data_col.mean(), data_col.std()
                if std > 0:
                    z_scores = ((data_col - mean) / std).abs()
                    indices = list(self._current_data[z_scores > threshold].index)

            if indices:
                anomalies[col] = indices

        total = sum(len(v) for v in anomalies.values())
        self.stats.anomalies_detected += total
        self._log(f"异常检测: 发现 {total} 个异常值")
        return anomalies

    def apply_field_mapping(
        self, mappings: list[FieldMapping]
    ) -> DataPipeline:
        """
        应用字段映射

        Args:
            mappings: 字段映射列表
        """
        if self._current_data is None or not mappings:
            return self

        rename_map = {}
        for m in mappings:
            if m.source_field in self._current_data.columns:
                rename_map[m.source_field] = m.target_field
                if m.transform is not None:
                    self._current_data[m.source_field] = self._current_data[
                        m.source_field
                    ].apply(m.transform)

        self._current_data.rename(columns=rename_map, inplace=True)
        self.stats.transformations_applied += len(rename_map)
        self._log(f"字段映射: {len(rename_map)} 个字段")
        return self

    def align_time(
        self,
        time_column: str,
        spec: TimeAlignmentSpec,
    ) -> DataPipeline:
        """
        时间对齐

        Args:
            time_column: 时间列名
            spec: 对齐规格
        """
        if self._current_data is None:
            return self

        if time_column not in self._current_data.columns:
            self._log(f"跳过时间对齐: 列 {time_column} 不存在")
            return self

        self._current_data[time_column] = self._current_data[time_column].astype(
            "datetime64[ns]"
        )
        self._current_data = self._current_data.set_index(time_column).sort_index()

        self._current_data = self._current_data.resample(spec.target_frequency).agg(
            "mean"
        )

        if spec.method == "ffill":
            self._current_data.fillna(method="ffill", inplace=True)
        elif spec.method == "bfill":
            self._current_data.fillna(method="bfill", inplace=True)
        elif spec.method == "interpolate":
            self._current_data.interpolate(method="linear", inplace=True)
        elif spec.fill_value is not None:
            self._current_data.fillna(spec.fill_value, inplace=True)

        self._current_data = self._current_data.reset_index()
        self._log(f"时间对齐: 频率={spec.target_frequency}")
        return self

    def merge(
        self,
        other: Any,
        on: str | list[str],
        strategy: str | None = None,
    ) -> DataPipeline:
        """
        数据合并

        Args:
            other: 合并的另一个数据源
            on: 合并键
            strategy: 合并策略，默认使用配置
        """
        if self._current_data is None:
            return self

        merge_how = strategy or self.config.merge_strategy
        self._current_data = self._current_data.merge(other, on=on, how=merge_how)
        self.stats.transformations_applied += 1
        self._log(f"数据合并: on={on}, how={merge_how}")
        return self

    def filter_rows(self, condition: Callable[[Any], Any]) -> DataPipeline:
        """
        行过滤

        Args:
            condition: 过滤条件函数
        """
        if self._current_data is None:
            return self

        before = len(self._current_data)
        self._current_data = self._current_data[condition(self._current_data)]
        dropped = before - len(self._current_data)
        self.stats.rows_dropped += dropped
        self._log(f"行过滤: 移除 {dropped} 行")
        return self

    def transform_column(
        self, column: str, func: Callable[[Any], Any]
    ) -> DataPipeline:
        """
        列转换

        Args:
            column: 列名
            func: 转换函数
        """
        if self._current_data is None:
            return self

        if column in self._current_data.columns:
            self._current_data[column] = self._current_data[column].apply(func)
            self.stats.transformations_applied += 1
            self._log(f"列转换: {column}")
        return self

    def execute(self) -> Any:
        """
        执行管道并返回结果

        Returns:
            处理后的数据
        """
        if self._current_data is None:
            raise RuntimeError("管道无数据，请先调用 load_data")

        self.stats.output_rows = len(self._current_data)
        self._log(
            f"管道执行完成: "
            f"{self.stats.input_rows} -> {self.stats.output_rows} 行"
        )

        return self._current_data

    def get_stats(self) -> PipelineStats:
        """获取管道统计信息"""
        return self.stats

    def reset(self) -> DataPipeline:
        """重置管道状态"""
        self._current_data = None
        self.stats = PipelineStats()
        self._pipeline_log.clear()
        return self

    def _log(self, message: str) -> None:
        """记录管道日志"""
        self._pipeline_log.append(message)
        logger.info("[Pipeline] %s", message)
