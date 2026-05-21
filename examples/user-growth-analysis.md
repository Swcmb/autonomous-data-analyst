# 用户增长分析示例

## 业务场景描述

某 SaaS 产品上线 18 个月，用户增长出现明显放缓。管理层发现最近一个季度的新用户获取量环比下降 20%，同时 7 日留存率从 45% 降至 32%。需要系统分析用户获取、激活、留存和流失的全链路，识别增长瓶颈并提出优化策略。

## 分析目标

- 分析用户增长放缓的根本原因（获取端 vs 留存端）
- 构建用户生命周期漏斗，定位转化效率最低的环节
- 识别影响用户留存的关键因素和行为模式
- 预测未来 6 个月用户增长趋势（基准情景 / 乐观情景 / 悲观情景）
- 制定用户增长优化策略和优先级排序

## 数据来源说明

| 数据源 | 格式 | 字段 | 时间范围 |
|--------|------|------|----------|
| 用户注册表 | CSV/Database | user_id, register_date, channel, campaign, device, country | 上线至今 |
| 行为日志 | Database | user_id, event_type, event_time, page, feature, duration_sec | 上线至今 |
| 订阅/付费表 | CSV | user_id, plan_type, start_date, end_date, amount, status, cancel_reason | 上线至今 |
| 推送/营销记录 | CSV | user_id, campaign_id, send_date, channel, opened, clicked, converted | 上线至今 |
| 客服工单 | CSV | user_id, ticket_id, category, created_at, resolved_at, satisfaction_score | 上线至今 |

## 分析方法

### Phase 1: 目标解析

```yaml
goal: "分析用户增长放缓原因并制定优化策略"
metrics:
  - name: "new_users"
    definition: "COUNT(DISTINCT user_id) WHERE register_date IN period"
    source: "user_registry"
  - name: "activation_rate"
    definition: "COUNT(users_completed_onboarding) / COUNT(new_users) * 100"
    source: "behavior_logs"
  - name: "retention_d7"
    definition: "COUNT(users_active_on_day7) / COUNT(new_users) * 100"
    source: "behavior_logs"
  - name: "churn_rate"
    definition: "COUNT(users_no_activity_30d) / COUNT(active_users_start_of_month) * 100"
    source: "behavior_logs"
  - name: "ltv"
    definition: "ARPU * (1 / monthly_churn_rate)"
    source: "subscription + behavior"
  - name: "cac"
    definition: "SUM(marketing_spend) / COUNT(new_users)"
    source: "marketing_spend + user_registry"
data_requirements:
  - source: "user_registry"
    fields: ["user_id", "register_date", "channel", "campaign", "device", "country"]
    time_range: "上线至今"
  - source: "behavior_logs"
    fields: ["user_id", "event_type", "event_time", "page", "feature", "duration_sec"]
    time_range: "上线至今"
  - source: "subscriptions"
    fields: ["user_id", "plan_type", "start_date", "end_date", "amount", "status"]
    time_range: "上线至今"
  - source: "marketing"
    fields: ["user_id", "campaign_id", "send_date", "channel", "opened", "clicked"]
    time_range: "上线至今"
assumptions:
  - assumption: "行为日志覆盖 95% 以上的用户操作"
    confidence: "high"
  - assumption: "30天无活跃视为流失"
    confidence: "medium"
  - assumption: "渠道归因为首次触达（First-touch）"
    confidence: "medium"
```

### Phase 2: 分析规划

```yaml
phases:
  - name: "数据清洗与整合"
    tasks:
      - "处理用户注册时间异常（未来时间、空值）"
      - "行为日志去重和事件标准化"
      - "构建用户生命周期时间线（注册→激活→留存→付费→流失）"
    agent: "data_engineer"
    expected_output: "user_lifecycle_dataset"
    fallback: "部分事件缺失时使用已有事件重建路径"
  - name: "获客分析"
    tasks:
      - "渠道获客量和质量分析"
      - "CAC 趋势分析"
      - "渠道 ROI 对比"
    agent: "analyst_acquisition"
    expected_output: "acquisition_analysis_report"
    fallback: "营销支出数据缺失时使用渠道流量替代"
  - name: "激活与留存分析"
    tasks:
      - "用户激活漏斗分析"
      - "同期群留存分析（Cohort Analysis）"
      - "留存驱动因素识别"
    agent: "analyst_retention"
    expected_output: "retention_analysis_report"
    fallback: "行为事件粒度不足时使用页面级聚合"
  - name: "流失分析"
    tasks:
      - "流失用户画像分析"
      - "流失前行为模式识别"
      - "流失预警因素提取"
    agent: "analyst_churn"
    expected_output: "churn_analysis_report"
    fallback: "无法识别流失原因时仅做描述性分析"
  - name: "预测与策略"
    tasks:
      - "用户增长趋势预测（ARIMA/Prophet）"
      - "LTV/CAC 健康度评估"
      - "增长策略优先级排序"
    agent: "analyst_forecast"
    expected_output: "growth_forecast_report"
    fallback: "模型不收敛时使用线性趋势外推"
dependencies: ["数据清洗与整合"]
```

