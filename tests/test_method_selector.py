"""方法选择模块测试"""

from __future__ import annotations

import pytest

from modules.method_selector import (
    ALL_METHODS,
    METHOD_REGISTRY,
    DataCharacteristic,
    MethodFamily,
    MethodRecommendation,
    select_method,
)


class TestMethodRegistry:
    """方法注册表测试"""

    def test_registry_has_6_families(self):
        """应有 6 个方法族"""
        assert len(METHOD_REGISTRY) == 6

    def test_all_methods_count(self):
        """应有 17 种方法"""
        assert len(ALL_METHODS) == 17

    def test_each_family_has_methods(self):
        """每个族至少有 1 种方法"""
        for family, methods in METHOD_REGISTRY.items():
            assert len(methods) >= 1, f"族 {family} 无方法"

    def test_registry_values(self):
        """注册表值为 AnalysisMethodInfo 列表"""
        for family_name, methods in METHOD_REGISTRY.items():
            assert isinstance(methods, list)
            for method in methods:
                assert method.family.value == family_name


class TestSelectMethod:
    """select_method 函数测试"""

    def test_regression_selection(self):
        """回归分析选择"""
        rec = select_method(
            "预测销售额", [DataCharacteristic.CONTINUOUS_TARGET], sample_size=100
        )
        assert isinstance(rec, MethodRecommendation)
        assert rec.primary_method is not None

    def test_clustering_selection(self):
        """聚类分析选择"""
        rec = select_method(
            "用户分群聚类", [DataCharacteristic.HIGH_DIMENSIONAL], sample_size=200
        )
        assert rec.primary_method is not None

    def test_time_series_selection(self):
        """时间序列选择"""
        rec = select_method(
            "分析时间趋势", [DataCharacteristic.TIME_INDEXED], sample_size=100
        )
        assert rec.primary_method is not None

    def test_small_sample(self):
        """小样本降级"""
        rec = select_method("分析", data_characteristics=[], sample_size=10)
        assert isinstance(rec, MethodRecommendation)

    def test_confidence_range(self):
        """置信度范围"""
        rec = select_method("回归分析", data_characteristics=[], sample_size=100)
        assert 0.0 <= rec.confidence <= 1.0

    def test_alternatives(self):
        """备选方法"""
        rec = select_method("分类预测", data_characteristics=[], sample_size=200)
        assert isinstance(rec.alternatives, list)
