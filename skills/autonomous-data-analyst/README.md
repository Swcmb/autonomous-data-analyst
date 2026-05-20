# autonomous-data-analyst

自主数据分析代理，用户只定义目标，AI自主完成全流程分析。

---

## 一句话描述

**autonomous-data-analyst** 是一个端到端的自主数据分析技能，用户只需用自然语言描述分析目标，技能即可自动完成数据获取、清洗、探索、建模、可视化、结论输出与自我审查的全流程，生成可直接用于业务决策的分析报告。

---

## 适用场景

- **销售与营收分析**：销售额趋势、产品/渠道表现、季节性波动、客户贡献度、价格弹性分析
- **市场趋势与竞品分析**：行业增长趋势、市场份额变化、竞品对标、新兴机会识别
- **用户行为与增长分析**：用户画像、漏斗转化、留存/流失分析、A/B测试评估、生命周期价值（LTV）
- **财务与风控分析**：利润/成本结构、现金流预测、异常交易检测、信用评分、风险预警
- **运营与供应链分析**：库存周转、物流效率、产能利用率、供应商绩效评估
- **产品与研发分析**：功能使用率、性能指标、Bug趋势、发布影响评估、NPS分析
- **营销与投放分析**：渠道ROI、广告效果归因、Campaign评估、品牌声量监测
- **人力资源分析**：人才流失预测、招聘效率、绩效分布、员工满意度分析
- **任何需要数据驱动决策的场景**：当业务方提出"帮我看看数据怎么说"时，直接使用本技能

---

## 核心能力矩阵

| 能力维度 | 子能力 | 说明 |
|----------|--------|------|
| **目标理解** | 意图解析、范围界定、产出定义 | 将模糊业务问题转化为可执行的分析任务 |
| **数据获取** | 文件读取、数据库连接、API调用、网页抓取 | 支持 CSV、Excel、Parquet、JSON、SQL、REST API、HTML 等 |
| **数据清洗** | 缺失处理、异常检测、类型转换、去重、归一化 | 自动识别数据质量问题并选择合适策略 |
| **探索分析** | 描述统计、分布分析、相关性、趋势分解 | 快速建立数据认知，发现初步模式 |
| **深入分析** | 回归、分类、聚类、时间序列、假设检验 | 根据目标与方法选择规则匹配最佳方法 |
| **可视化** | 趋势图、分布图、对比图、关系图、仪表盘 | 按规范自动生成出版级图表 |
| **结论输出** | 洞察提取、建议生成、风险提示 | 输出结构化报告，直接支撑决策 |
| **自我审查** | 一致性检查、方法验证、结果复核 | 确保分析结果可靠、可追溯 |
| **知识沉淀** | 流程保存、模板复用、技能迭代 | 分析方法与经验可累积复用 |

---

## 完整工作流说明（9个阶段）

### Phase 1：目标解析（Goal Parsing）

- **输入**：用户自然语言描述的分析目标
- **处理**：
  - 提取核心业务问题、分析范围、时间窗口、预期产出
  - 识别关键实体（产品、用户、渠道、时间等）
  - 判断分析类型（描述性、诊断性、预测性、规范性）
- **输出**：结构化分析任务定义（Analysis Task Definition）
- **Agent**：Planner Agent

### Phase 2：数据发现与接入（Data Discovery & Ingestion）

- **输入**：任务定义、可用数据源配置
- **处理**：
  - 匹配数据源（本地文件、数据库、API、网页）
  - 读取数据并建立初始 Schema
  - 评估数据质量与覆盖度
  - 若数据不足，触发数据补全策略（公开数据源、代理搜索）
- **输出**：已接入数据集 + 数据质量评估报告
- **Agent**：Data Agent

### Phase 3：数据清洗与预处理（Data Cleaning & Preprocessing）

- **输入**：原始数据集
- **处理**：
  - 缺失值检测与处理（删除、填充、插值、模型预测）
  - 异常值检测（IQR、Z-score、孤立森林）与处理
  - 数据类型推断与转换
  - 重复记录处理
  - 特征工程基础操作（编码、缩放、分箱）
  - 生成清洗日志
