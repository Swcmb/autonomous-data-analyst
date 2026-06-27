"""多智能体协作模块测试"""

from __future__ import annotations

import pytest

from modules.multi_agent_collaboration import (
    AgentResult,
    AgentRole,
    AggregatedResult,
    CollaborationMode,
    ParallelismDecision,
    decide_parallelism,
    run_collaboration,
    select_mode,
)


class TestDecideParallelism:
    """并行决策测试"""

    def test_small_data_no_parallel(self):
        """小数据不并行"""
        decision = decide_parallelism(
            data_size=50, has_dependencies=False, can_split_by_dimension=False
        )
        assert isinstance(decision, ParallelismDecision)
        assert decision.should_parallelize is False

    def test_large_data_parallel(self):
        """大数据可并行"""
        decision = decide_parallelism(
            data_size=500, has_dependencies=False, can_split_by_dimension=True
        )
        assert decision.should_parallelize is True

    def test_dependencies_block_parallel(self):
        """有依赖时不并行"""
        decision = decide_parallelism(
            data_size=500, has_dependencies=True, can_split_by_dimension=True
        )
        assert decision.should_parallelize is False


class TestSelectMode:
    """协作模式选择测试"""

    def test_no_deps_subagent(self):
        """无依赖 → SubAgent 并发"""
        mode = select_mode(has_dependencies=False, need_iteration=False, task_count=3)
        assert mode == CollaborationMode.SUBAGENT_CONCURRENT

    def test_with_deps_independent(self):
        """有依赖 → 独立多智能体"""
        mode = select_mode(has_dependencies=True, need_iteration=False, task_count=3)
        assert mode == CollaborationMode.INDEPENDENT_MULTI_AGENT

    def test_iteration_mode(self):
        """需要迭代 → 计划执行评审"""
        mode = select_mode(has_dependencies=False, need_iteration=True, task_count=3)
        assert mode == CollaborationMode.PLAN_EXECUTE_REVIEW


class TestRunCollaboration:
    """协作执行测试"""

    def _task_executor(self, task: dict) -> dict:
        """简单任务执行器"""
        return {"task_id": task.get("task_id", "unknown"), "result": "done"}

    def test_subagent_concurrent(self):
        """SubAgent 并发模式"""
        tasks = [{"task_id": "t1"}, {"task_id": "t2"}, {"task_id": "t3"}]
        result = run_collaboration(
            mode=CollaborationMode.SUBAGENT_CONCURRENT,
            tasks=tasks,
            task_executor=self._task_executor,
        )
        assert isinstance(result, AggregatedResult)
        assert len(result.results) == 3

    def test_independent_multi_agent(self):
        """独立多智能体模式"""
        tasks = [{"task_id": "t1"}, {"task_id": "t2"}]
        result = run_collaboration(
            mode=CollaborationMode.INDEPENDENT_MULTI_AGENT,
            agent_specs=tasks,
            agent_executor=self._task_executor,
        )
        assert isinstance(result, AggregatedResult)

    def test_empty_tasks(self):
        """空任务列表"""
        result = run_collaboration(
            mode=CollaborationMode.SUBAGENT_CONCURRENT,
            tasks=[],
            task_executor=self._task_executor,
        )
        assert len(result.results) == 0

    def test_executor_error_handling(self):
        """执行器异常处理"""
        def failing_executor(task):
            raise ValueError("test error")

        tasks = [{"task_id": "t1"}]
        result = run_collaboration(
            mode=CollaborationMode.SUBAGENT_CONCURRENT,
            tasks=tasks,
            task_executor=failing_executor,
        )
        assert len(result.results) == 1
        assert result.results[0].error is not None

    def test_consistency_score(self):
        """一致性评分"""
        tasks = [{"task_id": "t1"}, {"task_id": "t2"}]
        result = run_collaboration(
            mode=CollaborationMode.SUBAGENT_CONCURRENT,
            tasks=tasks,
            task_executor=self._task_executor,
        )
        assert result.consistency_score == 1.0
        assert result.has_conflict is False
