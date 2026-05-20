"""自主数据分析主入口 - 编排完整分析工作流"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from modules.analysis_planner import AnalysisPhase, AnalysisPlanner
from modules.assumption_tracker import AssumptionTracker, create_default_assumptions
from modules.data_pipeline import DataPipeline, PipelineConfig
from modules.data_source_detector import DataSourceDetector
from modules.dependency_installer import DependencyInstaller
from modules.goal_parser import AnalysisGoalSpec, parse_goal, refine_goal
from modules.method_selector import select_method
from modules.multi_agent_collaboration import (
    AggregatedResult,
    CollaborationMode,
    run_collaboration,
    select_mode,
)
from modules.report_generator import (
    AnalysisReport,
    MarkdownFormatter,
    ReportFormat,
    ReportGenerator,
)
from modules.self_review import ReviewReport, SelfReviewer
from modules.skill_persistence import (
    AnalysisSkill,
    SkillExtractor,
    SkillParameterizer,
    SkillReplayer,
    SkillStore,
    SkillVersionManager,
    SkillVersionStrategy,
)
from modules.visualization import Visualizer

logger = logging.getLogger(__name__)


class RunMode(Enum):
    """运行模式"""
    INTERACTIVE = "interactive"
    BATCH = "batch"
    REPLAY = "replay"


class WorkflowState(Enum):
    """工作流状态"""
    INIT = "init"
    PARSING = "parsing"
    ACQUIRING = "acquiring"
    CLEANING = "cleaning"
    PLANNING = "planning"
    EXECUTING = "executing"
    AGGREGATING = "aggregating"
    REVIEWING = "reviewing"
    REPORTING = "reporting"
    PERSISTING = "persisting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowContext:
    """工作流上下文 - 在各阶段间传递状态"""
    state: WorkflowState = WorkflowState.INIT
    goal_spec: AnalysisGoalSpec | None = None
    data_source: Any = None
    cleaned_data: Any = None
    analysis_plan: dict[str, Any] = field(default_factory=dict)
    execution_results: list[dict[str, Any]] = field(default_factory=list)
    aggregated_result: AggregatedResult | None = None
    review_report: ReviewReport | None = None
    final_report: AnalysisReport | None = None
    extracted_skill: AnalysisSkill | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    start_time: float = 0.0


@dataclass
class RunConfig:
    """运行配置"""
    run_mode: RunMode = RunMode.BATCH
    goal: str = ""
    data_path: str = ""
    output_dir: str = "./output"
    skill_dir: str = "./skills_data"
    skill_id: str = ""
    parameter_overrides: dict[str, Any] = field(default_factory=dict)
    max_review_iterations: int = 3
    enable_skill_persistence: bool = True
    log_level: str = "INFO"


def main(argv: list[str] | None = None) -> int:
    """
    主入口函数

    Args:
        argv: 命令行参数

    Returns:
        退出码
    """
    args = _parse_arguments(argv)
    _setup_logging(args.log_level)

    config = _build_config(args)
    logger.info("自主数据分析启动: mode=%s", config.run_mode.value)

    context = WorkflowContext(start_time=time.monotonic())

    try:
        if config.run_mode == RunMode.REPLAY:
            return _run_replay_mode(config, context)

        return _run_analysis(config, context)

    except KeyboardInterrupt:
        logger.info("用户中断执行")
        return 130
    except Exception as exc:
        logger.error("工作流执行失败: %s", exc, exc_info=True)
        context.state = WorkflowState.FAILED
        context.errors.append(str(exc))
        return 1


def _run_analysis(config: RunConfig, context: WorkflowContext) -> int:
    """
    运行完整分析流程

    Args:
        config: 运行配置
        context: 工作流上下文

    Returns:
        退出码
    """
    context.state = WorkflowState.PARSING
    goal_spec = _run_goal_parsing(config.goal)
    context.goal_spec = goal_spec
    logger.info("目标解析完成: category=%s, domain=%s", goal_spec.category.value, goal_spec.domain)

    context.state = WorkflowState.ACQUIRING
    data = _run_data_acquisition(config.data_path)
    context.data_source = data

    context.state = WorkflowState.CLEANING
    cleaned = _run_data_cleaning(data, goal_spec)
    context.cleaned_data = cleaned

    context.state = WorkflowState.PLANNING
    plan = _run_analysis_planning(goal_spec, cleaned)
    context.analysis_plan = plan

    context.state = WorkflowState.EXECUTING
    results = _run_multi_agent_execution(goal_spec, plan, cleaned)
    context.execution_results = results

    context.state = WorkflowState.AGGREGATING
    aggregated = _run_results_aggregation(results)
    context.aggregated_result = aggregated

    context.state = WorkflowState.REVIEWING
    review = _run_self_review(cleaned, results, aggregated, goal_spec)
    context.review_report = review

    context.state = WorkflowState.REPORTING
    report = _run_report_generation(goal_spec, cleaned, results, aggregated, review)
    context.final_report = report

    context.state = WorkflowState.PERSISTING
    if config.enable_skill_persistence:
        skill = _run_skill_persistence(
            goal_spec, plan, results, review, config.skill_dir
        )
        context.extracted_skill = skill

    context.state = WorkflowState.COMPLETED
    _output_results(report, config.output_dir)
    _log_workflow_summary(context)

    return 0


def _run_replay_mode(config: RunConfig, context: WorkflowContext) -> int:
    """
    运行技能回放模式

    Args:
        config: 运行配置
        context: 工作流上下文

    Returns:
        退出码
    """
    if not config.skill_id:
        logger.error("回放模式需要指定 skill_id")
        return 1

    store = SkillStore(storage_dir=config.skill_dir)
    skills = store.find_skills(tags=[config.skill_id])

    if not skills:
        logger.error("未找到技能: %s", config.skill_id)
        return 1

    target = skills[0]
    skill = store.load_skill(target.file_path)
    logger.info("加载技能: %s (版本 %s)", skill.metadata.name, skill.metadata.version)

    replayer = SkillReplayer()
    replayer.register_skill(skill)

    context.state = WorkflowState.ACQUIRING
    data = _run_data_acquisition(config.data_path)

    context.state = WorkflowState.EXECUTING
    replay_result = replayer.replay(
        skill_id=skill.metadata.skill_id,
        data=data,
        parameter_overrides=config.parameter_overrides,
    )

    context.execution_results = [replay_result]
    context.state = WorkflowState.REPORTING

    report = _build_replay_report(replay_result, config.goal)
    context.final_report = report

    context.state = WorkflowState.COMPLETED
    _output_results(report, config.output_dir)

    return 0


def _run_goal_parsing(goal: str) -> AnalysisGoalSpec:
    """
    执行目标解析

    Args:
        goal: 自然语言分析目标

    Returns:
        结构化的分析目标规格
    """
    spec = parse_goal(goal)

    if spec.confidence < 0.6:
        logger.warning("目标解析置信度较低: %.2f", spec.confidence)

    return spec


def _run_data_acquisition(data_path: str) -> Any:
    """
    执行数据获取

    Args:
        data_path: 数据路径

    Returns:
        获取到的数据
    """
    detector = DataSourceDetector()
    detection = detector.detect(data_path)
    logger.info("数据源检测完成: type=%s", detection.source_type.value)

    pipeline = DataPipeline()
    data = pipeline.load(detection)

    return data


def _run_data_cleaning(data: Any, goal_spec: AnalysisGoalSpec) -> Any:
    """
    执行数据清洗

    Args:
        data: 原始数据
        goal_spec: 分析目标

    Returns:
        清洗后的数据
    """
    config = PipelineConfig(
        auto_detect_types=True,
        handle_missing="interpolate",
        handle_outliers="clip",
    )

    pipeline = DataPipeline(config=config)
    cleaned = pipeline.clean(data)
    cleaned = pipeline.transform(cleaned, goal_spec)

    stats = pipeline.get_stats()
    logger.info("数据清洗完成: rows=%d, cols=%d", stats.row_count, stats.column_count)

    return cleaned


def _run_analysis_planning(
    goal_spec: AnalysisGoalSpec, data: Any
) -> dict[str, Any]:
    """
    执行分析规划

    Args:
        goal_spec: 分析目标
        data: 清洗后的数据

    Returns:
        分析计划
    """
    planner = AnalysisPlanner()
    plan = planner.create_plan(
        plan_id=f"plan_{goal_spec.category.value}",
        objective=goal_spec.objective,
        domain=goal_spec.domain,
        category=goal_spec.category.value,
    )

    planner.perceive(_build_data_summary(data))
    judgment = planner.judge()

    if not judgment.is_data_ready:
        logger.warning("数据未就绪: %s", judgment.plan_adjustment)

    plan_dict = {
        "plan_id": plan.plan_id,
        "goal_objective": plan.goal_objective,
        "steps": [
            {
                "step_id": s.step_id,
                "method": s.method.value,
                "description": s.description,
                "parameters": s.parameters,
            }
            for s in plan.steps
        ],
        "current_phase": plan.current_phase.value,
        "judgment": {
            "is_data_ready": judgment.is_data_ready,
            "next_method": judgment.next_method.value if judgment.next_method else None,
            "confidence": judgment.confidence,
        },
    }

    return plan_dict


def _run_multi_agent_execution(
    goal_spec: AnalysisGoalSpec,
    plan: dict[str, Any],
    data: Any,
) -> list[dict[str, Any]]:
    """
    执行多智能体分析

    Args:
        goal_spec: 分析目标
        plan: 分析计划
        data: 数据

    Returns:
        执行结果列表
    """
    mode = _select_collaboration_mode(plan)
    tasks = _build_agent_tasks(plan, data, goal_spec)

    result = run_collaboration(
        mode=mode,
        tasks=tasks,
        task_executor=_execute_single_task,
        max_workers=4,
    )

    results = [
        {
            "agent_id": r.agent_id,
            "output": r.output,
            "error": r.error,
            "execution_time_ms": r.execution_time_ms,
        }
        for r in result.results
    ]

    logger.info("多智能体执行完成: success=%d, failed=%d",
                len([r for r in results if r["error"] is None]),
                len([r for r in results if r["error"] is not None]))

    return results


def _run_results_aggregation(
    results: list[dict[str, Any]]
) -> AggregatedResult:
    """
    聚合分析结果

    Args:
        results: 执行结果列表

    Returns:
        聚合结果
    """
    aggregated = AggregatedResult(
        mode=CollaborationMode.SUBAGENT_CONCURRENT,
        results=[],
    )

    for result in results:
        from modules.multi_agent_collaboration import AgentResult, AgentRole
        aggregated.results.append(
            AgentResult(
                agent_id=result["agent_id"],
                role=AgentRole.EXECUTOR,
                output=result["output"],
                error=result["error"],
                execution_time_ms=result["execution_time_ms"],
            )
        )

    success_count = len([r for r in results if r["error"] is None])
    aggregated.consistency_score = success_count / max(len(results), 1)
    aggregated.has_conflict = any(r["error"] is not None for r in results)

    return aggregated


def _run_self_review(
    data: Any,
    results: list[dict[str, Any]],
    aggregated: AggregatedResult,
    goal_spec: AnalysisGoalSpec,
) -> ReviewReport:
    """
    执行自审验证

    Args:
        data: 数据
        results: 执行结果
        aggregated: 聚合结果
        goal_spec: 分析目标

    Returns:
        自审报告
    """
    reviewer = SelfReviewer()
    report = reviewer.review(
        data=data,
        results=_extract_findings(results),
        aggregated=aggregated,
        goal_spec=goal_spec,
    )

    if report.findings:
        logger.warning("自审发现 %d 个问题", len(report.findings))

    return report


def _run_report_generation(
    goal_spec: AnalysisGoalSpec,
    data: Any,
    results: list[dict[str, Any]],
    aggregated: AggregatedResult,
    review_report: ReviewReport,
) -> AnalysisReport:
    """
    生成分析报告

    Args:
        goal_spec: 分析目标
        data: 数据
        results: 执行结果
        aggregated: 聚合结果
        review_report: 自审报告

    Returns:
        分析报告
    """
    visualizer = Visualizer()
    report_gen = ReportGenerator()

    sections_data = _build_report_sections(
        goal_spec, data, results, aggregated, review_report, visualizer
    )

    report = report_gen.generate(
        report_id=f"report_{goal_spec.category.value}",
        title=f"{goal_spec.domain or '通用'}数据分析报告",
        sections_data=sections_data,
        metadata={
            "goal": goal_spec.original_goal,
            "category": goal_spec.category.value,
        },
    )

    logger.info("报告生成完成: id=%s", report.report_id)
    return report


def _run_skill_persistence(
    goal_spec: AnalysisGoalSpec,
    plan: dict[str, Any],
    results: list[dict[str, Any]],
    review_report: ReviewReport,
    skill_dir: str,
) -> AnalysisSkill | None:
    """
    执行技能持久化

    Args:
        goal_spec: 分析目标
        plan: 分析计划
        results: 执行结果
        review_report: 自审报告
        skill_dir: 技能存储目录

    Returns:
        提取的技能或 None
    """
    try:
        extractor = SkillExtractor()
        skill = extractor.extract_from_execution(
            goal_spec=_goal_spec_to_dict(goal_spec),
            pipeline_config={},
            analysis_plan=plan,
            results={"charts": [], "sections": []},
            review_report=_review_report_to_dict(review_report),
        )

        parameterizer = SkillParameterizer()
        skill = parameterizer.parameterize(skill)

        store = SkillStore(storage_dir=skill_dir)
        store.save_skill(skill)

        version_mgr = SkillVersionManager()
        version_mgr.create_version(
            skill=skill,
            strategy=SkillVersionStrategy.SEMANTIC,
            change_description="初始版本",
        )

        logger.info("技能持久化完成: id=%s", skill.metadata.skill_id)
        return skill

    except Exception as exc:
        logger.warning("技能持久化失败: %s", exc)
        return None


def _output_results(report: AnalysisReport, output_dir: str) -> None:
    """
    输出分析结果

    Args:
        report: 分析报告
        output_dir: 输出目录
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    md_content = MarkdownFormatter.format(report)
    md_file = output_path / f"{report.report_id}.md"
    md_file.write_text(md_content, encoding="utf-8")

    logger.info("报告已输出: %s", md_file)


