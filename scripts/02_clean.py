# -*- coding: utf-8 -*-
"""
02_clean.py —— 数据清洗与治理
=============================
治理内容：
    1. 重复值：以各表主键去重；
    2. 缺失值：日期字段按订单状态规则处理；评价文本缺失保留（用户未评论属正常业务形态）；
    3. 异常值：价格/运费非正值剔除；IQR 法识别极端值并单独标注（不直接删除，保留业务真实性）；
    4. 类型统一：全部时间字段解析为 datetime，金额保留两位小数；
    5. 多表对齐：orders↔items↔products↔translation↔customers↔payments 按主外键关联，
       只保留可完整对齐的记录，保证逻辑自洽；
    6. 口径说明：销售分析口径取 order_status == 'delivered'（已完成订单），
       取消/不可用订单仅用于漏斗分析；
    7. 导出：清洗后的明细表与聚合表输出为 CSV，并写入 SQLite，便于复用与验证。
"""
import os
import sqlite3
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
os.makedirs(CLEAN_DIR, exist_ok=True)

DATE_COLS_ORDERS = ["order_purchase_timestamp", "order_approved_at",
                    "order_delivered_carrier_date", "order_delivered_customer_date",
                    "order_estimated_delivery_date"]


def load_raw():
    read = lambda n: pd.read_csv(os.path.join(RAW_DIR, n + ".csv"))
    return {
        "orders": read("olist_orders_dataset"),
        "items": read("olist_order_items_dataset"),
        "payments": read("olist_order_payments_dataset"),
        "reviews": read("olist_order_reviews_dataset"),
        "customers": read("olist_customers_dataset"),
        "products": read("olist_products_dataset"),
        "translation": read("product_category_name_translation"),
    }


