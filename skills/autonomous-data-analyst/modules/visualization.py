"""可视化与图表选择模块 - 根据数据和分析类型自动选择并生成可视化"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """图表类型"""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    PIE = "pie"
    WATERFALL = "waterfall"


class AnalysisType(Enum):
    """分析类型"""
    TREND = "trend"
    COMPARISON = "comparison"
    DISTRIBUTION = "distribution"
    CORRELATION = "correlation"
    COMPOSITION = "composition"
    FLOW = "flow"
    OUTLIER = "outlier"


@dataclass
class ChartConfig:
    """图表配置"""
    chart_type: ChartType
    title: str = ""
    x_column: str = ""
    y_columns: list[str] = field(default_factory=list)
    group_by: str | None = None
    color_column: str | None = None
    annotations: list[str] = field(default_factory=list)
    show_legend: bool = True
    show_grid: bool = True
    width: int = 800
    height: int = 500


@dataclass
class AutoCaption:
    """自动生成的图注"""
    chart_type: str
    summary: str = ""
    key_insights: list[str] = field(default_factory=list)
    data_coverage: str = ""
    limitations: list[str] = field(default_factory=list)


# 颜色方案定义
COLOR_SCHEME = {
    "primary": ["#2563EB", "#7C3AED", "#059669", "#D97706", "#DC2626"],
    "risk_red": "#DC2626",
    "risk_yellow": "#F59E0B",
    "risk_blue": "#3B82F6",
    "neutral": "#6B7280",
    "background": "#FFFFFF",
    "text": "#1F2937",
    "grid": "#E5E7EB",
}

# 图表选择规则引擎
CHART_RULES: list[dict[str, Any]] = [
    {
        "analysis_type": AnalysisType.TREND,
        "data_types": ["time_series"],
        "chart_type": ChartType.LINE,
        "reason": "折线图最适合展示时间趋势变化",
    },
    {
        "analysis_type": AnalysisType.COMPARISON,
        "data_types": ["categorical"],
        "chart_type": ChartType.BAR,
        "reason": "柱状图适合对比不同类别的数值",
    },
    {
        "analysis_type": AnalysisType.CORRELATION,
        "data_types": ["continuous"],
        "chart_type": ChartType.SCATTER,
        "reason": "散点图适合展示变量间的相关关系",
    },
    {
        "analysis_type": AnalysisType.CORRELATION,
        "data_types": ["matrix"],
        "chart_type": ChartType.HEATMAP,
        "reason": "热力图适合展示多变量相关性矩阵",
    },
    {
        "analysis_type": AnalysisType.DISTRIBUTION,
        "data_types": ["continuous"],
        "chart_type": ChartType.HISTOGRAM,
        "reason": "直方图适合展示数据分布形态",
    },
    {
        "analysis_type": AnalysisType.OUTLIER,
        "data_types": ["continuous"],
        "chart_type": ChartType.BOX_PLOT,
        "reason": "箱线图适合识别异常值和展示分布统计",
    },
    {
        "analysis_type": AnalysisType.COMPOSITION,
        "data_types": ["categorical"],
        "chart_type": ChartType.PIE,
        "reason": "饼图适合展示部分占整体的比例",
    },
    {
        "analysis_type": AnalysisType.FLOW,
        "data_types": ["sequential"],
        "chart_type": ChartType.WATERFALL,
        "reason": "瀑布图适合展示数值的增减变化过程",
    },
]


class ChartSelector:
    """图表选择器 - 根据数据特征和分析类型自动选择图表"""

    @classmethod
    def select(
        cls,
        analysis_type: AnalysisType,
        data_characteristics: list[str],
        column_count: int = 1,
        has_time_column: bool = False,
    ) -> ChartConfig:
        """
        自动选择最合适的图表类型

        Args:
            analysis_type: 分析类型
            data_characteristics: 数据特征列表
            column_count: 涉及的列数
            has_time_column: 是否包含时间列

        Returns:
            ChartConfig: 推荐的图表配置
        """
        matched_rule = _find_matching_rule(
            analysis_type, data_characteristics, column_count
        )

        if matched_rule is None:
            matched_rule = _get_fallback_chart(analysis_type)

        config = cls._build_config(matched_rule, analysis_type)
        return config

    @classmethod
    def select_multiple(
        cls,
        analysis_types: list[AnalysisType],
        data_characteristics: list[str],
    ) -> list[ChartConfig]:
        """
        为多个分析类型选择图表

        Args:
            analysis_types: 分析类型列表
            data_characteristics: 数据特征列表

        Returns:
            图表配置列表
        """
        configs: list[ChartConfig] = []
        for atype in analysis_types:
            config = cls.select(atype, data_characteristics)
            configs.append(config)
        return configs

    @classmethod
    def _build_config(
        cls, rule: dict[str, Any], analysis_type: AnalysisType
    ) -> ChartConfig:
        """构建图表配置"""
        return ChartConfig(
            chart_type=rule["chart_type"],
            title=_generate_title(analysis_type, rule["chart_type"]),
            show_legend=rule["chart_type"] not in (ChartType.HISTOGRAM, ChartType.HEATMAP),
        )


def _find_matching_rule(
    analysis_type: AnalysisType,
    data_characteristics: list[str],
    column_count: int,
) -> dict[str, Any] | None:
    """查找匹配的图表规则"""
    char_set = set(data_characteristics)

    for rule in CHART_RULES:
        if rule["analysis_type"] != analysis_type:
            continue

        rule_types = set(rule["data_types"])
        if rule_types & char_set:
            return rule

    return None


def _get_fallback_chart(analysis_type: AnalysisType) -> dict[str, Any]:
    """获取兜底图表配置"""
    fallback_map: dict[AnalysisType, ChartType] = {
        AnalysisType.TREND: ChartType.LINE,
        AnalysisType.COMPARISON: ChartType.BAR,
        AnalysisType.DISTRIBUTION: ChartType.HISTOGRAM,
        AnalysisType.CORRELATION: ChartType.SCATTER,
        AnalysisType.COMPOSITION: ChartType.PIE,
        AnalysisType.FLOW: ChartType.BAR,
        AnalysisType.OUTLIER: ChartType.BOX_PLOT,
    }

    chart_type = fallback_map.get(analysis_type, ChartType.BAR)

    return {
        "analysis_type": analysis_type,
        "data_types": ["fallback"],
        "chart_type": chart_type,
        "reason": "使用默认图表配置",
    }


def _generate_title(analysis_type: AnalysisType, chart_type: ChartType) -> str:
    """生成图表标题"""
    title_map: dict[AnalysisType, str] = {
        AnalysisType.TREND: "趋势分析",
        AnalysisType.COMPARISON: "对比分析",
        AnalysisType.DISTRIBUTION: "分布分析",
        AnalysisType.CORRELATION: "相关性分析",
        AnalysisType.COMPOSITION: "构成分析",
        AnalysisType.FLOW: "流程分析",
        AnalysisType.OUTLIER: "异常值分析",
    }
    return title_map.get(analysis_type, "数据分析")


class ColorManager:
    """颜色管理器 - 管理图表配色和风险高亮"""

    def __init__(self, scheme_name: str = "default") -> None:
        self._scheme = dict(COLOR_SCHEME)

    def get_palette(self, count: int) -> list[str]:
        """获取指定数量的调色板"""
        palette = self._scheme["primary"]
        if count <= len(palette):
            return palette[:count]

        # 循环使用颜色
        result = list(palette)
        while len(result) < count:
            result.extend(palette)
        return result[:count]

    def get_risk_color(self, risk_level: str) -> str:
        """根据风险等级获取颜色"""
        risk_color_map: dict[str, str] = {
            "red": self._scheme["risk_red"],
            "yellow": self._scheme["risk_yellow"],
            "blue": self._scheme["risk_blue"],
        }
        return risk_color_map.get(risk_level, self._scheme["neutral"])

    def get_sequential_palette(self, count: int = 5) -> list[str]:
        """获取渐变色板（用于热力图等）"""
        base = self._scheme["primary"]
        return _interpolate_colors(base[0], base[2], count)

    def get_diverging_palette(self, count: int = 5) -> list[str]:
        """获取发散色板（用于正负值对比）"""
        negative = self._scheme["risk_red"]
        positive = self._scheme["primary"][2]  # 绿色
        return _interpolate_colors(negative, positive, count)


def _interpolate_colors(color1: str, color2: str, count: int) -> list[str]:
    """在两个颜色之间插值生成渐变色"""
    rgb1 = _hex_to_rgb(color1)
    rgb2 = _hex_to_rgb(color2)

    colors: list[str] = []
    for i in range(count):
        ratio = i / max(count - 1, 1)
        r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * ratio)
        g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * ratio)
        b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * ratio)
        colors.append(f"#{r:02X}{g:02X}{b:02X}")

    return colors


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """将十六进制颜色转换为 RGB"""
    hex_color = hex_color.lstrip("#")
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


class CaptionGenerator:
    """图注自动生成器"""

    @classmethod
    def generate(
        cls,
        chart_config: ChartConfig,
        data_summary: dict[str, Any],
        key_points: list[str] | None = None,
    ) -> AutoCaption:
        """
        自动生成图注

        Args:
            chart_config: 图表配置
            data_summary: 数据摘要
            key_points: 关键要点

        Returns:
            AutoCaption: 自动生成的图注
        """
        summary = _build_caption_summary(chart_config, data_summary)
        insights = key_points or _extract_default_insights(data_summary)
        coverage = _describe_data_coverage(data_summary)
        limitations = _identify_limitations(chart_config, data_summary)

        return AutoCaption(
            chart_type=chart_config.chart_type.value,
            summary=summary,
            key_insights=insights,
            data_coverage=coverage,
            limitations=limitations,
        )

    @classmethod
    def generate_for_trend(
        cls,
        data_summary: dict[str, Any],
        trend_direction: str = "",
        magnitude: float = 0.0,
    ) -> AutoCaption:
        """为趋势图生成专用图注"""
        direction_text = _describe_trend(trend_direction, magnitude)
        config = ChartConfig(chart_type=ChartType.LINE, title="趋势分析")

        return cls.generate(
            chart_config=config,
            data_summary=data_summary,
            key_points=[direction_text] if direction_text else None,
        )

    @classmethod
    def generate_for_comparison(
        cls,
        data_summary: dict[str, Any],
        comparison_results: dict[str, float],
    ) -> AutoCaption:
        """为对比图生成专用图注"""
        insights = _extract_comparison_insights(comparison_results)
        config = ChartConfig(chart_type=ChartType.BAR, title="对比分析")

        return cls.generate(
            chart_config=config,
            data_summary=data_summary,
            key_points=insights,
        )


def _build_caption_summary(
    config: ChartConfig, data_summary: dict[str, Any]
) -> str:
    """构建图注摘要"""
    row_count = data_summary.get("row_count", 0)
    col_count = data_summary.get("col_count", 0)
    chart_name = _get_chart_name(config.chart_type)

    return f"本{chart_name}基于 {row_count} 行 × {col_count} 列数据生成"


def _extract_default_insights(data_summary: dict[str, Any]) -> list[str]:
    """提取默认数据洞察"""
    insights: list[str] = []
    mean_val = data_summary.get("mean")
    if mean_val is not None:
        insights.append(f"平均值为 {mean_val:.2f}")

    std_val = data_summary.get("std")
    if std_val is not None:
        insights.append(f"标准差为 {std_val:.2f}")

    return insights


def _describe_data_coverage(data_summary: dict[str, Any]) -> str:
    """描述数据覆盖范围"""
    start = data_summary.get("start_date")
    end = data_summary.get("end_date")

    if start and end:
        return f"数据覆盖时间段: {start} 至 {end}"

    return "数据覆盖范围未指定"


def _identify_limitations(
    config: ChartConfig, data_summary: dict[str, Any]
) -> list[str]:
    """识别可视化局限性"""
    limitations: list[str] = []
    missing_ratio = data_summary.get("missing_ratio", 0.0)

    if missing_ratio > 0.1:
        limitations.append(f"数据缺失率 {missing_ratio:.1%}，可能影响展示准确性")

    row_count = data_summary.get("row_count", 0)
    if row_count < 30:
        limitations.append("样本量较小，统计结果需谨慎解读")

    return limitations


def _get_chart_name(chart_type: ChartType) -> str:
    """获取图表中文名称"""
    name_map: dict[ChartType, str] = {
        ChartType.LINE: "折线图",
        ChartType.BAR: "柱状图",
        ChartType.SCATTER: "散点图",
        ChartType.HEATMAP: "热力图",
        ChartType.HISTOGRAM: "直方图",
        ChartType.BOX_PLOT: "箱线图",
        ChartType.PIE: "饼图",
        ChartType.WATERFALL: "瀑布图",
    }
    return name_map.get(chart_type, "图表")


def _describe_trend(direction: str, magnitude: float) -> str:
    """描述趋势方向和幅度"""
    if not direction:
        return ""

    direction_map: dict[str, str] = {
        "up": "上升",
        "down": "下降",
        "stable": "平稳",
        "fluctuating": "波动",
    }
    direction_text = direction_map.get(direction, direction)
    return f"整体呈现{direction_text}趋势，变化幅度 {magnitude:.2%}"


def _extract_comparison_insights(
    results: dict[str, float]
) -> list[str]:
    """提取对比分析洞察"""
    insights: list[str] = []
    if not results:
        return insights

    sorted_items = sorted(results.items(), key=lambda x: x[1], reverse=True)
    top_item = sorted_items[0]
    bottom_item = sorted_items[-1]

    insights.append(f"最高值: {top_item[0]} ({top_item[1]:.2f})")
    insights.append(f"最低值: {bottom_item[0]} ({bottom_item[1]:.2f})")

    diff = top_item[1] - bottom_item[1]
    if bottom_item[1] != 0:
        gap_pct = diff / abs(bottom_item[1])
        insights.append(f"最大差距 {gap_pct:.1%}")

    return insights


class Visualizer:
    """可视化引擎 - 整合图表选择和图注生成"""

    def __init__(self) -> None:
        self.color_manager = ColorManager()
        self.caption_generator = CaptionGenerator()

    def create_visualization(
        self,
        analysis_type: AnalysisType,
        data_summary: dict[str, Any],
        data_characteristics: list[str] | None = None,
        key_points: list[str] | None = None,
    ) -> tuple[ChartConfig, AutoCaption]:
        """
        创建完整的可视化方案

        Args:
            analysis_type: 分析类型
            data_summary: 数据摘要
            data_characteristics: 数据特征
            key_points: 关键要点

        Returns:
            (图表配置, 图注) 元组
        """
        characteristics = data_characteristics or _infer_characteristics(data_summary)
        config = ChartSelector.select(analysis_type, characteristics)
        caption = self.caption_generator.generate(config, data_summary, key_points)

        return config, caption

    def create_batch_visualizations(
        self,
        analysis_types: list[AnalysisType],
        data_summary: dict[str, Any],
    ) -> list[tuple[ChartConfig, AutoCaption]]:
        """
        批量创建可视化方案

        Args:
            analysis_types: 分析类型列表
            data_summary: 数据摘要

        Returns:
            可视化方案列表
        """
        characteristics = _infer_characteristics(data_summary)
        results: list[tuple[ChartConfig, AutoCaption]] = []

        for atype in analysis_types:
            config = ChartSelector.select(atype, characteristics)
            caption = self.caption_generator.generate(config, data_summary)
            results.append((config, caption))

        return results


def _infer_characteristics(data_summary: dict[str, Any]) -> list[str]:
    """从数据摘要推断数据特征"""
    characteristics: list[str] = []

    if data_summary.get("has_time_column"):
        characteristics.append("time_series")

    if data_summary.get("numeric_columns", 0) > 0:
        characteristics.append("continuous")

    if data_summary.get("categorical_columns", 0) > 0:
        characteristics.append("categorical")

    if data_summary.get("column_count", 0) > 2:
        characteristics.append("matrix")

    if data_summary.get("is_sequential"):
        characteristics.append("sequential")

    if not characteristics:
        characteristics.append("categorical")

    return characteristics
