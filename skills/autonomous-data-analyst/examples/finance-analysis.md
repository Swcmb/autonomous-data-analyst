# 金融投资组合分析示例

## 业务场景描述

某资产管理公司需要对旗下三支主力基金（股票型、债券型、混合型）进行季度绩效评估。管理层需要了解各基金的风险收益特征、相关性结构、以及在当前市场环境下是否需要调整资产配置策略。同时需要为高净值客户提供定制化的投资组合优化建议。

## 分析目标

- 评估三支基金的季度收益表现和风险指标
- 分析基金之间的相关性及其对组合分散化的贡献
- 识别最优资产配置比例（最大化 Sharpe Ratio）
- 对比基准指数，评估主动管理能力
- 提供资产配置调整建议

## 数据来源说明

| 数据源 | 格式 | 字段 | 时间范围 |
|--------|------|------|----------|
| 基金净值 | CSV/API | fund_code, fund_name, nav, date, dividend | 2022-01-01 ~ 2024-Q1 |
| 基准指数 | CSV/API | index_code, index_name, close, date | 2022-01-01 ~ 2024-Q1 |
| 市场数据 | API (yfinance) | ticker, open, high, low, close, volume, date | 2022-01-01 ~ 2024-Q1 |
| 无风险利率 | CSV | date, rate_1y, rate_5y, shibor | 2022-01-01 ~ 2024-Q1 |
| 基金持仓 | CSV | fund_code, stock_code, stock_name, weight, date | 季度末快照 |

## 分析方法

### Phase 1: 目标解析

```yaml
goal: "评估三支主力基金季度绩效并优化资产配置建议"
metrics:
  - name: "total_return"
    definition: "(NAV_end - NAV_start + dividends) / NAV_start * 100"
    source: "fund_nav"
  - name: "annualized_return"
    definition: "((1 + total_return) ^ (365/days) - 1) * 100"
    source: "fund_nav"
  - name: "volatility"
    definition: "STD(daily_returns) * SQRT(252) * 100"
    source: "fund_nav daily returns"
  - name: "sharpe_ratio"
    definition: "(annualized_return - risk_free_rate) / volatility"
    source: "calculated"
  - name: "max_drawdown"
    definition: "MIN((peak - trough) / peak) * 100"
    source: "fund_nav cumulative"
  - name: "alpha"
    definition: "CAPM residual return"
    source: "regression of fund_return vs benchmark_return"
  - name: "beta"
    definition: "COVAR(fund, benchmark) / VAR(benchmark)"
    source: "regression slope"
data_requirements:
  - source: "fund_nav"
    fields: ["fund_code", "fund_name", "nav", "date", "dividend"]
    time_range: "2022-01-01 to 2024-03-31"
  - source: "benchmark"
    fields: ["index_code", "index_name", "close", "date"]
    time_range: "2022-01-01 to 2024-03-31"
  - source: "risk_free_rate"
    fields: ["date", "shibor"]
    time_range: "2022-01-01 to 2024-03-31"
  - source: "holdings"
    fields: ["fund_code", "stock_code", "weight", "date"]
    time_range: "quarterly snapshots"
assumptions:
  - assumption: "基金净值数据连续，无停牌导致的数据缺失"
    confidence: "high"
  - assumption: "使用 SHIBOR 作为无风险利率代理"
    confidence: "medium"
  - assumption: "历史收益分布近似正态，VaR 计算有效"
    confidence: "medium"
```

### Phase 2: 分析规划

```yaml
phases:
  - name: "数据清洗与预处理"
    tasks:
      - "处理净值数据中的缺失日（非交易日对齐）"
      - "计算日收益率序列"
      - "对齐各基金与基准的时间序列"
    agent: "data_engineer"
    expected_output: "aligned_returns_dataset"
    fallback: "使用前向填充处理非交易日，记录填充比例"
  - name: "绩效评估"
    tasks:
      - "计算各基金收益、波动率、Sharpe、最大回撤"
      - "CAPM 回归计算 Alpha 和 Beta"
      - "与基准指数对比分析"
    agent: "analyst_performance"
    expected_output: "performance_metrics_report"
    fallback: "数据窗口不足时使用简化指标"
  - name: "相关性分析"
    tasks:
      - "计算基金间相关系数矩阵"
      - "协方差矩阵分析"
      - "分散化效果评估"
    agent: "analyst_correlation"
    expected_output: "correlation_analysis_report"
    fallback: "样本不足时使用行业分类替代"
  - name: "组合优化"
    tasks:
      - "均值-方差优化（Markowitz）"
      - "蒙特卡洛模拟有效前沿"
      - "计算最优权重分配"
    agent: "analyst_optimizer"
    expected_output: "portfolio_optimization_report"
    fallback: "优化不收敛时使用等权或风险平价替代"
  - name: "风险诊断"
    tasks:
      - "VaR 和 CVaR 计算"
      - "压力测试（极端市场情景）"
      - "行业集中度分析"
    agent: "analyst_risk"
    expected_output: "risk_diagnostic_report"
    fallback: "无法计算 CVaR 时使用历史 VaR"
dependencies: ["数据清洗与预处理"]
```

