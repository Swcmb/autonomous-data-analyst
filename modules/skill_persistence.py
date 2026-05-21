"""技能持久化与复用模块 - 自动提取、参数化、保存和回放分析流程"""

from __future__ import annotations

import copy
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SkillVersionStrategy(Enum):
    """技能版本策略"""
    SEMANTIC = "semantic"
    TIMESTAMP = "timestamp"
    INCREMENTAL = "incremental"


@dataclass
class InputSpecification:
    """输入规格 - 定义技能所需的数据格式和必填字段"""
    data_format: str  # csv, json, parquet, etc.
    required_fields: list[str] = field(default_factory=list)
    optional_fields: list[str] = field(default_factory=list)
    field_types: dict[str, str] = field(default_factory=dict)
    validation_rules: dict[str, Any] = field(default_factory=dict)
    min_rows: int = 1
    description: str = ""


@dataclass
class ProcessingRule:
    """数据处理规则"""
    rule_id: str
    rule_type: str  # clean, transform, filter, aggregate, etc.
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    order: int = 0


@dataclass
class AnalysisLogic:
    """分析逻辑和方法选择标准"""
    logic_id: str
    method_name: str
    selection_criteria: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    fallback_method: str | None = None
    description: str = ""


@dataclass
class ChartTemplate:
    """图表模板和可视化配置"""
    template_id: str
    chart_type: str
    title_template: str = ""
    x_column: str | None = None
    y_columns: list[str] = field(default_factory=list)
    group_by: str | None = None
    style_config: dict[str, Any] = field(default_factory=dict)
    caption_template: str = ""
    enabled: bool = True


@dataclass
class OutputTemplate:
    """输出模板"""
    template_id: str
    section_name: str
    content_format: str  # markdown, table, text, etc.
    template_content: str = ""
    required: bool = True
    order: int = 0


@dataclass
class ExceptionRule:
    """异常处理规则"""
    rule_id: str
    exception_type: str
    handler_action: str  # skip, warn, error, fallback, etc.
    fallback_value: Any = None
    description: str = ""
    enabled: bool = True


@dataclass
class ReviewRule:
    """自审验证规则"""
    rule_id: str
    check_dimension: str
    threshold: float | None = None
    severity: str = "warning"  # info, warning, error
    description: str = ""
    enabled: bool = True


@dataclass
class SkillParameter:
    """技能参数定义"""
    param_name: str
    param_type: str  # str, int, float, bool, list, dict
    default_value: Any = None
    required: bool = False
    description: str = ""
    validation: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillMetadata:
    """技能元数据"""
    skill_id: str = ""
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    author: str = "auto-generated"
    created_at: str = ""
    updated_at: str = ""
    tags: list[str] = field(default_factory=list)
    category: str = ""
    success_count: int = 0
    last_used_at: str = ""


@dataclass
class AnalysisSkill:
    """完整的可复用分析技能"""
    metadata: SkillMetadata = field(default_factory=SkillMetadata)
    input_spec: InputSpecification | None = None
    processing_rules: list[ProcessingRule] = field(default_factory=list)
    analysis_logics: list[AnalysisLogic] = field(default_factory=list)
    chart_templates: list[ChartTemplate] = field(default_factory=list)
    output_templates: list[OutputTemplate] = field(default_factory=list)
    review_rules: list[ReviewRule] = field(default_factory=list)
    exception_rules: list[ExceptionRule] = field(default_factory=list)
    parameters: list[SkillParameter] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillRegistryEntry:
    """技能注册表条目"""
    skill_id: str
    name: str
    version: str
    file_path: str
    category: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: str = ""
    last_used_at: str = ""
    usage_count: int = 0


