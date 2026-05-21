# 电商销售分析示例

## 业务场景描述

某电商平台在 2024 年 Q1 季度发现整体销售额同比下降 12%，管理层需要快速定位问题根源并制定改进策略。涉及多个品类线、多渠道流量来源，需要跨维度分析以找出真正的业绩驱动因素和阻碍因素。

## 分析目标

- 找出 2024 Q1 销售额同比下降的主要驱动因素
- 识别表现优异和表现不佳的品类及渠道
- 分析用户购买行为变化趋势
- 提供可落地的业务改进建议

## 数据来源说明

| 数据源 | 格式 | 字段 | 时间范围 |
|--------|------|------|----------|
| 订单系统 | CSV/Database | order_id, user_id, sku_id, category, amount, quantity, payment_method, status, created_at | 2023-Q1 ~ 2024-Q1 |
| 商品信息 | CSV | sku_id, category, sub_category, price, cost, supplier | 静态数据 |
| 流量日志 | JSON/Database | session_id, user_id, channel, page_views, cart_add, purchase, timestamp | 2023-Q1 ~ 2024-Q1 |
| 用户画像 | CSV | user_id, age_group, gender, city_tier, register_date, membership_level | 静态数据 |

## 分析方法

### Phase 1: 目标解析

```yaml
goal: "分析2024年Q1电商销售同比下降原因并提出改进建议"
metrics:
  - name: "gmv"
    definition: "SUM(order_amount) WHERE status = 'completed'"
    source: "orders.amount"
  - name: "conversion_rate"
    definition: "COUNT(purchases) / COUNT(sessions) * 100"
    source: "traffic_logs"
  - name: "aov"
    definition: "SUM(order_amount) / COUNT(orders)"
    source: "orders.amount"
  - name: "repurchase_rate"
    definition: "COUNT(users_with_2+_orders) / COUNT(total_active_users)"
    source: "orders.user_id"
data_requirements:
  - source: "orders"
    fields: ["order_id", "user_id", "sku_id", "category", "amount", "quantity", "status", "created_at"]
    time_range: "2023-01-01 to 2024-03-31"
  - source: "traffic"
    fields: ["session_id", "user_id", "channel", "page_views", "cart_add", "purchase", "timestamp"]
    time_range: "2023-01-01 to 2024-03-31"
  - source: "products"
    fields: ["sku_id", "category", "sub_category", "price", "cost"]
    time_range: "static"
  - source: "users"
    fields: ["user_id", "age_group", "gender", "city_tier", "membership_level"]
    time_range: "static"
assumptions:
  - assumption: "订单数据完整，无系统故障导致的数据丢失"
    confidence: "high"
  - assumption: "流量日志中的 session_id 与订单系统可关联"
    confidence: "medium"
```

### Phase 2: 分析规划

```yaml
phases:
  - name: "数据清洗与整合"
    tasks:
      - "处理缺失值和异常订单（退款、取消）"
      - "统一品类命名规范"
      - "关联订单、流量、用户数据"
    agent: "data_engineer"
    expected_output: "cleaned_merged_dataset"
    fallback: "使用保守过滤策略，记录所有被排除的记录"
  - name: "趋势与同比分析"
    tasks:
      - "GMV 同比/环比趋势分析"
      - "各品类销售贡献拆解"
      - "渠道流量与转化分析"
    agent: "analyst_trend"
    expected_output: "trend_analysis_report"
    fallback: "数据不足时使用移动平均平滑"
  - name: "用户行为分析"
    tasks:
      - "用户分层（新/老/沉睡）"
      - "购买路径漏斗分析"
      - "复购行为分析"
    agent: "analyst_behavior"
    expected_output: "behavior_analysis_report"
    fallback: "用户ID缺失时使用匿名session分析"
  - name: "归因与诊断"
    tasks:
      - "销售额下降因素归因分析"
      - "价格弹性分析"
      - "品类-渠道交叉分析"
    agent: "analyst_diagnostic"
    expected_output: "attribution_report"
    fallback: "无法归因时使用描述性分析替代"
dependencies: ["数据清洗与整合"]
```

## 预期输出

### 分析报告结构

```markdown
# 2024年Q1电商销售同比下降分析报告

## 执行摘要
- Q1 GMV 同比下降 12%，主要由 XX 品类（-XX%）和 XX 渠道（-XX%）拖累
- 转化率从 X.X% 下降至 X.X%，为主要下降驱动因素
- XX 品类和 XX 渠道表现逆势增长，可作为重点发力方向
- 建议：优化 XX 品类供应链、加大 XX 渠道投入、推出 XX 营销活动

## 分析背景
- 分析目标：定位 Q1 销售下降原因并提出改进建议
- 数据来源：订单系统、流量日志、商品信息、用户画像
- 时间范围：2023-Q1 对比 2024-Q1
- 分析方法：趋势分析、归因分析、漏斗分析、用户分层

## 数据概况
- 订单总量：XXX 万条
- 数据质量：缺失率 X.X%，已处理
- 预处理步骤：剔除取消/退款订单、统一品类命名、关联多表

## 详细分析
### GMV 趋势分析
- 方法：同比环比拆解、贡献度分析
- 结果：XX 品类贡献了下降的 XX%
- 图表：月度GMV折线图（2023 vs 2024）、品类贡献瀑布图

### 渠道分析
- 方法：渠道ROI分析、流量-转化拆解
- 结果：XX 渠道流量下降 XX%，但转化率稳定
- 图表：渠道流量-转化气泡图、各渠道ROI柱状图

### 用户行为分析
- 方法：RFM 用户分层、购买漏斗分析
- 结果：新客获取成本上升 XX%，老客复购率下降 X%
- 图表：用户分层饼图、购买漏斗图、复购率趋势线

### 品类诊断
- 方法：品类波士顿矩阵、价格弹性分析
- 结果：XX 品类价格敏感度上升，XX 品类需求萎缩
- 图表：品类波士顿矩阵散点图、价格-销量关系图

## 风险评估
| 风险项 | 等级 | 描述 | 影响 | 建议 |
|--------|------|------|------|------|
| 流量日志与订单关联率仅 78% | Yellow | 部分 session 无法追踪到最终购买 | 渠道转化分析可能偏低 | 建议完善埋点系统 |
| 新客样本量偏少（n=2,300） | Yellow | 新客分析统计功效不足 | 新客策略建议需谨慎 | 建议延长观察窗口 |

## 业务建议
1. 针对 XX 品类：优化 SKU 结构，下架低效 SKU，引入爆款替代
2. 针对 XX 渠道：增加投放预算 X%，优化落地页提升转化
3. 用户运营：推出老客专属优惠，提升复购率 X 个百分点
4. 价格策略：对价格敏感品类实施动态定价，提升毛利率

## 附录
- 技术细节：使用的统计方法、模型参数
- 代码引用：分析脚本路径
- 原始输出：中间分析结果
```