## 预期输出

### 分析报告结构

```markdown
# 2024年Q1基金投资组合绩效评估与优化报告

## 执行摘要
- 股票型基金 Q1 收益 XX%，基准 XX%，Alpha 为 XX%
- 债券型基金波动率仅 X.X%，Sharpe Ratio 最优（X.XX）
- 当前等权组合 Sharpe 为 X.XX，优化后组合可提升至 X.XX
- 建议：提高债券型配置至 XX%，降低混合型至 XX%

## 分析背景
- 分析目标：季度绩效评估与资产配置优化
- 数据来源：基金净值、基准指数、无风险利率、持仓快照
- 时间范围：2022-01-01 ~ 2024-03-31
- 分析方法：CAPM回归、均值-方差优化、蒙特卡洛模拟

## 数据概况
- 基金净值数据：约 540 个交易日
- 数据质量：缺失率 0.X%，已前向填充
- 基准对齐：CSI 300 / 中证综合债

## 详细分析
### 基金绩效评估
- 方法：收益-风险指标计算、CAPM 回归
- 结果：三支基金指标对比表
- 图表：累计收益对比折线图、绩效指标雷达图

### 相关性与分散化
- 方法：相关系数矩阵、协方差分解
- 结果：股债相关性低（ρ=X.XX），分散化效果显著
- 图表：相关性热力图

### 组合优化
- 方法：Markowitz 均值-方差优化、蒙特卡洛模拟
- 结果：最优权重 [股票 XX%, 债券 XX%, 混合 XX%]
- 图表：有效前沿散点图、权重饼图

### 风险诊断
- 方法：历史 VaR (95%, 99%)、CVaR、压力测试
- 结果：99% VaR = -X.X%，极端情景下最大损失 -XX%
- 图表：收益分布直方图 + VaR 标记线

## 风险评估
| 风险项 | 等级 | 描述 | 影响 | 建议 |
|--------|------|------|------|------|
| 收益率非正态分布（偏度=-0.8） | Yellow | VaR 基于正态假设可能低估尾部风险 | 极端损失可能被低估 | 建议使用历史 VaR 或 CVaR |
| 数据窗口仅 2 年 | Yellow | 未能覆盖完整牛熊周期 | 长期风险收益特征可能不准确 | 建议拉长至 3-5 年 |
| 持仓数据非实时 | Blue | 使用季度末快照，期间可能有大额调仓 | 行业集中度分析存在滞后 | 建议获取月度持仓 |

## 业务建议
1. 资产配置：建议调整为 股票 35% / 债券 45% / 混合 20%，Sharpe 提升 XX%
2. 风险控制：设置单基金最大回撤阈值 -15%，触发时自动降仓
3. 再平衡：按季度执行再平衡，偏离目标权重 ±5% 时触发调整
4. 客户沟通：针对保守型客户推荐债券主导组合，进取型客户推荐优化组合

## 附录
- 技术细节：优化算法（SLSQP）、模拟次数（10,000次）
- 代码引用：分析脚本路径
- 原始输出：有效前沿数据、权重矩阵
```

## 关键指标

| 指标名称 | 计算公式 | 目标值 | 说明 |
|----------|----------|--------|------|
| 总收益率 | (NAV_end - NAV_start + div) / NAV_start | 跑赢基准 | 核心绩效指标 |
| 年化收益率 | (1 + total_return)^(365/days) - 1 | ≥ 8% | 标准化收益指标 |
| 年化波动率 | STD(daily_returns) × SQRT(252) | ≤ 20%（股票型） | 风险度量 |
| Sharpe Ratio | (年化收益 - 无风险利率) / 波动率 | ≥ 1.0 | 风险调整后收益 |
| 最大回撤 | MIN((peak - trough) / peak) | ≤ -15% | 极端风险控制 |
| Alpha (α) | CAPM 回归截距项 | > 0 | 主动管理能力 |
| Beta (β) | COVAR(fund, benchmark) / VAR(benchmark) | 接近 1.0 | 市场敏感度 |
| VaR (95%) | 历史法：5% 分位数 | ≤ -2%（日） | 在险价值 |
| CVaR (95%) | E[loss | loss > VaR] | ≤ -3%（日） | 条件在险价值 |
| 信息比率 | Alpha / 跟踪误差 | ≥ 0.5 | 超额收益稳定性 |

