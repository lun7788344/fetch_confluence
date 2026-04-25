---
name: fetch-confluence
description: 抓取 Confluence 页面内容并启动 brainstorming 分析。当用户提供 Confluence URL 并要求抓取、读取、分析 Confluence 页面时触发。全量抓取页面快照，由 AI 读取快照后判断需求范围并进行 brainstorming。
---

# Fetch Confluence & Brainstorm

## 触发条件
用户提供 Confluence URL，要求抓取页面内容。可能附带一个需求标题作为分析聚焦方向。

## 参数
从用户消息中提取：
- **url**（必填）: Confluence 页面地址
- **focus**（可选）: 需求标题关键词，用于指导 AI 的 brainstorming 聚焦方向（不影响抓取范围）

## 执行步骤

### Step 1: 运行抓取脚本

```bash
PYTHONIOENCODING=utf-8 python fetch_confluence.py --url "<url>"
```

- 脚本会将 playwright snapshot 原始内容直接写入项目根目录的 `ori-req-{pageId}.md` 文件
- 脚本输出 JSON: `{"pageId": "xxx", "file": "文件路径"}`

### Step 2: 读取快照文件并告知用户

读取脚本输出的文件路径，用 Read 工具读取 `ori-req-{pageId}.md` 的内容。

告知用户文件已生成，路径为 `req-{pageId}.md`。

### Step 3: 解析快照并生成需求文档

从 playwright snapshot（YAML 格式）中提取所有有效内容，整理为结构化 Markdown 写入项目根目录的 `req-{pageId}.md`。snapshot 中的关键节点类型：
- `paragraph [ref=eXXX]: 文本` — 直接包含文本
- `generic [ref=eXXX]: 文本` — 直接包含文本
- `text: 文本` — 文本节点
- `heading "标题" [level=N]` — 标题
- `table / rowgroup / row / cell` — 表格
- `list / listitem` — 列表

需要跳过的噪音节点（页面导航、菜单等）：
- `link "转至..."`, `link "Spaces"`, `link "People"` 等导航链接
- Page tree 导航结构
- `banner`, `navigation` 等页面框架元素
- footer 内容（Powered by, 联系管理员等）
- `generic [ref=eXXX]` 中重复的用户名+时间戳行

文档结构要求：
- 包含页面标题和来源 URL
- 按页面原始结构整理全部需求内容
- 表格数据以 Markdown 表格形式呈现
- 代码片段以代码块形式呈现
- 图片以 ref 标识列表附在内容末尾

写完文件后告知用户文件路径，等待用户确认内容无误。

### Step 4: 询问用户选择开发模式

用户确认需求文档内容无误后，使用 AskUserQuestion 工具询问用户选择开发模式：

```
AskUserQuestion({
  questions: [{
    question: "需求文档已确认，请选择下一步的工作模式：",
    header: "开发模式",
    options: [
      {
        label: "快速开发",
        description: "直接进入功能开发流程，适合需求明确、需要快速落地的场景。将调用 feature-dev 技能。"
      },
      {
        label: "深入思考",
        description: "先进行头脑风暴分析，充分探索方案和架构设计，适合复杂需求或需要多方案对比的场景。将调用 brainstorming 技能。"
      }
    ],
    multiSelect: false
  }]
})
```

**必须等待用户选择后才能继续下一步。**

### Step 5: 根据用户选择调用对应技能

#### 如果用户选择「快速开发」

使用 Skill 工具调用 `superpowers:feature-dev` 技能（如无此技能则使用 `superpowers:executing-plans`）：

```
Skill("superpowers:feature-dev", args="需求文档：req-{pageId}.md，核心需求：{摘要}，聚焦方向：{focus}")
```

#### 如果用户选择「深入思考」

使用 Skill 工具调用 `superpowers:brainstorming` 技能：

```
Skill("superpowers:brainstorming", args="聚焦方向：{focus}。需求文档：req-{pageId}.md，核心需求：{摘要}")
```

**不要自己进行分析或开发，必须通过 Skill 工具调用对应技能来完成。**

## 示例

**全量抓取:**
> 抓取这个页面: https://confluence.xxx.net/pages/viewpage.action?pageId=12345

执行流程：Step 1 抓取 → Step 2 读取快照 → Step 3 生成 `req-12345.md` → 等用户确认 → Step 4 询问开发模式 → Step 5 调用对应技能

**带聚焦方向 + 快速开发:**
> 抓取这个页面: https://confluence.xxx.net/pages/viewpage.action?pageId=12345，提取：决策表智能解析和导入

执行流程：同上，Step 4 用户选择「快速开发」→ Step 5 调用 `feature-dev`，传入 focus="决策表智能解析和导入"

**带聚焦方向 + 深入思考:**
> 抓取这个页面: https://confluence.xxx.net/pages/viewpage.action?pageId=12345，提取：决策表智能解析和导入

执行流程：同上，Step 4 用户选择「深入思考」→ Step 5 调用 `brainstorming`，传入 focus="决策表智能解析和导入"
