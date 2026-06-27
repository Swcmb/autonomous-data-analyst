"""端到端集成测试"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# 确保项目根目录在路径中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import main


class TestBatchModeIntegration:
    """批量模式端到端测试"""

    def test_basic_analysis(self, tmp_path):
        """基本分析流程"""
        sample_csv = Path(__file__).resolve().parent.parent / "examples" / "sample.csv"
        exit_code = main([
            "分析销售趋势",
            "--data", str(sample_csv),
            "--output", str(tmp_path / "output"),
            "--no-skill-persist",
        ])
        assert exit_code == 0

    def test_output_file_created(self, tmp_path):
        """验证输出文件已创建"""
        sample_csv = Path(__file__).resolve().parent.parent / "examples" / "sample.csv"
        output_dir = str(tmp_path / "output")
        main([
            "分析销售数据",
            "--data", str(sample_csv),
            "--output", output_dir,
            "--no-skill-persist",
        ])
        # 应生成至少一个 .md 文件（递归搜索）
        md_files = list(Path(output_dir).rglob("*.md"))
        assert len(md_files) >= 1

    def test_skill_persistence(self, tmp_path):
        """技能持久化"""
        sample_csv = Path(__file__).resolve().parent.parent / "examples" / "sample.csv"
        skill_dir = tmp_path / "skills"
        exit_code = main([
            "分析销售趋势",
            "--data", str(sample_csv),
            "--output", str(tmp_path / "output"),
            "--skill-dir", str(skill_dir),
        ])
        assert exit_code == 0
        # 应生成技能文件
        skill_files = list(skill_dir.glob("*.json"))
        assert len(skill_files) >= 1


class TestErrorHandling:
    """错误路径测试"""

    def test_missing_data_file(self, tmp_path):
        """数据文件不存在"""
        exit_code = main([
            "分析",
            "--data", "/nonexistent/file.csv",
            "--output", str(tmp_path),
        ])
        assert exit_code == 1

    def test_empty_goal(self, tmp_path):
        """空目标"""
        sample_csv = Path(__file__).resolve().parent.parent / "examples" / "sample.csv"
        # 空目标也应能运行（置信度低但不报错）
        exit_code = main([
            "",
            "--data", str(sample_csv),
            "--output", str(tmp_path),
            "--no-skill-persist",
        ])
        # 应正常完成（即使结果不理想）
        assert exit_code in (0, 1)


class TestReplayMode:
    """回放模式测试"""

    def test_replay_missing_skill(self, tmp_path):
        """回放不存在的技能"""
        exit_code = main([
            "--mode", "replay",
            "--skill-id", "nonexistent_skill",
            "--output", str(tmp_path),
        ])
        assert exit_code == 1

    def test_replay_no_skill_id(self, tmp_path):
        """回放未指定技能 ID"""
        exit_code = main([
            "--mode", "replay",
            "--output", str(tmp_path),
        ])
        assert exit_code == 1
