# -*- coding: utf-8 -*-
"""run_all.py —— 一键复现入口。

克隆仓库后，在仓库根目录执行：
    pip install -r requirements.txt
    python run_all.py

首次运行会从 Kaggle 官方公开 API 直接下载 Olist 数据 ZIP，随后依次完成：
数据加载校验 → 清洗治理 → 六大商业模型 → 23 张静态图表 → 交互式大屏。
"""
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    "00_download_data.py",
    "01_load.py",
    "02_clean.py",
    "03_analysis_models.py",
    "04_visuals.py",
    "05_dashboard.py",
]


def main():
    for step in STEPS:
        path = os.path.join(BASE_DIR, "scripts", step)
        print(f"\n{'='*60}\n>>> 执行 {step}\n{'='*60}")
        result = subprocess.run([sys.executable, path], cwd=BASE_DIR)
        if result.returncode != 0:
            print(f"[失败] {step} 执行出错，已中断。请检查报错信息。")
            sys.exit(1)
    print(
        "\n[全部完成] 图表见 outputs/figures/，结果表见 outputs/tables/，"
        "大屏见 outputs/fig24_交互式可视化大屏.html（浏览器打开）"
    )


if __name__ == "__main__":
    main()