def clean(d):
    log = []

    # ---------- 1. 类型统一：日期解析 ----------
    orders = d["orders"].copy()
    for c in DATE_COLS_ORDERS:
        orders[c] = pd.to_datetime(orders[c], errors="coerce")
    log.append(f"日期字段统一解析为 datetime：{len(DATE_COLS_ORDERS)} 个字段")

    # ---------- 2. 重复值处理 ----------
    before = len(orders)
    orders = orders.drop_duplicates(subset="order_id")
    customers = d["customers"].drop_duplicates(subset="customer_id")
    products = d["products"].drop_duplicates(subset="product_id")
    items = d["items"].drop_duplicates(subset=["order_id", "order_item_id"])
    payments = d["payments"].drop_duplicates(subset=["order_id", "payment_sequential"])
    log.append(f"主键去重：orders {before}->{len(orders)}（剔除 {before - len(orders)} 条）")

    # ---------- 3. 缺失值处理 ----------
    # 3.1 delivered 状态但缺交付时间：业务上不可能，视为脏数据剔除
    mask_bad = (orders["order_status"] == "delivered") & orders["order_delivered_customer_date"].isna()
    orders = orders[~mask_bad]
    log.append(f"缺失治理：剔除 'delivered 但无交付时间' 的脏数据 {mask_bad.sum()} 条")
    # 3.2 商品维度缺失的品类/规格字段填充为 unknown，保证关联后字段完整
    products["product_category_name"] = products["product_category_name"].fillna("unknown")
    for c in ["product_name_lenght", "product_description_lenght", "product_photos_qty",
              "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"]:
        products[c] = products[c].fillna(products[c].median())
    log.append("缺失治理：商品品类缺失填充 unknown，数值规格缺失填充中位数")

    # ---------- 4. 异常值处理 ----------
    items = items[(items["price"] > 0) & (items["freight_value"] >= 0)]
    # IQR 法标注极端价格（保留记录、仅打标签，避免误删高价耐用品的真实订单）
    q1, q3 = items["price"].quantile([0.25, 0.75])
    iqr = q3 - q1
    upper = q3 + 3 * iqr          # 采用 3 倍 IQR，仅标注极端离群
    items["is_price_outlier"] = items["price"] > upper
    log.append(f"异常值：价格/运费非正值已剔除；价格超 3×IQR 上界（{upper:.0f} 雷亚尔）标注 {items['is_price_outlier'].sum()} 条")

    # ---------- 5. 品类翻译 & 多表主外键对齐 ----------
    trans = dict(zip(d["translation"]["product_category_name"],
                     d["translation"]["product_category_name_english"]))
    products["category_english"] = products["product_category_name"].map(trans).fillna("other")

    payments_agg = (payments.groupby("order_id")
                    .agg(payment_value=("payment_value", "sum"),
                         payment_type=("payment_type", lambda s: s.mode().iat[0]),
                         payment_installments=("payment_installments", "max"))
                    .reset_index())
    reviews_agg = (d["reviews"].groupby("order_id")
                   .agg(review_score=("review_score", "mean")).reset_index())

    master = (items.merge(orders, on="order_id", how="inner")
                   .merge(products[["product_id", "category_english",
                                    "product_weight_g"]], on="product_id", how="inner")
                   .merge(customers[["customer_id", "customer_unique_id",
                                     "customer_city", "customer_state"]],
                          on="customer_id", how="inner")
                   .merge(payments_agg, on="order_id", how="inner")
                   .merge(reviews_agg, on="order_id", how="left"))
    # inner join 后不得存在关键外键缺失
    key_cols = ["order_id", "customer_unique_id", "category_english", "payment_value"]
    assert master[key_cols].notna().all().all(), "多表对齐后仍存在关键字段缺失"
    master["price"] = master["price"].round(2)
    master["freight_value"] = master["freight_value"].round(2)
    log.append(f"多表对齐：items×orders×products×customers×payments 内连接 -> 主表 {len(master):,} 行，关键外键零缺失")

    # ---------- 6. 指标派生 ----------
    master["item_gmv"] = master["price"]                      # 明细级 GMV
    master["purchase_date"] = master["order_purchase_timestamp"].dt.date
    master["purchase_month"] = master["order_purchase_timestamp"].dt.to_period("M").astype(str)
    master["purchase_week"] = master["order_purchase_timestamp"].dt.to_period("W").astype(str)
    master["purchase_hour"] = master["order_purchase_timestamp"].dt.hour
    master["purchase_dow"] = master["order_purchase_timestamp"].dt.day_of_week  # 0=周一
    master["delivery_days"] = (master["order_delivered_customer_date"]
                               - master["order_purchase_timestamp"]).dt.days
    log.append("指标派生：item_gmv / purchase_month / purchase_week / 小时 / 星期 / 配送时长")

    return orders, customers, products, items, payments, master, log


def export(orders, customers, products, items, payments, master, log):
    master.to_csv(os.path.join(CLEAN_DIR, "order_master.csv"), index=False)
    orders.to_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"), index=False)
    customers.to_csv(os.path.join(CLEAN_DIR, "customers_clean.csv"), index=False)
    products.to_csv(os.path.join(CLEAN_DIR, "products_clean.csv"), index=False)

    db = os.path.join(CLEAN_DIR, "olist_clean.db")
    if os.path.exists(db):
        os.remove(db)
    with sqlite3.connect(db) as conn:
        orders.to_sql("orders", conn, index=False)
        master.to_sql("order_master", conn, index=False)
        customers.to_sql("customers", conn, index=False)
        products.to_sql("products", conn, index=False)
    print(f"[导出] CSV ×4 + SQLite -> {CLEAN_DIR}")

    with open(os.path.join(CLEAN_DIR, "清洗日志.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(f"{i+1}. {s}" for i, s in enumerate(log)))
    for s in log:
        print("[清洗]", s)


def main():
    d = load_raw()
    orders, customers, products, items, payments, master, log = clean(d)
    export(orders, customers, products, items, payments, master, log)
    n_delivered = (orders["order_status"] == "delivered").sum()
    print(f"[完成] 清洗后主表 {len(master):,} 行；已交付订单 {n_delivered:,} 张（销售分析口径）")


if __name__ == "__main__":
    main()
