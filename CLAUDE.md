# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

自主数据分析代理（autonomous-data-analyst）—— 用户用自然语言描述分析目标，AI 自动完成数据获取、清洗、分析、可视化、报告生成和自审的全流程。纯 Python 框架，无 Web 服务。

## Commands

```bash
# 安装依赖
pip install -r requirements.txt

# 批量模式（默认）
python main.py "分析目标描述" --data ./data/file.csv --output ./output

# 交互模式
python main.py --mode interactive

# 回放模式（重放已保存的技能包）
python main.py --mode replay --skill-id <skill_id> --data ./data/new_data.csv

# 运行测试
pytest tests/ -v
```

CLI 参数：`goal`（位置参数）、`--data`、`--mode`（interactive/batch/replay）、`--skill-id`、`--output`（默认 `./output`）、`--skill-dir`（默认 `./skills_data`）、`--no-skill-persist`、`--log-level`（DEBUG/INFO/WARNING/ERROR）

项目配置：`pyproject.toml`（pytest 配置、依赖声明）

## Architecture

### 9 阶段分析流水线

`main.py` 是唯一入口，通过状态机（`WorkflowState` 枚举，12 个状态）驱动以下流水线：

1. **目标解析** (`goal_parser.py`) — 基于中文关键词匹配，提取分析类别、领域、指标、时间约束，生成 `AnalysisGoalSpec` 和任务图
2. **数据获取** (`data_source_detector.py`) — 检测数据源类型（文件/URL/数据库连接串），自动加载
3. **数据清洗** (`data_pipeline.py`) — 链式调用的可组合 Pipeline，支持缺失值处理、去重、归一化、异常检测、字段映射、时间对齐
4. **分析规划** (`analysis_planner.py`) — 感知-判断-行动循环，结合 `method_selector.py` 从 18 种分析方法中自动选择
5. **多智能体执行** (`multi_agent_collaboration.py`) — `ThreadPoolExecutor` 并行，三种协作模式（SubAgent 并发 / 维度拆分并行 / 计划-执行-评审迭代）
6. **结果聚合** — 冲突检测 + 一致性评分
7. **自审** (`self_review.py`) — 四维审查（数据一致性、样本风险、模型有效性、业务合理性），风险分级 RED/YELLOW/BLUE
8. **报告生成** (`report_generator.py`) — Builder 模式，输出 Markdown/YAML，7 个标准章节
9. **技能持久化** (`skill_persistence.py`) — 提取可复用分析模式，参数化后存储为 JSON 技能包，支持版本管理和一键回放

### 关键设计模式

- **Builder**: `ReportBuilder`、`DataPipeline`（链式调用 `.handle_missing().normalize().detect_anomalies()`）
- **Registry**: `METHOD_REGISTRY`（18 种方法 × 6 族）、`METHOD_DEPENDENCY_MAP`
- **State Machine**: `main.py` 中的 `WorkflowState` + `WorkflowContext`
- **Strategy**: `CollaborationMode` 枚举分派不同协作策略

### 模块依赖关系

`main.py` 依赖所有模块。模块间：`analysis_planner` → `method_selector`；`multi_agent_collaboration` → `analysis_planner`；`skill_persistence` 从执行结果中提取。所有模块通过 `modules/__init__.py` 导出到扁平命名空间。

## Code Conventions

- Python 3.10+，使用 `from __future__ import annotations`
- 注释、docstring、用户面向文本为**中文**；代码标识符为英文
- 类型注解使用内置泛型（`list[str]`、`dict[str, Any]`），不用 `typing.List`
- `modules/__init__.py` 通过 `__all__` 统一导出所有公共符号
- 新增分析方法需同时注册到 `method_selector.py` 的 `METHOD_REGISTRY` 和 `dependency_installer.py` 的 `METHOD_DEPENDENCY_MAP`
- 技能包存储在 `--skill-dir` 指定目录（默认 `./skills_data`），格式为 JSON

## Key Entry Points for Modifications

| 修改目标 | 文件 |
|:---|:---|
| 添加新分析方法 | `modules/method_selector.py` |
| 添加新数据源类型 | `modules/data_source_detector.py` + `modules/dependency_installer.py` |
| 修改清洗逻辑 | `modules/data_pipeline.py` |
| 修改报告模板 | `modules/report_generator.py` |
| 修改协作模式 | `modules/multi_agent_collaboration.py` |
| 修改自审规则 | `modules/self_review.py` |
| 修改可视化规则 | `modules/visualization.py` |
| 修改流水线编排 | `main.py` |
