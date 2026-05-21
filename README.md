# autonomous-data-analyst

自主数据分析代理，用户只需用自然语言描述分析目标，AI即可自动完成数据获取、清洗、探索、建模、可视化、结论输出与自我审查的全流程分析。

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

#### 命令行方式

```bash
# 基础分析 - 分析指定数据文件
python main.py "分析2024年Q1销售数据" --data ./data/sales.csv --output ./output

# 指定数据源和输出格式
python main.py "分析用户留存率" --data ./data/users.parquet --output ./output --mode batch

# 技能回放模式 - 使用已保存的分析流程
python main.py --mode replay --skill-id sales_analysis --data ./data/new_sales.csv

# 交互式模式 - 逐步确认分析过程
python main.py --mode interactive

# 深度分析模式
python main.py "评估当前信贷产品风险状况" --data ./data/loans.csv --output ./output --depth deep --log-level DEBUG
```

#### Python API

```python
from main import main

# 运行分析
result = main([
    "分析2024年Q1销售数据",
    "--data", "./data/sales.csv",
    "--output", "./output",
    "--depth", "standard"
])

# 检查结果
if result == 0:
    print("分析完成，报告已生成")
else:
    print(f"分析失败，错误码: {result}")
```

---

## 部署指南

### 本地开发环境

```bash
# 克隆项目
git clone <repository-url>
cd autonomous-data-analyst

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows PowerShell

# 安装依赖（开发模式）
pip install -e .

# 运行测试
python -m pytest tests/

# 启动应用
python main.py "分析示例数据" --data ./examples/data/sample.csv --output ./output
```

### Docker 部署

**Dockerfile**：
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p /app/data /app/output /app/skills_data

# 设置环境变量
ENV PYTHONPATH=/app

# 默认命令
CMD ["python", "main.py", "--mode", "batch"]
```

**构建与运行**：
```bash
# 构建镜像
docker build -t autonomous-data-analyst .

# 运行容器（批量模式）
docker run -v ./data:/app/data -v ./output:/app/output autonomous-data-analyst

# 运行容器（交互式模式）
docker run -it -v ./data:/app/data -v ./output:/app/output autonomous-data-analyst python main.py --mode interactive

# 指定分析目标
docker run -v ./data:/app/data -v ./output:/app/output autonomous-data-analyst \
    python main.py "分析销售数据" --data /app/data/sales.csv --output /app/output
```

### 配置说明

**config.yaml** 配置项说明：

```yaml
# 技能基础配置
name: autonomous-data-analyst
version: 1.0.0
description: 自主数据分析代理 - 端到端自动完成数据分析全流程

# 能力列表
capabilities:
  - autonomous-planning               # 自主规划
  - data-acquisition                  # 数据获取
  - multi-agent-collaboration         # 多Agent协作
  - goal-oriented-analysis            # 目标驱动分析
  - self-review-validation            # 自审验证
  - skill-persistence                 # 技能持久化

# Python依赖
dependencies:
  - pandas>=2.0
  - numpy>=1.24
  - yfinance>=0.2
  - requests>=2.31
  - sqlalchemy>=2.0
  - scikit-learn>=1.2
  - statsmodels>=0.14
  - matplotlib>=3.7
  - seaborn>=0.12
  - scipy>=1.10
  - plotly>=5.15
  - openpyxl>=3.1
  - pyarrow>=14.0

# 分析配置
analysis:
  default_depth: standard            # 默认分析深度: quick, standard, deep
  max_iterations: 3                  # 自审最大迭代次数
  confidence_threshold: 0.95         # 置信度阈值

# 输出配置
output:
  formats:                           # 支持的输出格式
    - markdown
    - html
    - pdf
  default_dir: ./output              # 默认输出目录

# 日志配置
logging:
  level: INFO                        # 日志级别
  format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```

---

## 命令行参数说明

```bash
python main.py [goal] [options]