## 图表类型建议

| 分析维度 | 图表类型 | 用途 | 配置建议 |
|----------|----------|------|----------|
| 累计收益 | 折线图 (Line Chart) | 对比三支基金与基准累计收益 | x: date, y: cumulative_return, color: fund |
| 绩效对比 | 雷达图 (Radar Chart) | 多维度绩效指标对比 | axes: return, volatility, sharpe, alpha, max_dd |
| 相关性 | 热力图 (Heatmap) | 基金间相关系数矩阵 | x: fund, y: fund, color: correlation |
| 收益分布 | 直方图 + KDE | 各基金日收益率分布 | x: daily_return, bins=50, kde=True |
| 有效前沿 | 散点图 (Scatter Plot) | 蒙特卡洛模拟组合的收益-风险分布 | x: volatility, y: return, color: sharpe |
| 权重分配 | 饼图/环形图 (Donut Chart) | 优化前后权重对比 | labels: fund, values: weight |
| 回撤分析 | 面积图 (Area Chart) | 累计回撤走势 | x: date, y: drawdown |
| VaR 分析 | 直方图 + 垂直线 | 收益分布与 VaR 标记 | x: return, vline: var_threshold |
| 压力测试 | 柱状图 (Bar Chart) | 不同压力情景下的预估损失 | x: scenario, y: loss, color: severity |
| 行业暴露 | 堆叠柱状图 (Stacked Bar) | 各基金的行业配置分布 | x: fund, y: weight, stack: sector |

## Skill Package 沉淀模板

```yaml
skill_name: "portfolio-performance-optimization"
version: "1.0.0"
description: "基金投资组合绩效评估与配置优化流程，适用于资产管理季度复盘"

input_spec:
  data_format: "csv|api|database"
  required_fields: ["fund_code", "nav", "date"]
  optional_fields: ["dividend", "benchmark_close", "risk_free_rate"]
  constraints:
    min_records: 200
    time_granularity: "daily"

data_processing:
  - step: "cleaning"
    rules: ["填充非交易日净值（前向填充）", "计算日收益率 = (nav_t - nav_t-1) / nav_t-1"]
  - step: "transformation"
    rules: ["对齐多基金时间序列", "计算累计收益率", "年化指标转换"]

analysis_logic:
  methods:
    - name: "CAPM回归"
      when: "需要评估基金的主动管理能力（Alpha）和市场风险（Beta）"
      parameters: { benchmark: "market_index", risk_free: "shibor" }
    - name: "均值-方差优化"
      when: "需要计算最优资产配置权重"
      parameters: { method: "SLSQP", constraint: "weights_sum_to_1" }
    - name: "蒙特卡洛模拟"
      when: "需要展示有效前沿和权重空间"
      parameters: { iterations: 10000, risk_free: 0.025 }
    - name: "历史VaR"
      when: "需要评估组合尾部风险"
      parameters: { confidence: 0.95, horizon: "1_day" }

chart_templates:
  - type: "line"
    config: { x: "date", y: "cumulative_return", color: "fund", title: "累计收益对比" }
  - type: "heatmap"
    config: { x: "fund", y: "fund", color: "correlation", title: "相关系数矩阵" }
  - type: "scatter"
    config: { x: "volatility", y: "return", color: "sharpe", title: "有效前沿" }

output_template:
  sections: ["执行摘要", "绩效评估", "相关性分析", "组合优化", "风险诊断", "业务建议"]

review_rules:
  - check: "数据一致性"
    criteria: "各基金交易日数量一致，收益率计算无NaN"
  - check: "sample_size"
    min_n: 200
  - check: "业务合理性"
    criteria: "Sharpe Ratio 应在 -2 到 5 之间，Beta 应在 0.3 到 2.0 之间"

exception_handling:
  - condition: "基准数据缺失"
    action: "使用 CSI 300 作为默认基准，标注风险 Yellow"
  - condition: "优化器不收敛"
    action: "切换为等权分配或风险平价模型，标注风险 Yellow"
  - condition: "数据窗口 < 1年"
    action: "仅输出描述性指标，不做预测性分析，标注风险 Red"
```