## 关键指标

| 指标名称 | 计算公式 | 目标值 | 说明 |
|----------|----------|--------|------|
| GMV | SUM(completed_order_amount) | 同比持平或增长 | 核心业务指标 |
| 订单量 | COUNT(completed_orders) | 同比增长 ≥ 5% | 衡量业务活跃度 |
| 客单价 AOV | GMV / 订单量 | ≥ 行业均值 | 衡量用户消费能力 |
| 转化率 | 购买session / 总session | ≥ 3.5% | 衡量流量质量 |
| 复购率 | 30天内再次购买用户 / 总购买用户 | ≥ 25% | 衡量用户粘性 |
| 退款率 | 退款订单 / 总订单 | ≤ 5% | 衡量商品质量 |
| 毛利率 | (GMV - COGS) / GMV | ≥ 30% | 衡量盈利能力 |

## 图表类型建议

| 分析维度 | 图表类型 | 用途 | 配置建议 |
|----------|----------|------|----------|
| GMV 趋势 | 折线图 (Line Chart) | 对比 2023 vs 2024 月度 GMV 走势 | x: month, y: gmv, color: year |
| 品类贡献 | 瀑布图 (Waterfall Chart) | 展示各品类对 GMV 变化的贡献 | x: category, y: contribution |
| 渠道对比 | 气泡图 (Bubble Chart) | 流量 vs 转化率 vs GMV 三维度 | x: traffic, y: conversion, size: gmv |
| 用户分层 | 饼图/环形图 (Donut Chart) | 新客/老客/沉睡客占比 | labels: segment, values: count |
| 购买漏斗 | 漏斗图 (Funnel Chart) | 浏览→加购→下单→支付转化率 | stages: view, cart, order, pay |
| 复购分析 | 折线图 (Line Chart) | 月度复购率趋势 | x: month, y: repurchase_rate |
| 品类矩阵 | 散点图 (Scatter Plot) | 市场份额 vs 增长率（波士顿矩阵） | x: growth_rate, y: market_share |
| 价格弹性 | 散点图 + 回归线 | 价格变动对销量的影响 | x: price_change, y: sales_change |
| 渠道 ROI | 柱状图 (Bar Chart) | 各渠道投入产出比 | x: channel, y: roi, color: performance |
| 热力图 | 热力图 (Heatmap) | 品类×时段销售密度 | x: hour/day, y: category, color: sales |

## Skill Package 沉淀模板

```yaml
skill_name: "ecommerce-sales-diagnostic"
version: "1.0.0"
description: "电商平台销售下降诊断分析流程，适用于GMV同比下降时的根因分析"

input_spec:
  data_format: "csv|database"
  required_fields: ["order_id", "user_id", "sku_id", "category", "amount", "status", "created_at"]
  optional_fields: ["channel", "payment_method", "coupon_code"]
  constraints:
    min_records: 1000
    time_granularity: "daily"

data_processing:
  - step: "cleaning"
    rules: ["排除 status IN ('cancelled', 'refunded') 的订单", "处理 amount 为负数的异常记录"]
  - step: "transformation"
    rules: ["按 category 聚合", "按 month 计算同比环比"]

analysis_logic:
  methods:
    - name: "贡献度拆解"
      when: "需要定位具体品类/渠道对整体变化的影响"
      parameters: { baseline_period: "YoY", method: "factor_decomposition" }
    - name: "漏斗分析"
      when: "需要评估用户转化路径效率"
      parameters: { stages: ["view", "cart", "order", "pay"] }
    - name: "RFM分层"
      when: "需要进行用户分层运营分析"
      parameters: { recency_days: 90, frequency_min: 2 }

chart_templates:
  - type: "line"
    config: { x: "month", y: "gmv", color: "year", title: "月度GMV趋势对比" }
  - type: "waterfall"
    config: { x: "category", y: "contribution", title: "品类GMV贡献拆解" }
  - type: "funnel"
    config: { stages: ["浏览", "加购", "下单", "支付"], title: "购买转化漏斗" }

output_template:
  sections: ["执行摘要", "GMV趋势分析", "渠道分析", "用户行为分析", "品类诊断", "业务建议"]

review_rules:
  - check: "数据一致性"
    criteria: "各渠道GMV之和 = 总GMV，误差 < 0.1%"
  - check: "sample_size"
    min_n: 100
  - check: "业务合理性"
    criteria: "转化率应在 1%-10% 合理范围内"

exception_handling:
  - condition: "品类字段缺失"
    action: "使用 sku_id 关联商品信息表获取品类"
  - condition: "同比数据不足"
    action: "改用环比分析，标注风险等级 Yellow"
```
