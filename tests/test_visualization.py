"""可视化模块测试"""

from __future__ import annotations

import pytest

from modules.visualization import (
    AnalysisType,
    AutoCaption,
    ChartConfig,
    ChartSelector,
    ChartType,
    ColorManager,
    CaptionGenerator,
    Visualizer,
)


class TestChartSelector:
    """图表选择器测试"""

    def test_trend_selects_line(self):
        """趋势分析 → 折线图"""
        selector = ChartSelector()
        config = selector.select(AnalysisType.TREND, [])
        assert config.chart_type == ChartType.LINE

    def test_comparison_selects_bar(self):
        """对比分析 → 柱状图"""
        selector = ChartSelector()
        config = selector.select(AnalysisType.COMPARISON, [])
        assert config.chart_type == ChartType.BAR

    def test_distribution_selects_histogram(self):
        """分布分析 → 直方图"""
        selector = ChartSelector()
        config = selector.select(AnalysisType.DISTRIBUTION, [])
        assert config.chart_type == ChartType.HISTOGRAM

    def test_composition_selects_pie(self):
        """构成分析 → 饼图"""
        selector = ChartSelector()
        config = selector.select(AnalysisType.COMPOSITION, [])
        assert config.chart_type == ChartType.PIE

    def test_returns_chart_config(self):
        """返回 ChartConfig"""
        selector = ChartSelector()
        for analysis_type in AnalysisType:
            result = selector.select(analysis_type, [])
            assert isinstance(result, ChartConfig)


class TestColorManager:
    """色彩管理器测试"""

    def test_get_palette(self):
        """获取调色板"""
        cm = ColorManager()
        palette = cm.get_palette(5)
        assert isinstance(palette, (list, tuple))
        assert len(palette) == 5

    def test_risk_colors(self):
        """风险色彩"""
        cm = ColorManager()
        risk_color = cm.get_risk_color("high")
        assert risk_color is not None


class TestCaptionGenerator:
    """图注生成器测试"""

    def test_generate_for_trend(self):
        """生成趋势图注"""
        gen = CaptionGenerator()
        caption = gen.generate_for_trend(
            data_summary={"shape": (10, 2)},
            trend_direction="上升",
            magnitude=0.5,
        )
        assert isinstance(caption, AutoCaption)


class TestVisualizer:
    """可视化器集成测试"""

    def test_creation(self):
        """创建可视化器"""
        viz = Visualizer()
        assert viz is not None
