"""假设跟踪模块 - 记录、验证和报告分析过程中的所有假设"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """置信度等级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationStatus(Enum):
    """验证状态"""
    PENDING = "pending"
    VALIDATED = "validated"
    INVALIDATED = "invalidated"
    UNTESTABLE = "untestable"


class AssumptionCategory(Enum):
    """假设类别"""
    DATA_QUALITY = "data_quality"
    STATISTICAL = "statistical"
    BUSINESS = "business"
    METHODOLOGICAL = "methodological"
    CAUSAL = "causal"


@dataclass
class Assumption:
    """单个假设"""
    assumption_id: str
    description: str
    category: AssumptionCategory
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    status: ValidationStatus = ValidationStatus.PENDING
    evidence: list[str] = field(default_factory=list)
    counter_evidence: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    validated_at: str | None = None
    impact_if_wrong: str = "medium"  # low, medium, high
    related_steps: list[str] = field(default_factory=list)


@dataclass
class AssumptionReport:
    """假设报告"""
    total_count: int = 0
    by_confidence: dict[str, int] = field(default_factory=dict)
    by_status: dict[str, int] = field(default_factory=dict)
    by_category: dict[str, int] = field(default_factory=dict)
    unvalidated: list[str] = field(default_factory=list)
    invalidated: list[str] = field(default_factory=list)
    risk_assessment: str = ""
    summary: str = ""


class AssumptionTracker:
    """假设跟踪器 - 管理分析全生命周期的假设"""

    def __init__(self, analysis_id: str = "") -> None:
        self.analysis_id = analysis_id
        self._assumptions: dict[str, Assumption] = {}

    def add_assumption(
        self,
        assumption_id: str,
        description: str,
        category: AssumptionCategory,
        confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM,
        impact_if_wrong: str = "medium",
        related_steps: list[str] | None = None,
    ) -> Assumption:
        """
        添加新假设

        Args:
            assumption_id: 假设标识
            description: 假设描述
            category: 假设类别
            confidence: 置信度
            impact_if_wrong: 假设错误的潜在影响
            related_steps: 相关的分析步骤

        Returns:
            创建的假设对象
        """
        if assumption_id in self._assumptions:
            return self._assumptions[assumption_id]

        assumption = Assumption(
            assumption_id=assumption_id,
            description=description,
            category=category,
            confidence=confidence,
            impact_if_wrong=impact_if_wrong,
            related_steps=related_steps or [],
        )

        self._assumptions[assumption_id] = assumption
        logger.info("添加假设: %s [%s]", assumption_id, category.value)

        return assumption

    def validate_assumption(
        self,
        assumption_id: str,
        status: ValidationStatus,
        evidence: list[str] | None = None,
        counter_evidence: list[str] | None = None,
    ) -> bool:
        """
        验证假设状态

        Args:
            assumption_id: 假设标识
            status: 验证结果状态
            evidence: 支持性证据
            counter_evidence: 反面证据

        Returns:
            是否成功更新
        """
        assumption = self._assumptions.get(assumption_id)
        if assumption is None:
            return False

        assumption.status = status
        assumption.validated_at = datetime.now().isoformat()

        if evidence:
            assumption.evidence.extend(evidence)

        if counter_evidence:
            assumption.counter_evidence.extend(counter_evidence)

        logger.info("假设验证: %s -> %s", assumption_id, status.value)

        return True

    def update_confidence(
        self,
        assumption_id: str,
        new_confidence: ConfidenceLevel,
    ) -> bool:
        """更新假设置信度"""
        assumption = self._assumptions.get(assumption_id)
        if assumption is None:
            return False

        assumption.confidence = new_confidence
        return True

    def add_evidence(
        self,
        assumption_id: str,
        evidence: str,
        is_counter: bool = False,
    ) -> bool:
        """添加证据到假设"""
        assumption = self._assumptions.get(assumption_id)
        if assumption is None:
            return False

        if is_counter:
            assumption.counter_evidence.append(evidence)
        else:
            assumption.evidence.append(evidence)

        return True

    def get_assumption(self, assumption_id: str) -> Assumption | None:
        """获取单个假设"""
        return self._assumptions.get(assumption_id)

    def get_all_assumptions(self) -> list[Assumption]:
        """获取所有假设"""
        return list(self._assumptions.values())

    def get_by_status(self, status: ValidationStatus) -> list[Assumption]:
        """按状态获取假设"""
        return [
            a for a in self._assumptions.values()
            if a.status == status
        ]

    def get_by_category(self, category: AssumptionCategory) -> list[Assumption]:
        """按类别获取假设"""
        return [
            a for a in self._assumptions.values()
            if a.category == category
        ]

    def get_high_risk(self) -> list[Assumption]:
        """获取高风险假设（低置信度 + 高影响）"""
        return [
            a for a in self._assumptions.values()
            if (a.confidence == ConfidenceLevel.LOW
                and a.impact_if_wrong == "high")
        ]

    def validate_against_data(
        self,
        data_summary: dict[str, Any],
    ) -> dict[str, bool]:
        """
        根据实际数据验证假设

        Args:
            data_summary: 数据摘要，包含 shape、missing_ratio 等

        Returns:
            假设 ID -> 验证结果的映射
        """
        results: dict[str, bool] = {}

        for aid, assumption in self._assumptions.items():
            validated = _check_assumption(assumption, data_summary)
            results[aid] = validated

            status = (
                ValidationStatus.VALIDATED
                if validated
                else ValidationStatus.INVALIDATED
            )
            self.validate_assumption(aid, status)

        return results

    def generate_report(self) -> AssumptionReport:
        """生成假设报告"""
        all_assumptions = list(self._assumptions.values())

        report = AssumptionReport(
            total_count=len(all_assumptions),
            by_confidence=self._count_by_field("confidence"),
            by_status=self._count_by_field("status"),
            by_category=self._count_by_field("category"),
            unvalidated=[
                a.assumption_id
                for a in all_assumptions
                if a.status == ValidationStatus.PENDING
            ],
            invalidated=[
                a.assumption_id
                for a in all_assumptions
                if a.status == ValidationStatus.INVALIDATED
            ],
        )

        report.risk_assessment = _assess_risk(all_assumptions)
        report.summary = _build_summary(report)

        return report

    def clear(self) -> None:
        """清空所有假设"""
        self._assumptions.clear()

    def _count_by_field(self, field_name: str) -> dict[str, int]:
        """按字段值统计数量"""
        counts: dict[str, int] = {}

        for assumption in self._assumptions.values():
            value = getattr(assumption, field_name, None)
            if value is None:
                continue

            key = value.value if hasattr(value, "value") else str(value)
            counts[key] = counts.get(key, 0) + 1

        return counts


