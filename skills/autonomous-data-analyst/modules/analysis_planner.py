"""分析规划模块 - 分析路径规划与动态调整"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class AnalysisPhase(Enum):
    """分析阶段"""
    PERCEPTION = "perception"
    JUDGMENT = "judgment"
    ACTION = "action"


class AnalysisMethod(Enum):
    """分析方法"""
    DESCRIPTIVE_STATS = "descriptive_stats"
    CORRELATION = "correlation"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"
    TIME_SERIES = "time_series"
    AB_TEST = "ab_test"
    FUNNEL = "funnel"
    COHORT = "cohort"
    SEGMENTATION = "segmentation"


@dataclass
class AnalysisStep:
    """分析步骤"""
    step_id: str
    method: AnalysisMethod
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    result: Any = None


@dataclass
class AnalysisPlan:
    """分析计划"""
    plan_id: str
    goal_objective: str
    steps: list[AnalysisStep] = field(default_factory=list)
    current_phase: AnalysisPhase = AnalysisPhase.PERCEPTION
    current_step_index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PerceptionResult:
    """感知阶段结果"""
    data_shape: tuple[int, int] | None = None
    missing_ratio: float = 0.0
    column_types: dict[str, str] = field(default_factory=dict)
    data_quality_score: float = 1.0
    anomalies: list[str] = field(default_factory=list)


@dataclass
class JudgmentResult:
    """判断阶段结果"""
    is_data_ready: bool = False
    next_method: AnalysisMethod | None = None
    plan_adjustment: str | None = None
    confidence: float = 0.0


# 领域到分析方法的映射
DOMAIN_METHOD_MAP: dict[str, list[AnalysisMethod]] = {
    "ecommerce": [
        AnalysisMethod.FUNNEL,
        AnalysisMethod.COHORT,
        AnalysisMethod.SEGMENTATION,
        AnalysisMethod.DESCRIPTIVE_STATS,
    ],
    "finance": [
        AnalysisMethod.TIME_SERIES,
        AnalysisMethod.REGRESSION,
        AnalysisMethod.DESCRIPTIVE_STATS,
    ],
    "user_growth": [
        AnalysisMethod.COHORT,
        AnalysisMethod.FUNNEL,
        AnalysisMethod.CLASSIFICATION,
        AnalysisMethod.SEGMENTATION,
    ],
    "marketing": [
        AnalysisMethod.AB_TEST,
        AnalysisMethod.CORRELATION,
        AnalysisMethod.SEGMENTATION,
    ],
}


class MethodSelector:
    """分析方法选择器"""

    @classmethod
    def select_methods(
        cls,
        domain: str | None,
        goal_category: str = "descriptive",
        data_available: bool = True,
    ) -> list[AnalysisMethod]:
        """
        根据领域和目标类别选择分析方法

        Args:
            domain: 业务领域
            goal_category: 目标类别
            data_available: 数据是否可用

        Returns:
            推荐的分析方法列表
        """
        if not data_available:
            return []

        base_methods = DOMAIN_METHOD_MAP.get(domain, [])

        # 根据目标类别调整方法
        if goal_category == "diagnostic":
            base_methods = [
                m for m in base_methods
                if m in (AnalysisMethod.CORRELATION, AnalysisMethod.REGRESSION)
            ] or [AnalysisMethod.CORRELATION]
        elif goal_category == "predictive":
            base_methods = [
                m for m in base_methods
                if m in (AnalysisMethod.REGRESSION, AnalysisMethod.CLASSIFICATION)
            ] or [AnalysisMethod.REGRESSION]

        # 确保基础统计方法始终存在
        if AnalysisMethod.DESCRIPTIVE_STATS not in base_methods:
            base_methods.insert(0, AnalysisMethod.DESCRIPTIVE_STATS)

        return base_methods


class AnalysisPlanner:
    """分析规划器 - 实现感知→判断→行动循环"""

    def __init__(self) -> None:
        self.current_plan: AnalysisPlan | None = None
        self.perception_cache: PerceptionResult | None = None

    def create_plan(
        self,
        plan_id: str,
        objective: str,
        domain: str | None = None,
        category: str = "descriptive",
    ) -> AnalysisPlan:
        """
        创建初始分析计划

        Args:
            plan_id: 计划标识
            objective: 分析目标
            domain: 业务领域
            category: 分析类别

        Returns:
            AnalysisPlan: 创建的分析计划
        """
        methods = MethodSelector.select_methods(domain, category)

        steps = [
            AnalysisStep(
                step_id=f"step_{i}",
                method=method,
                description=self._get_method_description(method),
            )
            for i, method in enumerate(methods)
        ]

        self.current_plan = AnalysisPlan(
            plan_id=plan_id,
            goal_objective=objective,
            steps=steps,
        )

        return self.current_plan

    def perceive(self, data_summary: dict[str, Any]) -> PerceptionResult:
        """
        感知阶段：收集数据特征

        Args:
            data_summary: 数据摘要信息

        Returns:
            PerceptionResult: 感知结果
        """
        shape = data_summary.get("shape")
        missing = data_summary.get("missing_ratio", 0.0)
        col_types = data_summary.get("column_types", {})
        anomalies = data_summary.get("anomalies", [])

        # 计算数据质量分数
        quality_score = self._calculate_quality_score(missing, anomalies)

        result = PerceptionResult(
            data_shape=shape,
            missing_ratio=missing,
            column_types=col_types,
            data_quality_score=quality_score,
            anomalies=anomalies,
        )

        self.perception_cache = result
        logger.info("感知阶段完成: 质量分数=%.2f", quality_score)

        return result

    def judge(self) -> JudgmentResult:
        """
        判断阶段：基于感知结果做决策

        Returns:
            JudgmentResult: 判断结果
        """
        if self.perception_cache is None:
            raise RuntimeError("需先执行感知阶段")

        perception = self.perception_cache

        # 数据质量判断
        is_ready = perception.data_quality_score >= 0.7
        adjustment: str | None = None

        if not is_ready:
            adjustment = "数据质量不足，需先进行数据清洗"
            logger.warning("数据质量不足: score=%.2f", perception.data_quality_score)
            return JudgmentResult(
                is_data_ready=False,
                plan_adjustment=adjustment,
                confidence=0.3,
            )

        # 获取下一步方法
        next_method = self._get_next_method()
        confidence = perception.data_quality_score

        return JudgmentResult(
            is_data_ready=True,
            next_method=next_method,
            confidence=confidence,
        )

    def execute_current_step(
        self, executor: Callable[[AnalysisStep], Any]
    ) -> AnalysisStep | None:
        """
        行动阶段：执行当前分析步骤

        Args:
            executor: 步骤执行函数

        Returns:
            执行的步骤或None
        """
        if self.current_plan is None:
            raise RuntimeError("无可用计划")

        if self.current_plan.current_step_index >= len(self.current_plan.steps):
            self.current_plan.current_phase = AnalysisPhase.ACTION
            logger.info("所有分析步骤已完成")
            return None

        step = self.current_plan.steps[self.current_plan.current_step_index]
        step.status = "running"

        try:
            step.result = executor(step)
            step.status = "completed"
            self.current_plan.current_step_index += 1
            logger.info("步骤 %s 执行完成", step.step_id)
        except Exception as exc:
            step.status = "failed"
            logger.error("步骤 %s 执行失败: %s", step.step_id, exc)
            self._handle_step_failure(step)

        return step

    def advance_plan(self) -> bool:
        """
        推进计划到下一阶段

        Returns:
            是否还有后续步骤
        """
        if self.current_plan is None:
            return False

        has_more = self.current_plan.current_step_index < len(self.current_plan.steps)

        if not has_more:
            self.current_plan.current_phase = AnalysisPhase.ACTION

        return has_more

    def adjust_plan(self, adjustment: str) -> None:
        """
        根据反馈动态调整计划

        Args:
            adjustment: 调整说明
        """
        if self.current_plan is None:
            return

        self.current_plan.metadata["adjustments"] = (
            self.current_plan.metadata.get("adjustments", [])
        )
        self.current_plan.metadata["adjustments"].append(adjustment)
        logger.info("计划已调整: %s", adjustment)

    def _get_next_method(self) -> AnalysisMethod | None:
        """获取下一个待执行的分析方法"""
        if self.current_plan is None:
            return None

        idx = self.current_plan.current_step_index
        if idx < len(self.current_plan.steps):
            return self.current_plan.steps[idx].method
        return None

    def _calculate_quality_score(
        self, missing_ratio: float, anomalies: list[str]
    ) -> float:
        """计算数据质量分数"""
        missing_penalty = missing_ratio * 0.5
        anomaly_penalty = min(len(anomalies) * 0.1, 0.3)
        score = 1.0 - missing_penalty - anomaly_penalty
        return max(score, 0.0)

    def _handle_step_failure(self, step: AnalysisStep) -> None:
        """处理步骤失败"""
        self.current_plan.metadata.setdefault("failures", [])
        self.current_plan.metadata["failures"].append(step.step_id)

    def _get_method_description(self, method: AnalysisMethod) -> str:
        """获取方法的中文描述"""
        descriptions: dict[AnalysisMethod, str] = {
            AnalysisMethod.DESCRIPTIVE_STATS: "描述性统计分析",
            AnalysisMethod.CORRELATION: "相关性分析",
            AnalysisMethod.REGRESSION: "回归分析",
            AnalysisMethod.CLUSTERING: "聚类分析",
            AnalysisMethod.CLASSIFICATION: "分类分析",
            AnalysisMethod.TIME_SERIES: "时间序列分析",
            AnalysisMethod.AB_TEST: "A/B 测试分析",
            AnalysisMethod.FUNNEL: "漏斗分析",
            AnalysisMethod.COHORT: "同期群分析",
            AnalysisMethod.SEGMENTATION: "分群分析",
        }
        return descriptions.get(method, method.value)
