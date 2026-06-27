"""报告生成模块测试"""

from __future__ import annotations

import pytest

from modules.report_generator import (
    AnalysisReport,
    MarkdownFormatter,
    ReportFormat,
    ReportGenerator,
    ReportSection,
)


@pytest.fixture
def report_gen():
    return ReportGenerator()


class TestReportGenerator:
    """报告生成器测试"""

    def test_generate_returns_report(self, report_gen):
        """生成报告"""
        sections_data = {
            "executive_summary": {"content": "测试摘要", "title": "摘要"},
            "analysis_background": {"content": "测试背景", "title": "背景"},
        }
        report = report_gen.generate(
            report_id="test_rpt",
            title="测试报告",
            sections_data=sections_data,
        )
        assert isinstance(report, AnalysisReport)
        assert report.report_id == "test_rpt"

    def test_generate_with_metadata(self, report_gen):
        """带元数据生成"""
        report = report_gen.generate(
            report_id="test",
            title="报告",
            sections_data={},
            metadata={"key": "value"},
        )
        assert report.metadata["key"] == "value"


class TestMarkdownFormatter:
    """Markdown 格式化器测试"""

    def test_format_basic(self):
        """基本格式化"""
        report = AnalysisReport(
            report_id="test",
            title="测试报告",
            generated_at="2024-01-01",
            sections=[
                ReportSection(section_id="s1", title="章节一", content="内容一"),
            ],
        )
        md = MarkdownFormatter.format(report)
        assert "测试报告" in md
        assert "章节一" in md
        assert "内容一" in md

    def test_format_empty_report(self):
        """空报告格式化"""
        report = AnalysisReport(
            report_id="empty",
            title="空报告",
            generated_at="2024-01-01",
        )
        md = MarkdownFormatter.format(report)
        assert "空报告" in md


class TestReportSection:
    """报告章节测试"""

    def test_creation(self):
        """创建章节"""
        section = ReportSection(section_id="s1", title="标题", content="内容")
        assert section.section_id == "s1"
        assert section.title == "标题"