class SkillExtractor:
    """技能提取器 - 从成功的分析流程中提取可复用技能"""

    @classmethod
    def extract_from_execution(
        cls,
        goal_spec: dict[str, Any],
        pipeline_config: dict[str, Any],
        analysis_plan: dict[str, Any],
        results: dict[str, Any],
        review_report: dict[str, Any],
    ) -> AnalysisSkill:
        """
        从一次成功的分析执行中提取技能

        Args:
            goal_spec: 目标解析结果
            pipeline_config: 数据处理配置
            analysis_plan: 分析计划
            results: 分析结果
            review_report: 自审报告

        Returns:
            AnalysisSkill: 提取的技能
        """
        skill = cls._create_base_skill(goal_spec)
        skill.input_spec = cls._extract_input_spec(goal_spec, pipeline_config)
        skill.processing_rules = cls._extract_processing_rules(pipeline_config)
        skill.analysis_logics = cls._extract_analysis_logics(analysis_plan, results)
        skill.chart_templates = cls._extract_chart_templates(results)
        skill.output_templates = cls._extract_output_templates(results)
        skill.review_rules = cls._extract_review_rules(review_report)
        skill.exception_rules = cls._extract_exception_rules(results)

        return skill

    @classmethod
    def _create_base_skill(cls, goal_spec: dict[str, Any]) -> AnalysisSkill:
        """创建基础技能框架"""
        category = goal_spec.get("category", "general")
        domain = goal_spec.get("domain", "unknown")

        metadata = SkillMetadata(
            skill_id=f"skill_{uuid.uuid4().hex[:8]}",
            name=f"{domain}_{category}_analysis",
            description=f"自动提取的{domain}领域{category}分析技能",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=[domain, category, "auto-extracted"],
            category=category,
        )

        return AnalysisSkill(metadata=metadata)

    @classmethod
    def _extract_input_spec(
        cls,
        goal_spec: dict[str, Any],
        pipeline_config: dict[str, Any],
    ) -> InputSpecification:
        """提取输入规格"""
        required = pipeline_config.get("required_fields", [])
        optional = pipeline_config.get("optional_fields", [])
        field_types = pipeline_config.get("field_types", {})

        return InputSpecification(
            data_format=pipeline_config.get("data_format", "csv"),
            required_fields=required,
            optional_fields=optional,
            field_types=field_types,
            validation_rules=pipeline_config.get("validation_rules", {}),
            min_rows=pipeline_config.get("min_rows", 1),
            description=f"适用于{goal_spec.get('category', '通用')}分析的输入数据规格",
        )

    @classmethod
    def _extract_processing_rules(
        cls, pipeline_config: dict[str, Any]
    ) -> list[ProcessingRule]:
        """提取数据处理规则"""
        rules: list[ProcessingRule] = []
        raw_rules = pipeline_config.get("processing_steps", [])

        for idx, step in enumerate(raw_rules):
            rules.append(
                ProcessingRule(
                    rule_id=f"rule_{idx:03d}",
                    rule_type=step.get("type", "transform"),
                    description=step.get("description", ""),
                    parameters=step.get("parameters", {}),
                    enabled=step.get("enabled", True),
                    order=idx,
                )
            )

        return rules

    @classmethod
    def _extract_analysis_logics(
        cls,
        analysis_plan: dict[str, Any],
        results: dict[str, Any],
    ) -> list[AnalysisLogic]:
        """提取分析逻辑"""
        logics: list[AnalysisLogic] = []
        steps = analysis_plan.get("steps", [])

        for idx, step in enumerate(steps):
            method = step.get("method", "")
            if not method:
                continue

            logics.append(
                AnalysisLogic(
                    logic_id=f"logic_{idx:03d}",
                    method_name=method,
                    selection_criteria=step.get("selection_criteria", {}),
                    parameters=step.get("parameters", {}),
                    fallback_method=step.get("fallback_method"),
                    description=step.get("description", ""),
                )
            )

        return logics

    @classmethod
    def _extract_chart_templates(
        cls, results: dict[str, Any]
    ) -> list[ChartTemplate]:
        """提取图表模板"""
        templates: list[ChartTemplate] = []
        charts = results.get("charts", [])

        for idx, chart in enumerate(charts):
            templates.append(
                ChartTemplate(
                    template_id=f"chart_{idx:03d}",
                    chart_type=chart.get("type", "bar"),
                    title_template=chart.get("title", ""),
                    x_column=chart.get("x_column"),
                    y_columns=chart.get("y_columns", []),
                    group_by=chart.get("group_by"),
                    style_config=chart.get("style_config", {}),
                    caption_template=chart.get("caption", ""),
                    enabled=True,
                )
            )

        return templates

    @classmethod
    def _extract_output_templates(
        cls, results: dict[str, Any]
    ) -> list[OutputTemplate]:
        """提取输出模板"""
        templates: list[OutputTemplate] = []
        sections = results.get("sections", [])

        for idx, section in enumerate(sections):
            templates.append(
                OutputTemplate(
                    template_id=f"output_{idx:03d}",
                    section_name=section.get("title", ""),
                    content_format=section.get("format", "markdown"),
                    template_content=section.get("content_template", ""),
                    required=section.get("required", True),
                    order=section.get("order", idx),
                )
            )

        return templates

    @classmethod
    def _extract_review_rules(
        cls, review_report: dict[str, Any]
    ) -> list[ReviewRule]:
        """提取自审规则"""
        rules: list[ReviewRule] = []
        checks = review_report.get("checks", [])

        for idx, check in enumerate(checks):
            rules.append(
                ReviewRule(
                    rule_id=f"review_{idx:03d}",
                    check_dimension=check.get("dimension", ""),
                    threshold=check.get("threshold"),
                    severity=check.get("severity", "warning"),
                    description=check.get("description", ""),
                    enabled=True,
                )
            )

        return rules

    @classmethod
    def _extract_exception_rules(
        cls, results: dict[str, Any]
    ) -> list[ExceptionRule]:
        """提取异常处理规则"""
        rules: list[ExceptionRule] = []
        exceptions = results.get("exceptions_handled", [])

        for idx, exc in enumerate(exceptions):
            rules.append(
                ExceptionRule(
                    rule_id=f"exception_{idx:03d}",
                    exception_type=exc.get("type", ""),
                    handler_action=exc.get("action", "warn"),
                    fallback_value=exc.get("fallback_value"),
                    description=exc.get("description", ""),
                    enabled=True,
                )
            )

        return rules