- **输出**：清洗后数据集 + 清洗报告
- **Agent**：Cleaner Agent

### Phase 4：探索性数据分析（Exploratory Data Analysis）

- **输入**：清洗后数据集
- **处理**：
  - 描述性统计（均值、中位数、方差、分位数）
  - 单变量分布分析
  - 多变量相关性分析（Pearson、Spearman）
  - 时间序列趋势分解（趋势、季节、残差）
  - 分组对比分析
  - 生成探索性图表
- **输出**：EDA 报告 + 初步发现
- **Agent**：Analyst Agent

### Phase 5：深入分析建模（Deep Analysis & Modeling）

- **输入**：EDA 结果 + 原始任务定义
- **处理**：
  - 根据分析目标选择建模方法（见"分析方法选择规则"）
  - 数据划分与交叉验证
  - 模型训练与调参
  - 模型评估与选择
  - 特征重要性分析
  - 敏感性分析（如适用）
- **输出**：建模结果 + 模型评估报告
- **Agent**：Analyst Agent + Model Specialist Agent

### Phase 6：可视化呈现（Visualization & Reporting）

- **输入**：分析结果 + 可视化规范
- **处理**：
  - 按数据类型选择图表类型
  - 应用配色、标注、排版规范
  - 生成可交互或静态图表
  - 组合仪表盘或报告页
- **输出**：图表文件 + 可视化报告
- **Agent**：Visualization Agent

### Phase 7：结论与建议输出（Insight & Recommendation）

- **输入**：全部分析结果
- **处理**：
  - 提取关键发现（按重要性和可信度排序）
  - 关联业务场景生成 actionable 建议
  - 标注数据局限性与不确定性
  - 生成结构化报告（摘要、详情、附录）
- **输出**：分析报告（Markdown/PDF/HTML）
- **Agent**：Reporter Agent

### Phase 8：自我审查（Self-Review & Validation）

- **输入**：完整分析成果包
- **处理**：
  - 数据一致性检查（源头到结论可追溯）
  - 方法合理性检查（方法选择是否匹配目标）
  - 统计显著性验证
  - 结论逻辑性审查
  - 可视化规范性检查
  - 生成审查评分与改进建议
- **输出**：审查报告 + 评分 + 修正后报告（如需要）
- **Agent**：Reviewer Agent

### Phase 9：知识沉淀与交付（Knowledge Capture & Delivery）

- **输入**：最终报告 + 全流程日志
- **处理**：
  - 提取分析流程模板
  - 保存特征工程 pipeline
  - 记录方法选择决策树
  - 归档可复用组件
  - 更新技能知识库
- **输出**：可复用模板 + 归档包
- **Agent**：Knowledge Agent

---

## 输入规范（YAML格式）

```yaml
# 分析任务输入规范
analysis_task:
  # 必填：分析目标描述（自然语言）
  goal: "分析2024年Q1销售数据下降原因并提出改进建议"

  # 可选：业务领域（帮助方法选择）
  domain: "retail" | "finance" | "marketing" | "hr" | "operations" | "product" | "other"

  # 可选：时间范围
  time_range:
    start: "2024-01-01"
    end: "2024-03-31"

  # 可选：数据源配置
  data_sources:
    - type: "csv"
      path: "/data/sales_q1.csv"
    - type: "excel"
      path: "/data/product_catalog.xlsx"
      sheet: "Sheet1"
    - type: "sql"
      connection: "postgresql://user:pass@host:5432/db"
      query: "SELECT * FROM orders WHERE status = 'completed'"
    - type: "api"
      url: "https://api.example.com/metrics"
      method: "GET"
      headers: {}
      params: {}
    - type: "parquet"
      path: "/data/events.parquet"
    - type: "json"
      path: "/data/responses.json"

  # 可选：重点关注维度
  focus_dimensions:
    - "region"
    - "product_category"
    - "customer_segment"

  # 可选：排除维度/数据
  exclude:
    - "internal_test_accounts"
    - "outlier_transactions"

  # 可选：输出格式偏好
  output_format: "markdown" | "html" | "pdf" | "all"

  # 可选：分析深度
  depth: "quick" | "standard" | "deep"
  # quick: 描述统计 + 基础可视化，约15分钟
  # standard: 完整EDA + 适度建模，约45分钟
  # deep: 深度建模 + 多方法对比，约2小时

  # 可选：置信度阈值
  confidence_threshold: 0.95

  # 可选：并发限制
  concurrency_limit: 4

  # 可选：额外约束
  constraints:
    max_rows: 1000000
    memory_limit_mb: 4096
    require_reproducibility: true
```

