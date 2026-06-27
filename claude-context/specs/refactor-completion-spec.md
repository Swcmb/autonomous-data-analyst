# 项目完成与重构规格文档（v2 - 审查修订版）

## 1. Purpose（目的）

将 autonomous-data-analyst 从"模块骨架完成但无法运行"推进到"端到端可运行、有测试覆盖、代码质量达标"的交付状态，并推送到 GitHub。

## 2. Boundaries（边界）

### 范围内
- 修复 main.py 与所有模块的 API 对接
- 实现 `_execute_single_task` 的真实分析逻辑
- 实现交互模式（interactive）的用户输入循环
- 补充单元测试（pytest）
- 代码重构：消除重复、统一风格、优化结构
- 创建示例数据文件 `examples/sample.csv`
- 推送到 GitHub 仓库

### 范围外
- 不新增分析方法（保持现有 18 种）
- 不引入 Web UI 或 REST API
- 不引入异步框架（保持同步 + ThreadPoolExecutor）
- 不修改 .trae/ 目录下的设计文档

## 3. Technical Approach（技术方案）

### Phase 0: 基线验证（新增）

在任何修改前，验证当前状态并建立基线：
1. 运行 `python main.py "test" --data examples/sample.csv` 记录失败模式
2. 运行 `python -c "from modules import *"` 验证模块可导入
3. 创建 `examples/sample.csv`（20 行 × 5 列：日期、产品、销售额、数量、类别）
4. 提交基线状态（sample.csv + 当前代码快照）

### Phase 1: 修复 API 对接

#### 1a. DataPipeline 新增 `load(detection_result)` 方法

在 `modules/data_pipeline.py` 的 `DataPipeline` 类中新增：

```python
def load(self, detection_result: DetectionResult) -> DataPipeline:
```

**实现逻辑：**
- 提取 `detection_result.primary_source`（类型 `DataSourceInfo`）
- 根据 `primary_source.access_protocol` 分派：
  - `AccessProtocol.LOCAL_FILE`：根据文件扩展名调用 `pd.read_csv/read_excel/read_parquet/read_json`
  - `AccessProtocol.HTTP/HTTPS`：`requests.get()` 下载到临时文件后加载
  - `AccessProtocol.MYSQL/POSTGRESQL/SQLITE`：`sqlalchemy.create_engine` + `pd.read_sql`
  - 其他协议：记录警告，返回空 DataFrame
- 文件不存在时抛出 `FileNotFoundError`
- 加载后调用 `load_data(df)` 设置内部状态
- 返回 self 支持链式调用

#### 1b. DataPipeline 新增 `clean()` 便捷方法

```python
def clean(self, data: Any = None) -> DataPipeline:
```

**实现逻辑：**
- 若传入 data，先调用 `load_data(data)`
- 串联：`handle_missing()` → `deduplicate()` → `_clip_anomalies()`（新增内部方法）
- `_clip_anomalies()`：用 IQR 方法将异常值 clip 到 `[Q1-1.5*IQR, Q3+1.5*IQR]` 范围
- 返回 self

#### 1c. DataPipeline 新增 `transform(data, goal_spec)` 方法

```python
def transform(self, data: Any, goal_spec: Any = None) -> Any:
```

**实现逻辑：**
- 若传入 data，先设置为当前数据
- 根据 `config.normalization_method` 调用 `normalize()`
- 返回处理后的 `self._current_data`

#### 1d. 修复 PipelineConfig 字段不匹配

main.py 第 297-300 行使用了不存在的字段名。修改 main.py：

```python
# 修复前（错误）
config = PipelineConfig(
    auto_detect_types=True,
    handle_missing="interpolate",
    handle_outliers="clip",
)

# 修复后（使用 PipelineConfig 实际字段）
config = PipelineConfig(
    fill_missing_strategy="mean",      # 实际支持：mean/median/mode/forward/drop
    normalization_method=None,
    anomaly_detection_method="iqr",
)
```

#### 1e. 修复 SelfReviewer 调用签名

main.py 第 460-466 行调用了不存在的 `reviewer.review()`。修改为调用 `run_review()`，并提供正确的参数映射：

