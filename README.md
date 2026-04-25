# fetch-confluence

Claude Code 插件，用于抓取 Confluence 页面内容并生成结构化需求文档，支持自动登录、快照提取和 brainstorming 分析。

## 依赖

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| Python | >= 3.8 | 运行抓取脚本 |
| Node.js | >= 16 | 运行 playwright-cli |
| `@playwright/cli` | >= 0.1.0 | npm 全局包，浏览器自动化 |
| `playwright` (Python) | >= 1.40 | Python 包，提供浏览器驱动 |

## 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `CONFLUENCE_USERNAME` | 是 | Confluence 登录用户名 |
| `CONFLUENCE_PASSWORD` | 是 | Confluence 登录密码 |

## 安装

### 1. 安装 playwright-cli（npm 全局包）

```bash
npm install -g @playwright/cli
```

### 2. 安装 Playwright 浏览器

```bash
playwright install chromium
```

或者通过 playwright-cli 初始化：

```bash
playwright-cli install
```

### 3. 安装 Python 依赖

```bash
pip install playwright
```

### 4. 设置环境变量

**Windows (PowerShell):**
```powershell
$env:CONFLUENCE_USERNAME = "your_username"
$env:CONFLUENCE_PASSWORD = "your_password"
```

**macOS / Linux:**
```bash
export CONFLUENCE_USERNAME="your_username"
export CONFLUENCE_PASSWORD="your_password"
```

也可以将环境变量写入 `.env` 文件或 shell profile 中持久化。

### 5. 安装插件到 Claude Code

```bash
claude plugin add /path/to/fetch_confluence
```

## 使用

在 Claude Code 中直接对话即可触发：

**基本抓取：**
```
抓取这个页面: https://confluence.example.net/pages/viewpage.action?pageId=12345
```

**带聚焦方向：**
```
抓取这个页面: https://confluence.example.net/pages/viewpage.action?pageId=12345，提取：决策表智能解析和导入
```

## 执行流程

```
用户提供 URL
    │
    ▼
Step 1: 运行 fetch_confluence.py
    │  playwright-cli 自动登录 + 获取页面 snapshot
    │  输出 ori-req-{pageId}.md
    ▼
Step 2: AI 读取快照文件
    │
    ▼
Step 3: 解析 snapshot，生成 req-{pageId}.md
    │  结构化 Markdown 需求文档
    ▼
Step 4: 等待用户确认内容
    │
    ▼
Step 5: 询问开发模式
    ├── 快速开发 → 调用 feature-dev 技能
    └── 深入思考 → 调用 brainstorming 技能
```

## 项目结构

```
fetch_confluence/
├── .claude-plugin/
│   └── plugin.json          # 插件清单
├── skills/
│   └── fetch-confluence/
│       ├── skill.md         # 技能定义（触发条件 + 执行步骤）
│       └── fetch_confluence.py  # 抓取脚本
└── README.md
```

## 注意事项

- 脚本使用 `playwright-cli` 以 headed 模式打开浏览器，需要图形界面环境
- Confluence 页面必须使用表单登录（`os_username` / `os_password`）
- 抓取的是页面 accessibility snapshot，不是 HTML，适合 AI 解析
- 生成的 `ori-req-{pageId}.md` 为原始快照，`req-{pageId}.md` 为 AI 整理后的结构化文档

## License

MIT