class SkillParameterizer:
    """技能参数化系统 - 将硬编码值转换为可配置参数"""

    @classmethod
    def parameterize(cls, skill: AnalysisSkill) -> AnalysisSkill:
        """
        对技能进行参数化处理

        Args:
            skill: 待参数化的技能

        Returns:
            AnalysisSkill: 参数化后的技能
        """
        skill = copy.deepcopy(skill)
        parameters: list[SkillParameter] = []

        parameters.extend(cls._extract_parameters_from_input_spec(skill.input_spec))
        parameters.extend(
            cls._extract_parameters_from_processing_rules(skill.processing_rules)
        )
        parameters.extend(
            cls._extract_parameters_from_analysis_logics(skill.analysis_logics)
        )
        parameters.extend(
            cls._extract_parameters_from_chart_templates(skill.chart_templates)
        )

        skill.parameters = cls._deduplicate_parameters(parameters)
        return skill

    @classmethod
    def _extract_parameters_from_input_spec(
        cls, spec: InputSpecification | None
    ) -> list[SkillParameter]:
        """从输入规格提取参数"""
        params: list[SkillParameter] = []
        if spec is None:
            return params

        params.append(
            SkillParameter(
                param_name="data_format",
                param_type="str",
                default_value=spec.data_format,
                required=True,
                description="数据输入格式",
            )
        )
        params.append(
            SkillParameter(
                param_name="min_rows",
                param_type="int",
                default_value=spec.min_rows,
                required=False,
                description="最小数据行数",
                validation={"min": 1},
            )
        )

        return params

    @classmethod
    def _extract_parameters_from_processing_rules(
        cls, rules: list[ProcessingRule]
    ) -> list[SkillParameter]:
        """从处理规则提取参数"""
        params: list[SkillParameter] = []
        for rule in rules:
            for key, value in rule.parameters.items():
                param_type = cls._infer_type(value)
                params.append(
                    SkillParameter(
                        param_name=f"{rule.rule_id}_{key}",
                        param_type=param_type,
                        default_value=value,
                        required=False,
                        description=f"处理规则 {rule.rule_id} 的 {key} 参数",
                    )
                )
        return params

    @classmethod
    def _extract_parameters_from_analysis_logics(
        cls, logics: list[AnalysisLogic]
    ) -> list[SkillParameter]:
        """从分析逻辑提取参数"""
        params: list[SkillParameter] = []
        for logic in logics:
            for key, value in logic.parameters.items():
                param_type = cls._infer_type(value)
                params.append(
                    SkillParameter(
                        param_name=f"{logic.logic_id}_{key}",
                        param_type=param_type,
                        default_value=value,
                        required=False,
                        description=f"分析逻辑 {logic.logic_id} 的 {key} 参数",
                    )
                )
        return params

    @classmethod
    def _extract_parameters_from_chart_templates(
        cls, templates: list[ChartTemplate]
    ) -> list[SkillParameter]:
        """从图表模板提取参数"""
        params: list[SkillParameter] = []
        for template in templates:
            for key, value in template.style_config.items():
                param_type = cls._infer_type(value)
                params.append(
                    SkillParameter(
                        param_name=f"{template.template_id}_{key}",
                        param_type=param_type,
                        default_value=value,
                        required=False,
                        description=f"图表模板 {template.template_id} 的 {key} 参数",
                    )
                )
        return params

    @classmethod
    def _infer_type(cls, value: Any) -> str:
        """推断参数类型"""
        type_map: dict[type, str] = {
            str: "str",
            int: "int",
            float: "float",
            bool: "bool",
            list: "list",
            dict: "dict",
        }
        return type_map.get(type(value), "str")

    @classmethod
    def _deduplicate_parameters(
        cls, parameters: list[SkillParameter]
    ) -> list[SkillParameter]:
        """去重参数列表"""
        seen: set[str] = set()
        unique: list[SkillParameter] = []

        for param in parameters:
            if param.param_name not in seen:
                seen.add(param.param_name)
                unique.append(param)

        return unique


