"""技能持久化模块测试"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from modules.skill_persistence import (
    AnalysisSkill,
    SkillExtractor,
    SkillMetadata,
    SkillParameterizer,
    SkillReplayer,
    SkillStore,
    SkillVersionManager,
    SkillVersionStrategy,
)


@pytest.fixture
def sample_skill():
    """创建示例技能"""
    metadata = SkillMetadata(
        skill_id="test_skill_001",
        name="测试分析技能",
        version="1.0.0",
        description="用于测试的技能",
        tags=["test"],
    )
    return AnalysisSkill(metadata=metadata)


class TestSkillExtractor:
    """技能提取器测试"""

    def test_extract_returns_skill(self):
        """提取返回 AnalysisSkill"""
        extractor = SkillExtractor()
        skill = extractor.extract_from_execution(
            goal_spec={"category": "exploratory", "domain": "ecommerce"},
            pipeline_config={},
            analysis_plan={"steps": []},
            results={"charts": [], "sections": []},
            review_report={"checks": []},
        )
        assert isinstance(skill, AnalysisSkill)
        assert skill.metadata.skill_id


class TestSkillParameterizer:
    """技能参数化器测试"""

    def test_parameterize_returns_skill(self, sample_skill):
        """参数化返回技能"""
        result = SkillParameterizer.parameterize(sample_skill)
        assert isinstance(result, AnalysisSkill)


class TestSkillStore:
    """技能存储测试"""

    def test_save_and_load(self, tmp_skill_dir, sample_skill):
        """保存和加载技能"""
        store = SkillStore(storage_dir=tmp_skill_dir)
        store.save_skill(sample_skill)

        # 加载技能
        skills = store.list_skills()
        assert len(skills) == 1

        loaded = store.load_skill(skills[0].file_path)
        # metadata 可能是 dict 或 SkillMetadata
        skill_id = loaded.metadata.get("skill_id") if isinstance(loaded.metadata, dict) else loaded.metadata.skill_id
        assert skill_id == sample_skill.metadata.skill_id

    def test_find_skills_by_tag(self, tmp_skill_dir, sample_skill):
        """按标签查找技能"""
        store = SkillStore(storage_dir=tmp_skill_dir)
        store.save_skill(sample_skill)

        found = store.find_skills(tags=["test"])
        assert len(found) == 1

    def test_delete_skill(self, tmp_skill_dir, sample_skill):
        """删除技能"""
        store = SkillStore(storage_dir=tmp_skill_dir)
        store.save_skill(sample_skill)
        assert len(store.list_skills()) == 1

        store.delete_skill(sample_skill.metadata.skill_id)
        assert len(store.list_skills()) == 0

    def test_list_empty(self, tmp_skill_dir):
        """空目录列表"""
        store = SkillStore(storage_dir=tmp_skill_dir)
        assert store.list_skills() == []


class TestSkillVersionManager:
    """技能版本管理器测试"""

    def test_create_version(self, tmp_skill_dir, sample_skill):
        """创建版本"""
        mgr = SkillVersionManager()
        version = mgr.create_version(
            skill=sample_skill,
            strategy=SkillVersionStrategy.SEMANTIC,
            change_description="初始版本",
        )
        assert isinstance(version, str)

    def test_get_versions(self, tmp_skill_dir, sample_skill):
        """获取版本列表"""
        mgr = SkillVersionManager()
        mgr.create_version(
            skill=sample_skill,
            strategy=SkillVersionStrategy.SEMANTIC,
            change_description="v1",
        )
        versions = mgr.get_versions(sample_skill.metadata.skill_id)
        assert len(versions) >= 1


class TestSkillReplayer:
    """技能回放器测试"""

    def test_register_and_replay(self, sample_skill):
        """注册和回放"""
        replayer = SkillReplayer()
        replayer.register_skill(sample_skill)
        result = replayer.replay(
            skill_id=sample_skill.metadata.skill_id,
            data=None,
        )
        assert isinstance(result, dict)
