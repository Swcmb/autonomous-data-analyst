"""报告生成模块 - 结构化分析报告生成"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """报告输出格式"""
    MARKDOWN = "markdown"
    YAML = "yaml"


@dataclass
class ReportSection:
    """报告章节"""
    section_id: str
    title: str
    content: str = ""
    subsections: list[ReportSection] = field(default_factory=list)
    charts: list[dict[str, Any]] = field(default_factory=list)
    order: int = 0


@dataclass
class AnalysisReport:
    """完整的分析报告"""
    report_id: str = ""
    title: str = ""
    generated_at: str = ""
    sections: list[ReportSection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    summary: str = ""


@dataclass
class SectionTemplate:
    """章节模板"""
    section_id: str
    title: str
    description: str = ""
    required: bool = True
    order: int = 0


# 标准报告模板定义
STANDARD_REPORT_TEMPLATE: list[SectionTemplate] = [
    SectionTemplate(
        section_id="executive_summary",
        title="执行摘要",
        description="分析结论和核心发现的简明概述",
        order=1,
    ),
    SectionTemplate(
        section_id="analysis_background",
        title="分析背景",
        description="分析目标、问题定义和业务上下文",
        order=2,
    ),
    SectionTemplate(
        section_id="data_overview",
        title="数据概览",
        description="数据来源、规模、质量和预处理说明",
        order=3,
    ),
    SectionTemplate(
        section_id="detailed_findings",
        title="详细发现",
        description="分析过程、方法和具体发现（含图表）",
        order=4,
    ),
    SectionTemplate(
        section_id="risk_assessment",
        title="风险评估",
        description="分析局限性和潜在风险说明",
        order=5,
    ),
    SectionTemplate(
        section_id="recommendations",
        title="建议",
        description="基于分析发现的可操作建议",
        order=6,
    ),
    SectionTemplate(
        section_id="appendix",
        title="附录",
        description="技术细节、补充数据和方法说明",
        required=False,
        order=7,
    ),
]


class ReportBuilder:
    """报告构建器 - 组装报告的各个章节"""

    def __init__(self, template: list[SectionTemplate] | None = None) -> None:
        self._template = template or STANDARD_REPORT_TEMPLATE
        self._sections: dict[str, ReportSection] = {}

    def add_section(
        self,
        section_id: str,
        content: str,
        title: str | None = None,
        charts: list[dict[str, Any]] | None = None,
    ) -> ReportBuilder:
        """
        添加或更新章节内容

        Args:
            section_id: 章节标识
            content: 章节内容
            title: 章节标题（可选，默认使用模板标题）
            charts: 关联图表列表

        Returns:
            self，支持链式调用
        """
        template_item = _find_template(self._template, section_id)
        section_title = title or (template_item.title if template_item else section_id)

        self._sections[section_id] = ReportSection(
            section_id=section_id,
            title=section_title,
            content=content,
            charts=charts or [],
            order=template_item.order if template_item else 0,
        )

        return self

    def add_subsection(
        self,
        parent_id: str,
        subsection: ReportSection,
    ) -> ReportBuilder:
        """添加子章节"""
        parent = self._sections.get(parent_id)
        if parent is None:
            logger.warning("父章节 %s 不存在，跳过子章节添加", parent_id)
            return self

        parent.subsections.append(subsection)
        return self

    def build(
        self,
        report_id: str = "",
        title: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> AnalysisReport:
        """
        构建完整报告

        Args:
            report_id: 报告标识
            title: 报告标题
            metadata: 元数据

        Returns:
            AnalysisReport: 完整的分析报告
        """
        sorted_sections = sorted(
            self._sections.values(), key=lambda s: s.order
        )

        report = AnalysisReport(
            report_id=report_id or f"report_{datetime.now():%Y%m%d%H%M%S}",
            title=title or "数据分析报告",
            generated_at=datetime.now().isoformat(),
            sections=sorted_sections,
            metadata=metadata or {},
        )

        report.summary = _generate_report_summary(sorted_sections)

        logger.info("报告构建完成: %s, 章节数=%d", report.report_id, len(sorted_sections))

        return report

    def get_missing_sections(self) -> list[str]:
        """获取模板中尚未添加的必填章节"""
        missing: list[str] = []
        for tmpl in self._template:
            if tmpl.required and tmpl.section_id not in self._sections:
                missing.append(tmpl.section_id)
        return missing


def _find_template(
    template: list[SectionTemplate], section_id: str
) -> SectionTemplate | None:
    """查找模板中的章节定义"""
    for item in template:
        if item.section_id == section_id:
            return item
    return None


def _generate_report_summary(sections: list[ReportSection]) -> str:
    """生成报告摘要"""
    summary_section = None
    for section in sections:
        if section.section_id == "executive_summary":
            summary_section = section
            break

    if summary_section and summary_section.content:
        return summary_section.content[:200] + "..." if len(summary_section.content) > 200 else summary_section.content

    return "报告已生成，包含以下章节: " + ", ".join(s.title for s in sections)


class MarkdownFormatter:
    """Markdown 格式转换器"""

    @classmethod
    def format(cls, report: AnalysisReport) -> str:
        """
        将报告转换为 Markdown 格式

        Args:
            report: 分析报告对象

        Returns:
            Markdown 格式的报告文本
        """
        lines: list[str] = []

        lines.append(f"# {report.title}")
        lines.append("")
        lines.append(f"**报告编号:** {report.report_id}")
        lines.append(f"**生成时间:** {report.generated_at}")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## 摘要")
        lines.append("")
        lines.append(report.summary)
        lines.append("")

        for section in report.sections:
            lines.extend(_format_section(section))

        if report.metadata:
            lines.extend(_format_metadata(report.metadata))

        return "\n".join(lines)


def _format_section(section: ReportSection, level: int = 2) -> list[str]:
    """格式化单个章节"""
    lines: list[str] = []
    heading = "#" * level
    lines.append(f"{heading} {section.title}")
    lines.append("")

    if section.content:
        lines.append(section.content)
        lines.append("")

    if section.charts:
        lines.extend(_format_charts(section.charts))

    if section.subsections:
        for sub in section.subsections:
            lines.extend(_format_section(sub, level + 1))

    return lines


def _format_charts(charts: list[dict[str, Any]]) -> list[str]:
    """格式化图表引用"""
    lines: list[str] = []
    lines.append("### 图表")
    lines.append("")

    for i, chart in enumerate(charts, 1):
        title = chart.get("title", f"图表 {i}")
        chart_type = chart.get("type", "chart")
        lines.append(f"- **{title}** ({chart_type})")

        if chart.get("caption"):
            lines.append(f"  > {chart['caption']}")

    lines.append("")
    return lines


def _format_metadata(metadata: dict[str, Any]) -> list[str]:
    """格式化元数据"""
    lines: list[str] = []
    lines.append("---")
    lines.append("")
    lines.append("## 元数据")
    lines.append("")

    for key, value in metadata.items():
        lines.append(f"- **{key}:** {value}")

    lines.append("")
    return lines


class YamlFormatter:
    """YAML 格式转换器"""

    @classmethod
    def format(cls, report: AnalysisReport) -> str:
        """
        将报告转换为 YAML 格式

        Args:
            report: 分析报告对象

        Returns:
            YAML 格式的报告文本
        """
        lines: list[str] = []

        lines.append(f"report_id: {report.report_id}")
        lines.append(f"title: {report.title}")
        lines.append(f"generated_at: {report.generated_at}")
        lines.append(f"summary: {report.summary}")
        lines.append("")
        lines.append("sections:")

        for section in report.sections:
            lines.extend(_format_yaml_section(section))

        if report.metadata:
            lines.append("")
            lines.append("metadata:")
            for key, value in report.metadata.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)


def _format_yaml_section(section: ReportSection, indent: int = 2) -> list[str]:
    """格式化 YAML 章节"""
    lines: list[str] = []
    prefix = " " * indent

    lines.append(f"{prefix}- section_id: {section.section_id}")
    lines.append(f"{prefix}  title: {section.title}")
    lines.append(f"{prefix}  content: |")

    content_lines = section.content.split("\n")
    for content_line in content_lines:
        lines.append(f"{prefix}    {content_line}")

    if section.subsections:
        lines.append(f"{prefix}  subsections:")
        for sub in section.subsections:
            lines.extend(_format_yaml_section(sub, indent + 4))

    return lines


class ReportGenerator:
    """报告生成器 - 整合报告构建和格式转换"""

    def __init__(self) -> None:
        self.builder = ReportBuilder()

    def generate(
        self,
        report_id: str,
        title: str,
        sections_data: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> AnalysisReport:
        """
        生成结构化报告

        Args:
            report_id: 报告标识
            title: 报告标题
            sections_data: 各章节数据 {section_id: {content, charts, ...}}
            metadata: 元数据

        Returns:
            AnalysisReport: 生成的报告
        """
        for section_id, data in sections_data.items():
            self.builder.add_section(
                section_id=section_id,
                content=data.get("content", ""),
                title=data.get("title"),
                charts=data.get("charts"),
            )

        return self.builder.build(
            report_id=report_id,
            title=title,
            metadata=metadata,
        )

    def export(
        self,
        report: AnalysisReport,
        fmt: ReportFormat = ReportFormat.MARKDOWN,
    ) -> str:
        """
        导出报告为指定格式

        Args:
            report: 报告对象
            fmt: 输出格式

        Returns:
            格式化后的报告文本
        """
        if fmt == ReportFormat.MARKDOWN:
            return MarkdownFormatter.format(report)
        if fmt == ReportFormat.YAML:
            return YamlFormatter.format(report)

        raise ValueError(f"不支持的报告格式: {fmt}")

    def generate_and_export(
        self,
        report_id: str,
        title: str,
        sections_data: dict[str, Any],
        fmt: ReportFormat = ReportFormat.MARKDOWN,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        生成并导出报告

        Args:
            report_id: 报告标识
            title: 报告标题
            sections_data: 章节数据
            fmt: 输出格式
            metadata: 元数据

        Returns:
            格式化后的报告文本
        """
        report = self.generate(report_id, title, sections_data, metadata)
        return self.export(report, fmt)


