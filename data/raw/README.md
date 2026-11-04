# 原始数据目录

本目录不直接托管原始 CSV。首次执行 `python run_all.py` 时，`scripts/00_download_data.py` 会通过 Kaggle 官方公开 API 下载 Olist 数据 ZIP，并解压分析所需的 8 张 CSV。

数据源页面：https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

该过程是数据源官方文件的直接下载，不解析网页、不模拟登录、不使用爬虫。地理编码表不参与本分析，因此不下载。
