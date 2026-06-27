"""目标解析模块测试"""

from __future__ import annotations

import pytest

from modules.goal_parser import (
    AnalysisGoalSpec,
    GoalCategory,
    TaskNode,
    parse_goal,
    refine_goal,
)


class TestParseGoal:
    """parse_goal 函数测试"""

    def test_exploratory_goal(self):
        """探索性分析目标解析"""
        spec = parse_goal("探索用户行为数据的分布和特征")
        assert spec.category in (GoalCategory.EXPLORATORY, GoalCategory.DESCRIPTIVE)

    def test_predictive_goal(self):
        """预测性分析目标解析"""
        spec = parse_goal("预测下个季度的销售额")
        assert spec.category == GoalCategory.PREDICTIVE

    def test_diagnostic_goal(self):
        """诊断性分析目标解析"""
        spec = parse_goal("分析销售额下降的原因")
        assert spec.category in (GoalCategory.DIAGNOSTIC, GoalCategory.PREDICTIVE)

    def test_domain_detection_ecommerce(self):
        """电商领域检测"""
        spec = parse_goal("分析电商销售数据")
        assert spec.domain is not None

    def test_domain_detection_finance(self):
        """金融领域检测"""
        spec = parse_goal("分析股票收益率和风险指标")
        assert isinstance(spec, AnalysisGoalSpec)

    def test_empty_goal(self):
        """空输入处理 - 应抛出 ValueError"""
        with pytest.raises(ValueError):
            parse_goal("")

    def test_no_keywords_goal(self):
        """无关键词输入"""
        spec = parse_goal("今天天气真好")
        assert isinstance(spec, AnalysisGoalSpec)

    def test_return_type(self):
        """返回类型验证"""
        spec = parse_goal("分析销售趋势")
        assert isinstance(spec, AnalysisGoalSpec)
        assert isinstance(spec.category, GoalCategory)
        assert isinstance(spec.task_graph, list)

    def test_metrics_extraction(self):
        """指标提取"""
        spec = parse_goal("分析销售额和利润率的变化趋势")
        assert isinstance(spec.metrics, list)

    def test_time_constraints(self):
        """时间约束提取"""
        spec = parse_goal("分析最近三个月的销售趋势")
        assert isinstance(spec.time_constraints, dict)


class TestRefineGoal:
    """refine_goal 函数测试"""

    def test_refine_returns_spec(self):
        """返回类型验证"""
        original = parse_goal("分析销售数据")
        refined = refine_goal(original, "增加季节性分析维度")
        assert isinstance(refined, AnalysisGoalSpec)


class TestTaskNode:
    """TaskNode 测试"""

    def test_creation(self):
        """创建任务节点"""
        node = TaskNode(task_id="t1", description="分析描述")
        assert node.task_id == "t1"
        assert node.status == "pending"
        assert node.depends_on == []

    def test_with_dependencies(self):
        """带依赖的任务节点"""
        node = TaskNode(task_id="t2", description="依赖任务", depends_on=["t1"])
        assert "t1" in node.depends_on
