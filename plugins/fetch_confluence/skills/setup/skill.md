---
name: setup
description: 检测并自动安装 fetch-confluence 插件所需的全部依赖。当用户要求设置环境、检查依赖、首次使用、或运行 /setup 时触发。
---

# Setup: 依赖检测与安装

## 触发条件
用户要求设置环境、检查依赖、首次使用插件、或运行 `/setup`。

## 执行策略

按顺序检测每个依赖。缺失的自动安装，需要人类操作的打印提示并等待确认。

检测完成后打印汇总报告。

---

## Dep 1: Python >= 3.8

**检测：**
```bash
python --version 2>&1 || python3 --version 2>&1
```

**通过条件：** 输出包含 Python 版本 >= 3.8。

**未通过 → 自动安装：**
- Debian/Ubuntu: `sudo apt-get update && sudo apt-get install -y python3 python3-pip`
- macOS: `brew install python@3.11`
- Windows → **需要人类处理**，打印提示：
  > 请安装 Python 3.8+：https://www.python.org/downloads/
  > 安装时勾选 "Add Python to PATH"。

---

## Dep 2: Node.js >= 16

**检测：**
```bash
node --version 2>&1
```

**通过条件：** 输出包含版本 >= 16。

**未通过 → 自动安装：**
- macOS: `brew install node@18`
- Linux: `curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs`
- Windows → **需要人类处理**，打印提示：
  > 请安装 Node.js 16+：https://nodejs.org/

---

## Dep 3: @playwright/cli（npm 全局包）

**检测：**
```bash
npm list -g @playwright/cli 2>&1
```

**通过条件：** 输出包含 `@playwright/cli` 及版本号。

**未通过 → 自动安装：**
```bash
npm install -g @playwright/cli
```

---

## Dep 4: playwright（Python 包 >= 1.40）

**检测：**
```bash
pip show playwright 2>&1 || pip3 show playwright 2>&1
```

**通过条件：** 输出包含 `Version:` 且 >= 1.40。

**未通过 → 自动安装：**
```bash
pip install "playwright>=1.40" || pip3 install "playwright>=1.40"
```

---

## Dep 5: Chromium 浏览器

**检测：**
```bash
where chrome 2>/dev/null; where google-chrome 2>/dev/null; which chromium-browser 2>/dev/null; which google-chrome 2>/dev/null
```

**通过条件：** 找到 chrome/chromium 二进制文件。

**未通过 → 自动安装：**
```bash
playwright install chromium
```

---

## Dep 6: 环境变量（需要人类处理）

**检测：**
```bash
echo "CONFLUENCE_USERNAME=${CONFLUENCE_USERNAME:-<NOT_SET>}" && echo "CONFLUENCE_PASSWORD=${CONFLUENCE_PASSWORD:-<NOT_SET>}"
```

**通过条件：** 两个变量都不是 `<NOT_SET>`。

**未通过 → 不自动执行**，打印以下提示：

> **需要你设置 Confluence 登录凭证：**
>
> Windows (PowerShell，当前会话):
> ```powershell
> $env:CONFLUENCE_USERNAME = "你的用户名"
> $env:CONFLUENCE_PASSWORD = "你的密码"
> ```
>
> Windows (PowerShell，持久化):
> ```powershell
> [Environment]::SetEnvironmentVariable("CONFLUENCE_USERNAME", "你的用户名", "User")
> [Environment]::SetEnvironmentVariable("CONFLUENCE_PASSWORD", "你的密码", "User")
> ```
>
> macOS / Linux (当前会话):
> ```bash
> export CONFLUENCE_USERNAME="你的用户名"
> export CONFLUENCE_PASSWORD="你的密码"
> ```
>
> 也可以在项目根目录创建 `.env` 文件：
> ```
> CONFLUENCE_USERNAME=你的用户名
> CONFLUENCE_PASSWORD=你的密码
> ```
>
> 设置完成后告诉我。

**等待用户确认后再继续。**

---

## 最终汇总

所有检测完成后，打印如下格式的报告：

```
=== 依赖检测报告 ===
Python:           ✓ 3.10.x / ✗ 未安装
Node.js:          ✓ v18.x.x / ✗ 未安装
@playwright/cli:  ✓ x.x.x   / ✗ 未安装
playwright (py):  ✓ 1.xx.x  / ✗ 未安装
Chromium:         ✓ 已安装   / ✗ 未安装
环境变量:          ✓ 已设置   / ✗ 需要人类处理
===================
```

- 全部 ✓ → 告知用户环境就绪，可以使用 `/fetch-confluence` 抓取页面。
- 有 ✗ 且已自动修复 → 告知用户哪些依赖已自动安装，建议重新运行 `/setup` 验证。
- 有 ✗ 且需要人类处理 → 等待用户完成操作后再次运行 `/setup`。