class SkillReplayer:
    """技能一键回放机制 - 根据保存的技能重新执行分析"""

    def __init__(self) -> None:
        self._skill_store: dict[str, AnalysisSkill] = {}

    def register_skill(self, skill: AnalysisSkill) -> None:
        """注册技能到内存存储"""
        self._skill_store[skill.metadata.skill_id] = skill
        logger.info("技能已注册: %s", skill.metadata.name)

    def replay(
        self,
        skill_id: str,
        data: Any,
        parameter_overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        回放指定技能

        Args:
            skill_id: 技能标识
            data: 输入数据
            parameter_overrides: 参数覆盖值

        Returns:
            分析结果字典
        """
        skill = self._skill_store.get(skill_id)
        if skill is None:
            raise ValueError(f"技能 {skill_id} 未找到")

        validated_data = self._validate_input(skill, data)
        effective_params = self._resolve_parameters(
            skill, parameter_overrides or {}
        )

        result = {
            "skill_id": skill_id,
            "skill_name": skill.metadata.name,
            "input_validated": True,
            "parameters_used": effective_params,
            "processing_results": self._execute_processing(
                skill, validated_data, effective_params
            ),
            "analysis_results": self._execute_analysis(
                skill, validated_data, effective_params
            ),
            "visualization_config": self._generate_visualization_config(
                skill, effective_params
            ),
            "output_template": self._generate_output_config(skill),
            "review_config": self._generate_review_config(skill),
            "replayed_at": datetime.now().isoformat(),
        }

        self._update_usage_stats(skill)
        logger.info("技能回放完成: %s", skill.metadata.name)

        return result

    def _validate_input(
        self, skill: AnalysisSkill, data: Any
    ) -> Any:
        """验证输入数据是否符合技能规格"""
        spec = skill.input_spec
        if spec is None:
            return data

        if hasattr(data, "columns") and hasattr(data, "shape"):
            self._check_required_columns(spec, data.columns.tolist())
            self._check_min_rows(spec, data.shape[0])

        return data

    def _check_required_columns(
        self, spec: InputSpecification, actual_columns: list[str]
    ) -> None:
        """检查必填列是否存在"""
        missing = [f for f in spec.required_fields if f not in actual_columns]
        if missing:
            raise ValueError(f"缺少必填字段: {', '.join(missing)}")

    def _check_min_rows(self, spec: InputSpecification, row_count: int) -> None:
        """检查最小行数"""
        if row_count < spec.min_rows:
            raise ValueError(
                f"数据行数 {row_count} 低于最小要求 {spec.min_rows}"
            )

    def _resolve_parameters(
        self, skill: AnalysisSkill, overrides: dict[str, Any]
    ) -> dict[str, Any]:
        """解析最终参数值"""
        params: dict[str, Any] = {}

        for param in skill.parameters:
            value = overrides.get(param.param_name, param.default_value)
            params[param.param_name] = self._validate_param_value(param, value)

        return params

    def _validate_param_value(
        self, param: SkillParameter, value: Any
    ) -> Any:
        """验证参数值"""
        if value is None and param.required:
            raise ValueError(f"必填参数 {param.param_name} 未提供")

        return value

    def _execute_processing(
        self,
        skill: AnalysisSkill,
        data: Any,
        params: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """执行数据处理步骤"""
        results: list[dict[str, Any]] = []

        for rule in sorted(skill.processing_rules, key=lambda r: r.order):
            if not rule.enabled:
                continue

            results.append(
                {
                    "rule_id": rule.rule_id,
                    "rule_type": rule.rule_type,
                    "status": "executed",
                    "parameters": self._apply_params(rule.parameters, params),
                }
            )

        return results

    def _execute_analysis(
        self,
        skill: AnalysisSkill,
        data: Any,
        params: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """执行分析步骤"""
        results: list[dict[str, Any]] = []

        for logic in skill.analysis_logics:
            results.append(
                {
                    "logic_id": logic.logic_id,
                    "method_name": logic.method_name,
                    "status": "ready",
                    "parameters": self._apply_params(logic.parameters, params),
                    "fallback_method": logic.fallback_method,
                }
            )

        return results

    def _generate_visualization_config(
        self, skill: AnalysisSkill, params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """生成可视化配置"""
        configs: list[dict[str, Any]] = []

        for template in skill.chart_templates:
            if not template.enabled:
                continue

            configs.append(
                {
                    "template_id": template.template_id,
                    "chart_type": template.chart_type,
                    "title": template.title_template,
                    "x_column": template.x_column,
                    "y_columns": template.y_columns,
                    "group_by": template.group_by,
                    "style_config": self._apply_params(
                        template.style_config, params
                    ),
                }
            )

        return configs

    def _generate_output_config(
        self, skill: AnalysisSkill
    ) -> list[dict[str, Any]]:
        """生成输出配置"""
        configs: list[dict[str, Any]] = []

        for template in sorted(skill.output_templates, key=lambda t: t.order):
            configs.append(
                {
                    "template_id": template.template_id,
                    "section_name": template.section_name,
                    "content_format": template.content_format,
                    "required": template.required,
                }
            )

        return configs

    def _generate_review_config(
        self, skill: AnalysisSkill
    ) -> list[dict[str, Any]]:
        """生成自审配置"""
        configs: list[dict[str, Any]] = []

        for rule in skill.review_rules:
            if not rule.enabled:
                continue

            configs.append(
                {
                    "rule_id": rule.rule_id,
                    "check_dimension": rule.check_dimension,
                    "threshold": rule.threshold,
                    "severity": rule.severity,
                }
            )

        return configs

    def _apply_params(
        self, template_params: dict[str, Any], resolved_params: dict[str, Any]
    ) -> dict[str, Any]:
        """将解析后的参数应用到模板参数中"""
        result = dict(template_params)

        for key, value in resolved_params.items():
            placeholder = f"{{{key}}}"
            for template_key, template_value in result.items():
                if isinstance(template_value, str) and placeholder in template_value:
                    result[template_key] = template_value.replace(
                        placeholder, str(value)
                    )

        return result

    def _update_usage_stats(self, skill: AnalysisSkill) -> None:
        """更新技能使用统计"""
        skill.metadata.success_count += 1
        skill.metadata.last_used_at = datetime.now().isoformat()


class SkillVersionManager:
    """技能版本管理器"""

    def __init__(self) -> None:
        self._version_map: dict[str, list[dict[str, Any]]] = {}

    def create_version(
        self,
        skill: AnalysisSkill,
        strategy: SkillVersionStrategy = SkillVersionStrategy.SEMANTIC,
        change_description: str = "",
    ) -> str:
        """
        创建技能新版本

        Args:
            skill: 技能对象
            strategy: 版本策略
            change_description: 变更描述

        Returns:
            新版本号
        """
        new_version = self._calculate_new_version(
            skill.metadata.version, strategy
        )

        version_record = {
            "version": new_version,
            "created_at": datetime.now().isoformat(),
            "change_description": change_description,
            "skill_snapshot": self._serialize_skill(skill),
        }

        skill_id = skill.metadata.skill_id
        if skill_id not in self._version_map:
            self._version_map[skill_id] = []

        self._version_map[skill_id].append(version_record)
        skill.metadata.version = new_version
        skill.metadata.updated_at = datetime.now().isoformat()

        logger.info("技能版本已创建: %s -> %s", skill_id, new_version)
        return new_version

    def get_versions(self, skill_id: str) -> list[dict[str, Any]]:
        """获取技能的所有版本"""
        return self._version_map.get(skill_id, [])

    def get_version(
        self, skill_id: str, version: str
    ) -> dict[str, Any] | None:
        """获取指定版本"""
        versions = self._version_map.get(skill_id, [])
        for v in versions:
            if v["version"] == version:
                return v
        return None

    def rollback(
        self, skill_id: str, target_version: str
    ) -> AnalysisSkill | None:
        """回滚到指定版本"""
        version_record = self.get_version(skill_id, target_version)
        if version_record is None:
            return None

        return self._deserialize_skill(version_record["skill_snapshot"])

    def _calculate_new_version(
        self, current: str, strategy: SkillVersionStrategy
    ) -> str:
        """计算新版本号"""
        if strategy == SkillVersionStrategy.SEMANTIC:
            return self._bump_semantic_version(current)
        if strategy == SkillVersionStrategy.TIMESTAMP:
            return datetime.now().strftime("%Y%m%d%H%M%S")

        return self._bump_incremental_version(current)

    def _bump_semantic_version(self, version: str) -> str:
        """增加语义化版本号（补丁版本）"""
        parts = version.split(".")
        if len(parts) == 3:
            try:
                parts[2] = str(int(parts[2]) + 1)
                return ".".join(parts)
            except ValueError:
                pass
        return version + ".1"

    def _bump_incremental_version(self, version: str) -> str:
        """增加递增版本号"""
        try:
            return str(int(version) + 1)
        except ValueError:
            return "1"

    def _serialize_skill(self, skill: AnalysisSkill) -> dict[str, Any]:
        """序列化技能对象"""
        return asdict(skill)

    def _deserialize_skill(self, data: dict[str, Any]) -> AnalysisSkill:
        """反序列化技能对象"""
        return self._dict_to_dataclass(data, AnalysisSkill)

    def _dict_to_dataclass(
        self, data: dict[str, Any], cls: type
    ) -> Any:
        """将字典转换为 dataclass 对象"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class SkillStore:
    """技能存储 - 保存和加载技能到文件"""

    def __init__(self, storage_dir: str | Path = "./skills_data") -> None:
        self._storage_dir = Path(storage_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._registry_file = self._storage_dir / "skill_registry.json"

    def save_skill(
        self,
        skill: AnalysisSkill,
        file_path: str | Path | None = None,
    ) -> Path:
        """
        保存技能到文件

        Args:
            skill: 技能对象
            file_path: 目标文件路径（可选，默认使用技能名）

        Returns:
            保存的文件路径
        """
        if file_path is None:
            file_name = f"{skill.metadata.skill_id}.json"
            file_path = self._storage_dir / file_name
        else:
            file_path = Path(file_path)

        file_path.parent.mkdir(parents=True, exist_ok=True)
        skill_data = self._serialize(skill)
        file_path.write_text(json.dumps(skill_data, ensure_ascii=False, indent=2))

        self._update_registry(skill, str(file_path))
        logger.info("技能已保存: %s", file_path)

        return file_path

    def load_skill(self, file_path: str | Path) -> AnalysisSkill:
        """
        从文件加载技能

        Args:
            file_path: 技能文件路径

        Returns:
            AnalysisSkill: 加载的技能
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"技能文件不存在: {file_path}")

        skill_data = json.loads(file_path.read_text())
        skill = self._deserialize(skill_data)
        logger.info("技能已加载: %s", file_path)

        return skill

    def list_skills(self) -> list[SkillRegistryEntry]:
        """列出所有已注册的技能"""
        if not self._registry_file.exists():
            return []

        registry_data = json.loads(self._registry_file.read_text())
        return [
            SkillRegistryEntry(**entry)
            for entry in registry_data.get("skills", [])
        ]

    def find_skills(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
        min_version: str | None = None,
    ) -> list[SkillRegistryEntry]:
        """按条件查找技能"""
        all_skills = self.list_skills()
        results = all_skills

        if category:
            results = [s for s in results if s.category == category]

        if tags:
            results = [
                s for s in results if any(t in s.tags for t in tags)
            ]

        return results

    def delete_skill(self, skill_id: str) -> bool:
        """删除指定技能"""
        skills = self.list_skills()
        target = next((s for s in skills if s.skill_id == skill_id), None)

        if target is None:
            return False

        file_path = Path(target.file_path)
        if file_path.exists():
            file_path.unlink()

        self._remove_from_registry(skill_id)
        logger.info("技能已删除: %s", skill_id)

        return True

    def _serialize(self, skill: AnalysisSkill) -> dict[str, Any]:
        """序列化技能"""
        return asdict(skill)

    def _deserialize(self, data: dict[str, Any]) -> AnalysisSkill:
        """反序列化技能"""
        return self._dict_to_dataclass(data, AnalysisSkill)

    def _dict_to_dataclass(
        self, data: dict[str, Any], cls: type
    ) -> Any:
        """将字典转换为 dataclass"""
        fields = cls.__dataclass_fields__ if hasattr(cls, "__dataclass_fields__") else {}
        converted: dict[str, Any] = {}

        for key, value in data.items():
            if key not in fields:
                continue

            field_type = fields[key].type
            if hasattr(field_type, "__origin__"):
                converted[key] = value
            elif isinstance(value, dict) and hasattr(field_type, "__dataclass_fields__"):
                converted[key] = self._dict_to_dataclass(value, field_type)
            else:
                converted[key] = value

        return cls(**converted)

    def _update_registry(
        self, skill: AnalysisSkill, file_path: str
    ) -> None:
        """更新技能注册表"""
        registry = self._load_registry()
        existing = next(
            (s for s in registry["skills"] if s["skill_id"] == skill.metadata.skill_id),
            None,
        )

        entry = {
            "skill_id": skill.metadata.skill_id,
            "name": skill.metadata.name,
            "version": skill.metadata.version,
            "file_path": file_path,
            "category": skill.metadata.category,
            "tags": skill.metadata.tags,
            "created_at": skill.metadata.created_at,
            "last_used_at": skill.metadata.last_used_at,
            "usage_count": skill.metadata.success_count,
        }

        if existing:
            idx = registry["skills"].index(existing)
            registry["skills"][idx] = entry
        else:
            registry["skills"].append(entry)

        self._save_registry(registry)

    def _remove_from_registry(self, skill_id: str) -> None:
        """从注册表中移除技能"""
        registry = self._load_registry()
        registry["skills"] = [
            s for s in registry["skills"] if s["skill_id"] != skill_id
        ]
        self._save_registry(registry)

    def _load_registry(self) -> dict[str, Any]:
        """加载注册表"""
        if self._registry_file.exists():
            return json.loads(self._registry_file.read_text())
        return {"skills": [], "updated_at": ""}

    def _save_registry(self, registry: dict[str, Any]) -> None:
        """保存注册表"""
        registry["updated_at"] = datetime.now().isoformat()
        self._registry_file.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2)
        )
