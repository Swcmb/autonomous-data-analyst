# Changelog

所有重要的提示词文件变更都将记录在此。

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
项目版本遵循 [语义化版本控制](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-05-21

### 新增

- 建立正式的文件管理系统
- 创建 `.trae/prompts/` 目录用于存放 AI Agent 提示词文件
- 创建 `.trae/specs/` 目录用于存放设计规范文档
- 制定文件命名约定规范

### 变更

- 将 `prompt.md`（原根目录）重命名为 `agent-system-prompt.md` 并移动到 `.trae/prompts/autonomous-data-analyst/`
- 将 `.trae/specs/autonomous-data-analyst/prompt.md` 重命名为 `skill-design-specification.md`

### 文档

- 创建 `.trae/prompts/README.md` 文件命名规范文档
- 创建本 CHANGELOG.md 文件用于版本跟踪

### 文件清单

| 文件路径 | 版本 | 说明 |
|----------|------|------|
| `.trae/prompts/autonomous-data-analyst/agent-system-prompt.md` | v1.0.0 | Autonomous Data Analyst Agent 系统提示词 |
| `.trae/specs/autonomous-data-analyst/skill-design-specification.md` | v1.0.0 | Skill 设计规范与需求文档 |

## 版本控制规范

### 版本号格式

```
Major.Minor.Patch
```

- **Major**: 重大变更，可能破坏兼容性
- **Minor**: 新增功能，向后兼容
- **Patch**: 修复问题，向后兼容

### 变更类型

| 标签 | 说明 |
|------|------|
| `新增` | 添加新功能或新文件 |
| `变更` | 修改现有功能或文件 |
| `弃用` | 即将移除的功能 |
| `移除` | 已移除的功能 |
| `修复` | 修复 bug 或问题 |
| `安全` | 安全相关的修复 |
| `文档` | 文档更新 |

### 变更记录要求

每次修改提示词文件时，必须：

1. 更新本 CHANGELOG.md
2. 在文件头部添加版本信息
3. 记录变更原因和影响范围
4. 如有必要，添加审核人信息

### 审核流程

```
修改申请 → 代码审查 → 更新 CHANGELOG → 合并 → 版本发布
```

### 版本归档

每个版本发布时，应创建归档快照：

- 生成版本标签
- 保存完整文件快照
- 更新文件清单

---

*本文件遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/) 格式*