| main.py 原参数 | → run_review 参数 | 映射逻辑 |
|---|---|---|
| `data` | `data_context` | `{"sample_size": len(data) if hasattr(data, '__len__') else 0, "field_defs": {col: str(dtype) for col, dtype in data.dtypes.items()} if hasattr(data, 'dtypes') else {}}` |
| `results` | `model_context` | `{"metrics": {"success_rate": success_count/total}, "model_type": "multi_agent", "cv_results": None}` |
| `goal_spec` + `results` | `business_context` | `{"findings": _extract_findings(results), "recommendations": [], "goal": goal_spec.objective}` |
| 无 | `review_id` | `f"review_{goal_spec.category.value}"` |

修改后的调用：
```python
reviewer = SelfReviewer()
report = reviewer.run_review(
    review_id=f"review_{goal_spec.category.value}",
    data_context=_build_data_context(data),
    model_context=_build_model_context(results),
    business_context=_build_business_context(goal_spec, results),
)
```

### Phase 2: 实现真实任务执行

#### 2a. 实现 `_dispatch_analysis_method`

**接口契约：**
```python
def _dispatch_analysis_method(method_name: str, data: Any, params: dict) -> dict[str, Any]:
    """
    根据方法名分派到具体分析实现
    
    Args:
        method_name: 方法名称（中文，如 "线性回归"、"K-Means 聚类"）
        data: pandas DataFrame
        params: 方法参数字典
    
    Returns:
        {"summary": str, "metrics": dict, "details": Any}
    """
```

**实现映射表（18 种方法 → 实际调用）：**

| 方法名 | 实际调用 | 返回 metrics |
|---|---|---|
| 线性回归 | `sklearn.linear_model.LinearRegression` | r2, coef, intercept |
| 逻辑回归 | `sklearn.linear_model.LogisticRegression` | accuracy, coef |
| 多项式回归 | `sklearn.preprocessing.PolynomialFeatures` + LinearRegression | r2 |
| K-Means 聚类 | `sklearn.cluster.KMeans` | labels, inertia, centers |
| 层次聚类 | `scipy.cluster.hierarchy.linkage` | labels |
| DBSCAN | `sklearn.cluster.DBSCAN` | labels, n_clusters |
| 决策树 | `sklearn.tree.DecisionTreeClassifier` | accuracy, feature_importance |
| 随机森林 | `sklearn.ensemble.RandomForestClassifier` | accuracy, feature_importance |
| SVM | `sklearn.svm.SVC` | accuracy |
| ARIMA | `statsmodels.tsa.arima.model.ARIMA` | aic, forecast |
| Prophet | 降级：使用 `scipy.stats.linregress` 替代 | `{"summary": "Prophet 不可用，使用线性趋势替代", "metrics": {"slope": ..., "p_value": ...}, "details": linregress_result}` |
| 趋势检测 | `scipy.stats.linregress` | slope, p_value, r_value |
| A/B 测试 | `scipy.stats.ttest_ind` | t_stat, p_value, effect_size |
| 双重差分 | 降级：返回不支持提示 | `{"summary": "双重差分需要面板数据（含时间维度和分组标识）", "metrics": {}, "details": "需确认数据包含 treatment/control 分组列和前后时间标记"}` |
| t 检验 | `scipy.stats.ttest_ind` | t_stat, p_value |
| 卡方检验 | `scipy.stats.chi2_contingency` | chi2, p_value |
| ANOVA | `scipy.stats.f_oneway` | f_stat, p_value |
| 描述性统计 | `pandas.DataFrame.describe()` | summary_stats |

**依赖缺失处理：** import 失败时，通过 `DependencyInstaller` 尝试自动安装；若仍失败，返回 `{"summary": "方法 {name} 的依赖不可用", "metrics": {}, "error": str(exc)}` 而非抛出异常。

#### 2b. 实现交互模式

在 main.py 中为 `RunMode.INTERACTIVE` 添加独立处理路径 `_run_interactive_mode(config)`：

