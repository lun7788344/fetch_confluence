---
name: fetch-confluence
description: 抓取 Confluence 页面内容并生成 req-{pageId}.md 需求文档。当用户提供 Confluence URL 并要求抓取、读取、提取、整理、分析 Confluence 页面时触发。必须先落盘结构化需求文档并校验文件存在，再向用户汇报或进入后续开发模式。
---

# Fetch Confluence & Brainstorm

## 触发条件
用户提供 Confluence URL，要求抓取页面内容。可能附带一个需求标题作为分析聚焦方向。

## 不可省略的交付要求

- 必须生成项目根目录下的 `req-{pageId}.md`。这是本 skill 的核心交付物，不是可选步骤。
- 即使用户只要求“提取某几项”“只看第 1/2 点”“简单总结”，也必须先把提取结果写入 `req-{pageId}.md`，然后再给用户简短汇报。
- 不要用聊天正文替代 `req-{pageId}.md`；不要因为用户请求范围较小而跳过写文件。
- 在汇报用户前，必须检查 `req-{pageId}.md` 已存在且内容非空。检查失败时，先补写文件，不要继续后续步骤。
- `req-{pageId}.md` 已写入并通过检查后，必须先让用户确认需求内容是否正确。
- 用户未明确确认前，必须停止在确认步骤；不要询问开发模式，不要调用其他技能，不要开始分析或开发。

## 参数
从用户消息中提取：
- **url**（必填）: Confluence 页面地址
- **focus**（可选）: 需求标题关键词，用于指导 AI 的 brainstorming 聚焦方向（不影响抓取范围）

## 执行步骤

### Step 1: 运行抓取脚本

**必须传入 `--output-dir` 指向用户的当前项目目录**（即 Claude Code 的工作目录，不是 skill 文件所在目录）。用 Bash 工具执行：

```bash
PYTHONIOENCODING=utf-8 python "<skill_dir>/fetch_confluence.py" --url "<url>" --output-dir "<cwd>"
```

其中：
- `<skill_dir>` = 本 skill.md 所在目录的绝对路径
- `<cwd>` = 用户当前项目的根目录（Claude Code 的工作目录）

- 脚本会将 playwright snapshot 原始内容写入 `--output-dir` 指定目录下的 `ori-req-{pageId}.md`
- 脚本输出 JSON: `{"pageId": "xxx", "file": "原始快照路径", "rawFile": "原始快照路径", "reqFile": "需求文档路径"}`。其中 `file` 是兼容旧流程的别名，优先使用 `rawFile`。

### Step 2: 读取原始快照文件

读取脚本输出 JSON 中的 `rawFile` 路径，用 Read 工具读取 `ori-req-{pageId}.md` 的内容。

此时只代表原始快照已生成；不要告知用户 `req-{pageId}.md` 已生成，因为需求文档还没有写入。

### Step 3: 解析快照并生成需求文档

从 playwright snapshot（YAML 格式）中提取有效内容，整理为结构化 Markdown 写入脚本输出 JSON 中的 `reqFile`，即项目根目录的 `req-{pageId}.md`。

如果用户指定了提取范围：
- `req-{pageId}.md` 仍然必须生成
- 文档应聚焦用户指定范围，并在开头写明“提取范围”
- 不要直接在聊天中输出完整提取内容来替代文件

如果用户没有指定提取范围，则按页面原始结构整理全部需求内容。

snapshot 中的关键节点类型：
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

写完文件后必须执行一次文件检查：确认 `req-{pageId}.md` 存在且内容非空。检查通过后进入 Step 4。

如果你发现自己准备回复类似“我已经读取了快照内容，下面是提取结果”，先停止并检查：是否已经写入并校验 `req-{pageId}.md`。没有写入就必须先写文件。

### Step 4: 等待用户确认需求内容

告知用户 `req-{pageId}.md` 已生成，并请用户确认需求内容是否正确。此步骤必须单独停顿等待用户回复。

推荐回复格式：

```
已生成需求文档：req-{pageId}.md
请确认文档内容是否正确；确认后我再继续让你选择下一步开发模式。
```

**必须等待用户明确确认后才能继续 Step 5。**

如果用户要求修改或补充需求文档，先更新 `req-{pageId}.md`，再次检查文件存在且内容非空，然后继续停在 Step 4 让用户确认。

### Step 5: 询问用户选择开发模式

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

### Step 6: 根据用户选择调用对应技能

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

执行流程：Step 1 抓取 → Step 2 读取快照 → Step 3 生成 `req-12345.md` → Step 4 等用户确认需求内容 → Step 5 询问开发模式 → Step 6 调用对应技能

**带聚焦方向 + 快速开发:**
> 抓取这个页面: https://confluence.xxx.net/pages/viewpage.action?pageId=12345，提取：决策表智能解析和导入

执行流程：同上，Step 4 用户确认需求内容 → Step 5 用户选择「快速开发」→ Step 6 调用 `feature-dev`，传入 focus="决策表智能解析和导入"

**带聚焦方向 + 深入思考:**
> 抓取这个页面: https://confluence.xxx.net/pages/viewpage.action?pageId=12345，提取：决策表智能解析和导入

执行流程：同上，Step 4 用户确认需求内容 → Step 5 用户选择「深入思考」→ Step 6 调用 `brainstorming`，传入 focus="决策表智能解析和导入"