## 预期输出

### 分析报告结构

```markdown
# SaaS产品用户增长诊断与优化策略报告

## 执行摘要
- 新用户环比下降 20%，主要由 XX 渠道获客减少（-XX%）和 XX 渠道 CAC 上升（+XX%）导致
- 7日留存率降至 32%，关键流失点在 Day 2-3（激活后未形成使用习惯）
- 影响留存的最关键因素：完成 onboarding 的用户留存率 58%，未完成仅 12%
- 预测：若维持现状，6个月后 MAU 将下降至 XX；若执行优化策略，可回升至 XX
- 建议优先级：优化 onboarding 流程 > 调整渠道结构 > 推出激活激励活动

## 分析背景
- 分析目标：定位增长放缓原因，制定优化策略
- 数据来源：用户注册、行为日志、订阅、营销记录
- 时间范围：产品上线至今（18个月）
- 分析方法：漏斗分析、同期群分析、生存分析、趋势预测

## 数据概况
- 总注册用户：XX 万
- 行为事件量：XX 百万条
- 数据质量：缺失率 X.X%，已清洗
- 预处理步骤：事件去重、时间对齐、生命周期标记

## 详细分析
### 获客分析
- 方法：渠道获客趋势、CAC 计算、渠道 ROI
- 结果：渠道 A 获客占比从 40% 降至 25%，CAC 从 ¥XX 升至 ¥XX
- 图表：渠道获客趋势图、CAC 月度柱状图

### 激活与留存分析
- 方法：激活漏斗、Cohort 留存曲线、生存分析
- 结果：激活率从 65% 降至 48%，Day 3 为关键流失点
- 图表：激活漏斗图、Cohort 热力图、K-Means 留存曲线

### 留存驱动因素
- 方法：特征重要性分析（随机森林）、逻辑回归
- 结果：Top 3 驱动因素：完成 onboarding、7天内使用核心功能 X、收到个性化推送
- 图表：特征重要性排序图、决策树可视化

### 流失分析
- 方法：流失用户画像对比、流失前行为序列分析
- 结果：流失用户平均使用时长仅 X 天，核心功能使用率低于留存用户 XX%
- 图表：流失/留存用户对比雷达图、流失时间分布直方图

### 增长预测
- 方法：Prophet 时间序列预测、情景分析
- 结果：基准情景 6月后 MAU = XX，优化情景 MAU = XX
- 图表：三情景预测折线图

## 风险评估
| 风险项 | 等级 | 描述 | 影响 | 建议 |
|--------|------|------|------|------|
| 行为日志覆盖不完整（缺失移动 App） | Yellow | 移动端用户行为数据仅 60% 可追踪 | 留存分析可能低估移动用户活跃度 | 建议完善 App 埋点 |
| 流失定义主观（30天阈值） | Blue | 不同品类用户活跃周期不同 | 部分低频用户可能被误判为流失 | 建议按品类设置差异化阈值 |
| 预测模型基于历史趋势 | Yellow | 未纳入市场竞争变化和新品发布影响 | 预测可能偏离实际 | 建议按月更新模型参数 |

## 业务建议
1. 立即执行（1-2周）：优化 onboarding 流程，将关键引导步骤缩短至 3 步以内
2. 短期（1个月）：调整渠道预算，将 XX 渠道预算转移至 ROI 更高的 XX 渠道
3. 中期（3个月）：推出新用户激活激励计划（7天内完成 X 功能使用奖励 XX）
4. 长期（6个月）：构建用户健康评分体系，实现流失预警和自动干预

## 附录
- 技术细节：Prophet 模型参数、随机森林超参数
- 代码引用：分析脚本路径
- 原始输出：Cohort 矩阵、预测数据

```

## 关键指标

| 指标名称 | 计算公式 | 目标值 | 说明 |
|----------|----------|--------|------|
| 新用户数 | COUNT(DISTINCT user_id) GROUP BY register_date | 月环比 ≥ 0 | 增长核心指标 |
| 激活率 | 完成 onboarding 用户 / 新用户 | ≥ 60% | 衡量首次体验 |
| 7日留存率 | Day 7 活跃用户 / 当日新用户 | ≥ 40% | 衡量早期留存 |
| 30日留存率 | Day 30 活跃用户 / 当日新用户 | ≥ 20% | 衡量长期留存 |
| 月流失率 | 30天无活跃用户 / 月初活跃用户 | ≤ 8% | 衡量用户流失 |
| CAC | 营销支出 / 新用户数 | ≤ ¥XX | 获客成本 |
| LTV | ARPU / 月流失率 | ≥ 3×CAC | 用户生命周期价值 |
| LTV/CAC | LTV 除以 CAC | ≥ 3.0 | 增长健康度 |
| 付费转化率 | 付费用户 / 总用户 | ≥ 5% | 商业化效率 |
| NPS | 推荐者% - 批评者% | ≥ 30 | 用户满意度 |

