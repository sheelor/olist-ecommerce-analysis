# -*- coding: utf-8 -*-
"""
01_load.py —— 数据加载与结构概览
================================
功能：从 data/raw/ 读取 Olist 巴西电商公开数据集 9 张原始表，
     输出各表规模、字段类型、缺失概览，并生成 schema 说明文档。

数据来源（合规声明详见 docs/数据来源合规声明.md）：
    Kaggle · Olist Brazilian E-Commerce Public Dataset
    https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
    获取方式：Kaggle 官方公开下载（一次性 ZIP 文件，非爬虫）
    License: CC BY-NC-SA 4.0
"""
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# 数据集 9 张表的清单与主外键角色说明
TABLES = {
    "olist_orders_dataset":              "订单主表（主键 order_id）",
    "olist_order_items_dataset":         "订单明细表（外键 order_id / product_id / seller_id）",
    "olist_order_payments_dataset":      "订单支付表（外键 order_id）",
    "olist_order_reviews_dataset":       "订单评价表（外键 order_id）",
    "olist_customers_dataset":           "客户维度表（主键 customer_id）",
    "olist_products_dataset":            "商品维度表（主键 product_id）",
    "olist_sellers_dataset":             "卖家维度表（主键 seller_id）",
    "olist_geolocation_dataset":         "地理编码表（zip_code_prefix 关联）",
    "product_category_name_translation": "品类葡英翻译对照表",
}


def load_raw():
    """读取全部原始 CSV，返回 {表名: DataFrame} 字典。"""
    frames = {}
    for name in TABLES:
        path = os.path.join(RAW_DIR, name + ".csv")
        if not os.path.exists(path):
            # 地理编码表体积较大（约61MB）且本分析未使用，压缩分发时可省略，
            # 重新从 Kaggle 官方下载放回 data/raw/ 即可恢复全量校验
            print(f"[跳过] {name:<42s} 文件不存在（可选表，不影响分析流程）")
            continue
        frames[name] = pd.read_csv(path)
        print(f"[加载] {name:<42s} {frames[name].shape[0]:>8,} 行 × {frames[name].shape[1]} 列")
    return frames


def schema_report(frames):
    """生成各表字段/类型/缺失率概览，写入 docs/schema说明.md。"""
    lines = ["# Olist 数据集 Schema 说明\n",
             "| 数据表 | 角色 | 记录数 | 字段数 |", "| --- | --- | --- | --- |"]
    for name, df in frames.items():
        lines.append(f"| {name} | {TABLES[name]} | {df.shape[0]:,} | {df.shape[1]} |")
    lines.append("\n## 各表字段明细\n")
    for name, df in frames.items():
        lines.append(f"### {name}\n")
        lines.append("| 字段 | 类型 | 非空数 | 缺失率 |")
        lines.append("| --- | --- | --- | --- |")
        for col in df.columns:
            miss = df[col].isna().mean()
            lines.append(f"| {col} | {df[col].dtype} | {df[col].notna().sum():,} | {miss:.2%} |")
        lines.append("")
    out = os.path.join(DOCS_DIR, "schema说明.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[输出] schema 说明 -> {out}")


def main():
    frames = load_raw()
    schema_report(frames)
    # 规模校验：作业要求主表记录数不少于 500 条
    n_orders = frames["olist_orders_dataset"].shape[0]
    assert n_orders >= 500, "主表记录数不足 500 条"
    print(f"[校验] 订单主表 {n_orders:,} 条 >= 500，规模达标；本数据集规模充足，无需抽样、无需 Faker 补充。")


if __name__ == "__main__":
    main()