---

## 输出规范

### 基础输出结构

```
analysis_output/
├── report.md                    # 主分析报告（Markdown）
├── report.html                  # HTML版报告（可选）
├── report.pdf                   # PDF版报告（可选）
├── charts/                      # 图表目录
│   ├── 01_sales_trend.png
│   ├── 02_category_comparison.png
│   ├── 03_correlation_heatmap.png
│   └── ...
├── data/
│   ├── raw_metadata.json        # 原始数据元信息
│   ├── cleaned_metadata.json    # 清洗后数据元信息
│   └── features.parquet         # 特征数据集
├── models/
│   ├── model_card.json          # 模型卡片
│   └── model_artifacts.pkl      # 模型文件（如适用）
├── logs/
│   ├── pipeline.log             # 全流程日志
│   ├── cleaning_report.json     # 清洗报告
│   ├── eda_report.json          # EDA报告
│   └── review_report.json       # 审查报告
├── templates/
│   └── reusable_pipeline.yaml   # 可复用pipeline模板
└── summary.json                 # 执行摘要（机器可读）
```

### summary.json 结构

```json
{
  "task_id": "uuid",
  "goal": "分析目标原文",
  "status": "completed",
  "duration_seconds": 1800,
  "phases_completed": ["goal_parsing", "data_ingestion", "cleaning", "eda", "modeling", "visualization", "reporting", "review", "knowledge_capture"],
  "key_findings": [
    {"finding": "描述性发现", "confidence": 0.95, "evidence": "支持数据"},
    {"finding": "诊断性发现", "confidence": 0.88, "evidence": "支持数据"}
  ],
  "recommendations": [
    {"action": "建议内容", "priority": "high", "impact_estimate": "影响预估"}
  ],
  "data_quality_score": 0.87,
  "model_performance": {"metric": "value"},
  "review_score": 0.92,
  "limitations": ["已知局限性列表"]
}
```

---

## 数据处理规则

### 缺失值处理策略

| 缺失比例 | 处理方式 |
|----------|----------|
| < 5% | 删除含缺失行（若数据量充足）或均值/中位数/众数填充 |
| 5% - 20% | KNN 填充、回归预测填充、多重插补（MICE） |
| 20% - 50% | 引入缺失指示特征 + 中位数/众数填充 |
| > 50% | 评估列重要性，非核心特征可删除；核心特征使用高级填充或业务规则填充 |

### 异常值处理策略

| 检测方法 | 适用场景 | 处理方式 |
|----------|----------|----------|
| IQR（1.5x/3x） | 数值型、中等规模 | 截断或标记 |
| Z-score（>3） | 近似正态分布 | 删除或 Winsorize |
| 孤立森林（Isolation Forest） | 高维、非线性 | 单独分析或排除 |
| 业务规则 | 已知合理范围 | 按业务逻辑修正或标记 |

### 数据类型处理

- **数值型**：保持精度，必要时标准化/归一化
- **类别型**：低频类别合并为"Other"，One-Hot 编码或 Target Encoding
- **时间型**：解析为标准 datetime 格式，提取年/月/日/周/小时/季度等衍生特征
- **文本型**：TF-IDF 向量化或 Embedding，情感分析（如适用）
- **地理型**：经纬度解析、区域聚合

