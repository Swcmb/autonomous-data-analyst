"""共享测试 fixtures"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

# 确保项目根目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def sample_df():
    """20 行测试 DataFrame"""
    return pd.read_csv(Path(__file__).resolve().parent.parent / "examples" / "sample.csv")


@pytest.fixture
def small_df():
    """5 行小型 DataFrame，用于快速测试"""
    return pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=5),
        "product": ["A", "B", "A", "B", "A"],
        "revenue": [100, 200, 150, 250, 120],
        "quantity": [10, 20, 15, 25, 12],
        "category": ["x", "y", "x", "y", "x"],
    })


@pytest.fixture
def numeric_df():
    """纯数值 DataFrame，用于回归/聚类测试"""
    import numpy as np
    rng = np.random.RandomState(42)
    return pd.DataFrame({
        "feature1": rng.randn(50),
        "feature2": rng.randn(50),
        "target": rng.randn(50),
    })


@pytest.fixture
def tmp_skill_dir(tmp_path):
    """临时技能存储目录"""
    return str(tmp_path / "skills")
