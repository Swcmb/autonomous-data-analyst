"""自审验证系统 - 对分析结果进行四维度的自动审查"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """风险等级"""
    RED = "red"        # 关键问题，必须修复
    YELLOW = "yellow"  # 需要注意，建议优化
    BLUE = "blue"      # 提示信息，可选处理


class ReviewDimension(Enum):
    """审核维度"""
    DATA_CONSISTENCY = "data_consistency"
    SAMPLE_SIZE_RISK = "sample_size_risk"
    MODEL_EFFECTIVENESS = "model_effectiveness"
    BUSINESS_RATIONALITY = "business_rationality"


@dataclass
class ReviewFinding:
    """单个审查发现"""
    finding_id: str
    dimension: ReviewDimension
    risk_level: RiskLevel
    description: str
    evidence: str = ""
    suggestion: str = ""
    severity_score: float = 0.0  # 0-10，数值越大越严重


@dataclass
class ReviewReport:
    """审查报告"""
    report_id: str = ""
    overall_risk: RiskLevel = RiskLevel.BLUE
    findings: list[ReviewFinding] = field(default_factory=list)
    summary: str = ""
    by_dimension: dict[str, list[ReviewFinding]] = field(default_factory=dict)
    by_risk_level: dict[str, list[ReviewFinding]] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


# 小样本阈值定义
SMALL_SAMPLE_THRESHOLD = 30
MODERATE_SAMPLE_THRESHOLD = 100


class DataConsistencyChecker:
    """数据一致性检查器"""

    def check(
        self,
        field_defs: dict[str, Any],
        time_defs: dict[str, Any] | None = None,
        aggregation_logic: dict[str, Any] | None = None,
        join_specs: list[dict[str, Any]] | None = None,
    ) -> list[ReviewFinding]:
        """
        检查数据一致性

        Args:
            field_defs: 字段定义字典
            time_defs: 时间定义（起始时间、结束时间、时区等）
            aggregation_logic: 聚合逻辑描述
            join_specs: JOIN规格列表

        Returns:
            审查发现列表
        """
        findings: list[ReviewFinding] = []
        findings.extend(self._check_field_consistency(field_defs))
        findings.extend(self._check_time_consistency(time_defs or {}))
        findings.extend(self._check_aggregation_logic(aggregation_logic or {}))
        findings.extend(self._check_join_correctness(join_specs or []))
        return findings

    def _check_field_consistency(
        self, field_defs: dict[str, Any]
    ) -> list[ReviewFinding]:
        """检查字段定义的一致性"""
        findings: list[ReviewFinding] = []
        required_keys = {"name", "type", "nullable"}
        missing_fields = []

        for field_name, definition in field_defs.items():
            if not isinstance(definition, dict):
                missing_fields.append(field_name)
                continue
            missing = required_keys - set(definition.keys())
            if missing:
                missing_fields.append(field_name)

        if missing_fields:
            findings.append(ReviewFinding(
                finding_id="field_def_incomplete",
                dimension=ReviewDimension.DATA_CONSISTENCY,
                risk_level=RiskLevel.YELLOW,
                description=f"以下字段定义不完整: {', '.join(missing_fields)}",
                suggestion="补充字段的类型、可空性等元数据定义",
                severity_score=5.0,
            ))

        return findings

    def _check_time_consistency(
        self, time_defs: dict[str, Any]
    ) -> list[ReviewFinding]:
        """检查时间定义的一致性"""
        findings: list[ReviewFinding] = []
        if not time_defs:
            return findings

        start = time_defs.get("start_time")
        end = time_defs.get("end_time")
        timezone = time_defs.get("timezone")

        if start and end and start > end:
            findings.append(ReviewFinding(
                finding_id="time_range_invalid",
                dimension=ReviewDimension.DATA_CONSISTENCY,
                risk_level=RiskLevel.RED,
                description="时间范围定义异常：起始时间晚于结束时间",
                suggestion="检查并修正时间范围定义",
                severity_score=9.0,
            ))

        if not timezone:
            findings.append(ReviewFinding(
                finding_id="timezone_missing",
                dimension=ReviewDimension.DATA_CONSISTENCY,
                risk_level=RiskLevel.BLUE,
                description="未指定时区，可能导致时间计算偏差",
                suggestion="明确指定分析使用的时区（如 Asia/Shanghai）",
                severity_score=3.0,
            ))

        return findings

    def _check_aggregation_logic(
        self, logic: dict[str, Any]
    ) -> list[ReviewFinding]:
        """检查聚合逻辑的合理性"""
        findings: list[ReviewFinding] = []
        if not logic:
            return findings

        group_by = logic.get("group_by", [])
        agg_functions = logic.get("aggregations", [])

        if not group_by and agg_functions:
            findings.append(ReviewFinding(
                finding_id="global_aggregation",
                dimension=ReviewDimension.DATA_CONSISTENCY,
                risk_level=RiskLevel.YELLOW,
                description="聚合操作缺少 GROUP BY 子句，将进行全局聚合",
                suggestion="确认是否需要对全局数据进行聚合，或添加合适的分组字段",
                severity_score=6.0,
            ))

        return findings

    def _check_join_correctness(
        self, join_specs: list[dict[str, Any]]
    ) -> list[ReviewFinding]:
        """检查 JOIN 操作的正确性"""
        findings: list[ReviewFinding] = []
        for i, spec in enumerate(join_specs):
            left_keys = spec.get("left_keys", [])
            right_keys = spec.get("right_keys", [])

            if len(left_keys) != len(right_keys):
                findings.append(ReviewFinding(
                    finding_id=f"join_key_mismatch_{i}",
                    dimension=ReviewDimension.DATA_CONSISTENCY,
                    risk_level=RiskLevel.RED,
                    description=f"JOIN 操作 #{i+1} 的键数量不匹配",
                    evidence=f"左表键: {left_keys}, 右表键: {right_keys}",
                    suggestion="确保左右表的 JOIN 键数量和类型一致",
                    severity_score=8.5,
                ))

        return findings


class SampleSizeRiskChecker:
    """样本量风险检查器"""

    def check(
        self,
        sample_size: int,
        group_sizes: dict[str, int] | None = None,
        population_size: int | None = None,
    ) -> list[ReviewFinding]:
        """
        检查样本量相关风险

        Args:
            sample_size: 总样本量
            group_sizes: 各分组样本量
            population_size: 总体规模

        Returns:
            审查发现列表
        """
        findings: list[ReviewFinding] = []
        findings.extend(self._check_small_sample(sample_size))
        findings.extend(self._check_bias_risk(sample_size, population_size))
        findings.extend(self._check_data_skew(group_sizes))
        return findings

    def _check_small_sample(self, sample_size: int) -> list[ReviewFinding]:
        """检查小样本风险"""
        findings: list[ReviewFinding] = []

        if sample_size < SMALL_SAMPLE_THRESHOLD:
            findings.append(ReviewFinding(
                finding_id="small_sample_critical",
                dimension=ReviewDimension.SAMPLE_SIZE_RISK,
                risk_level=RiskLevel.RED,
                description=f"样本量过小 ({sample_size})，低于统计学最低要求 ({SMALL_SAMPLE_THRESHOLD})",
                suggestion="扩大样本量或说明分析局限性",
                severity_score=9.0,
            ))
        elif sample_size < MODERATE_SAMPLE_THRESHOLD:
            findings.append(ReviewFinding(
                finding_id="small_sample_warning",
                dimension=ReviewDimension.SAMPLE_SIZE_RISK,
                risk_level=RiskLevel.YELLOW,
                description=f"样本量偏小 ({sample_size})，分析结果可能存在较大波动",
                suggestion="谨慎解读结果，建议扩大样本量后复核",
                severity_score=6.0,
            ))

        return findings

    def _check_bias_risk(
        self, sample_size: int, population_size: int | None
    ) -> list[ReviewFinding]:
        """检查样本偏差风险"""
        findings: list[ReviewFinding] = []
        if population_size is None:
            return findings

        coverage = sample_size / max(population_size, 1)
        if coverage < 0.05 and population_size > 10000:
            findings.append(ReviewFinding(
                finding_id="sample_coverage_low",
                dimension=ReviewDimension.SAMPLE_SIZE_RISK,
                risk_level=RiskLevel.YELLOW,
                description=f"样本覆盖率过低 ({coverage:.2%})，可能存在选择偏差",
                suggestion="评估样本代表性，考虑分层抽样或加权处理",
                severity_score=6.5,
            ))

        return findings

    def _check_data_skew(
        self, group_sizes: dict[str, int] | None
    ) -> list[ReviewFinding]:
        """检查数据倾斜"""
        findings: list[ReviewFinding] = []
        if not group_sizes or len(group_sizes) < 2:
            return findings

        sizes = list(group_sizes.values())
        max_size = max(sizes)
        min_size = min(sizes)
        ratio = max_size / max(min_size, 1)

        if ratio > 10:
            findings.append(ReviewFinding(
                finding_id="data_skew_severe",
                dimension=ReviewDimension.SAMPLE_SIZE_RISK,
                risk_level=RiskLevel.RED,
                description=f"分组样本量严重失衡，最大/最小比例: {ratio:.1f}",
                evidence=f"分组样本量: {group_sizes}",
                suggestion="考虑重采样、过采样小类或欠采样大类",
                severity_score=8.0,
            ))
        elif ratio > 5:
            findings.append(ReviewFinding(
                finding_id="data_skew_moderate",
                dimension=ReviewDimension.SAMPLE_SIZE_RISK,
                risk_level=RiskLevel.YELLOW,
                description=f"分组样本量存在失衡，最大/最小比例: {ratio:.1f}",
                suggestion="注意样本不平衡对分析结果的影响",
                severity_score=5.5,
            ))

        return findings


class ModelEffectivenessChecker:
    """模型有效性检查器"""

    def check(
        self,
        model_metrics: dict[str, float] | None = None,
        model_type: str = "",
        cv_results: dict[str, float] | None = None,
    ) -> list[ReviewFinding]:
        """
        检查模型有效性

        Args:
            model_metrics: 模型评估指标（准确率、R²、RMSE 等）
            model_type: 模型类型
            cv_results: 交叉验证结果

        Returns:
            审查发现列表
        """
        findings: list[ReviewFinding] = []
        metrics = model_metrics or {}
        findings.extend(self._check_goodness_of_fit(metrics, model_type))
        findings.extend(self._check_error_rate(metrics, model_type))
        findings.extend(self._check_stability(cv_results))
        findings.extend(self._check_overfitting(metrics, cv_results))
        return findings

    def _check_goodness_of_fit(
        self, metrics: dict[str, float], model_type: str
    ) -> list[ReviewFinding]:
        """检查模型拟合度"""
        findings: list[ReviewFinding] = []

        r_squared = metrics.get("r_squared") or metrics.get("r2")
        if r_squared is not None:
            if r_squared < 0.3:
                findings.append(ReviewFinding(
                    finding_id="poor_fit",
                    dimension=ReviewDimension.MODEL_EFFECTIVENESS,
                    risk_level=RiskLevel.RED,
                    description=f"模型拟合度差 (R²={r_squared:.3f})，解释能力不足",
                    suggestion="考虑添加特征、调整模型或使用非线性方法",
                    severity_score=8.0,
                ))
            elif r_squared < 0.5:
                findings.append(ReviewFinding(
                    finding_id="moderate_fit",
                    dimension=ReviewDimension.MODEL_EFFECTIVENESS,
                    risk_level=RiskLevel.YELLOW,
                    description=f"模型拟合度一般 (R²={r_squared:.3f})",
                    suggestion="可尝试特征工程或模型调优提升拟合度",
                    severity_score=5.0,
                ))

        accuracy = metrics.get("accuracy")
        if accuracy is not None and accuracy < 0.5:
            findings.append(ReviewFinding(
                finding_id="low_accuracy",
                dimension=ReviewDimension.MODEL_EFFECTIVENESS,
                risk_level=RiskLevel.RED,
                description=f"模型准确率低 (accuracy={accuracy:.3f})，低于随机猜测",
                suggestion="检查特征质量、数据标注或更换模型",
                severity_score=9.0,
            ))

        return findings

    def _check_error_rate(
        self, metrics: dict[str, float], model_type: str
    ) -> list[ReviewFinding]:
        """检查模型错误率"""
        findings: list[ReviewFinding] = []

        mae = metrics.get("mae")
        rmse = metrics.get("rmse")
        if mae is not None and rmse is not None:
            if rmse > mae * 2:
                findings.append(ReviewFinding(
                    finding_id="outlier_impact",
                    dimension=ReviewDimension.MODEL_EFFECTIVENESS,
                    risk_level=RiskLevel.YELLOW,
                    description="RMSE 显著大于 MAE，可能存在异常值影响",
                    suggestion="检查并处理数据中的异常值",
                    severity_score=5.5,
                ))

        return findings

    def _check_stability(
        self, cv_results: dict[str, float] | None
    ) -> list[ReviewFinding]:
        """检查模型稳定性"""
        findings: list[ReviewFinding] = []
        if not cv_results:
            return findings

        scores = cv_results.get("cv_scores", [])
        if len(scores) >= 2:
            mean_score = sum(scores) / len(scores)
            std_dev = _calculate_std(scores, mean_score)
            cv_ratio = std_dev / max(mean_score, 1e-10)

            if cv_ratio > 0.2:
                findings.append(ReviewFinding(
                    finding_id="model_unstable",
                    dimension=ReviewDimension.MODEL_EFFECTIVENESS,
                    risk_level=RiskLevel.RED,
                    description=f"模型不稳定，交叉验证变异系数: {cv_ratio:.2%}",
                    evidence=f"CV 均值: {mean_score:.4f}, 标准差: {std_dev:.4f}",
                    suggestion="增加样本量、正则化或简化模型",
                    severity_score=7.5,
                ))
            elif cv_ratio > 0.1:
                findings.append(ReviewFinding(
                    finding_id="model_moderate_variance",
                    dimension=ReviewDimension.MODEL_EFFECTIVENESS,
                    risk_level=RiskLevel.YELLOW,
                    description=f"模型存在一定波动，交叉验证变异系数: {cv_ratio:.2%}",
                    suggestion="监控模型表现，必要时进行调优",
                    severity_score=4.5,
                ))

        return findings

    def _check_overfitting(
        self,
        metrics: dict[str, float],
        cv_results: dict[str, float] | None,
    ) -> list[ReviewFinding]:
        """检查过拟合风险"""
        findings: list[ReviewFinding] = []
        if not cv_results:
            return findings

        train_score = metrics.get("train_score", 1.0)
        val_score = cv_results.get("val_score") or cv_results.get("cv_mean")

        if val_score is not None:
            gap = train_score - val_score
            if gap > 0.3:
                findings.append(ReviewFinding(
                    finding_id="overfitting_critical",
                    dimension=ReviewDimension.MODEL_EFFECTIVENESS,
                    risk_level=RiskLevel.RED,
                    description=f"模型过拟合严重，训练/验证差距: {gap:.3f}",
                    suggestion="使用正则化、减少特征或增加训练数据",
                    severity_score=8.5,
                ))
            elif gap > 0.15:
                findings.append(ReviewFinding(
                    finding_id="overfitting_warning",
                    dimension=ReviewDimension.MODEL_EFFECTIVENESS,
                    risk_level=RiskLevel.YELLOW,
                    description=f"模型存在过拟合倾向，训练/验证差距: {gap:.3f}",
                    suggestion="考虑交叉验证早停或增加正则化强度",
                    severity_score=6.0,
                ))

        return findings


class BusinessRationalityChecker:
    """业务合理性检查器"""

    def check(
        self,
        findings: list[str],
        recommendations: list[str],
        business_context: dict[str, Any] | None = None,
    ) -> list[ReviewFinding]:
        """
        检查分析结论的业务合理性

        Args:
            findings: 分析发现列表
            recommendations: 建议列表
            business_context: 业务上下文

        Returns:
            审查发现列表
        """
        review_findings: list[ReviewFinding] = []
        review_findings.extend(self._check_actionability(recommendations))
        review_findings.extend(
            self._check_business_common_sense(findings, business_context or {})
        )
        review_findings.extend(
            self._check_over_inference(findings, recommendations)
        )
        return review_findings

    def _check_actionability(
        self, recommendations: list[str]
    ) -> list[ReviewFinding]:
        """检查建议的可操作性"""
        findings: list[ReviewFinding] = []
        if not recommendations:
            findings.append(ReviewFinding(
                finding_id="no_recommendations",
                dimension=ReviewDimension.BUSINESS_RATIONALITY,
                risk_level=RiskLevel.YELLOW,
                description="分析未提供具体建议，结论缺乏可操作性",
                suggestion="基于分析发现补充可落地的业务建议",
                severity_score=5.0,
            ))
            return findings

        actionable_count = sum(
            1 for rec in recommendations if _is_actionable(rec)
        )
        ratio = actionable_count / len(recommendations)

        if ratio < 0.5:
            findings.append(ReviewFinding(
                finding_id="low_actionability",
                dimension=ReviewDimension.BUSINESS_RATIONALITY,
                risk_level=RiskLevel.YELLOW,
                description=f"仅 {ratio:.0%} 的建议具有可操作性",
                suggestion="确保每条建议都包含明确的行动指引",
                severity_score=5.5,
            ))

        return findings

    def _check_business_common_sense(
        self,
        findings: list[str],
        context: dict[str, Any],
    ) -> list[ReviewFinding]:
        """检查是否违背业务常识"""
        review_findings: list[ReviewFinding] = []
        business_rules = context.get("rules", [])

        for finding in findings:
            for rule in business_rules:
                if _contradicts_rule(finding, rule):
                    review_findings.append(ReviewFinding(
                        finding_id=f"contradicts_rule_{hash(rule) % 10000}",
                        dimension=ReviewDimension.BUSINESS_RATIONALITY,
                        risk_level=RiskLevel.RED,
                        description=f"分析结论与业务规则冲突: {rule}",
                        evidence=finding,
                        suggestion="重新审视分析逻辑，确保与业务规则一致",
                        severity_score=9.0,
                    ))

        return review_findings

    def _check_over_inference(
        self,
        findings: list[str],
        recommendations: list[str],
    ) -> list[ReviewFinding]:
        """检查是否存在过度推断"""
        findings_list: list[ReviewFinding] = []

        strong_words = ["必然", "确定", "绝对", "100%", "完全", "导致"]
        for rec in recommendations:
            matched = [w for w in strong_words if w in rec]
            if len(matched) >= 2:
                findings_list.append(ReviewFinding(
                    finding_id=f"over_inference_{hash(rec) % 10000}",
                    dimension=ReviewDimension.BUSINESS_RATIONALITY,
                    risk_level=RiskLevel.YELLOW,
                    description=f"建议中存在过度推断，使用了绝对化表述: {matched}",
                    evidence=rec,
                    suggestion="使用更审慎的表述，如'可能'、'倾向'等",
                    severity_score=6.0,
                ))

        return findings_list


def _calculate_std(values: list[float], mean: float) -> float:
    """计算标准差"""
    if len(values) < 2:
        return 0.0
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5


def _is_actionable(text: str) -> bool:
    """判断建议是否具有可操作性"""
    action_keywords = ["增加", "减少", "优化", "调整", "实施", "验证", "测试"]
    return any(kw in text for kw in action_keywords)


def _contradicts_rule(finding: str, rule: str) -> bool:
    """判断发现是否与规则冲突"""
    contradiction_markers = ["不相关", "无影响", "负相关"]
    rule_markers = ["必须", "不能", "禁止", "要求"]
    return (
        any(m in finding for m in contradiction_markers)
        and any(m in rule for m in rule_markers)
    )


class SelfReviewer:
    """自审引擎 - 执行四维度的自动审查"""

    def __init__(self) -> None:
        self.consistency_checker = DataConsistencyChecker()
        self.sample_checker = SampleSizeRiskChecker()
        self.model_checker = ModelEffectivenessChecker()
        self.business_checker = BusinessRationalityChecker()

    def run_review(
        self,
        review_id: str,
        data_context: dict[str, Any] | None = None,
        model_context: dict[str, Any] | None = None,
        business_context: dict[str, Any] | None = None,
    ) -> ReviewReport:
        """
        执行完整的四维审查

        Args:
            review_id: 审查标识
            data_context: 数据上下文（字段定义、样本信息等）
            model_context: 模型上下文（指标、交叉验证等）
            business_context: 业务上下文（规则、发现、建议等）

        Returns:
            ReviewReport: 审查报告
        """
        all_findings: list[ReviewFinding] = []

        all_findings.extend(self._review_data_consistency(data_context or {}))
        all_findings.extend(self._review_sample_size(data_context or {}))
        all_findings.extend(self._review_model_effectiveness(model_context or {}))
        all_findings.extend(self._review_business_rationality(business_context or {}))

        report = ReviewReport(
            report_id=review_id,
            findings=all_findings,
        )

        report.overall_risk = _determine_overall_risk(all_findings)
        report.by_dimension = _group_by_dimension(all_findings)
        report.by_risk_level = _group_by_risk_level(all_findings)
        report.summary = _build_review_summary(report)
        report.recommendations = _extract_recommendations(all_findings)

        logger.info("自审完成: 风险等级=%s, 发现数=%d", report.overall_risk.value, len(all_findings))

        return report

    def _review_data_consistency(
        self, context: dict[str, Any]
    ) -> list[ReviewFinding]:
        """执行数据一致性审查"""
        field_defs = context.get("field_defs", {})
        time_defs = context.get("time_defs")
        agg_logic = context.get("aggregation_logic")
        join_specs = context.get("join_specs")
        return self.consistency_checker.check(field_defs, time_defs, agg_logic, join_specs)

    def _review_sample_size(
        self, context: dict[str, Any]
    ) -> list[ReviewFinding]:
        """执行样本量风险审查"""
        sample_size = context.get("sample_size", 0)
        group_sizes = context.get("group_sizes")
        population_size = context.get("population_size")
        return self.sample_checker.check(sample_size, group_sizes, population_size)

    def _review_model_effectiveness(
        self, context: dict[str, Any]
    ) -> list[ReviewFinding]:
        """执行模型有效性审查"""
        metrics = context.get("metrics")
        model_type = context.get("model_type", "")
        cv_results = context.get("cv_results")
        return self.model_checker.check(metrics, model_type, cv_results)

    def _review_business_rationality(
        self, context: dict[str, Any]
    ) -> list[ReviewFinding]:
        """执行业务合理性审查"""
        findings = context.get("findings", [])
        recommendations = context.get("recommendations", [])
        return self.business_checker.check(findings, recommendations, context)


def _determine_overall_risk(findings: list[ReviewFinding]) -> RiskLevel:
    """根据所有发现确定整体风险等级"""
    if not findings:
        return RiskLevel.BLUE

    max_severity = max(f.severity_score for f in findings)

    if max_severity >= 8.0:
        return RiskLevel.RED
    if max_severity >= 5.0:
        return RiskLevel.YELLOW
    return RiskLevel.BLUE


def _group_by_dimension(
    findings: list[ReviewFinding]
) -> dict[str, list[ReviewFinding]]:
    """按维度分组"""
    groups: dict[str, list[ReviewFinding]] = {}
    for finding in findings:
        key = finding.dimension.value
        groups.setdefault(key, []).append(finding)
    return groups


def _group_by_risk_level(
    findings: list[ReviewFinding]
) -> dict[str, list[ReviewFinding]]:
    """按风险等级分组"""
    groups: dict[str, list[ReviewFinding]] = {}
    for finding in findings:
        key = finding.risk_level.value
        groups.setdefault(key, []).append(finding)
    return groups


def _build_review_summary(report: ReviewReport) -> str:
    """构建审查摘要"""
    parts: list[str] = []
    parts.append(f"审查报告 {report.report_id}")
    parts.append(f"整体风险等级: {report.overall_risk.value}")
    parts.append(f"共发现 {len(report.findings)} 个问题")

    if report.by_risk_level.get(RiskLevel.RED.value):
        red_count = len(report.by_risk_level[RiskLevel.RED.value])
        parts.append(f"其中 {red_count} 个关键问题需立即处理")

    if report.by_dimension:
        for dim, dim_findings in report.by_dimension.items():
            parts.append(f"- {dim}: {len(dim_findings)} 个发现")

    return "\n".join(parts)


def _extract_recommendations(findings: list[ReviewFinding]) -> list[str]:
    """从审查发现中提取建议"""
    return [
        f.suggestion
        for f in findings
        if f.suggestion
    ]
