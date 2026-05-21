# autonomous-data-analyst

端到端自主数据分析代理，用户只需用自然语言描述分析目标，AI即可自动完成数据获取、清洗、探索、建模、可视化、结论输出与自我审查的全流程分析。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 基础使用 - 分析销售数据
python main.py "分析2024年Q1销售数据" --data ./data/sales.csv --output ./output

# 交互式模式
python main.py --mode interactive

# 技能回放模式
python main.py --mode replay --skill-id sales_analysis --data ./data/new_sales.csv
```

## 功能特性

- **目标驱动分析**: 将自然语言业务问题转化为可执行的分析任务
- **多数据源支持**: CSV、Excel、Parquet、JSON、SQL、REST API
- **自动数据清洗**: 缺失值处理、异常检测、类型转换、去重
- **智能方法选择**: 根据分析目标自动匹配最佳分析方法
- **多智能体协作**: Planner、Data、Cleaner、Analyst、Visualizer 等角色分工协作
- **自我审查验证**: 确保分析结果可靠、可追溯
- **技能持久化**: 分析流程可保存复用

## 核心模块

| 模块 | 职责 |
|------|------|
| `goal_parser` | 目标解析，将自然语言转化为结构化任务 |
| `data_pipeline` | 数据获取、清洗、预处理 |
| `analysis_planner` | 分析规划与任务编排 |
| `method_selector` | 根据目标选择分析方法 |
| `multi_agent_collaboration` | 多智能体协作执行 |
| `visualization` | 图表生成与可视化 |
| `report_generator` | 报告生成 |
| `self_review` | 分析结果自我审查 |
| `skill_persistence` | 技能存储与回放 |

## 使用方法

### 命令行

```bash
python main.py [goal] [options]

# 位置参数
goal                    自然语言分析目标（replay模式不需要）

# 可选参数
--data DATA             数据源路径
--mode MODE             运行模式: interactive, batch, replay (默认: batch)
--skill-id SKILL_ID     技能回放模式下的技能标识
--output OUTPUT         输出目录（默认: ./output）
--skill-dir SKILL_DIR   技能存储目录（默认: ./skills_data）
--no-skill-persist      禁用技能持久化
--log-level LOG_LEVEL   日志级别: DEBUG, INFO, WARNING, ERROR
```

### Python API

```python
from main import main

result = main([
    "分析2024年Q1销售数据",
    "--data", "./data/sales.csv",
    "--output", "./output"
])

if result == 0:
    print("分析完成")
```

### 运行模式

| 模式 | 说明 |
|------|------|
| `batch` | 批量模式，一次性完成所有分析步骤 |
| `interactive` | 交互式模式，逐步确认分析过程 |
| `replay` | 技能回放模式，复用已保存的分析流程 |

## 配置说明

```yaml
name: autonomous-data-analyst
version: 1.0.0
description: 自主数据分析代理
capabilities:
  - autonomous-planning
  - data-acquisition
  - multi-agent-collaboration
  - goal-oriented-analysis
  - self-review-validation
  - skill-persistence
```

## 支持的数据源

| 类型 | 格式 | 示例 |
|------|------|------|
| CSV | `.csv` | `--data ./data/sales.csv` |
| Excel | `.xlsx`, `.xls` | `--data ./data/report.xlsx` |
| Parquet | `.parquet` | `--data ./data/events.parquet` |
| JSON | `.json` | `--data ./data/config.json` |
| SQL | 连接字符串 | `--data "postgresql://user:pass@host:5432/db"` |
| API | URL | `--data "https://api.example.com/data"` |

## 输出结构

```
output/
├── report_xxx.md          # 主分析报告
├── charts/                # 图表目录
├── data/                  # 数据文件
├── models/                # 模型文件（如适用）
├── logs/                  # 日志文件
└── summary.json           # 执行摘要
```

## 目录结构

```
autonomous-data-analyst/
├── main.py                # 主入口
├── config.yaml            # 配置文件
├── requirements.txt       # 依赖清单
├── modules/               # 核心模块
│   ├── analysis_planner.py
│   ├── data_pipeline.py
│   ├── goal_parser.py
│   ├── method_selector.py
│   ├── multi_agent_collaboration.py
│   ├── report_generator.py
│   ├── self_review.py
│   ├── skill_persistence.py
│   └── visualization.py
├── examples/              # 示例文件
└── .trae/                 # 配置与规格目录
    ├── prompts/           # AI提示词
    └── specs/             # 设计规范
```

## 分析流程

1. **目标解析**: 理解用户自然语言目标，生成结构化任务定义
2. **数据获取**: 匹配并接入数据源
3. **数据清洗**: 处理缺失值、异常值，数据类型转换
4. **探索分析**: 描述统计、分布分析、相关性分析
5. **深入建模**: 根据目标选择建模方法，执行分析
6. **可视化**: 生成图表和仪表盘
7. **报告生成**: 输出结构化分析报告
8. **自我审查**: 验证分析质量和结论可靠性
9. **知识沉淀**: 保存分析流程为可复用技能

## 示例

```bash
# 电商销售分析
python main.py "分析2024年Q1各品类销售表现，找出下降品类及原因" \
  --data ./data/sales_q1.csv \
  --output ./output

# 金融风控分析
python main.py "评估当前信贷产品风险状况，识别高风险客群特征" \
  --data "postgresql://analyst:password@db:5432/loans" \
  --output ./output
```

## 分析方法选择

| 分析目标 | 推荐方法 |
|----------|----------|
| 趋势分析 | 时间序列分解、移动平均 |
| 归因分析 | 贡献度拆解、回归分析 |
| 用户分群 | K-Means、DBSCAN |
| 预测 | ARIMA、Prophet |
| 相关性 | Pearson、Spearman相关分析 |

## 许可证

MIT License