位置参数:
  goal                    自然语言分析目标（可选，replay模式不需要）

可选参数:
  --help                  显示帮助信息
  --data DATA             数据源路径（文件路径或数据库连接字符串）
  --mode MODE             运行模式: interactive, batch, replay (默认: batch)
  --skill-id SKILL_ID     技能回放模式下的技能标识
  --output OUTPUT         输出目录（默认: ./output）
  --skill-dir SKILL_DIR   技能存储目录（默认: ./skills_data）
  --no-skill-persist      禁用技能持久化
  --log-level LOG_LEVEL   日志级别: DEBUG, INFO, WARNING, ERROR (默认: INFO)
```

**参数详细说明**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `goal` | str | - | 自然语言分析目标（batch/interactive模式必填） |
| `--data` | str | - | 数据源路径，支持CSV、Excel、Parquet、JSON、SQL连接 |
| `--mode` | str | batch | 运行模式：interactive（交互式）、batch（批量）、replay（技能回放） |
| `--skill-id` | str | - | replay模式下指定要回放的技能ID |
| `--output` | str | ./output | 报告和图表输出目录 |
| `--skill-dir` | str | ./skills_data | 已保存技能的存储目录 |
| `--no-skill-persist` | flag | False | 是否禁用技能持久化 |
| `--log-level` | str | INFO | 日志级别 |

---

## 示例调用方式

### 案例1：电商销售分析

```bash
python main.py "分析2024年Q1各品类销售表现，找出下降品类及原因，提出Q2改进策略" \
  --data ./data/sales_q1.csv \
  --data ./data/products.csv \
  --output ./output \
  --depth standard
```

### 案例2：金融风控分析

```bash
python main.py "评估当前信贷产品风险状况，识别高风险客群特征" \
  --data "postgresql://analyst:password@db:5432/loans" \
  --output ./output \
  --depth deep \
  --log-level DEBUG
```

### 案例3：用户增长分析

```bash
python main.py "分析2024年用户增长趋势，识别关键转化漏斗瓶颈" \
  --data ./data/user_events.parquet \
  --output ./output \
  --depth standard
```

### 案例4：技能回放

```bash
# 首次运行分析（会自动保存技能）
python main.py "分析月度销售趋势" --data ./data/sales.csv --output ./output

# 后续使用相同配置分析新数据（不需要重新定义目标）
python main.py --mode replay --skill-id monthly_sales_trend --data ./data/new_sales.csv
```

### 案例5：交互式分析

```bash
python main.py --mode interactive

