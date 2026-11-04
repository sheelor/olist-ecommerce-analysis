# Olist 巴西电商用户价值与销售趋势可视化分析

> 《商业数据分析》期末大作业 · 从真实数据获取到交互式大屏的端到端商业数据分析

## 一、项目简介

基于 Kaggle 官方公开的 **Olist 巴西电商数据集**（99,441 张订单、约 1,322 万雷亚尔 GMV），使用纯 Python 技术栈完成 **数据合规获取 → 清洗治理 → 六大商业分析模型 → 23 张静态图表 → 交互式可视化大屏** 的全流程分析，回答三个商业问题：

1. 平台销售趋势如何、未来半年怎么走？（环比/同比 + SARIMA 预测）
2. 哪些客户最有价值、如何分层运营？（RFM 八分类 + ABC 帕累托 + 同期群留存）
3. 品类组合与搭配销售有什么机会？（波士顿矩阵 + Apriori 购物篮分析）

本公开仓库只包含代码、数据说明、模型结果、图表和交互大屏，**不包含课程论文 Word/PDF 文件**。

## 二、数据来源

合规声明详见 `docs/数据来源合规声明.md`。

- **名称**：Olist Brazilian E-Commerce Public Dataset
- **URL**：https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- **获取方式**：Kaggle 官方公开 ZIP 文件直接下载，**非网页爬虫**
- **获取日期**：2026-11-03
- **License**：CC BY-NC-SA 4.0
- **规模**：订单主表 99,441 条，满足主表不少于 500 条的要求，无需抽样

为控制仓库体积，原始 CSV、清洗主表和 SQLite 数据库不直接托管。首次运行时，程序会从 Kaggle 官方公开 API 下载原始 ZIP，并自动生成清洗产物。

## 三、目录结构

```text
olist-ecommerce-analysis/
├── .github/workflows/
│   └── generate-assets.yml  # 从官方数据重新生成图表与结果表
├── data/
│   ├── raw/                 # 首次运行自动下载原始 CSV
│   └── clean/               # 运行后生成清洗结果与 SQLite
├── scripts/
│   ├── 00_download_data.py  # Kaggle 官方 ZIP 下载与解压
│   ├── 01_load.py           # 数据加载与 schema 说明
│   ├── 02_clean.py          # 缺失、异常、重复治理与多表对齐
│   ├── 03_analysis_models.py# RFM / 同期群 / BCG / SARIMA / Apriori / ABC
│   ├── 04_visuals.py        # 23 张静态图表，统一 150dpi
│   └── 05_dashboard.py      # 14 组件 Pyecharts 交互大屏
├── outputs/
│   ├── figures/             # fig01–fig23 + fig24 大屏截图
│   ├── tables/              # 9 张模型结果表
│   └── fig24_交互式可视化大屏.html
├── docs/
│   ├── 数据来源合规声明.md
│   ├── schema说明.md
│   └── 图表索引.md
├── requirements.txt
├── run_all.py               # 一键复现入口
└── README.md
```

## 四、一键复现

```bash
pip install -r requirements.txt
python run_all.py
```

`run_all.py` 会依次执行数据下载、加载校验、清洗治理、模型计算、静态可视化和交互大屏生成。首次运行需要联网下载官方数据，其余步骤无需人工干预。

也可以分步执行：

```bash
python scripts/00_download_data.py
python scripts/01_load.py
python scripts/02_clean.py
python scripts/03_analysis_models.py
python scripts/04_visuals.py
python scripts/05_dashboard.py
```

大屏查看：使用 Chrome、Edge 等浏览器打开 `outputs/fig24_交互式可视化大屏.html`。该页面为自包含静态 HTML，不需要启动后端服务。

## 五、商业分析模型

| 模型 | 参数与业务依据 | 核心结论 |
| --- | --- | --- |
| RFM 八分类 | R/M 中位数切分；F 按“是否复购”切分，避免低复购导致中位数退化 | 重要发展与重要挽留客户贡献约 78% GMV |
| 同期群留存 | 首购月分群 × 12 月龄 | 次月平均留存约 5.45%，复购体系是主要短板 |
| 波士顿矩阵 | 2018H1 对 2017H1 同比；相对份额阈值 0.5 | 健康美妆具备规模优势，家居用品和汽车配件有增长潜力 |
| SARIMA 预测 | (1,1,1)(1,0,1,12)；时间外推回测 | MAPE=5.58%，RMSE=7.16 万雷亚尔，输出点预测与 95% 置信区间 |
| Apriori 关联规则 | 780 个多品类订单；support≥2%、confidence≥15% | 家居舒适与床浴桌台、母婴与玩具存在正向强关联 |
| 帕累托 ABC | 累计 GMV 80%/95% 双阈值 | 前 45% 客户贡献约 80% GMV |

## 六、可视化与大屏

- **模板复现类 15 张**（fig01–fig15）：折线、柱线组合、帕累托、环形、堆叠面积、散点、直方、横向条形、玫瑰、漏斗、瀑布、雷达、热力、KPI 卡和箱线图。
- **业务模型图 8 张**（fig16–fig23）：RFM 气泡、RFM 八分类、同期群热力、BCG 四象限、SARIMA 预测、SARIMA 回测、关联规则和 ABC 累计曲线。
- **交互大屏 1 个**（fig24）：包含总标题、数据口径、6 项 KPI、4 个业务分区和 14 个分析组件，支持悬停提示、图例筛选、区域缩放、季度时间轴联动和品类点击下钻。

全部图表由 Matplotlib/Pyecharts 代码生成，未使用 Power BI、Tableau、FineBI 或 Excel 截图替代。详细对应关系见 `docs/图表索引.md`。

## 七、AI 使用披露

本项目在代码调试、图表样式调优、交互事件排查和文字润色环节使用了 AI 助手（Kimi）辅助。全部数据获取、清洗、模型计算与图表生成均由可复现代码完成，AI 输出经过运行验证和人工核对，未使用 AI 伪造数据或替代数据源核验。

交互大屏采用“本地复现—平台预览—手动发布”的交付路径。公开发布需要使用者手动操作；平台预览不等同于已经上线。
