"""
autonomous-data-analyst 模块包

提供自主数据分析能力，包括：
- 目标解析 (goal_parser)
- 分析规划 (analysis_planner)
- 数据源检测 (data_source_detector)
- 数据处理管道 (data_pipeline)
- 依赖安装 (dependency_installer)
- 多智能体协作 (multi_agent_collaboration)
- 方法选择 (method_selector)
- 假设跟踪 (assumption_tracker)
- 自审验证 (self_review)
- 可视化 (visualization)
- 报告生成 (report_generator)
"""

from __future__ import annotations

from .analysis_planner import (
    AnalysisPhase,
    AnalysisPlan,
    AnalysisPlanner,
    AnalysisStep,
    AnalysisMethod,
    JudgmentResult,
    MethodSelector,
    PerceptionResult,
)
from .assumption_tracker import (
    Assumption,
    AssumptionCategory,
    AssumptionReport,
    AssumptionTracker,
    ConfidenceLevel,
    ValidationStatus,
    create_default_assumptions,
)
from .data_pipeline import (
    DataPipeline,
    PipelineConfig,
    PipelineStats,
    FieldMapping,
    TimeAlignmentSpec,
)
from .data_source_detector import (
    DataSourceDetector,
    DataSourceInfo,
    DataSourceType,
    AccessProtocol,
    DetectionResult,
)
from .dependency_installer import (
    DependencyInstaller,
    DependencySpec,
    InstallResult,
)
from .goal_parser import (
    AnalysisGoalSpec,
    DeliverableSpec,
    GoalCategory,
    ImplicitRequirement,
    MetricSpec,
    TaskNode,
    TimeGranularity,
    parse_goal,
    refine_goal,
)
from .method_selector import (
    AnalysisMethodInfo,
    DataCharacteristic,
    METHOD_REGISTRY,
    MethodFamily,
    MethodRecommendation,
    ALL_METHODS,
    get_all_methods,
    get_method_parameters,
    get_methods_by_family,
    select_method,
    validate_data_for_method,
)
from .multi_agent_collaboration import (
    AgentResult,
    AgentRole,
    AggregatedResult,
    CollaborationMode,
    ParallelismDecision,
    decide_parallelism,
    execute_independent_multi_agent,
    execute_plan_execute_review,
    execute_subagents_concurrent,
    run_collaboration,
    select_mode,
)
from .report_generator import (
    AnalysisReport,
    MarkdownFormatter,
    ReportBuilder,
    ReportFormat,
    ReportGenerator,
    ReportSection,
    SectionTemplate,
    YamlFormatter,
    generate_auto_summary,
)
from .self_review import (
    BusinessRationalityChecker,
    DataConsistencyChecker,
    ModelEffectivenessChecker,
    ReviewDimension,
    ReviewFinding,
    ReviewReport,
    RiskLevel,
    SampleSizeRiskChecker,
    SelfReviewer,
)
from .visualization import (
    AnalysisType,
    AutoCaption,
    CaptionGenerator,
    ChartConfig,
    ChartSelector,
    ChartType,
    ColorManager,
    Visualizer,
)
from .skill_persistence import (
    AnalysisSkill,
    AnalysisLogic,
    ChartTemplate,
    ExceptionRule,
    InputSpecification,
    OutputTemplate,
    ProcessingRule,
    ReviewRule,
    SkillExtractor,
    SkillMetadata,
    SkillParameter,
    SkillParameterizer,
    SkillReplayer,
    SkillRegistryEntry,
    SkillStore,
    SkillVersionManager,
    SkillVersionStrategy,
)

__all__ = [
    # analysis_planner
    "AnalysisGoalSpec",
    "AnalysisMethod",
    "AnalysisPhase",
    "AnalysisPlan",
    "AnalysisPlanner",
    "AnalysisStep",
    "DeliverableSpec",
    "AccessProtocol",
    "DataPipeline",
    "DataSourceDetector",
    "DataSourceInfo",
    "DataSourceType",
    "DependencyInstaller",
    "DependencySpec",
    "DetectionResult",
    "FieldMapping",
    "GoalCategory",
    "ImplicitRequirement",
    "InstallResult",
    "JudgmentResult",
    "MethodSelector",
    "MetricSpec",
    "PerceptionResult",
    "PipelineConfig",
    "PipelineStats",
    "TaskNode",
    "TimeAlignmentSpec",
    "TimeGranularity",
    "parse_goal",
    "refine_goal",
    # multi_agent_collaboration
    "AgentResult",
    "AgentRole",
    "AggregatedResult",
    "CollaborationMode",
    "ParallelismDecision",
    "decide_parallelism",
    "execute_independent_multi_agent",
    "execute_plan_execute_review",
    "execute_subagents_concurrent",
    "run_collaboration",
    "select_mode",
    # method_selector
    "AnalysisMethodInfo",
    "DataCharacteristic",
    "MethodFamily",
    "MethodRecommendation",
    "METHOD_REGISTRY",
    "ALL_METHODS",
    "get_all_methods",
    "get_method_parameters",
    "get_methods_by_family",
    "select_method",
    "validate_data_for_method",
    # assumption_tracker
    "Assumption",
    "AssumptionCategory",
    "AssumptionReport",
    "AssumptionTracker",
    "ConfidenceLevel",
    "ValidationStatus",
    "create_default_assumptions",
    # self_review
    "BusinessRationalityChecker",
    "DataConsistencyChecker",
    "ModelEffectivenessChecker",
    "ReviewDimension",
    "ReviewFinding",
    "ReviewReport",
    "RiskLevel",
    "SampleSizeRiskChecker",
    "SelfReviewer",
    # visualization
    "AnalysisType",
    "AutoCaption",
    "CaptionGenerator",
    "ChartConfig",
    "ChartSelector",
    "ChartType",
    "ColorManager",
    "Visualizer",
    # report_generator
    "AnalysisReport",
    "MarkdownFormatter",
    "ReportBuilder",
    "ReportFormat",
    "ReportGenerator",
    "ReportSection",
    "SectionTemplate",
    "YamlFormatter",
    "generate_auto_summary",
    # skill_persistence
    "AnalysisSkill",
    "AnalysisLogic",
    "ChartTemplate",
    "ExceptionRule",
    "InputSpecification",
    "OutputTemplate",
    "ProcessingRule",
    "ReviewRule",
    "SkillExtractor",
    "SkillMetadata",
    "SkillParameter",
    "SkillParameterizer",
    "SkillReplayer",
    "SkillRegistryEntry",
    "SkillStore",
    "SkillVersionManager",
    "SkillVersionStrategy",
]
