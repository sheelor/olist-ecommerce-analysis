# Olist 数据集 Schema 说明

| 数据表 | 角色 | 记录数 | 字段数 |
| --- | --- | --- | --- |
| olist_orders_dataset | 订单主表（主键 order_id） | 99,441 | 8 |
| olist_order_items_dataset | 订单明细表（外键 order_id / product_id / seller_id） | 112,650 | 7 |
| olist_order_payments_dataset | 订单支付表（外键 order_id） | 103,886 | 5 |
| olist_order_reviews_dataset | 订单评价表（外键 order_id） | 99,224 | 7 |
| olist_customers_dataset | 客户维度表（主键 customer_id） | 99,441 | 5 |
| olist_products_dataset | 商品维度表（主键 product_id） | 32,951 | 9 |
| olist_sellers_dataset | 卖家维度表（主键 seller_id） | 3,095 | 4 |
| olist_geolocation_dataset | 地理编码表（zip_code_prefix 关联） | 1,000,163 | 5 |
| product_category_name_translation | 品类葡英翻译对照表 | 71 | 2 |

## 各表字段明细

### olist_orders_dataset

| 字段 | 类型 | 非空数 | 缺失率 |
| --- | --- | --- | --- |
| order_id | str | 99,441 | 0.00% |
| customer_id | str | 99,441 | 0.00% |
| order_status | str | 99,441 | 0.00% |
| order_purchase_timestamp | str | 99,441 | 0.00% |
| order_approved_at | str | 99,281 | 0.16% |
| order_delivered_carrier_date | str | 97,658 | 1.79% |
| order_delivered_customer_date | str | 96,476 | 2.98% |
| order_estimated_delivery_date | str | 99,441 | 0.00% |

### olist_order_items_dataset

| 字段 | 类型 | 非空数 | 缺失率 |
| --- | --- | --- | --- |
| order_id | str | 112,650 | 0.00% |
| order_item_id | int64 | 112,650 | 0.00% |
| product_id | str | 112,650 | 0.00% |
| seller_id | str | 112,650 | 0.00% |
| shipping_limit_date | str | 112,650 | 0.00% |
| price | float64 | 112,650 | 0.00% |
| freight_value | float64 | 112,650 | 0.00% |

### olist_order_payments_dataset

| 字段 | 类型 | 非空数 | 缺失率 |
| --- | --- | --- | --- |
| order_id | str | 103,886 | 0.00% |
| payment_sequential | int64 | 103,886 | 0.00% |
| payment_type | str | 103,886 | 0.00% |
| payment_installments | int64 | 103,886 | 0.00% |
| payment_value | float64 | 103,886 | 0.00% |

### olist_order_reviews_dataset

| 字段 | 类型 | 非空数 | 缺失率 |
| --- | --- | --- | --- |
| review_id | str | 99,224 | 0.00% |
| order_id | str | 99,224 | 0.00% |
| review_score | int64 | 99,224 | 0.00% |
| review_comment_title | str | 11,568 | 88.34% |
| review_comment_message | str | 40,977 | 58.70% |
| review_creation_date | str | 99,224 | 0.00% |
| review_answer_timestamp | str | 99,224 | 0.00% |

### olist_customers_dataset

| 字段 | 类型 | 非空数 | 缺失率 |
| --- | --- | --- | --- |
| customer_id | str | 99,441 | 0.00% |
| customer_unique_id | str | 99,441 | 0.00% |
| customer_zip_code_prefix | int64 | 99,441 | 0.00% |
| customer_city | str | 99,441 | 0.00% |
| customer_state | str | 99,441 | 0.00% |

### olist_products_dataset

| 字段 | 类型 | 非空数 | 缺失率 |
| --- | --- | --- | --- |
| product_id | str | 32,951 | 0.00% |
| product_category_name | str | 32,341 | 1.85% |
| product_name_lenght | float64 | 32,341 | 1.85% |
| product_description_lenght | float64 | 32,341 | 1.85% |
| product_photos_qty | float64 | 32,341 | 1.85% |
| product_weight_g | float64 | 32,949 | 0.01% |
| product_length_cm | float64 | 32,949 | 0.01% |
| product_height_cm | float64 | 32,949 | 0.01% |
| product_width_cm | float64 | 32,949 | 0.01% |

### olist_sellers_dataset

| 字段 | 类型 | 非空数 | 缺失率 |
| --- | --- | --- | --- |
| seller_id | str | 3,095 | 0.00% |
| seller_zip_code_prefix | int64 | 3,095 | 0.00% |
| seller_city | str | 3,095 | 0.00% |
| seller_state | str | 3,095 | 0.00% |

### olist_geolocation_dataset

| 字段 | 类型 | 非空数 | 缺失率 |
| --- | --- | --- | --- |
| geolocation_zip_code_prefix | int64 | 1,000,163 | 0.00% |
| geolocation_lat | float64 | 1,000,163 | 0.00% |
| geolocation_lng | float64 | 1,000,163 | 0.00% |
| geolocation_city | str | 1,000,163 | 0.00% |
| geolocation_state | str | 1,000,163 | 0.00% |

### product_category_name_translation

| 字段 | 类型 | 非空数 | 缺失率 |
| --- | --- | --- | --- |
| product_category_name | str | 71 | 0.00% |
| product_category_name_english | str | 71 | 0.00% |