## 图表类型建议

| 分析维度 | 图表类型 | 用途 | 配置建议 |
|----------|----------|------|----------|
| 用户增长趋势 | 折线图 (Line Chart) | 月度新用户数和累计用户趋势 | x: month, y: [new_users, cumulative_users] |
| 渠道对比 | 堆叠柱状图 (Stacked Bar) | 各渠道月度获客量 | x: month, y: users, stack: channel |
| CAC 趋势 | 折线 + 柱状组合图 | CAC 趋势与获客量对比 | x: month, y1: cac (line), y2: new_users (bar) |
| 激活漏斗 | 漏斗图 (Funnel Chart) | 注册→激活→核心功能使用→付费 | stages: register, activate, use_core, pay |
| Cohort 留存 | 热力图 (Heatmap) | 按注册月份分组的留存率矩阵 | x: day, y: cohort_month, color: retention_rate |
| 留存曲线 | 折线图 (Line Chart) | 不同渠道/人群的留存曲线对比 | x: day, y: retention_rate, color: channel |
| 特征重要性 | 水平柱状图 (Horizontal Bar) | 影响留存的因素排序 | x: importance, y: feature |
| 流失用户画像 | 雷达图 (Radar Chart) | 流失 vs 留存用户多维度对比 | axes: usage_days, features_used, sessions, time_spent, support_tickets |
| 用户健康分布 | 小提琴图 (Violin Plot) | 用户健康评分分布 | x: segment, y: health_score |
| 增长预测 | 折线图 + 置信区间 (Line + Ribbon) | 三情景预测及置信区间 | x: month, y: predicted_mau, ribbon: confidence_band |
| 行为序列 | 桑基图 (Sankey Diagram) | 用户注册后的行为路径流向 | nodes: events, links: flow_volume |
| 生存分析 | 阶梯线图 (Step Line) | K-Means 生存函数曲线 | x: days, y: survival_probability, color: cohort |

## Skill Package 沉淀模板

```yaml
skill_name: "user-growth-diagnostic"
version: "1.0.0"
description: "SaaS产品用户增长全链路诊断流程，适用于增长放缓、留存下降时的根因分析"

input_spec:
  data_format: "csv|database"
  required_fields: ["user_id", "register_date", "event_type", "event_time"]
  optional_fields: ["channel", "campaign", "plan_type", "amount", "device"]
  constraints:
    min_records: 5000
    time_granularity: "daily"

data_processing:
  - step: "cleaning"
    rules: ["排除 register_date 为空的记录", "行为日志按 user_id + event_time 去重"]
  - step: "transformation"
    rules: ["标记用户生命周期阶段", "计算同期群归属", "生成日粒度活跃矩阵"]

analysis_logic:
  methods:
    - name: "Cohort留存分析"
      when: "需要评估不同时期注册用户的留存差异"
      parameters: { cohort_unit: "month", retention_days: [1, 3, 7, 14, 30] }
    - name: "漏斗分析"
      when: "需要评估用户转化路径效率"
      parameters: { stages: ["register", "activate", "use_core", "pay"] }
    - name: "特征重要性"
      when: "需要识别影响留存的关键因素"
      parameters: { method: "random_forest", target: "retained_d7" }
    - name: "Prophet预测"
      when: "需要预测未来用户增长趋势"
      parameters: { horizon: "180_days", uncertainty: 0.95 }

chart_templates:
  - type: "heatmap"
    config: { x: "day", y: "cohort_month", color: "retention_rate", title: "Cohort留存矩阵" }
  - type: "funnel"
    config: { stages: ["注册", "激活", "核心功能", "付费"], title: "用户转化漏斗" }
  - type: "line"
    config: { x: "month", y: "predicted_mau", ribbon: "confidence", title: "用户增长预测" }

output_template:
  sections: ["执行摘要", "获客分析", "激活与留存", "留存驱动因素", "流失分析", "增长预测", "业务建议"]

review_rules:
  - check: "数据一致性"
    criteria: "各渠道新用户之和 = 总新用户，误差 < 1%"
  - check: "sample_size"
    min_n: 100
  - check: "业务合理性"
    criteria: "LTV/CAC 应 > 1.0，7日留存率应在 10%-70% 范围内"

exception_handling:
  - condition: "行为日志不完整"
    action: "使用注册和付费数据做粗粒度分析，标注风险 Yellow"
  - condition: "用户量 < 5000"
    action: "仅做描述性分析，不做预测建模，标注风险 Yellow"
  - condition: "缺乏营销支出数据"
    action: "跳过 CAC 计算，使用渠道流量替代评估，标注风险 Blue"
```
