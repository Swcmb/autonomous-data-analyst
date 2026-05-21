# Prompts 目录文件命名规范

## 目录结构

```
.trae/
├── prompts/                    # AI Agent 系统提示词目录
│   ├── README.md              # 本文件
│   ├── CHANGELOG.md           # 版本变更日志
│   └── [agent-name]/          # 特定 Agent 的提示词目录
│       └── *.md              # 提示词文件
└── specs/                     # 设计规范目录（供人类设计师使用）
    └── [agent-name]/          # 特定 Agent 的设计规范目录
        └── *.md              # 规范文件
```

## 文件命名约定

### 1. 供人类设计师/开发者使用的文件

此类文件包含 "specification"、"design" 或 "requirements" 关键词：

| 关键词 | 用途说明 | 示例 |
|--------|----------|------|
| `specification` | 完整的规格说明文档 | `skill-design-specification.md` |
| `design` | 设计方案文档 | `agent-architecture-design.md` |
| `requirements` | 需求分析文档 | `functional-requirements.md` |

### 2. 供 AI Agent 使用的文件

此类文件包含 "prompt"、"system" 或 "agent" 关键词：

| 关键词 | 用途说明 | 示例 |
|--------|----------|------|
| `prompt` | AI 提示词文件 | `agent-system-prompt.md` |
| `system` | 系统级提示词 | `analysis-agent-system-prompt.md` |
| `agent` | Agent 专用配置 | `data-analyst-agent-config.md` |

### 3. 通用命名规则

- **命名格式**: 采用 kebab-case（小写字母，连字符分隔）
- **长度限制**: 建议不超过 64 个字符
- **清晰性**: 文件名应能清晰表达文件用途

### 命名示例

```
# 设计规范文件（人类使用）
skill-design-specification.md
agent-requirements.md
system-architecture-design.md

# Agent 提示词文件（AI 使用）
agent-system-prompt.md
data-pipeline-agent-prompt.md
analysis-planner-system-prompt.md
```

## 文件类型区分速查表

| 文件特征 | 目标受众 | 存放位置 |
|----------|----------|----------|
| 包含 "specification" | 人类设计师 | `.trae/specs/` |
| 包含 "design" | 人类开发者 | `.trae/specs/` |
| 包含 "requirements" | 人类产品经理 | `.trae/specs/` |
| 包含 "prompt" | AI Agent | `.trae/prompts/` |
| 包含 "system" | AI Agent | `.trae/prompts/` |
| 包含 "agent" | AI Agent | `.trae/prompts/` |

## 版本控制要求

所有提示词文件应作为正式代码工件进行版本控制：

1. **变更日志**: 每次修改必须更新 CHANGELOG.md
2. **变更描述**: 记录修改原因、内容和影响
3. **版本号**: 使用语义化版本控制（Major.Minor.Patch）
4. **审核追踪**: 重要修改需要审核记录