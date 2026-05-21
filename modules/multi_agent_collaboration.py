"""多智能体协作模块 - 实现子智能体并行、独立多智能体、规划-执行-评审三种协作模式"""

from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class CollaborationMode(Enum):
    """协作模式"""
    SUBAGENT_CONCURRENT = "subagent_concurrent"
    INDEPENDENT_MULTI_AGENT = "independent_multi_agent"
    PLAN_EXECUTE_REVIEW = "plan_execute_review"


class AgentRole(Enum):
    """智能体角色"""
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"


@dataclass
class AgentResult:
    """单个智能体的执行结果"""
    agent_id: str
    role: AgentRole | None = None
    output: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    execution_time_ms: float = 0.0


@dataclass
class AggregatedResult:
    """聚合后的结果"""
    mode: CollaborationMode
    results: list[AgentResult] = field(default_factory=list)
    summary: str | None = None
    consistency_score: float = 1.0
    has_conflict: bool = False
    conflicts: list[str] = field(default_factory=list)


@dataclass
class ParallelismDecision:
    """并行决策结果"""
    should_parallelize: bool = False
    reason: str = ""
    split_strategy: str | None = None
    estimated_speedup: float = 1.0


PARALLELISM_THRESHOLD = 100  # 数据量阈值


def decide_parallelism(
    data_size: int,
    has_dependencies: bool,
    can_split_by_dimension: bool,
) -> ParallelismDecision:
    """
    判断是否可以并行执行

    Args:
        data_size: 数据量大小
        has_dependencies: 任务间是否存在依赖
        can_split_by_dimension: 是否可按维度拆分

    Returns:
        并行决策结果
    """
    if data_size < PARALLELISM_THRESHOLD:
        return ParallelismDecision(
            reason="数据量低于并行阈值"
        )

    if has_dependencies:
        return ParallelismDecision(
            reason="任务间存在依赖关系，无法并行"
        )

    if not can_split_by_dimension:
        return ParallelismDecision(
            reason="无法按维度拆分，并行效率低"
        )

    speedup = min(data_size / PARALLELISM_THRESHOLD, 4.0)

    return ParallelismDecision(
        should_parallelize=True,
        reason="满足并行条件：数据量充足、无依赖、可按维度拆分",
        split_strategy="dimension_split",
        estimated_speedup=speedup,
    )


def execute_subagents_concurrent(
    tasks: list[dict[str, Any]],
    task_executor: Callable[[dict[str, Any]], Any],
    max_workers: int = 4,
) -> AggregatedResult:
    """
    子智能体并发模式：拆分独立任务并行执行后聚合

    Args:
        tasks: 独立任务列表
        task_executor: 单个任务执行函数
        max_workers: 最大并发数

    Returns:
        聚合结果
    """
    if not tasks:
        return AggregatedResult(mode=CollaborationMode.SUBAGENT_CONCURRENT)

    results = _run_parallel_tasks(tasks, task_executor, max_workers)
    aggregated = _aggregate_results(results, CollaborationMode.SUBAGENT_CONCURRENT)

    logger.info("子智能体并发完成: %d 个任务", len(tasks))

    return aggregated


def execute_independent_multi_agent(
    agent_specs: list[dict[str, Any]],
    agent_executor: Callable[[dict[str, Any]], Any],
    aggregation_fn: Callable[[list[AgentResult]], dict[str, Any]] | None = None,
    max_workers: int = 4,
) -> AggregatedResult:
    """
    独立多智能体模式：不同智能体处理不同维度后统一聚合

    Args:
        agent_specs: 各智能体规格配置
        agent_executor: 智能体执行函数
        aggregation_fn: 自定义聚合函数
        max_workers: 最大并发数

    Returns:
        聚合结果
    """
    if not agent_specs:
        return AggregatedResult(mode=CollaborationMode.INDEPENDENT_MULTI_AGENT)

    results = _run_parallel_tasks(agent_specs, agent_executor, max_workers)

    if aggregation_fn is not None:
        summary_data = aggregation_fn(results)
        summary = str(summary_data)
    else:
        summary = _build_default_summary(results)

    aggregated = _aggregate_results(results, CollaborationMode.INDEPENDENT_MULTI_AGENT)
    aggregated.summary = summary

    logger.info("独立多智能体完成: %d 个智能体", len(agent_specs))

    return aggregated


