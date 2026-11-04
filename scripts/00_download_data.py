# -*- coding: utf-8 -*-
"""从 Kaggle 官方公开 API 下载 Olist 数据 ZIP 并解压 CSV。

这是数据源提供的直接文件下载，不解析网页、不模拟登录、不使用爬虫。
仅首次运行或原始 CSV 缺失时需要联网。
"""
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
URL = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce"
REQUIRED = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    missing = [name for name in REQUIRED if not (RAW_DIR / name).exists()]
    if not missing:
        print("[数据检查] 原始 CSV 已齐全，跳过下载。")
        return

    print("[数据下载] 正在从 Kaggle 官方公开 API 获取 Olist ZIP……")
    request = Request(URL, headers={"User-Agent": "Olist-course-reproduction/1.0"})
    with urlopen(request, timeout=120) as response:
        payload = response.read()

    with ZipFile(BytesIO(payload)) as archive:
        for name in REQUIRED:
            target = RAW_DIR / name
            if target.exists():
                continue
            with archive.open(name) as source, target.open("wb") as output:
                output.write(source.read())
            print(f"[解压] {name}")

    # 地理编码表不参与本分析，不下载解压，避免增加约 61MB 的本地文件。
    print("[数据下载] 完成。地理编码表为可选项，未纳入下载。")


if __name__ == "__main__":
    main()