def _select_collaboration_mode(plan: dict[str, Any]) -> CollaborationMode:
    """选择协作模式"""
    step_count = len(plan.get("steps", []))
    has_deps = step_count > 2

    return select_mode(
        has_dependencies=has_deps,
        need_iteration=False,
        task_count=step_count,
    )


def _build_agent_tasks(
    plan: dict[str, Any],
    data: Any,
    goal_spec: AnalysisGoalSpec,
) -> list[dict[str, Any]]:
    """构建智能体任务列表"""
    tasks: list[dict[str, Any]] = []

    for step in plan.get("steps", []):
        tasks.append(
            {
                "task_id": step["step_id"],
                "method": step["method"],
                "data": data,
                "parameters": step.get("parameters", {}),
                "goal_category": goal_spec.category.value,
            }
        )

    return tasks


def _execute_single_task(task: dict[str, Any]) -> dict[str, Any]:
    """执行单个任务"""
    method = task.get("method", "unknown")
    logger.info("执行任务: %s (方法: %s)", task["task_id"], method)

    return {
        "task_id": task["task_id"],
        "method": method,
        "status": "completed",
        "result": f"{method} 执行结果",
    }


def _build_data_summary(data: Any) -> dict[str, Any]:
    """构建数据摘要"""
    summary: dict[str, Any] = {}

    if hasattr(data, "shape"):
        summary["shape"] = data.shape
    if hasattr(data, "isnull"):
        summary["missing_ratio"] = float(data.isnull().mean().mean())
    if hasattr(data, "dtypes"):
        summary["column_types"] = {
            col: str(dtype) for col, dtype in data.dtypes.items()
        }

    return summary


