"""
Confluence 页面抓取脚本
将 playwright snapshot 原始内容直接写入 req-{pageId}.md 文件。

用法:
  python fetch_confluence.py --url <confluence_url>
"""
import subprocess
import re
import sys
import argparse
import time
import os


if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def run_cli(cmd: str, timeout: int = 30) -> str:
    result = subprocess.run(
        cmd, shell=True, capture_output=True, timeout=timeout
    )
    raw = result.stdout or b""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("gbk", errors="replace")
    stderr_text = (result.stderr or b"").decode("gbk", errors="replace")
    return text + stderr_text


def main():
    parser = argparse.ArgumentParser(description="抓取 Confluence 页面内容")
    parser.add_argument("--url", required=True, help="Confluence 页面 URL")
    args = parser.parse_args()

    # 1. 提取 pageId
    page_id_match = re.search(r'pageId=(\d+)', args.url)
    page_id = page_id_match.group(1) if page_id_match else "unknown"

    # 2. 从环境变量读取凭证
    username = os.environ.get("CONFLUENCE_USERNAME", "")
    password = os.environ.get("CONFLUENCE_PASSWORD", "")
    if not username or not password:
        print(json.dumps({
            "error": "缺少环境变量 CONFLUENCE_USERNAME 或 CONFLUENCE_PASSWORD",
            "hint": "请设置环境变量后再运行，例如: export CONFLUENCE_USERNAME=xxx CONFLUENCE_PASSWORD=xxx",
        }, ensure_ascii=False))
        sys.exit(1)

    # 3. 打开页面并登录
    run_cli(f'playwright-cli open "{args.url}" --headed')
    run_cli(f'playwright-cli fill "input[name=\'os_username\']" "{username}"', timeout=10)
    run_cli(f'playwright-cli fill "input[name=\'os_password\']" "{password}"', timeout=10)
    run_cli("playwright-cli press Enter", timeout=15)
    time.sleep(3)

    # 4. 获取原始 snapshot
    snapshot = run_cli("playwright-cli snapshot --raw", timeout=30)

    # 5. 写入 req 文件（调用时的当前工作目录）
    project_root = os.getcwd()
    output_path = os.path.join(project_root, f"ori-req-{page_id}.md")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# Confluence Page Snapshot\n\n")
        f.write(f"> URL: {args.url}\n")
        f.write(f"> pageId: {page_id}\n\n")
        f.write("```yaml\n")
        f.write(snapshot)
        f.write("\n```\n")

    # 输出文件路径供 AI 读取
    print(json.dumps({"pageId": page_id, "file": output_path}, ensure_ascii=False))


if __name__ == "__main__":
    import json
    main()
