"""分析方法选择模块 - 基于目标和数据特征自动选择分析方法"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MethodFamily(Enum):
    """方法族"""
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    CLASSIFICATION = "classification"
    TIME_SERIES = "time_series"
    CAUSAL = "causal"
    STATISTICAL_TEST = "statistical_test"


class DataCharacteristic(Enum):
    """数据特征"""
    CONTINUOUS_TARGET = "continuous_target"
    CATEGORICAL_TARGET = "categorical_target"
    TIME_INDEXED = "time_indexed"
    HIGH_DIMENSIONAL = "high_dimensional"
    SMALL_SAMPLE = "small_sample"
    HAS_TREATMENT_CONTROL = "has_treatment_control"


@dataclass
class AnalysisMethodInfo:
    """分析方法的完整描述"""
    name: str
    family: MethodFamily
    when_to_use: str
    required_data: list[str]
    parameters: dict[str, Any] = field(default_factory=dict)
    min_samples: int = 30
    supports_causal: bool = False
    complexity: str = "low"  # low, medium, high


@dataclass
class MethodRecommendation:
    """方法推荐结果"""
    primary_method: AnalysisMethodInfo
    alternatives: list[AnalysisMethodInfo] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""


# 回归分析方法
LINEAR_REGRESSION = AnalysisMethodInfo(
    name="线性回归",
    family=MethodFamily.REGRESSION,
    when_to_use="分析连续变量之间的线性关系，预测数值型目标",
    required_data=["连续型特征", "连续型目标变量"],
    parameters={"fit_intercept": True, "normalize": False},
    min_samples=50,
)

LOGISTIC_REGRESSION = AnalysisMethodInfo(
    name="逻辑回归",
    family=MethodFamily.REGRESSION,
    when_to_use="二分类或多分类问题，需要概率输出",
    required_data=["特征变量", "类别型目标变量"],
    parameters={"penalty": "l2", "max_iter": 1000},
    min_samples=100,
)

POLYNOMIAL_REGRESSION = AnalysisMethodInfo(
    name="多项式回归",
    family=MethodFamily.REGRESSION,
    when_to_use="变量间存在非线性关系但可通过多项式拟合",
    required_data=["连续型特征", "连续型目标变量"],
    parameters={"degree": 2},
    min_samples=50,
)

# 聚类方法
KMEANS = AnalysisMethodInfo(
    name="K-Means 聚类",
    family=MethodFamily.CLUSTERING,
    when_to_use="将样本划分为 K 个簇，数据分布较均匀",
    required_data=["数值型特征"],
    parameters={"n_clusters": 3, "max_iter": 300, "n_init": 10},
    min_samples=100,
    complexity="low",
)

HIERARCHICAL_CLUSTERING = AnalysisMethodInfo(
    name="层次聚类",
    family=MethodFamily.CLUSTERING,
    when_to_use="需要探索层次结构或不确定簇数量时",
    required_data=["数值型特征", "距离矩阵"],
    parameters={"linkage": "ward", "metric": "euclidean"},
    min_samples=50,
    complexity="medium",
)

DBSCAN = AnalysisMethodInfo(
    name="DBSCAN 密度聚类",
    family=MethodFamily.CLUSTERING,
    when_to_use="簇形状不规则或存在噪声点",
    required_data=["数值型特征"],
    parameters={"eps": 0.5, "min_samples": 5},
    min_samples=50,
    complexity="medium",
)

# 分类方法
DECISION_TREE = AnalysisMethodInfo(
    name="决策树",
    family=MethodFamily.CLASSIFICATION,
    when_to_use="需要可解释性强的分类模型",
    required_data=["特征变量", "类别型目标变量"],
    parameters={"max_depth": 5, "min_samples_split": 10},
    min_samples=100,
    complexity="low",
)

RANDOM_FOREST = AnalysisMethodInfo(
    name="随机森林",
    family=MethodFamily.CLASSIFICATION,
    when_to_use="需要高精度且能处理非线性关系",
    required_data=["特征变量", "类别型目标变量"],
    parameters={"n_estimators": 100, "max_depth": None},
    min_samples=200,
    complexity="medium",
)

SVM = AnalysisMethodInfo(
    name="支持向量机",
    family=MethodFamily.CLASSIFICATION,
    when_to_use="高维数据中小样本分类",
    required_data=["数值型特征", "类别型目标变量"],
    parameters={"kernel": "rbf", "C": 1.0},
    min_samples=100,
    complexity="high",
)

# 时间序列方法
ARIMA = AnalysisMethodInfo(
    name="ARIMA 模型",
    family=MethodFamily.TIME_SERIES,
    when_to_use="平稳时间序列的预测分析",
    required_data=["时间索引", "单变量序列"],
    parameters={"order": (1, 1, 1)},
    min_samples=50,
    complexity="medium",
)

PROPHET = AnalysisMethodInfo(
    name="Prophet 模型",
    family=MethodFamily.TIME_SERIES,
    when_to_use="含季节性和趋势的时间序列预测",
    required_data=["日期列", "数值列"],
    parameters={"seasonality_mode": "multiplicative"},
    min_samples=100,
    complexity="low",
)

TREND_DETECTION = AnalysisMethodInfo(
    name="趋势检测",
    family=MethodFamily.TIME_SERIES,
    when_to_use="识别数据的长期趋势和突变点",
    required_data=["时间索引", "数值序列"],
    parameters={"method": "mann_kendall"},
    min_samples=30,
    complexity="low",
)

# 因果分析方法
AB_TEST = AnalysisMethodInfo(
    name="A/B 测试",
    family=MethodFamily.CAUSAL,
    when_to_use="比较实验组和对照组的差异",
    required_data=["分组标识", "指标变量"],
    parameters={"significance_level": 0.05},
    min_samples=100,
    supports_causal=True,
    complexity="low",
)

DIFFERENCE_IN_DIFFERENCES = AnalysisMethodInfo(
    name="双重差分法",
    family=MethodFamily.CAUSAL,
    when_to_use="评估政策或干预措施的因果效应",
    required_data=["时间前后数据", "处理组/对照组", "结果变量"],
    parameters={"parallel_trend_check": True},
    min_samples=200,
    supports_causal=True,
    complexity="high",
)

# 统计检验方法
T_TEST = AnalysisMethodInfo(
    name="t 检验",
    family=MethodFamily.STATISTICAL_TEST,
    when_to_use="比较两组均值是否存在显著差异",
    required_data=["两组数值数据"],
    parameters={"alternative": "two-sided"},
    min_samples=20,
    complexity="low",
)

CHI_SQUARE = AnalysisMethodInfo(
    name="卡方检验",
    family=MethodFamily.STATISTICAL_TEST,
    when_to_use="检验分类变量之间的独立性",
    required_data=["两个分类变量"],
    parameters={},
    min_samples=30,
    complexity="low",
)

ANOVA = AnalysisMethodInfo(
    name="方差分析 (ANOVA)",
    family=MethodFamily.STATISTICAL_TEST,
    when_to_use="比较三组及以上均值差异",
    required_data=["分组变量", "连续型结果变量"],
    parameters={},
    min_samples=30,
    complexity="low",
)

# 方法注册表
METHOD_REGISTRY: dict[str, list[AnalysisMethodInfo]] = {
    MethodFamily.REGRESSION.value: [LINEAR_REGRESSION, LOGISTIC_REGRESSION, POLYNOMIAL_REGRESSION],
    MethodFamily.CLUSTERING.value: [KMEANS, HIERARCHICAL_CLUSTERING, DBSCAN],
    MethodFamily.CLASSIFICATION.value: [DECISION_TREE, RANDOM_FOREST, SVM],
    MethodFamily.TIME_SERIES.value: [ARIMA, PROPHET, TREND_DETECTION],
    MethodFamily.CAUSAL.value: [AB_TEST, DIFFERENCE_IN_DIFFERENCES],
    MethodFamily.STATISTICAL_TEST.value: [T_TEST, CHI_SQUARE, ANOVA],
}

ALL_METHODS: list[AnalysisMethodInfo] = [
    m for methods in METHOD_REGISTRY.values() for m in methods
]


def select_method(
    goal_description: str,
    data_characteristics: list[DataCharacteristic],
    sample_size: int = 100,
    target_type: str | None = None,
) -> MethodRecommendation:
    """
    根据目标和数据特征自动选择最合适的分析方法

    Args:
        goal_description: 目标描述（关键词匹配）
        data_characteristics: 数据特征列表
        sample_size: 样本量
        target_type: 目标变量类型 (continuous/categorical/time)

    Returns:
        方法推荐结果
    """
    candidates = _filter_by_goal(goal_description)
    candidates = _filter_by_data(candidates, data_characteristics)
    candidates = _filter_by_sample(candidates, sample_size)

    if not candidates:
        candidates = _get_fallback_methods(target_type)

    primary = candidates[0]
    alternatives = candidates[1:3]
    confidence = _calculate_confidence(primary, data_characteristics)
    reasoning = _build_reasoning(primary, goal_description)

    return MethodRecommendation(
        primary_method=primary,
        alternatives=alternatives,
        confidence=confidence,
        reasoning=reasoning,
    )


def get_methods_by_family(family: MethodFamily) -> list[AnalysisMethodInfo]:
    """获取指定方法族的所有方法"""
    return list(METHOD_REGISTRY.get(family.value, []))


def get_all_methods() -> list[AnalysisMethodInfo]:
    """获取所有可用方法"""
    return list(ALL_METHODS)


def _filter_by_goal(description: str) -> list[AnalysisMethodInfo]:
    """根据目标描述过滤方法"""
    goal_keywords = _extract_goal_keywords(description)
    if not goal_keywords:
        return list(ALL_METHODS)

    scored: list[tuple[int, AnalysisMethodInfo]] = []
    for method in ALL_METHODS:
        score = _score_method_for_goal(method, goal_keywords)
        if score > 0:
            scored.append((score, method))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored]


def _filter_by_data(
    methods: list[AnalysisMethodInfo],
    characteristics: list[DataCharacteristic],
) -> list[AnalysisMethodInfo]:
    """根据数据特征过滤方法"""
    if not characteristics:
        return methods

    filtered: list[AnalysisMethodInfo] = []
    for method in methods:
        if _is_data_compatible(method, characteristics):
            filtered.append(method)

    return filtered if filtered else methods


def _filter_by_sample(
    methods: list[AnalysisMethodInfo],
    sample_size: int,
) -> list[AnalysisMethodInfo]:
    """根据样本量过滤方法"""
    return [m for m in methods if m.min_samples <= sample_size]


def _extract_goal_keywords(description: str) -> list[str]:
    """从目标描述中提取关键词"""
    keyword_map: dict[str, list[str]] = {
        "predict": ["预测", "预估", "forecast"],
        "classify": ["分类", "判别", "识别"],
        "cluster": ["聚类", "分群", "分组", "细分"],
        "correlate": ["相关", "关联", "关系"],
        "causal": ["因果", "影响", "效应", "干预"],
        "trend": ["趋势", "走向", "变化"],
        "compare": ["比较", "差异", "对比"],
        "regression": ["回归", "拟合"],
        "test": ["检验", "测试", "验证"],
    }

    found: list[str] = []
    for key, keywords in keyword_map.items():
        if any(kw in description for kw in keywords):
            found.append(key)

    return found


def _score_method_for_goal(
    method: AnalysisMethodInfo,
    keywords: list[str],
) -> int:
    """计算方法与目标的匹配分数"""
    score = 0
    description_lower = (
        method.when_to_use + " " + method.name
    ).lower()

    for kw in keywords:
        if kw in description_lower:
            score += 2

    family_score = {
        "predict": {MethodFamily.REGRESSION, MethodFamily.TIME_SERIES},
        "classify": {MethodFamily.CLASSIFICATION},
        "cluster": {MethodFamily.CLUSTERING},
        "correlate": {MethodFamily.REGRESSION},
        "causal": {MethodFamily.CAUSAL},
        "trend": {MethodFamily.TIME_SERIES},
        "compare": {MethodFamily.STATISTICAL_TEST, MethodFamily.CAUSAL},
        "regression": {MethodFamily.REGRESSION},
        "test": {MethodFamily.STATISTICAL_TEST},
    }

    for kw in keywords:
        if method.family in family_score.get(kw, set()):
            score += 3

    return score


def _is_data_compatible(
    method: AnalysisMethodInfo,
    characteristics: list[DataCharacteristic],
) -> bool:
    """检查方法是否与数据特征兼容"""
    char_set = set(characteristics)

    if DataCharacteristic.CONTINUOUS_TARGET in char_set:
        if method.family == MethodFamily.CLASSIFICATION:
            return False

    if DataCharacteristic.CATEGORICAL_TARGET in char_set:
        if method.family in (MethodFamily.REGRESSION, MethodFamily.TIME_SERIES):
            return False

    if DataCharacteristic.TIME_INDEXED in char_set:
        if method.family == MethodFamily.TIME_SERIES:
            return True

    if DataCharacteristic.HAS_TREATMENT_CONTROL in char_set:
        if method.supports_causal:
            return True

    return True


def _get_fallback_methods(target_type: str | None) -> list[AnalysisMethodInfo]:
    """无匹配时的兜底方法"""
    fallback_map: dict[str, list[AnalysisMethodInfo]] = {
        "continuous": [LINEAR_REGRESSION, TREND_DETECTION],
        "categorical": [LOGISTIC_REGRESSION, CHI_SQUARE],
        "time": [TREND_DETECTION, PROPHET],
    }
    return fallback_map.get(target_type, [T_TEST, LINEAR_REGRESSION])


def _calculate_confidence(
    method: AnalysisMethodInfo,
    characteristics: list[DataCharacteristic],
) -> float:
    """计算推荐置信度"""
    base = 0.6

    if characteristics:
        base += 0.1 * len(characteristics)

    if method.complexity == "low":
        base += 0.1

    return round(min(base, 1.0), 2)


def _build_reasoning(method: AnalysisMethodInfo, goal: str) -> str:
    """构建推荐理由"""
    return (
        f"选择 {method.name}，原因：{method.when_to_use}。"
        f"适用于目标：'{goal}'"
    )


def get_method_parameters(method_name: str) -> dict[str, Any] | None:
    """获取指定方法的默认参数"""
    for method in ALL_METHODS:
        if method.name == method_name:
            return dict(method.parameters)
    return None


def validate_data_for_method(
    method: AnalysisMethodInfo,
    sample_size: int,
    has_time_column: bool = False,
    has_categorical_target: bool = False,
) -> list[str]:
    """
    验证数据是否满足方法要求

    Returns:
        不满足的要求列表
    """
    issues: list[str] = []

    if sample_size < method.min_samples:
        issues.append(
            f"样本量 {sample_size} 低于最低要求 {method.min_samples}"
        )

    if method.family == MethodFamily.TIME_SERIES and not has_time_column:
        issues.append("时间序列方法需要时间索引列")

    if method.family == MethodFamily.CLASSIFICATION and not has_categorical_target:
        issues.append("分类方法需要类别型目标变量")

    return issues