def _extract_findings(results: list[dict[str, Any]]) -> list[str]:
    """提取分析发现"""
    findings: list[str] = []

    for result in results:
        if result.get("error") is None:
            findings.append(str(result.get("result", "")))

    return findings


def _build_report_sections(
    goal_spec: AnalysisGoalSpec,
    data: Any,
    results: list[dict[str, Any]],
    aggregated: AggregatedResult,
    review_report: ReviewReport,
    visualizer: Visualizer,
) -> dict[str, Any]:
    """构建报告章节数据"""
    sections: dict[str, Any] = {}

    sections["executive_summary"] = {
        "content": _build_executive_summary(goal_spec, results, aggregated),
        "title": "执行摘要",
    }

    sections["analysis_background"] = {
        "content": goal_spec.original_goal,
        "title": "分析背景",
    }

    sections["data_overview"] = {
        "content": _build_data_overview(data),
        "title": "数据概览",
    }

    sections["detailed_findings"] = {
        "content": "\n".join(f"- {f}" for f in _extract_findings(results)),
        "title": "详细发现",
    }

    sections["risk_assessment"] = {
        "content": _build_risk_assessment(review_report),
        "title": "风险评估",
    }

    sections["recommendations"] = {
        "content": _build_recommendations(goal_spec, results),
        "title": "建议",
    }

    return sections


