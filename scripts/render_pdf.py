#!/usr/bin/env python3
"""
AI板块投资报告 PDF 渲染脚本

用法:
    python scripts/render_pdf.py <html_path> <output_path>

示例:
    python scripts/render_pdf.py templates/ai-sector-briefing-playwright.html output/AI板块投资报告.pdf
"""

import sys
import os
from pathlib import Path

def html_to_pdf(html_path, output_path):
    """
    使用 Playwright 将 HTML 渲染为 PDF
    
    Args:
        html_path: HTML 文件路径
        output_path: 输出 PDF 路径
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("错误：未安装 Playwright。请运行以下命令安装：")
        print("  pip install playwright --break-system-packages")
        print("  python -m playwright install chromium")
        print("  python -m playwright install-deps chromium")
        sys.exit(1)
    
    # 检查 Playwright 是否能正常启动（验证系统依赖）
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
    except Exception as e:
        error_msg = str(e).lower()
        if "libatk" in error_msg or "shared libraries" in error_msg or "libxcomposite" in error_msg:
            print("错误：Playwright 缺少系统依赖库。让 Playwright 自动检测并安装正确版本：")
            print("  python -m playwright install-deps chromium")
            print("\n如果 install-deps 失败，请尝试（需要 sudo）：")
            print("  python -m playwright install-deps --force")
        else:
            print(f"错误：Playwright 启动失败: {e}")
        sys.exit(1)
    
    # 确保输出目录存在
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 480, 'height': 900})
        
        # 加载 HTML 文件
        html_absolute = Path(html_path).resolve()
        page.goto(f'file://{html_absolute}')
        page.wait_for_load_state('networkidle')
        
        # 生成 PDF
        page.pdf(
            path=output_path,
            format='A4',
            print_background=True,
            margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
        )
        browser.close()
    
    print(f"✓ PDF生成成功: {output_path}")


def main():
    if len(sys.argv) != 3:
        print("用法: python scripts/render_pdf.py <html_path> <output_path>")
        print("示例: python scripts/render_pdf.py templates/ai-sector-briefing-playwright.html output/report.pdf")
        sys.exit(1)
    
    html_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(html_path):
        print(f"错误: HTML 文件不存在: {html_path}")
        sys.exit(1)
    
    html_to_pdf(html_path, output_path)


if __name__ == '__main__':
    main()