def _check_assumption(
    assumption: Assumption,
    data_summary: dict[str, Any],
) -> bool:
    """检查单个假设是否与数据一致"""
    category = assumption.category

    if category == AssumptionCategory.DATA_QUALITY:
        return _check_data_quality(assumption, data_summary)

    if category == AssumptionCategory.STATISTICAL:
        return _check_statistical(assumption, data_summary)

    return True


def _check_data_quality(
    assumption: Assumption,
    data_summary: dict[str, Any],
) -> bool:
    """验证数据质量相关假设"""
    missing_ratio = data_summary.get("missing_ratio", 0.0)

    if "缺失" in assumption.description or "missing" in assumption.description:
        if missing_ratio > 0.3:
            return False

    return True


def _check_statistical(
    assumption: Assumption,
    data_summary: dict[str, Any],
) -> bool:
    """验证统计相关假设"""
    shape = data_summary.get("shape")

    if shape is not None:
        sample_size = shape[0] if isinstance(shape, (list, tuple)) else 0
        if sample_size < 30:
            if "正态" in assumption.description:
                return False

    return True


def _assess_risk(assumptions: list[Assumption]) -> str:
    """评估整体风险"""
    if not assumptions:
        return "无假设记录"

    high_risk_count = sum(
        1 for a in assumptions
        if a.confidence == ConfidenceLevel.LOW
        and a.impact_if_wrong == "high"
    )

    unvalidated_count = sum(
        1 for a in assumptions
        if a.status == ValidationStatus.PENDING
    )

    invalidated_count = sum(
        1 for a in assumptions
        if a.status == ValidationStatus.INVALIDATED
    )

    if invalidated_count > 0:
        return f"高风险: {invalidated_count} 个假设已被推翻"

    if high_risk_count > 2:
        return f"中高风险: {high_risk_count} 个假设置信度低且影响大"

    if unvalidated_count > len(assumptions) * 0.5:
        return f"中等风险: {unvalidated_count} 个假设未验证"

    return "风险较低"


def _build_summary(report: AssumptionReport) -> str:
    """构建报告摘要"""
    parts: list[str] = []

    parts.append(f"共记录 {report.total_count} 个假设")

    if report.invalidated:
        parts.append(
            f"{len(report.invalidated)} 个假设已被推翻: "
            f"{', '.join(report.invalidated)}"
        )

    if report.unvalidated:
        parts.append(
            f"{len(report.unvalidated)} 个假设待验证: "
            f"{', '.join(report.unvalidated)}"
        )

    parts.append(f"风险评估: {report.risk_assessment}")

    return "。".join(parts) + "。"


def create_default_assumptions(
    tracker: AssumptionTracker,
    analysis_type: str = "",
) -> list[Assumption]:
    """
    为常见分析类型创建默认假设

    Args:
        tracker: 假设跟踪器
        analysis_type: 分析类型

    Returns:
        创建的假设列表
    """
    defaults: dict[str, list[tuple[str, str, AssumptionCategory]]] = {
        "regression": [
            ("linearity", "变量间存在线性关系", AssumptionCategory.STATISTICAL),
            ("homoscedasticity", "残差方差恒定", AssumptionCategory.STATISTICAL),
            ("no_multicollinearity", "特征间无强共线性", AssumptionCategory.STATISTICAL),
        ],
        "time_series": [
            ("stationarity", "时间序列平稳或可差分平稳", AssumptionCategory.STATISTICAL),
            ("no_structural_break", "无结构性突变", AssumptionCategory.STATISTICAL),
        ],
        "ab_test": [
            ("random_assignment", "随机分组有效", AssumptionCategory.CAUSAL),
            ("no_interference", "组间无干扰 (SUTVA)", AssumptionCategory.CAUSAL),
            ("parallel_trends", "处理组与对照组趋势平行", AssumptionCategory.CAUSAL),
        ],
    }

    assumptions: list[Assumption] = []
    type_defaults = defaults.get(analysis_type, [])

    for aid, desc, category in type_defaults:
        assumption = tracker.add_assumption(
            assumption_id=f"{analysis_type}_{aid}",
            description=desc,
            category=category,
        )
        assumptions.append(assumption)

    # 添加通用假设
    tracker.add_assumption(
        assumption_id="data_representative",
        description="样本数据能代表总体",
        category=AssumptionCategory.DATA_QUALITY,
        confidence=ConfidenceLevel.MEDIUM,
    )

    tracker.add_assumption(
        assumption_id="measurement_valid",
        description="测量工具和方法有效",
        category=AssumptionCategory.METHODOLOGICAL,
        confidence=ConfidenceLevel.HIGH,
    )

    return assumptions