### 数据量分级处理

| 数据量 | 策略 |
|--------|------|
| < 10K 行 | 全量处理，精细方法 |
| 10K - 100K 行 | 全量处理，适度抽样验证 |
| 100K - 1M 行 | 分布式处理或分块处理，抽样 EDA |
| > 1M 行 | 分层抽样 + 代表性分析，或切换分布式引擎 |

---

## 分析方法选择规则

### 按分析目标选择

| 分析目标 | 推荐方法 | 触发条件 |
|----------|----------|----------|
| "趋势是什么" | 时间序列分解（STL）、移动平均、Holt-Winters | 含时间维度 |
| "为什么下降/上升" | 归因分析、分解贡献、假设检验、回归分析 | 比较型目标 |
| "谁最重要" | 特征重要性（Random Forest、XGBoost）、Shapley 值 | 多因素场景 |
| "未来会怎样" | ARIMA、Prophet、XGBoost 时序预测、LSTM | 预测型目标 |
| "有哪些群体" | K-Means、DBSCAN、层次聚类、PCA 降维 | 分群/细分目标 |
| "是否有关联" | 相关分析、卡方检验、互信息 | 关联型目标 |
| "差异是否显著" | T检验、ANOVA、Mann-Whitney U、卡方检验 | 比较/验证型目标 |
| "如何优化" | A/B 测试分析、敏感性分析、优化模型 | 决策优化型目标 |
| "风险在哪里" | 异常检测、规则引擎、风险评分卡 | 风控目标 |
| "用户行为路径" | 漏斗分析、Markov 链、序列模式挖掘 | 行为分析目标 |

### 自动选择逻辑

```
IF 目标含时间维度 AND 需要预测 → 时间序列方法族
ELIF 目标含比较词（差异、影响、原因） → 统计检验 + 回归方法族
ELIF 目标含分类词（群体、分群、类型） → 聚类方法族
ELIF 目标含关联词（关系、影响、相关） → 相关性/因果方法族
ELIF 目标含优化词（最优、最佳、改进） → 优化/实验方法族
ELSE → 描述性 + 探索性方法族
```

### 模型选择优先级

1. **简单优先**：优先使用可解释性强的模型（线性回归、逻辑回归、决策树）
2. **性能验证**：复杂模型（XGBoost、神经网络）需在简单模型基线上有显著提升
3. **业务适配**：金融/医疗等强监管场景优先可解释模型
4. **资源约束**：大数据量或低资源场景选择轻量模型

---

## 可视化规范

### 图表类型选择规则

| 数据关系 | 推荐图表 | 避免 |
|----------|----------|------|
| 趋势变化（时间序列） | 折线图、面积图 | 饼图 |
| 类别对比 | 柱状图、条形图 | 3D 图 |
| 构成比例 | 堆叠柱状图、环形图 | 3D 饼图 |
| 分布形态 | 直方图、密度图、箱线图 | 散点图（大数据量） |
| 相关性 | 散点图、热力图、气泡图 | 柱状图 |
| 地理分布 | 地图、Choropleth | 表格 |
| 流程/漏斗 | 漏斗图、桑基图 | 折线图 |

### 设计规范

- **配色**：使用 ColorBrewer 或 Tableau 调色板，确保色盲友好
- **标注**：关键数据点必须标注数值，图表标题清晰描述结论
- **字体**：标题 ≥ 14px，正文 ≥ 12px，保持中英文混排美观
- **比例**：黄金比例优先，避免过宽或过高
- **图例**：统一位置，避免遮挡数据
- **网格线**：浅灰色、低透明度，不喧宾夺主
- **输出格式**：PNG（300 DPI）用于报告，SVG 用于可交互场景

### 禁止事项

- 不使用 3D 图表（除非有明确三维需求）
- 不使用误导性截断轴（必须从 0 开始，除非有特殊说明）
- 不隐藏不利数据或选择性呈现
- 不在同一图表混合过多类别（≤ 8 个系列）

