# Autonomous Data Analyst Skill 规格文档

## Why
当前数据分析任务需要用户逐步指导AI完成每个步骤，效率低下且无法复用。需要将"这一类分析如何被AI自动完成"抽象为一套标准化、模块化、可长期演进的Skill系统，实现"用户只定义目标，AI自主完成全流程分析"。

## What Changes
- 新增 autonomous-data-analyst Skill，包含完整的自主规划、数据获取、分析、可视化、审查、报告输出能力
- 新增多Agent协作架构，支持SubAgent并发、Independent Multi-Agent、Plan→Execute模式
- 新增自我审查与校准机制，包含数据一致性、样本量风险、模型有效性、业务合理性审查
- 新增Skill沉淀与复用机制，支持参数化、多数据源、多时间范围、多指标体系

## Impact
- Affected specs: autonomous-data-analyst
- Affected code: 
  - `skills/autonomous-data-analyst/` - Skill主目录
  - `skills/autonomous-data-analyst/prompt.md` - Skill核心提示词
  - `skills/autonomous-data-analyst/config.yaml` - 配置文件
  - `skills/autonomous-data-analyst/README.md` - 使用说明
  - `skills/autonomous-data-analyst/examples/` - 示例目录

## ADDED Requirements

### Requirement: 自主规划能力
The system shall provide autonomous planning capabilities that:
- Parse natural language analysis goals into structured task graphs
- Auto-decompose analysis paths based on objectives
- Dynamically adjust execution steps based on intermediate results
- Implement perception → judgment → action cycle

#### Scenario: 用户输入模糊分析目标
- **WHEN** user provides "分析哪些商品应该涨价以提高利润"
- **THEN** system shall automatically determine required data sources, analysis methods, profit models, and generate analysis route

### Requirement: 自动数据获取与处理
The system shall provide autonomous data pipeline that:
- Auto-detect data source types (financial, e-commerce, CRM, ERP, logs, public stats)
- Auto-acquire data from APIs, databases, web pages, files, public sources
- Auto-process data: missing values, deduplication, normalization, anomaly detection, field mapping, time alignment, data merging
- Auto-identify and install required dependencies (pandas, yfinance, requests, sqlalchemy, sklearn, statsmodels, matplotlib, seaborn)

#### Scenario: 用户提供数据源但未提供数据
- **WHEN** user specifies data source without actual data
- **THEN** system shall attempt to fetch data from specified source automatically

### Requirement: 多Agent协作
The system shall provide multi-agent collaboration with three modes:
- SubAgent concurrent mode: for large data, batch analysis, independent subtasks
- Independent Multi-Agent mode: different agents complete different analysis dimensions, unified aggregation
- Plan → Execute mode: Planner for planning, Executor for execution, Reviewer for validation

#### Scenario: 大数据量并行分析
- **WHEN** data volume > 100 AND subtasks have no dependencies AND can be split by dimension
- **THEN** system shall automatically trigger parallel execution

### Requirement: 目标驱动分析
The system shall provide goal-oriented analysis with:
- Goal Parser: convert natural language to analysis task graph, metric system, data requirements, analysis paths
- Method Selector: auto-select regression, clustering, classification, time series, causal analysis, A/B test, statistical tests
- All assumptions must be explicitly recorded with confidence level and written into final report

#### Scenario: 用户仅描述业务目标
- **WHEN** user describes only business objective without specifying methods
- **THEN** system shall autonomously decide methods, models, charts, metrics, and assumptions

### Requirement: 自我审查与校准
The system shall provide self-review and validation covering:
- Data consistency: field definitions, time definitions, aggregation logic, JOIN correctness
- Sample size risk: small sample risk, bias risk, data skew
- Model effectiveness: goodness of fit, error rate, stability, overfitting risk
- Business rationality: actionability, business common sense, over-inference

Risk levels: Red (critical), Yellow (attention), Blue (notice)

#### Scenario: 分析完成后的自动审查
- **WHEN** analysis results are generated
- **THEN** system shall execute comprehensive review and output risk assessment

### Requirement: Skill沉淀与复用
The system shall provide skill persistence that:
- Auto-extract successful analysis flows
- Auto-encapsulate into reusable Skills
- Support one-click replay

Skill must include: input specs, data processing rules, analysis logic, chart templates, output templates, review rules, exception handling rules

#### Scenario: 成功分析后的Skill封装
- **WHEN** analysis completes successfully
- **THEN** system shall offer to extract flow and encapsulate as reusable Skill

## MODIFIED Requirements
None

## REMOVED Requirements
None
