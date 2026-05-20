"""目标解析模块 - 将自然语言分析目标解析为结构化任务图"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GoalCategory(Enum):
    """分析目标类别"""
    EXPLORATORY = "exploratory"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"
    DESCRIPTIVE = "descriptive"


class TimeGranularity(Enum):
    """时间粒度"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class MetricSpec:
    """指标规格"""
    name: str
    aggregation: str | None = None
    threshold: float | None = None
    direction: str = "asc"  # asc 或 desc


@dataclass
class DeliverableSpec:
    """交付物规格"""
    deliverable_type: str  # report, dashboard, chart, table, model
    format: str | None = None
    description: str = ""


@dataclass
class ImplicitRequirement:
    """隐式需求"""
    requirement_type: str
    description: str
    confidence: float  # 0.0 - 1.0


@dataclass
class TaskNode:
    """任务图中的单个节点"""
    task_id: str
    description: str
    depends_on: list[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low, medium, high
    status: str = "pending"


@dataclass
class AnalysisGoalSpec:
    """分析目标规格 - 解析后的结构化输出"""
    original_goal: str
    category: GoalCategory
    objective: str
    metrics: list[MetricSpec] = field(default_factory=list)
    deliverables: list[DeliverableSpec] = field(default_factory=list)
    implicit_requirements: list[ImplicitRequirement] = field(default_factory=list)
    time_constraints: dict[str, Any] = field(default_factory=dict)
    task_graph: list[TaskNode] = field(default_factory=list)
    domain: str | None = None
    confidence: float = 0.0


# 关键词映射表
CATEGORY_KEYWORDS: dict[GoalCategory, list[str]] = {
    GoalCategory.EXPLORATORY: ["探索", "发现", "了解", "查看", "浏览"],
    GoalCategory.DIAGNOSTIC: ["诊断", "原因", "为什么", "根因", "分析原因"],
    GoalCategory.PREDICTIVE: ["预测", "预估", " forecast", "趋势", "未来"],
    GoalCategory.PRESCRIPTIVE: ["优化", "建议", "推荐", "改进", "提升"],
    GoalCategory.DESCRIPTIVE: ["描述", "统计", "概况", "总结", "报告"],
}

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "ecommerce": ["电商", "交易", "订单", "商品", "店铺", "GMV"],
    "finance": ["财务", "营收", "利润", "成本", "预算", "审计"],
    "marketing": ["营销", "推广", "投放", "渠道", "转化"],
    "user_growth": ["用户增长", "留存", "拉新", "活跃", "DAU", "MAU"],
    "supply_chain": ["供应链", "库存", "物流", "仓储", "采购"],
    "hr": ["人力资源", "员工", "招聘", "绩效", "薪酬"],
}

TIME_KEYWORDS: dict[str, list[str]] = {
    "daily": ["每日", "每天", "日级", "按天"],
    "weekly": ["每周", "周级", "按周"],
    "monthly": ["每月", "月度", "月级", "按月"],
    "quarterly": ["每季度", "季度", "按季度"],
    "yearly": ["每年", "年度", "年级", "按年"],
}


def _extract_category(goal: str) -> GoalCategory:
    """从目标描述中提取分析类别"""
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in goal for kw in keywords):
            return category
    return GoalCategory.DESCRIPTIVE


def _extract_domain(goal: str) -> str | None:
    """识别业务领域"""
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in goal for kw in keywords):
            return domain
    return None


def _extract_metrics(goal: str) -> list[MetricSpec]:
    """从目标中提取关键指标"""
    metrics: list[MetricSpec] = []
    metric_patterns = [
        r"(关注|重点|核心|关键).*?([\u4e00-\u9fa5a-zA-Z]+)(?:指标|数据|数值)",
        r"([\u4e00-\u9fa5a-zA-Z]+)(?:率|额|量|数|比|均值|中位数)",
    ]
    for pattern in metric_patterns:
        matches = re.findall(pattern, goal)
        for match in matches:
            name = match[1] if len(match) > 1 else match[0]
            metrics.append(MetricSpec(name=name))
    return metrics


def _extract_time_constraints(goal: str) -> dict[str, Any]:
    """提取时间相关约束"""
    constraints: dict[str, Any] = {}
    for granularity, keywords in TIME_KEYWORDS.items():
        if any(kw in goal for kw in keywords):
            constraints["granularity"] = granularity
            break

    date_pattern = r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})"
    dates = re.findall(date_pattern, goal)
    if dates:
        constraints["date_range"] = dates[:2]
    return constraints