**交互流程：**
1. 初始化日志，打印欢迎信息
2. 若 `config.data_path` 为空，提示用户输入数据路径：
   a. 提示 `请输入数据文件路径：`
   b. 验证路径存在且可读
   c. 若不存在，提示 "文件不存在，请重新输入" 并回到 a
   d. 最多重试 3 次，超出后打印错误并退出（返回码 1）
   e. 路径验证通过后，后续所有迭代复用该路径
3. 循环：
   a. 提示 `请输入分析目标（输入 quit 退出）：`
   b. 读取用户输入，空输入则提示并继续
   c. `quit`/`exit`/`q` 退出循环
   d. 调用 `_run_analysis()` 执行完整流水线
   e. 捕获异常，打印错误信息，继续循环（不因单次失败退出）
   f. 打印结果摘要（报告路径、风险等级、耗时）
4. 打印退出信息

> **注：** main.py 已有 `def main(argv: list[str] | None = None) -> int` 签名（第 105 行），集成测试可直接调用 `main(argv)` 获取退出码，无需 subprocess.run。

### Phase 3: 测试

#### 3a. 测试基础设施

创建 `tests/conftest.py`，包含共享 fixtures：

```python
@pytest.fixture
def sample_df():
    """20 行测试 DataFrame：date, product, revenue, quantity, category"""
    return pd.read_csv("examples/sample.csv")

@pytest.fixture
def sample_goal_spec():
    """标准分析目标规格"""
    return parse_goal("分析电商销售数据的趋势和季节性")

@pytest.fixture
def tmp_skill_dir(tmp_path):
    """临时技能存储目录"""
    return str(tmp_path / "skills")

@pytest.fixture(autouse=True)
def _isolate_working_dir(tmp_path, monkeypatch):
    """自动隔离：每个测试在临时目录中运行，避免污染项目文件"""
    monkeypatch.chdir(tmp_path)
```

#### 3b. 单元测试（按模块）

- `test_goal_parser.py`：5 类目标解析 + 边界（空输入、无关键词）
- `test_data_pipeline.py`：load、clean、transform、链式调用 + 空数据边界
- `test_method_selector.py`：各方法族选择 + 最小样本量
- `test_self_review.py`：四维审查各触发一种 RED 发现
- `test_multi_agent.py`：三种协作模式 + 并行决策
- `test_skill_persistence.py`：提取→保存→加载→回放完整链路
- `test_report_generator.py`：Markdown 输出格式验证
- `test_visualization.py`：图表选择规则覆盖

#### 3c. 集成测试

`test_main_integration.py`：
- 端到端批量模式：`main(["分析销售趋势", "--data", "examples/sample.csv", "--output", str(tmp_path)])` 断言退出码 0 且输出文件存在
- 回放模式：先批量运行产生技能，再回放验证
- 错误路径：无效数据路径 → 退出码 1

### Phase 4: 重构与配置

#### 4a. 创建 pyproject.toml

```toml
[project]
name = "autonomous-data-analyst"
version = "1.0.0"
requires-python = ">=3.10"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

#### 4b. 代码风格统一
- 所有公共方法补齐 Google style docstring
- main.py 辅助函数按职责分组并添加 region 注释

#### 4c. 更新 README.md
- 补充实际可运行的命令示例
- 添加测试运行说明

### Phase 5: GitHub 推送

项目已有本地 git 历史（7 commits）。操作：
1. `gh repo create autonomous-data-analyst --public --source=. --push`（使用 gh CLI 创建远程仓库并推送）
2. 若仓库已存在：`git remote add origin git@github.com:Swcmb/autonomous-data-analyst.git && git push -u origin main`

## 4. Success Criteria（成功标准）

- [ ] `python main.py "分析销售趋势" --data examples/sample.csv` 完整执行不报错
- [ ] `pytest tests/ -v` 全部通过
- [ ] `python main.py --mode interactive` 可正常输入目标并获取结果
- [ ] `python main.py --mode replay --skill-id <id>` 可正常回放
- [ ] GitHub 仓库可访问，代码已推送

## 5. Contingency（应急方案）

- 分析方法实现困难时降级为结构化提示，不阻塞流水线
- 测试编写优先保证 goal_parser、data_pipeline、main 集成
- GitHub 推送失败保留本地 git 历史