---

## 多Agent协作规则

### Agent角色定义

| Agent | 职责 | 权限 |
|-------|------|------|
| **Planner Agent** | 目标解析、任务拆分、流程编排 | 启动/终止流程、修改计划 |
| **Data Agent** | 数据发现、接入、Schema 推断 | 读取数据源、缓存数据 |
| **Cleaner Agent** | 数据清洗、质量评估、预处理 | 修改数据、生成清洗报告 |
| **Analyst Agent** | 探索分析、统计检验、方法执行 | 运行分析脚本、选择方法 |
| **Model Specialist Agent** | 模型训练、调参、评估 | 训练/保存模型、生成评估 |
| **Visualization Agent** | 图表生成、排版、仪表盘 | 创建/修改图表 |
| **Reporter Agent** | 报告撰写、洞察提取、建议生成 | 编辑报告、整合输出 |
| **Reviewer Agent** | 质量审查、一致性验证、评分 | 否决/要求修正、独立评分 |
| **Knowledge Agent** | 流程归档、模板提取、知识沉淀 | 更新知识库、保存模板 |

### 协作协议

- **顺序执行**：默认按 9 阶段顺序推进，前阶段输出为后阶段输入
- **并行机会**：数据接入可并行、多模型可并行训练、图表可并行生成
- **回滚机制**：任何阶段失败可回退至最近稳定状态
- **仲裁规则**：Analyst 与 Model Specialist 方法选择分歧由 Planner 裁决
- **审查独立**：Reviewer Agent 完全独立，不参与前面任何阶段
- **冲突解决**：争议升级至 Planner，记录决策日志

### 通信格式

```json
{
  "from": "analyst_agent",
  "to": "visualization_agent",
  "type": "deliverable",
  "payload": {
    "results": {},
    "metadata": {},
    "requirements": "图表类型偏好"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 结果审校规则

### 审查清单（Checklist）

| 审查项 | 检查标准 | 通过条件 |
|--------|----------|----------|
| 数据一致性 | 结论中的数据与原始数据一致 | 抽样验证 100% 匹配 |
| 方法合理性 | 所选方法与目标匹配 | 符合方法选择规则 |
| 统计显著性 | 关键结论有统计支持 | p-value < 0.05 或等效标准 |
| 结论逻辑性 | 结论有数据支持，无跳跃推理 | 每个结论可追溯至分析结果 |
| 可视化准确性 | 图表数据与源数据一致 | 无错误、误导或不一致 |
| 完整性 | 覆盖用户目标的所有子问题 | 无遗漏 |
| 可重现性 | 提供完整复现路径 | 给定数据 + 代码 = 相同结果 |
| 局限性声明 | 明确标注数据/方法局限 | 有完整局限性章节 |
| 建议可操作性 | 建议具体、可执行 | 包含 Action、Owner、Timeline |

### 评分体系

- **90-100 分**：优秀，可直接交付
- **80-89 分**：良好，微调后交付
- **70-79 分**：合格，需补充分析后交付
- **60-69 分**：需改进，返回 Analyst 修正
- **< 60 分**：不合格，重新分析

### 自动修正规则

- 数据不一致 → 自动重新提取验证
- 图表不规范 → 自动按规范重绘
- 结论缺乏支持 → 补充分析方法或降低置信度标注
- 缺失局限性 → 自动生成局限性章节

---

## 异常处理与兜底策略

### 异常分类与处理

| 异常类型 | 检测方式 | 处理策略 |
|----------|----------|----------|
| 数据源不可达 | 连接超时、返回错误 | 尝试备选数据源；若无，报告数据缺失 |
| 数据质量极差 | 缺失率 > 80%、无有效记录 | 终止流程，告知用户数据不可用 |
| 分析方法失败 | 模型不收敛、统计假设不满足 | 降级至简单方法；记录降级原因 |
| 计算资源不足 | 内存溢出、超时 | 切换抽样策略或分块处理 |
| 结果矛盾 | 多方法结论不一致 | 增加分析方法权重讨论，标注不确定性 |
| 审查不通过 | Reviewer 评分 < 60 | 自动返回修正，最多重试 3 次 |
| 用户目标模糊 | 无法解析出明确任务 | 向用户请求澄清，提供结构化问题 |

### 兜底策略（Fallback）

1. **数据兜底**：无可用数据时，提供公开数据源建议或模拟数据（明确标注）
2. **方法兜底**：复杂方法失败时，回退至描述性统计 + 基础可视化
3. **精度兜底**：高精度要求无法满足时，明确标注置信度降级
4. **时间兜底**：超时未完成时，输出已完成部分的阶段性报告
5. **质量兜底**：审查持续不通过时，输出当前最佳结果 + 完整局限性说明

### 错误报告格式

```json
{
  "error_type": "data_unavailable",
  "phase": "data_ingestion",
  "message": "无法连接到数据库 postgresql://...",
  "fallback_applied": "使用本地CSV备用数据源",
  "impact": "分析范围缩小至本地数据覆盖范围",
  "user_action_required": false
}
```

---

## Skill复用模板

### 快速复用

```yaml
# reusable_template.yaml
name: "{{ task_name }}"
domain: "{{ domain }}"
depth: "{{ depth }}"