def _extract_deliverables(goal: str) -> list[DeliverableSpec]:
    """识别期望的交付物"""
    deliverables: list[DeliverableSpec] = []
    type_keywords = {
        "report": ["报告", "文档"],
        "dashboard": ["看板", "仪表盘", "大屏"],
        "chart": ["图表", "可视化", "图"],
        "table": ["表格", "数据表", "明细"],
        "model": ["模型", "算法", "预测结果"],
    }
    for del_type, keywords in type_keywords.items():
        if any(kw in goal for kw in keywords):
            deliverables.append(
                DeliverableSpec(deliverable_type=del_type, description=goal)
            )
    return deliverables


def _identify_implicit_requirements(
    category: GoalCategory, domain: str | None
) -> list[ImplicitRequirement]:
    """根据类别和领域推断隐式需求"""
    requirements: list[ImplicitRequirement] = []

    if category == GoalCategory.PREDICTIVE:
        requirements.append(
            ImplicitRequirement(
                requirement_type="data_quality",
                description="需要历史数据作为训练集",
                confidence=0.9,
            )
        )

    if domain in ("ecommerce", "finance"):
        requirements.append(
            ImplicitRequirement(
                requirement_type="compliance",
                description="涉及敏感数据，需脱敏处理",
                confidence=0.8,
            )
        )

    requirements.append(
        ImplicitRequirement(
            requirement_type="reproducibility",
            description="分析过程应可复现",
            confidence=0.95,
        )
    )

    return requirements


def _build_task_graph(
    category: GoalCategory, metrics: list[MetricSpec]
) -> list[TaskNode]:
    """构建分析任务图"""
    tasks: list[TaskNode] = []

    # 数据准备阶段
    tasks.append(
        TaskNode(
            task_id="data_preparation",
            description="数据获取、清洗和预处理",
            estimated_complexity="medium",
        )
    )

    # 探索分析阶段
    tasks.append(
        TaskNode(
            task_id="exploratory_analysis",
            description="数据分布、相关性、基础统计",
            depends_on=["data_preparation"],
            estimated_complexity="low",
        )
    )

    if category == GoalCategory.DIAGNOSTIC:
        tasks.append(
            TaskNode(
                task_id="root_cause_analysis",
                description="根因分析和假设验证",
                depends_on=["exploratory_analysis"],
                estimated_complexity="high",
            )
        )
    elif category == GoalCategory.PREDICTIVE:
        tasks.append(
            TaskNode(
                task_id="model_building",
                description="特征工程和模型训练",
                depends_on=["exploratory_analysis"],
                estimated_complexity="high",
            )
        )

    # 报告生成
    tasks.append(
        TaskNode(
            task_id="report_generation",
            description="生成分析报告和可视化",
            depends_on=[tasks[-1].task_id],
            estimated_complexity="medium",
        )
    )

    return tasks


def parse_goal(goal: str) -> AnalysisGoalSpec:
    """
    将自然语言分析目标解析为结构化规格

    Args:
        goal: 自然语言描述的分析目标

    Returns:
        AnalysisGoalSpec: 结构化的分析目标规格
    """
    if not goal or not goal.strip():
        raise ValueError("分析目标不能为空")

    cleaned_goal = goal.strip()
    category = _extract_category(cleaned_goal)
    domain = _extract_domain(cleaned_goal)
    metrics = _extract_metrics(cleaned_goal)
    time_constraints = _extract_time_constraints(cleaned_goal)
    deliverables = _extract_deliverables(cleaned_goal)
    implicit_reqs = _identify_implicit_requirements(category, domain)
    task_graph = _build_task_graph(category, metrics)

    # 计算解析置信度
    has_metrics = len(metrics) > 0
    has_deliverables = len(deliverables) > 0
    confidence = 0.5 + 0.2 * has_metrics + 0.2 * has_deliverables + 0.1 * bool(domain)

    return AnalysisGoalSpec(
        original_goal=cleaned_goal,
        category=category,
        objective=cleaned_goal,
        metrics=metrics,
        deliverables=deliverables,
        implicit_requirements=implicit_reqs,
        time_constraints=time_constraints,
        task_graph=task_graph,
        domain=domain,
        confidence=min(confidence, 1.0),
    )


def refine_goal(spec: AnalysisGoalSpec, user_feedback: str) -> AnalysisGoalSpec:
    """
    根据用户反馈细化分析目标

    Args:
        spec: 当前分析目标规格
        user_feedback: 用户的补充说明或修改意见

    Returns:
        AnalysisGoalSpec: 细化后的规格
    """
    # 补充指标
    new_metrics = _extract_metrics(user_feedback)
    for m in new_metrics:
        if m.name not in [existing.name for existing in spec.metrics]:
            spec.metrics.append(m)

    # 补充时间约束
    new_constraints = _extract_time_constraints(user_feedback)
    spec.time_constraints.update(new_constraints)

    # 更新置信度
    spec.confidence = min(spec.confidence + 0.1, 1.0)

    return spec