def generate_auto_summary(
    findings: list[str],
    key_metrics: dict[str, float],
    risk_level: str = "",
) -> str:
    """
    自动生成报告摘要

    Args:
        findings: 分析发现列表
        key_metrics: 关键指标
        risk_level: 风险等级

    Returns:
        摘要文本
    """
    parts: list[str] = []

    parts.append(_summarize_metrics(key_metrics))
    parts.append(_summarize_findings(findings))

    if risk_level:
        parts.append(f"整体风险等级: {_describe_risk(risk_level)}")

    return "\n\n".join(parts)


def _summarize_metrics(metrics: dict[str, float]) -> str:
    """摘要关键指标"""
    if not metrics:
        return ""

    parts: list[str] = ["关键指标:"]
    for name, value in metrics.items():
        parts.append(f"- {name}: {value:.2f}")

    return "\n".join(parts)


def _summarize_findings(findings: list[str]) -> str:
    """摘要分析发现"""
    if not findings:
        return ""

    parts: list[str] = [f"共发现 {len(findings)} 项关键发现:"]
    for i, finding in enumerate(findings[:5], 1):
        parts.append(f"{i}. {finding}")

    if len(findings) > 5:
        parts.append(f"... 及其他 {len(findings) - 5} 项发现")

    return "\n".join(parts)


def _describe_risk(risk_level: str) -> str:
    """描述风险等级"""
    risk_map: dict[str, str] = {
        "red": "高（需立即处理）",
        "yellow": "中（建议关注）",
        "blue": "低（正常范围）",
    }
    return risk_map.get(risk_level, risk_level)