data_sources:
  - type: "{{ source_type }}"
    path: "{{ source_path }}"

focus_dimensions:
  - "{{ dim_1 }}"
  - "{{ dim_2 }}"

output_format: "{{ output_format }}"

# 保存的分析方法配置
methodology:
  eda_methods: ["descriptive", "correlation", "distribution"]
  modeling_methods: ["{{ method_1 }}", "{{ method_2 }}"]
  visualization_types: ["{{ chart_1 }}", "{{ chart_2 }}"]

# 可复用的特征工程pipeline
feature_pipeline:
  - step: "impute"
    strategy: "knn"
  - step: "encode"
    strategy: "one_hot"
  - step: "scale"
    strategy: "standard"
```

### 模板调用方式

```python
# 加载已保存模板
template = load_template("sales_analysis_template")

# 替换参数
template.fill({
    "task_name": "2024Q2销售分析",
    "domain": "retail",
    "source_path": "/data/sales_q2.csv",
    "dim_1": "region",
    "dim_2": "product_category"
})

# 执行分析
result = run_analysis(template)
```

### 知识积累

- 每次分析完成后自动保存方法论到 `knowledge_base/`
- 同类任务自动推荐历史最佳方法组合
- 支持手动标注"优质分析"供未来参考
- 版本化管理分析模板，支持 A/B 对比

---

## 示例调用方式

### 案例1：电商销售分析

```
分析目标：分析2024年Q1各品类销售表现，找出下降品类及原因，提出Q2改进策略

输入配置：
  goal: "分析2024年Q1各品类销售表现，找出下降品类及原因，提出Q2改进策略"
  domain: "retail"
  time_range:
    start: "2024-01-01"
    end: "2024-03-31"
  data_sources:
    - type: "csv"
      path: "./data/sales_q1.csv"
    - type: "csv"
      path: "./data/products.csv"
  focus_dimensions:
    - "category"
    - "region"
    - "channel"
  depth: "standard"
  output_format: "all"

预期输出：
  - 各品类销售额趋势图
  - 品类表现对比柱状图
  - 下降品类归因分析
  - Q2策略建议报告
```

### 案例2：金融风控分析

```
分析目标：评估当前信贷产品风险状况，识别高风险客群特征，优化风控策略

输入配置：
  goal: "评估当前信贷产品风险状况，识别高风险客群特征，优化风控策略"
  domain: "finance"
  time_range:
    start: "2023-01-01"
    end: "2024-03-31"
  data_sources:
    - type: "sql"
      connection: "postgresql://analyst:***@db:5432/loans"
      query: "SELECT * FROM loan_applications WHERE status IN ('approved', 'defaulted')"
    - type: "csv"
      path: "./data/macro_indicators.csv"
  focus_dimensions:
    - "age_group"
    - "income_level"
    - "credit_score"
    - "loan_purpose"
  depth: "deep"
  confidence_threshold: 0.99
  output_format: "pdf"