def _build_executive_summary(
    goal_spec: AnalysisGoalSpec,
    results: list[dict[str, Any]],
    aggregated: AggregatedResult,
) -> str:
    """构建执行摘要"""
    success_count = len([r for r in results if r.get("error") is None])
    total = len(results)

    parts = [
        f"本次{goal_spec.domain or '通用'}分析共执行 {total} 个分析步骤，",
        f"其中 {success_count} 个成功完成。",
        f"整体一致性分数: {aggregated.consistency_score:.2%}",
    ]

    return "".join(parts)


def _build_data_overview(data: Any) -> str:
    """构建数据概览"""
    if hasattr(data, "shape"):
        return f"数据规模: {data.shape[0]} 行 × {data.shape[1]} 列"
    return "数据概览信息不可用"


def _build_risk_assessment(review_report: ReviewReport) -> str:
    """构建风险评估"""
    if not review_report.findings:
        return "未发现明显风险"

    parts = ["发现以下风险:"]
    for finding in review_report.findings:
        parts.append(f"- {finding.description} (严重度: {finding.severity})")

    return "\n".join(parts)


def _build_recommendations(
    goal_spec: AnalysisGoalSpec,
    results: list[dict[str, Any]],
) -> str:
    """构建建议"""
    recommendations: list[str] = [
        f"基于{goal_spec.domain or '通用'}分析结果，建议:",
        "1. 定期复现分析流程，验证结论稳定性",
        "2. 关注数据质量变化，及时更新分析模型",
    ]

    return "\n".join(recommendations)