def execute_plan_execute_review(
    planner_fn: Callable[[], list[dict[str, Any]]],
    executor_fn: Callable[[dict[str, Any]], Any],
    reviewer_fn: Callable[[list[AgentResult]], dict[str, Any]],
    max_iterations: int = 3,
    max_workers: int = 4,
) -> AggregatedResult:
    """
    规划-执行-评审模式：Planner、Executor、Reviewer 智能体迭代协作

    Args:
        planner_fn: 规划器函数，返回任务列表
        executor_fn: 执行器函数
        reviewer_fn: 评审器函数
        max_iterations: 最大迭代次数
        max_workers: 最大并发数

    Returns:
        聚合结果
    """
    all_results: list[AgentResult] = []
    iteration = 0
    approved = False

    while iteration < max_iterations and not approved:
        iteration += 1
        logger.info("规划-执行-评审迭代: %d/%d", iteration, max_iterations)

        tasks = planner_fn()
        if not tasks:
            logger.warning("规划器返回空任务列表")
            break

        step_results = _run_parallel_tasks(tasks, executor_fn, max_workers)
        all_results.extend(step_results)

        review_outcome = reviewer_fn(step_results)
        approved = review_outcome.get("approved", False)

        if not approved:
            logger.info("评审未通过，进入下一轮迭代")

    aggregated = _aggregate_results(all_results, CollaborationMode.PLAN_EXECUTE_REVIEW)
    aggregated.summary = f"迭代 {iteration} 轮，{'通过' if approved else '未通过'}评审"

    logger.info("规划-执行-评审完成: %d 轮迭代", iteration)

    return aggregated


def run_collaboration(
    mode: CollaborationMode,
    **kwargs: Any,
) -> AggregatedResult:
    """
    统一入口：根据协作模式分发到对应执行器

    Args:
        mode: 协作模式
        **kwargs: 各模式所需的参数

    Returns:
        聚合结果
    """
    handlers: dict[CollaborationMode, Callable[..., AggregatedResult]] = {
        CollaborationMode.SUBAGENT_CONCURRENT: execute_subagents_concurrent,
        CollaborationMode.INDEPENDENT_MULTI_AGENT: execute_independent_multi_agent,
        CollaborationMode.PLAN_EXECUTE_REVIEW: execute_plan_execute_review,
    }

    handler = handlers.get(mode)
    if handler is None:
        raise ValueError(f"未知的协作模式: {mode}")

    return handler(**kwargs)


def _run_parallel_tasks(
    tasks: list[dict[str, Any]],
    executor_fn: Callable[[dict[str, Any]], Any],
    max_workers: int,
) -> list[AgentResult]:
    """并行执行任务列表"""
    results: list[AgentResult] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures: dict[Future, dict[str, Any]] = {
            pool.submit(executor_fn, task): task for task in tasks
        }
        for future in as_completed(futures):
            task_spec = futures[future]
            task_id = task_spec.get("task_id", "unknown")
            result = _collect_future_result(future, task_id)
            results.append(result)

    return results


def _collect_future_result(future: Future, task_id: str) -> AgentResult:
    """收集单个 Future 的执行结果"""
    import time
    start = time.monotonic()

    try:
        output = future.result()
        elapsed = (time.monotonic() - start) * 1000
        return AgentResult(
            agent_id=task_id,
            output=output,
            execution_time_ms=elapsed,
        )
    except Exception as exc:
        elapsed = (time.monotonic() - start) * 1000
        return AgentResult(
            agent_id=task_id,
            error=str(exc),
            execution_time_ms=elapsed,
        )


def _aggregate_results(
    results: list[AgentResult],
    mode: CollaborationMode,
) -> AggregatedResult:
    """聚合结果并检查一致性"""
    aggregated = AggregatedResult(mode=mode, results=results)

    if not results:
        return aggregated

    conflicts = _detect_conflicts(results)
    aggregated.has_conflict = len(conflicts) > 0
    aggregated.conflicts = conflicts
    aggregated.consistency_score = _calculate_consistency(results)

    return aggregated


def _detect_conflicts(results: list[AgentResult]) -> list[str]:
    """检测结果间的冲突"""
    conflicts: list[str] = []
    successful = [r for r in results if r.error is None]

    if len(successful) < 2:
        return conflicts

    outputs = [r.output for r in successful]
    output_types = {type(o).__name__ for o in outputs}

    if len(output_types) > 1:
        conflicts.append(
            f"结果类型不一致: {', '.join(sorted(output_types))}"
        )

    error_count = len([r for r in results if r.error is not None])
    if error_count > 0:
        conflicts.append(f"{error_count} 个智能体执行失败")

    return conflicts


def _calculate_consistency(results: list[AgentResult]) -> float:
    """计算一致性分数"""
    if not results:
        return 1.0

    successful = [r for r in results if r.error is None]
    if not successful:
        return 0.0

    success_ratio = len(successful) / len(results)
    return round(success_ratio, 2)


def _build_default_summary(results: list[AgentResult]) -> str:
    """构建默认摘要"""
    success_count = len([r for r in results if r.error is None])
    total = len(results)
    return f"共 {total} 个智能体，{success_count} 个成功"


def select_mode(
    has_dependencies: bool,
    need_iteration: bool,
    task_count: int,
) -> CollaborationMode:
    """
    自动选择最合适的协作模式

    Args:
        has_dependencies: 任务间是否存在依赖
        need_iteration: 是否需要迭代评审
        task_count: 任务数量

    Returns:
        推荐的协作模式
    """
    if need_iteration:
        return CollaborationMode.PLAN_EXECUTE_REVIEW

    if has_dependencies:
        return CollaborationMode.INDEPENDENT_MULTI_AGENT

    if task_count > 1:
        return CollaborationMode.SUBAGENT_CONCURRENT

    return CollaborationMode.INDEPENDENT_MULTI_AGENT