预期输出：
  - 风险分布热力图
  - 高风险客群画像
  - 风险因子重要性排序
  - 风控策略优化建议
  - 模型评估报告（AUC、KS等指标）
```

### 案例3：用户增长分析

```
分析目标：分析近半年用户增长情况，找出流失关键节点，提出留存提升方案

输入配置：
  goal: "分析近半年用户增长情况，找出流失关键节点，提出留存提升方案"
  domain: "product"
  time_range:
    start: "2023-10-01"
    end: "2024-03-31"
  data_sources:
    - type: "api"
      url: "https://analytics.company.com/api/users/events"
      params:
        from: "2023-10-01"
        to: "2024-03-31"
    - type: "parquet"
      path: "./data/user_profiles.parquet"
  focus_dimensions:
    - "acquisition_channel"
    - "user_segment"
    - "feature_usage"
  depth: "deep"
  output_format: "html"

预期输出：
  - 用户增长漏斗图
  - 留存曲线（Cohort Analysis）
  - 流失预警模型
  - 关键流失节点分析
  - 留存提升方案（按优先级排序）
  - 交互式HTML报告
```

---

## 版本迭代建议

### v0.1（当前版本）

- 基础 9 阶段工作流
- 核心 Agent 角色定义
- 单数据源支持（CSV、Excel）
- 基础可视化

### v0.2 建议

- [ ] 支持更多数据源（SQL、API、Parquet、JSON）
- [ ] 增加时间序列预测能力（Prophet、ARIMA）
- [ ] 完善可视化规范与模板库
- [ ] 增加审查评分自动化

### v0.3 建议

- [ ] 引入多模态数据支持（文本、图像元数据）
- [ ] 实现知识图谱构建
- [ ] 支持在线/增量分析
- [ ] 增加 A/B 测试分析模块
- [ ] 优化并行执行引擎

### v1.0 路线图

- [ ] 完整多 Agent 自主协作（无人工干预）
- [ ] 自学习方法选择（基于历史成功率）
- [ ] 实时数据流支持（Kafka、WebSocket）
- [ ] 协作编辑与实时报告
- [ ] API 化对外服务
- [ ] 插件化架构（自定义 Agent、自定义方法）

### 持续改进

- 收集用户反馈，优化方法选择规则
- 积累行业模板，提升分析质量
- 定期更新依赖库，保持技术前沿
- 建立分析质量基准，持续自我提升

---

## 依赖项

```
pandas, numpy, yfinance, requests, sqlalchemy,
scikit-learn, statsmodels, matplotlib, seaborn,
scipy, plotly, openpyxl, pyarrow
```

## 目录结构

```
autonomous-data-analyst/
├── config.yaml              # 技能配置文件
├── README.md                # 使用说明（本文件）
├── agents/
│   ├── planner.py           # Planner Agent
│   ├── data_agent.py        # Data Agent
│   ├── cleaner.py           # Cleaner Agent
│   ├── analyst.py           # Analyst Agent
│   ├── model_specialist.py  # Model Specialist Agent
│   ├── visualizer.py        # Visualization Agent
│   ├── reporter.py          # Reporter Agent
│   ├── reviewer.py          # Reviewer Agent
│   └── knowledge.py         # Knowledge Agent
├── core/
│   ├── pipeline.py          # 工作流编排
│   ├── method_selector.py   # 方法选择器
│   ├── validators.py        # 验证器
│   └── utils.py             # 工具函数
├── templates/
│   ├── sales_analysis.yaml  # 销售分析模板
│   ├── finance_risk.yaml    # 金融风控模板
│   └── user_growth.yaml     # 用户增长模板
├── knowledge_base/          # 知识沉淀
├── examples/                # 示例文件
└── requirements.txt         # 依赖声明
```