# 交互式模式下会逐步确认：
# 1. 确认分析目标
# 2. 选择数据源
# 3. 确认分析计划
# 4. 审查分析结果
```

---

## 支持的数据源

| 类型 | 格式 | 示例 |
|------|------|------|
| CSV | `.csv` | `--data ./data/sales.csv` |
| Excel | `.xlsx`, `.xls` | `--data ./data/report.xlsx` |
| Parquet | `.parquet` | `--data ./data/events.parquet` |
| JSON | `.json` | `--data ./data/config.json` |
| SQL | 连接字符串 | `--data "postgresql://user:pass@host:5432/db"` |
| API | URL | `--data "https://api.example.com/data"` |

---

## 分析深度选项

| 深度 | 说明 | 预计时间 |
|------|------|----------|
| `quick` | 描述统计 + 基础可视化 | ~15分钟 |
| `standard` | 完整EDA + 适度建模 | ~45分钟 |
| `deep` | 深度建模 + 多方法对比 | ~2小时 |

---

## 输出结构

分析完成后，输出目录结构如下：

```
output/
├── report_xxx.md              # 主分析报告（Markdown）
├── report_xxx.html            # HTML版报告（可选）
├── report_xxx.pdf             # PDF版报告（可选）
├── charts/                    # 图表目录
│   ├── 01_sales_trend.png
│   ├── 02_category_comparison.png
│   └── ...
├── data/
│   ├── raw_metadata.json      # 原始数据元信息
│   ├── cleaned_metadata.json  # 清洗后数据元信息
│   └── features.parquet       # 特征数据集
├── models/
│   ├── model_card.json        # 模型卡片
│   └── model_artifacts.pkl    # 模型文件
├── logs/
│   ├── pipeline.log           # 全流程日志
│   ├── cleaning_report.json   # 清洗报告
│   └── review_report.json     # 审查报告
└── summary.json               # 执行摘要（机器可读）
```

---

## 核心能力

| 能力维度 | 说明 |
|----------|------|
| **目标理解** | 将模糊业务问题转化为可执行的分析任务 |
| **数据获取** | 支持CSV、Excel、Parquet、JSON、SQL、API等多种数据源 |
| **数据清洗** | 自动识别数据质量问题并选择合适处理策略 |
| **探索分析** | 快速建立数据认知，发现初步模式 |
| **深入分析** | 根据目标与方法选择规则匹配最佳分析方法 |
| **可视化** | 按规范自动生成出版级图表 |
| **结论输出** | 输出结构化报告，直接支撑决策 |
| **自我审查** | 确保分析结果可靠、可追溯 |
| **知识沉淀** | 分析方法与经验可累积复用 |

---

## 适用场景

- **销售与营收分析**：销售额趋势、产品/渠道表现、季节性波动
- **市场趋势与竞品分析**：行业增长趋势、市场份额变化
- **用户行为与增长分析**：用户画像、漏斗转化、留存分析
- **财务与风控分析**：利润/成本结构、异常交易检测、风险预警
- **运营与供应链分析**：库存周转、物流效率、产能利用率
- **产品与研发分析**：功能使用率、性能指标、Bug趋势
- **营销与投放分析**：渠道ROI、广告效果归因
- **人力资源分析**：人才流失预测、招聘效率、绩效分布

---

## 目录结构

```
autonomous-data-analyst/
├── config.yaml                           # 技能配置文件
├── main.py                              # 主入口函数
├── README.md                            # 使用说明（本文件）
├── PROJECT_STRUCTURE.md                 # 项目结构说明
├── modules/                             # Python模块目录
│   ├── __init__.py                      # 模块包初始化
│   ├── analysis_planner.py              # 分析规划器
│   ├── assumption_tracker.py            # 假设追踪器
│   ├── data_pipeline.py                 # 数据管道
│   ├── data_source_detector.py          # 数据源检测器
│   ├── dependency_installer.py          # 依赖安装器
│   ├── goal_parser.py                   # 目标解析器
│   ├── method_selector.py               # 方法选择器
│   ├── multi_agent_collaboration.py     # 多智能体协作
│   ├── report_generator.py              # 报告生成器
│   ├── self_review.py                   # 自审模块
│   ├── skill_persistence.py             # 技能持久化
│   └── visualization.py                 # 可视化模块
├── examples/                            # 示例文件
│   ├── ecommerce-analysis.md            # 电商分析示例
│   ├── finance-analysis.md              # 金融分析示例
│   └── user-growth-analysis.md         # 用户增长分析示例
└── .trae/                               # 配置与规格目录
    ├── prompts/                         # AI Agent提示词目录
    │   ├── README.md                    # 文件命名规范
    │   ├── CHANGELOG.md                 # 版本变更日志
    │   └── autonomous-data-analyst/
    │       └── agent-system-prompt.md   # 系统提示词
    └── specs/                           # 设计规范目录
        └── autonomous-data-analyst/
            ├── skill-design-specification.md  # 设计规范文档
            ├── spec.md                  # 规格说明
            ├── checklist.md             # 检查清单
            └── tasks.md                 # 任务分解
```

---

## 版本历史

查看 [CHANGELOG.md](.trae/prompts/CHANGELOG.md) 获取完整版本变更记录。

---

## 许可证

MIT License - 详见 LICENSE 文件