def _build_replay_report(
    replay_result: dict[str, Any],
    goal: str,
) -> AnalysisReport:
    """构建回放报告"""
    from modules.report_generator import ReportSection

    return AnalysisReport(
        report_id=f"replay_{replay_result.get('skill_id', 'unknown')}",
        title="技能回放报告",
        generated_at=replay_result.get("replayed_at", ""),
        sections=[
            ReportSection(
                section_id="replay_summary",
                title="回放摘要",
                content=f"技能 {replay_result.get('skill_name', '')} 回放完成",
            ),
            ReportSection(
                section_id="parameters",
                title="使用参数",
                content=str(replay_result.get("parameters_used", {})),
            ),
        ],
        metadata={"original_goal": goal},
    )


def _goal_spec_to_dict(spec: AnalysisGoalSpec) -> dict[str, Any]:
    """将目标规格转换为字典"""
    return {
        "category": spec.category.value,
        "domain": spec.domain,
        "objective": spec.objective,
    }


def _review_report_to_dict(report: ReviewReport) -> dict[str, Any]:
    """将自审报告转换为字典"""
    return {
        "checks": [
            {
                "dimension": f.dimension.value if hasattr(f.dimension, "value") else str(f.dimension),
                "severity": f.severity.value if hasattr(f.severity, "value") else f.severity,
                "description": f.description,
            }
            for f in report.findings
        ]
    }


def _log_workflow_summary(context: WorkflowContext) -> None:
    """记录工作流摘要"""
    elapsed = time.monotonic() - context.start_time
    state = context.state.value

    logger.info(
        "工作流完成: state=%s, elapsed=%.2fs, errors=%d",
        state,
        elapsed,
        len(context.errors),
    )


def _setup_logging(log_level: str) -> None:
    """配置日志"""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="自主数据分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "goal",
        nargs="?",
        default="",
        help="自然语言分析目标",
    )
    parser.add_argument(
        "--data",
        default="",
        help="数据源路径",
    )
    parser.add_argument(
        "--mode",
        choices=["interactive", "batch", "replay"],
        default="batch",
        help="运行模式",
    )
    parser.add_argument(
        "--skill-id",
        default="",
        help="技能回放模式下的技能标识",
    )
    parser.add_argument(
        "--output",
        default="./output",
        help="输出目录",
    )
    parser.add_argument(
        "--skill-dir",
        default="./skills_data",
        help="技能存储目录",
    )
    parser.add_argument(
        "--no-skill-persist",
        action="store_true",
        help="禁用技能持久化",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="日志级别",
    )

    return parser.parse_args(argv)


def _build_config(args: argparse.Namespace) -> RunConfig:
    """构建运行配置"""
    mode_map = {
        "interactive": RunMode.INTERACTIVE,
        "batch": RunMode.BATCH,
        "replay": RunMode.REPLAY,
    }

    return RunConfig(
        run_mode=mode_map.get(args.mode, RunMode.BATCH),
        goal=args.goal,
        data_path=args.data,
        output_dir=args.output,
        skill_dir=args.skill_dir,
        skill_id=args.skill_id,
        enable_skill_persistence=not args.no_skill_persist,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    sys.exit(main())
