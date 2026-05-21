# Autonomous Data Analyst - 项目结构说明

## 概述

本项目是一个自主数据分析代理系统，实现"用户只定义目标，AI自主完成全流程分析"的核心目标。项目采用模块化设计，代码与配置分离，便于维护和扩展。

---

## 目录结构

```
autonomous-data-analyst/                    # 项目根目录
├── main.py                                 # 主入口函数
├── config.yaml                             # 全局配置文件
├── README.md                               # 项目说明文档
├── PROJECT_STRUCTURE.md                    # 本文件 - 项目结构说明
├── modules/                                # Python核心模块
│   ├── __init__.py                         # 模块包初始化
│   ├── analysis_planner.py                 # 分析规划器 - 规划分析路径
│   ├── assumption_tracker.py               # 假设追踪器 - 管理分析假设
│   ├── data_pipeline.py                    # 数据管道 - 数据加载与清洗
│   ├── data_source_detector.py             # 数据源检测器 - 自动识别数据源
│   ├── dependency_installer.py             # 依赖安装器 - 自动安装依赖
│   ├── goal_parser.py                      # 目标解析器 - 解析自然语言目标
│   ├── method_selector.py                  # 方法选择器 - 选择分析方法
│   ├── multi_agent_collaboration.py        # 多智能体协作 - 协调多Agent
│   ├── report_generator.py                 # 报告生成器 - 生成分析报告
│   ├── self_review.py                      # 自审模块 - 验证分析结果
│   ├── skill_persistence.py                # 技能持久化 - 沉淀可复用技能
│   └── visualization.py                    # 可视化模块 - 生成图表
├── examples/                               # 示例文件
│   ├── ecommerce-analysis.md               # 电商分析示例
│   ├── finance-analysis.md                 # 金融分析示例
│   └── user-growth-analysis.md            # 用户增长分析示例
└── .trae/                                  # 配置与规格目录（Trae系统专用）
    ├── prompts/                            # AI Agent提示词目录
    │   ├── README.md                       # 文件命名规范文档
    │   ├── CHANGELOG.md                    # 版本变更日志
    │   └── autonomous-data-analyst/
    │       └── agent-system-prompt.md      # AI Agent系统提示词
    └── specs/                              # 设计规范目录
        └── autonomous-data-analyst/
            ├── skill-design-specification.md # Skill设计规范文档
            ├── spec.md                     # 规格说明文档
            ├── checklist.md                # 检查清单
            └── tasks.md                    # 任务分解文档
```

---

## 目录职责说明

### 核心代码层

| 目录/文件 | 职责 | 状态 |
|-----------|------|------|
| `main.py` | 工作流编排主入口 | 生产就绪 |
| `config.yaml` | 全局配置（名称、版本、依赖） | 生产就绪 |
| `modules/` | 业务逻辑核心模块 | 生产就绪 |

### 模块详细说明

| 模块文件 | 职责描述 | 核心功能 |
|----------|----------|----------|
| `analysis_planner.py` | 分析规划 | 感知→判断→行动循环 |
| `assumption_tracker.py` | 假设管理 | 记录假设及可信度 |
| `data_pipeline.py` | 数据处理 | 加载、清洗、转换 |
| `data_source_detector.py` | 数据源识别 | 自动检测API/数据库/文件 |
| `dependency_installer.py` | 依赖管理 | 自动安装所需库 |
| `goal_parser.py` | 目标解析 | 自然语言→结构化任务 |
| `method_selector.py` | 方法选择 | 回归/聚类/时间序列等 |
| `multi_agent_collaboration.py` | 多Agent协作 | 并行执行与结果聚合 |
| `report_generator.py` | 报告生成 | 结构化报告输出 |
| `self_review.py` | 自审验证 | 数据一致性/样本量/模型有效性检查 |
| `skill_persistence.py` | 技能沉淀 | 参数化与复用 |
| `visualization.py` | 可视化 | 图表生成 |

### 配置与规格层

| 目录 | 职责 | 描述 |
|------|------|------|
| `.trae/prompts/` | AI提示词存储 | 存放AI Agent使用的系统提示词 |
| `.trae/specs/` | 设计规范存储 | 存放供人类设计师使用的规格文档 |

---

## 文件命名规范

### 命名原则

| 文件类型 | 命名关键词 | 示例 |
|----------|-----------|------|
| AI提示词文件 | `prompt`, `system`, `agent` | `agent-system-prompt.md` |
| 设计规范文件 | `specification`, `design`, `requirements` | `skill-design-specification.md` |
| 通用文档 | 描述性名称 | `README.md`, `CHANGELOG.md` |

### 格式要求

- 采用 **kebab-case**（小写字母 + 连字符分隔）
- 长度不超过64个字符
- 文件名应清晰表达文件用途

---

## 版本控制

### 变更记录

所有配置文件变更记录在 `.trae/prompts/CHANGELOG.md`

### 版本号格式

```
Major.Minor.Patch
```

- **Major**: 重大变更，可能破坏兼容性
- **Minor**: 新增功能，向后兼容
- **Patch**: 修复问题，向后兼容

---

## 扩展指南

### 添加新模块

1. 在 `modules/` 目录下创建新文件
2. 在 `modules/__init__.py` 中导出模块
3. 在 `main.py` 中导入并集成到工作流

### 添加新提示词

1. 在 `.trae/prompts/` 或 `.trae/specs/` 创建对应目录
2. 按照命名规范命名文件
3. 更新 `CHANGELOG.md` 记录变更

### 添加新示例

1. 在 `examples/` 目录下创建新的 markdown 文件
2. 遵循统一的示例格式

---

## 关键路径映射

| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `prompt.md` (根目录) | `.trae/prompts/autonomous-data-analyst/agent-system-prompt.md` | AI提示词文件 |
| `.trae/specs/autonomous-data-analyst/prompt.md` | `.trae/specs/autonomous-data-analyst/skill-design-specification.md` | 设计规范文件 |
| `skills/autonomous-data-analyst/` | `autonomous-data-analyst/` | 项目根目录已调整 |

---

## 联系方式

如有问题或建议，请参考 `README.md` 中的联系信息。