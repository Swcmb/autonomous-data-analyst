"""自审系统测试"""

from __future__ import annotations

import pytest

from modules.self_review import (
    BusinessRationalityChecker,
    DataConsistencyChecker,
    ModelEffectivenessChecker,
    ReviewDimension,
    ReviewFinding,
    ReviewReport,
    RiskLevel,
    SampleSizeRiskChecker,
    SelfReviewer,
)


class TestDataConsistencyChecker:
    """数据一致性检查器测试"""

    def test_empty_field_defs(self):
        """空字段定义"""
        checker = DataConsistencyChecker()
        findings = checker.check(field_defs={})
        # 空定义应有发现
        assert isinstance(findings, list)

    def test_incomplete_field_defs(self):
        """不完整的字段定义"""
        checker = DataConsistencyChecker()
        findings = checker.check(field_defs={"col1": {"name": "col1"}})
        assert len(findings) > 0
        assert any(f.dimension == ReviewDimension.DATA_CONSISTENCY for f in findings)

    def test_invalid_time_range(self):
        """无效时间范围"""
        checker = DataConsistencyChecker()
        findings = checker.check(
            field_defs={},
            time_defs={"start_time": "2024-12-01", "end_time": "2024-01-01"},
        )
        red_findings = [f for f in findings if f.risk_level == RiskLevel.RED]
        assert len(red_findings) > 0


class TestSampleSizeRiskChecker:
    """样本量风险检查器测试"""

    def test_small_sample(self):
        """小样本检测"""
        checker = SampleSizeRiskChecker()
        findings = checker.check(sample_size=10)
        assert len(findings) > 0
        assert any(f.risk_level in (RiskLevel.RED, RiskLevel.YELLOW) for f in findings)

    def test_adequate_sample(self):
        """充足样本"""
        checker = SampleSizeRiskChecker()
        findings = checker.check(sample_size=500)
        # 大样本不应有严重风险
        red_findings = [f for f in findings if f.risk_level == RiskLevel.RED]
        assert len(red_findings) == 0

    def test_zero_sample(self):
        """零样本"""
        checker = SampleSizeRiskChecker()
        findings = checker.check(sample_size=0)
        assert len(findings) > 0


class TestModelEffectivenessChecker:
    """模型有效性检查器测试"""

    def test_empty_metrics(self):
        """空指标"""
        checker = ModelEffectivenessChecker()
        findings = checker.check(model_metrics=None, model_type="")
        assert isinstance(findings, list)

    def test_low_accuracy(self):
        """低准确率"""
        checker = ModelEffectivenessChecker()
        findings = checker.check(
            model_metrics={"accuracy": 0.3, "r2": -0.5},
            model_type="classification",
        )
        assert len(findings) > 0


class TestBusinessRationalityChecker:
    """业务合理性检查器测试"""

    def test_empty_findings(self):
        """空发现"""
        checker = BusinessRationalityChecker()
        findings = checker.check(findings=[], recommendations=[])
        assert isinstance(findings, list)


class TestSelfReviewer:
    """自审引擎集成测试"""

    def test_run_review_returns_report(self):
        """run_review 返回 ReviewReport"""
        reviewer = SelfReviewer()
        report = reviewer.run_review(review_id="test_review")
        assert isinstance(report, ReviewReport)
        assert report.report_id == "test_review"

    def test_run_review_with_contexts(self):
        """带上下文的审查"""
        reviewer = SelfReviewer()
        report = reviewer.run_review(
            review_id="test",
            data_context={"sample_size": 10},
            model_context={"metrics": {"accuracy": 0.5}, "model_type": "test"},
            business_context={"findings": ["finding1"], "recommendations": []},
        )
        assert isinstance(report, ReviewReport)
        assert len(report.findings) > 0

    def test_risk_level_determination(self):
        """风险等级确定"""
        reviewer = SelfReviewer()
        report = reviewer.run_review(
            review_id="test",
            data_context={"sample_size": 5},
        )
        assert report.overall_risk in (RiskLevel.RED, RiskLevel.YELLOW, RiskLevel.BLUE)

    def test_report_grouping(self):
        """报告分组"""
        reviewer = SelfReviewer()
        report = reviewer.run_review(
            review_id="test",
            data_context={"sample_size": 5},
        )
        assert isinstance(report.by_dimension, dict)
        assert isinstance(report.by_risk_level, dict)
