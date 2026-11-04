# -*- coding: utf-8 -*-
"""
04_visuals.py —— Python 数据可视化（全 Python 实现，未使用任何 BI 软件）
=========================================================================
对照《Excel 数据可视化——从图表到数据大屏》典型模板复现 15 种图表
（fig01–fig15），并输出与第 4 章模型一一对应的业务模型图 8 张
（fig16–fig23）。全部图片分辨率 150dpi、中文字体 Noto Sans CJK SC、
统一命名与配色规范，输出至 outputs/figures/。
"""
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch

warnings.filterwarnings("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
FIG_DIR = os.path.join(BASE_DIR, "outputs", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ---------------- 全局风格（贴近教材模板：简洁白底、商务蓝主色、网格弱化） ----------------
C_MAIN = "#2563EB"; C_ACC = "#F59E0B"; C_TEAL = "#06B6D4"; C_RED = "#EF4444"
C_GRAY = "#9CA3AF"; C_GREEN = "#10B981"; C_PURPLE = "#8B5CF6"
PALETTE = [C_MAIN, C_ACC, C_TEAL, C_RED, C_GREEN, C_PURPLE, "#60A5FA", "#FBBF24", "#34D399"]

# 主要品类英文名的中文对照（图表可读性优化，原始字段仍为英文）
CAT_CN = {
    "health_beauty": "健康美妆", "watches_gifts": "腕表礼品", "bed_bath_table": "床浴桌台",
    "sports_leisure": "运动休闲", "computers_accessories": "电脑配件", "furniture_decor": "家具装饰",
    "housewares": "家居用品", "auto": "汽车配件", "cool_stuff": "酷玩好物", "toys": "玩具",
    "baby": "母婴用品", "garden_tools": "园艺工具", "perfumery": "香水香氛", "office_furniture": "办公家具",
    "electronics": "电子产品", "telephony": "电话通讯", "musical_instruments": "乐器",
    "stationery_store": "文具", "pet_shop": "宠物用品", "construction_tools_construction": "建筑工具",
    "home_confort": "家居舒适", "home_comfort_2": "家居舒适2", "unknown": "未知品类", "other": "其他",
}


def cn(x):
    """品类名英译中，未收录的保留原名"""
    return CAT_CN.get(x, x)


def apply_style():
    # 显式注册 Noto CJK 字体（.ttc 合集在部分环境下不会被 matplotlib 自动发现）
    for fp in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
               "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
        if os.path.exists(fp):
            try:
                fm.fontManager.addfont(fp)
            except Exception:
                pass
    plt.rcParams.update({
        "font.sans-serif": ["Noto Sans CJK JP", "Noto Sans CJK SC", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.dpi": 150, "savefig.dpi": 150,
        "axes.edgecolor": "#D1D5DB", "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlesize": 14, "axes.titleweight": "bold",
        "axes.labelsize": 11, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
        "legend.fontsize": 9.5, "figure.facecolor": "white",
        "axes.grid": True, "grid.color": "#E5E7EB", "grid.linewidth": 0.7,
    })


def save(fig, name):
    fig.savefig(os.path.join(FIG_DIR, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[图表] {name}")


def load_all():
    m = pd.read_csv(os.path.join(CLEAN_DIR, "order_master.csv"),
                    parse_dates=["order_purchase_timestamp"])
    orders = pd.read_csv(os.path.join(CLEAN_DIR, "orders_clean.csv"),
                         parse_dates=["order_purchase_timestamp", "order_approved_at",
                                      "order_delivered_carrier_date", "order_delivered_customer_date"])
    d = m[m["order_status"] == "delivered"].copy()
    t = {f[:-4]: pd.read_csv(os.path.join(TABLES_DIR, f))
         for f in os.listdir(TABLES_DIR) if f.endswith(".csv")}
    return d, orders, t


# ============ 模板复现类（fig01–fig15） ============
def fig01_line(d):
    """模板1·折线趋势图：月度 GMV 与 3 期移动平均"""
    s = d[d["purchase_month"] >= "2017-01"].groupby("purchase_month")["item_gmv"].sum() / 1e4
    ma = s.rolling(3).mean()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(s.index, s.values, marker="o", ms=5, lw=2, color=C_MAIN, label="月度 GMV")
    ax.plot(ma.index, ma.values, lw=2, ls="--", color=C_ACC, label="3 期移动平均")
    ax.fill_between(s.index, s.values, alpha=0.10, color=C_MAIN)
    # 标注黑五峰值与高速扩张段
    pk = s.idxmax()
    ax.annotate(f"黑五大促峰值\n{pk}：{s.max():.1f} 万雷亚尔",
                xy=(list(s.index).index(pk), s.max()),
                xytext=(list(s.index).index(pk) - 5.2, s.max() * 0.97),
                fontsize=9.5, color=C_RED,
                arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.2))
    ax.axvspan("2017-01", "2018-05", alpha=0.04, color=C_GREEN)
    ax.text("2018-05", s.max() * 1.02, "2018H1 同比 +181.6%", color=C_GREEN,
            fontsize=9.5, ha="right", fontweight="bold")
    ax.set_title("图1 月度 GMV 趋势与移动平均（2017.01–2018.08）")
    ax.set_xlabel("月份"); ax.set_ylabel("GMV（万雷亚尔）")
    ax.grid(axis="y", alpha=0.3); ax.legend(loc="upper left", frameon=False)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    save(fig, "fig01_月度GMV趋势折线图.png")


def fig02_bar_line(d):
    """模板2·柱线组合图：月度 GMV 与环比增速"""
    s = d[d["purchase_month"] >= "2017-01"].groupby("purchase_month")["item_gmv"].sum() / 1e4
    mom = s.pct_change() * 100
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(s.index, s.values, color=C_MAIN, alpha=0.85, width=0.62, label="GMV")
    ax.set_ylabel("GMV（万雷亚尔）")
    ax2 = ax.twinx()
    ax2.plot(mom.index, mom.values, color=C_RED, marker="s", ms=4.5, lw=1.8, label="环比增速")
    ax2.axhline(0, color=C_GRAY, lw=0.8, ls=":")
    ax2.set_ylabel("环比增速（%）")
    ax.set_title("图2 月度 GMV 与环比增速组合图")
    ax.set_xlabel("月份")
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)
    ax.grid(axis="y", alpha=0.3)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    save(fig, "fig02_GMV环比柱线组合图.png")


def fig03_pareto(d):
    """模板3·帕累托图：品类 GMV 集中度"""
    s = d.groupby("category_english")["item_gmv"].sum().sort_values(ascending=False).head(15) / 1e4
    cum = s.cumsum() / s.sum() * 100
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.bar(range(len(s)), s.values, color=C_MAIN, alpha=0.9)
    ax.set_xticks(range(len(s)))
    ax.set_xticklabels([cn(c) for c in s.index], rotation=40, ha="right")
    ax.set_ylabel("GMV（万雷亚尔）")
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.plot(range(len(s)), cum.values, color=C_ACC, marker="o", ms=4.5, lw=2)
    ax2.axhline(80, color=C_RED, ls="--", lw=1.2)
    # 标注累计占比与 80% 分界
    for i in [0, 2, 4, 7, 14]:
        ax2.annotate(f"{cum.iloc[i]:.0f}%", (i, cum.iloc[i]), xytext=(0, 8),
                     textcoords="offset points", ha="center", fontsize=9, color=C_ACC, fontweight="bold")
    n80 = int((cum < 80).sum()) + 1
    ax2.annotate(f"前 {n80} 个品类即覆盖 80% GMV", xy=(n80 - 1, 80), xytext=(n80 + 1, 55),
                 fontsize=10, color=C_RED, arrowprops=dict(arrowstyle="->", color=C_RED))
    ax2.set_ylabel("累计占比（%）"); ax2.set_ylim(0, 108)
    ax.set_title("图3 品类 GMV 帕累托图（Top15）")
    ax.grid(axis="y", alpha=0.6)
    save(fig, "fig03_品类GMV帕累托图.png")


def fig04_donut(d):
    """模板4·环形占比图：Top8 品类 GMV 结构"""
    s = d.groupby("category_english")["item_gmv"].sum().sort_values(ascending=False)
    top = s.head(8); other = pd.Series({"其他品类": s.iloc[8:].sum()})
    s = pd.concat([top, other]) / 1e4
    fig, ax = plt.subplots(figsize=(7.5, 6))
    w, _, at = ax.pie(s.values, labels=[cn(c) for c in s.index], autopct="%.1f%%", pctdistance=0.78,
                      colors=PALETTE + [C_GRAY], startangle=90,
                      wedgeprops=dict(width=0.42, edgecolor="white"),
                      textprops={"fontsize": 9})
    for t_ in at:
        t_.set_fontsize(8.5)
    ax.text(0, 0, "GMV\n品类结构", ha="center", va="center", fontsize=13, fontweight="bold")
    ax.set_title("图4 Top8 品类 GMV 环形占比图")
    save(fig, "fig04_TOP品类占比环形图.png")


def fig05_stacked_area(d):
    """模板5·堆叠面积图：Top5 品类月度结构变化"""
    top5 = d.groupby("category_english")["item_gmv"].sum().nlargest(5).index
    x = d[d["category_english"].isin(top5) & (d["purchase_month"] >= "2017-01")]
    pv = x.pivot_table(index="purchase_month", columns="category_english",
                       values="item_gmv", aggfunc="sum").fillna(0) / 1e4
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.stackplot(range(len(pv)), [pv[c] for c in pv.columns], labels=[cn(c) for c in pv.columns],
                 colors=PALETTE[:5], alpha=0.85)
    ax.set_xticks(range(len(pv)))
    ax.set_xticklabels(pv.index, rotation=45, ha="right")
    ax.set_title("图5 Top5 品类月度 GMV 堆叠面积图")
    ax.set_xlabel("月份"); ax.set_ylabel("GMV（万雷亚尔）")
    ax.legend(loc="upper left", frameon=False, ncol=2)
    ax.grid(axis="y", alpha=0.3)
    save(fig, "fig05_品类结构堆叠面积图.png")


def fig06_scatter(d):
    """模板6·散点关系图：商品价格与运费（随机抽样 5000，随机种子 42）"""
    s = d.sample(5000, random_state=42)
    fig, ax = plt.subplots(figsize=(8, 5.2))
    sc = ax.scatter(s["price"], s["freight_value"], s=8, alpha=0.35,
                    c=s["delivery_days"], cmap="viridis")
    cb = fig.colorbar(sc, ax=ax); cb.set_label("配送时长（天）")
    r = s[["price", "freight_value"]].corr().iloc[0, 1]
    ax.set_title(f"图6 商品价格与运费散点图（相关系数 r={r:.2f}，抽样 n=5000, seed=42）")
    ax.set_xlabel("商品价格（雷亚尔）"); ax.set_ylabel("运费（雷亚尔）")
    ax.set_xlim(0, s["price"].quantile(0.99)); ax.set_ylim(0, s["freight_value"].quantile(0.99))
    ax.grid(alpha=0.25)
    save(fig, "fig06_价格与运费散点图.png")


def fig07_hist(d):
    """模板7·直方分布图：订单支付金额分布"""
    pay = d.groupby("order_id")["payment_value"].first()
    cap = pay.quantile(0.99)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.hist(pay[pay <= cap], bins=60, color=C_TEAL, alpha=0.85, edgecolor="white")
    ax.axvline(pay.median(), color=C_RED, ls="--", lw=1.5,
               label=f"中位数 = {pay.median():.0f} 雷亚尔")
    ax.set_title("图7 订单支付金额分布直方图（99 分位截尾）")
    ax.set_xlabel("订单金额（雷亚尔）"); ax.set_ylabel("订单数")
    ax.legend(frameon=False); ax.grid(axis="y", alpha=0.3)
    save(fig, "fig07_订单金额分布直方图.png")


def fig08_hbar(d):
    """模板8·横向条形图：Top15 州 GMV 排行"""
    s = (d.drop_duplicates("order_id")
         .groupby("customer_state")["item_gmv"].sum().nlargest(15).sort_values() / 1e4)
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    bars = ax.barh(s.index, s.values, color=C_MAIN, alpha=0.88, height=0.62)
    bars[-1].set_color(C_ACC)
    for b, v in zip(bars, s.values):
        ax.text(v + s.max() * 0.01, b.get_y() + b.get_height() / 2,
                f"{v:,.0f}", va="center", fontsize=8.5)
    ax.set_title("图8 Top15 州 GMV 横向条形图（圣保罗州居首，橙色高亮）")
    ax.set_xlabel("GMV（万雷亚尔）"); ax.set_ylabel("州")
    ax.grid(axis="x", alpha=0.3)
    save(fig, "fig08_TOP州GMV横向条形图.png")


def fig09_rose(d):
    """模板9·玫瑰图（极坐标）：订单评分分布"""
    s = d.drop_duplicates("order_id")["review_score"].dropna()
    cnt = s.round().value_counts().reindex([1, 2, 3, 4, 5]).fillna(0)
    theta = np.linspace(0, 2 * np.pi, 5, endpoint=False)
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, polar=True)
    ax.bar(theta, cnt.values, width=2 * np.pi / 5 * 0.85,
           color=[C_RED, C_ACC, C_GRAY, C_TEAL, C_MAIN], alpha=0.88, edgecolor="white")
    ax.set_xticks(theta)
    ax.set_xticklabels([f"{i} 星\n({v / cnt.sum() * 100:.1f}%)" for i, v in cnt.items()])
    ax.set_yticklabels([])
    ax.set_title("图9 订单评分分布玫瑰图", pad=18)
    save(fig, "fig09_评分分布玫瑰图.png")


def fig10_funnel(orders):
    """模板10·漏斗图：订单履约状态转化"""
    stages = ["全部下单", "支付批准", "卖家发货", "买家签收"]
    vals = [len(orders),
            orders["order_approved_at"].notna().sum(),
            orders["order_delivered_carrier_date"].notna().sum(),
            orders["order_delivered_customer_date"].notna().sum()]
    rates = [v / vals[0] * 100 for v in vals]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    max_v = vals[0]
    for i, (st, v, r) in enumerate(zip(stages, vals, rates)):
        w = v / max_v
        left = (1 - w) / 2
        ax.barh(-i, w, left=left, height=0.72, color=PALETTE[i], alpha=0.9)
        ax.text(0.5, -i, f"{st}  {v:,}（{r:.1f}%）", ha="center", va="center",
                fontsize=11, color="white", fontweight="bold")
    ax.set_xlim(0, 1); ax.set_ylim(-3.6, 0.6); ax.axis("off")
    ax.set_title("图10 订单履约转化漏斗图")
    save(fig, "fig10_订单履约转化漏斗图.png")


def fig11_waterfall(d):
    """模板11·瀑布图：2018H1 GMV 品类贡献构成"""
    x = d[(d["purchase_month"] >= "2018-01") & (d["purchase_month"] <= "2018-06")]
    s = x.groupby("category_english")["item_gmv"].sum().nlargest(5) / 1e4
    other = x[~x["category_english"].isin(s.index)]["item_gmv"].sum() / 1e4
    labels = list(s.index) + ["其他品类", "总计"]
    vals = list(s.values) + [other]
    fig, ax = plt.subplots(figsize=(9.5, 5))
    cum = 0
    for i, v in enumerate(vals):
        ax.bar(i, v, bottom=cum, color=PALETTE[i % len(PALETTE)], alpha=0.88, width=0.6)
        ax.text(i, cum + v + 3, f"{v:,.0f}", ha="center", fontsize=9)
        cum += v
    ax.bar(len(vals), cum, color=C_MAIN, alpha=0.95, width=0.6)
    ax.text(len(vals), cum + 3, f"{cum:,.0f}", ha="center", fontsize=9.5, fontweight="bold")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([cn(c) for c in labels], rotation=20, ha="right")
    ax.set_title("图11 2018H1 GMV 品类贡献瀑布图")
    ax.set_ylabel("GMV（万雷亚尔）"); ax.grid(axis="y", alpha=0.3)
    save(fig, "fig11_GMV构成瀑布图.png")


def fig12_radar(d):
    """模板12·雷达图：Top5 品类多维指标画像"""
    top5 = d.groupby("category_english")["item_gmv"].sum().nlargest(5).index
    x = d[d["category_english"].isin(top5)].copy()
    x["ym"] = np.where(x["purchase_month"] < "2018-01", "y17", "y18")
    rows = {}
    for c in top5:
        sub = x[x["category_english"] == c]
        pv = sub.pivot_table(index="ym", values="item_gmv", aggfunc="sum")
        rows[c] = [
            sub["item_gmv"].sum(),                       # GMV 规模
            sub.groupby("order_id")["price"].sum().mean(),  # 平均客单价
            sub["review_score"].mean(),                  # 平均评分
            (sub["delivery_days"] <= 20).mean() * 100,   # 20 天内送达率
            (pv.loc["y18", "item_gmv"] / max(pv.loc["y17", "item_gmv"], 1)) * 100,  # 18/17 扩张指数
        ]
    df = pd.DataFrame(rows, index=["GMV规模", "客单价", "平均评分", "及时送达率", "扩张指数"])
    df = df / df.max(axis=1).values[:, None] * 100     # 归一化到 0–100
    angles = np.linspace(0, 2 * np.pi, 5, endpoint=False).tolist()
    angles += angles[:1]
    fig = plt.figure(figsize=(7.5, 6.5))
    ax = fig.add_subplot(111, polar=True)
    for i, c in enumerate(top5):
        v = df[c].tolist(); v += v[:1]
        ax.plot(angles, v, lw=2, color=PALETTE[i], label=cn(c))
        ax.fill(angles, v, alpha=0.08, color=PALETTE[i])
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(df.index)
    ax.set_title("图12 Top5 品类多维指标雷达图（归一化）", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), frameon=False)
    save(fig, "fig12_品类多维指标雷达图.png")


def fig13_heatmap(d):
    """模板13·热力图：星期 × 时段下单热度"""
    pv = d.drop_duplicates("order_id").pivot_table(
        index="purchase_dow", columns="purchase_hour",
        values="order_id", aggfunc="count").fillna(0)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    im = ax.imshow(pv.values, aspect="auto", cmap="YlGnBu")
    ax.set_xticks(range(pv.shape[1])); ax.set_xticklabels([f"{h}时" for h in pv.columns], fontsize=8)
    ax.set_yticks(range(7)); ax.set_yticklabels(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
    fig.colorbar(im, ax=ax, label="订单数")
    ax.set_title("图13 星期 × 时段下单热度图")
    save(fig, "fig13_下单时段星期热力图.png")


def fig14_kpi(d, orders):
    """模板14·KPI 仪表卡：核心经营指标一屏总览"""
    od = d.drop_duplicates("order_id")
    cards = [
        ("总 GMV", f"R$ {d['item_gmv'].sum() / 1e6:,.2f}M", C_MAIN),
        ("成交订单", f"{od['order_id'].nunique():,}", C_TEAL),
        ("客单价", f"R$ {od.groupby('order_id')['payment_value'].first().mean():,.0f}", C_ACC),
        ("独立客户", f"{d['customer_unique_id'].nunique():,}", C_PURPLE),
        ("好评率(≥4星)", f"{(od['review_score'] >= 4).mean() * 100:.1f}%", C_GREEN),
        ("平均配送时长", f"{od['delivery_days'].mean():.1f} 天", C_RED),
        ("复购客户占比", f"{(od.groupby('customer_unique_id')['order_id'].nunique() > 1).mean() * 100:.1f}%", C_GRAY),
        ("在售品类", f"{d['category_english'].nunique()}", "#4E8CC9"),
    ]
    fig, axes = plt.subplots(2, 4, figsize=(12, 5.2))
    for ax, (name, val, color) in zip(axes.flat, cards):
        ax.axis("off")
        box = FancyBboxPatch((0.03, 0.08), 0.94, 0.84, boxstyle="round,pad=0.02",
                             fc=color, ec="none", alpha=0.92,
                             transform=ax.transAxes)
        ax.add_patch(box)
        ax.text(0.5, 0.62, name, ha="center", va="center", fontsize=12.5,
                color="white", transform=ax.transAxes)
        ax.text(0.5, 0.32, val, ha="center", va="center", fontsize=15.5,
                color="white", fontweight="bold", transform=ax.transAxes)
    fig.suptitle("图14 核心经营 KPI 仪表卡（Olist 2016.09–2018.08）",
                 fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    save(fig, "fig14_核心KPI仪表卡.png")


def fig15_box(d):
    """模板15·箱线图：Top8 品类价格分布"""
    top8 = d.groupby("category_english")["item_gmv"].sum().nlargest(8).index
    data = [d[d["category_english"] == c]["price"].clip(upper=1500) for c in top8]
    fig, ax = plt.subplots(figsize=(9.5, 5))
    bp = ax.boxplot(data, vert=False, patch_artist=True, showfliers=False,
                    medianprops=dict(color=C_RED, lw=1.8))
    for patch, c in zip(bp["boxes"], PALETTE):
        patch.set_facecolor(c); patch.set_alpha(0.75)
    ax.set_yticklabels([cn(c) for c in top8], fontsize=10)
    ax.set_title("图15 Top8 品类价格分布箱线图（1500 雷亚尔截尾，隐藏离群点）")
    ax.set_xlabel("商品价格（雷亚尔）"); ax.grid(axis="x", alpha=0.3)
    save(fig, "fig15_TOP品类价格箱线图.png")


# ============ 业务模型图（fig16–fig23，与第 4 章模型一一对应） ============
def fig16_rfm_bubble(t):
    """模型图1·RFM 气泡散点：R × F，气泡=M，颜色=分层（抽样 8000, seed=42）"""
    rfm = t["rfm_客户明细"].sample(min(8000, len(t["rfm_客户明细"])), random_state=42)
    segs = sorted(rfm["客户分层"].unique())
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    for i, sg in enumerate(segs):
        s = rfm[rfm["客户分层"] == sg]
        x = s["F_购买次数"] + np.random.RandomState(42).uniform(-0.28, 0.28, len(s))
        ax.scatter(x, s["R_最近购买距今天数"],
                   s=np.clip(s["M_累计消费金额"] / 6, 8, 300),
                   alpha=0.4, color=PALETTE[i % len(PALETTE)], label=sg, edgecolors="none")
    # R 中位数切分参考线
    ax.axhline(219, color=C_RED, ls="--", lw=1.2, alpha=0.8)
    ax.text(5.35, 232, "R 中位数 = 219 天（切分线）", color=C_RED, fontsize=9, ha="right")
    ax.annotate("单次购买客户密集区（F=1）\n复购转化是最大短板", xy=(1, 480), xytext=(2.6, 560),
                fontsize=10, color="#374151",
                arrowprops=dict(arrowstyle="->", color="#374151", lw=1))
    ax.set_xlim(0.4, 5.6)
    ax.set_xlabel("F 购买次数（抖动显示）"); ax.set_ylabel("R 最近购买距快照日天数")
    ax.set_title("图16 RFM 客户价值气泡散点图（气泡大小 = 累计消费金额 M）")
    ax.legend(frameon=False, ncol=2, fontsize=8.5, loc="upper right")
    ax.grid(alpha=0.25)
    save(fig, "fig16_RFM气泡散点图.png")


def fig17_rfm_seg(t):
    """模型图2·RFM 八分类结构：客户数柱 + GMV 占比线"""
    seg = t["rfm_八分类汇总"].sort_values("客户数", ascending=False)
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.bar(seg["客户分层"], seg["客户数"], color=C_MAIN, alpha=0.88, width=0.6, label="客户数")
    ax.set_ylabel("客户数")
    for i, v in enumerate(seg["客户数"]):
        ax.text(i, v + seg["客户数"].max() * 0.01, f"{v:,}", ha="center", fontsize=8.5)
    ax2 = ax.twinx()
    ax2.plot(seg["客户分层"], seg["GMV占比"], color=C_ACC, marker="D", ms=6, lw=2, label="GMV 占比")
    for i, v in enumerate(seg["GMV占比"]):
        ax2.annotate(f"{v:.1f}%", (i, v), xytext=(0, 9), textcoords="offset points",
                     ha="center", fontsize=9, color=C_ACC, fontweight="bold")
    ax2.set_ylabel("GMV 占比（%）"); ax2.set_ylim(0, seg["GMV占比"].max() * 1.25)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right", frameon=False)
    ax.set_title("图17 RFM 八分类客户结构与 GMV 贡献")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    ax.grid(axis="y", alpha=0.3)
    save(fig, "fig17_RFM八分类客户结构图.png")


def fig18_cohort(t):
    """模型图3·同期群留存热力图"""
    pv = pd.read_csv(os.path.join(TABLES_DIR, "cohort_留存率矩阵.csv"), index_col=0) * 100
    fig, ax = plt.subplots(figsize=(10, 6.5))
    mask0 = pv.copy()
    im = ax.imshow(mask0.values, aspect="auto", cmap="Blues", vmin=0, vmax=12)
    ax.set_xticks(range(pv.shape[1])); ax.set_xticklabels([f"M+{c}" for c in pv.columns], fontsize=8.5)
    ax.set_yticks(range(pv.shape[0])); ax.set_yticklabels(pv.index, fontsize=8)
    for i in range(pv.shape[0]):
        for j in range(pv.shape[1]):
            v = pv.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.1f}" if v < 99.5 else "100", ha="center", va="center",
                        fontsize=6.8, color="white" if v > 6 else "#333333")
    fig.colorbar(im, ax=ax, label="留存率（%）")
    ax.set_title("图18 同期群月度留存热力图（首购月 × 月龄，%）")
    ax.set_xlabel("月龄"); ax.set_ylabel("首购同期群")
    save(fig, "fig18_同期群留存热力图.png")


def fig19_bcg(t):
    """模型图4·波士顿矩阵：相对份额 × 同比增速四象限气泡"""
    bcg = pd.read_csv(os.path.join(TABLES_DIR, "bcg_品类矩阵.csv"), index_col=0)
    x_thr, y_thr = 0.5, bcg["同比增速"].median()
    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.scatter(bcg["相对市场份额"], bcg["同比增速"] * 100,
               s=bcg["GMV_2018H1"] / 2500, alpha=0.5, color=C_MAIN, edgecolors="white")
    # 手工错峰排布标签，避免重叠
    offsets = {"construction_tools_construction": (0, 8), "electronics": (0, 8),
               "musical_instruments": (0, -14), "stationery_store": (34, 2),
               "telephony": (10, 10), "pet_shop": (-8, 10), "office_furniture": (0, -15),
               "perfumery": (-14, 8), "garden_tools": (12, 8), "toys": (0, -14),
               "cool_stuff": (0, -15), "baby": (0, 10), "auto": (0, 10),
               "housewares": (0, 10), "furniture_decor": (0, -16),
               "computers_accessories": (0, 10), "sports_leisure": (12, -16),
               "bed_bath_table": (24, -16), "watches_gifts": (0, 10), "health_beauty": (0, 10)}
    for name, r in bcg.iterrows():
        ax.annotate(cn(name), (r["相对市场份额"], r["同比增速"] * 100),
                    fontsize=9, ha="center", va="bottom",
                    xytext=offsets.get(name, (0, 6)), textcoords="offset points")
    # 现金牛与潜力品类强调
    for star, col in [("health_beauty", C_GREEN), ("housewares", C_ACC), ("auto", C_ACC)]:
        if star in bcg.index:
            r = bcg.loc[star]
            ax.scatter([r["相对市场份额"]], [r["同比增速"] * 100],
                       s=r["GMV_2018H1"] / 2500, alpha=0.65, color=col, edgecolors="white")
    ax.axvline(x_thr, color=C_GRAY, ls="--", lw=1.2)
    ax.axhline(y_thr * 100, color=C_GRAY, ls="--", lw=1.2)
    kw = dict(fontsize=11, fontweight="bold", alpha=0.65)
    ax.text(0.97, 0.97, "明星 ★", transform=ax.transAxes, ha="right", va="top", color=C_GREEN, **kw)
    ax.text(0.03, 0.97, "问题 ?", transform=ax.transAxes, ha="left", va="top", color=C_ACC, **kw)
    ax.text(0.97, 0.03, "现金牛 ￥", transform=ax.transAxes, ha="right", va="bottom", color=C_MAIN, **kw)
    ax.text(0.03, 0.03, "瘦狗 ✕", transform=ax.transAxes, ha="left", va="bottom", color=C_RED, **kw)
    ax.set_xlabel("相对市场份额（品类份额 / 最大品类份额）")
    ax.set_ylabel("同比增速（%，2018H1 vs 2017H1）")
    ax.set_title("图19 品类波士顿矩阵四象限图（气泡 = 2018H1 GMV）")
    ax.grid(alpha=0.25)
    save(fig, "fig19_波士顿矩阵四象限图.png")


def fig20_sarima_fc(t):
    """模型图5·SARIMA 点预测 + 95% 置信区间"""
    hist = t["月度GMV序列"]; fc = t["sarima_预测"]
    hx = pd.to_datetime(hist["月份"]); fx = pd.to_datetime(fc["月份"])
    fig, ax = plt.subplots(figsize=(9.5, 5))
    ax.plot(hx, hist["GMV"] / 1e4, marker="o", ms=4, color=C_MAIN, lw=1.8, label="历史 GMV")
    ax.plot(fx, fc["点预测GMV"] / 1e4, marker="s", ms=5, color=C_RED, lw=2, ls="--", label="SARIMA 点预测")
    ax.fill_between(fx, fc["95%置信下界"] / 1e4, fc["95%置信上界"] / 1e4,
                    color=C_RED, alpha=0.15, label="95% 置信区间")
    # 标注预测峰值与回测精度
    pk_i = fc["点预测GMV"].idxmax()
    ax.annotate(f"预测黑五峰值\n{fc.loc[pk_i,'月份']}：{fc.loc[pk_i,'点预测GMV']/1e4:.1f} 万雷亚尔",
                xy=(fx[list(fc.index).index(pk_i)], fc.loc[pk_i, "点预测GMV"] / 1e4),
                xytext=(hx.iloc[-1], fc["点预测GMV"].max() / 1e4 + 28),
                fontsize=9.5, color=C_RED,
                arrowprops=dict(arrowstyle="->", color=C_RED, lw=1.2))
    ax.text(0.01, 0.95, "回测 MAPE = 5.58%（近 6 个月）", transform=ax.transAxes,
            fontsize=10, color=C_MAIN, va="top", bbox=dict(boxstyle="round,pad=0.4", fc="#EFF6FF", ec=C_MAIN, alpha=0.9))
    ax.set_title("图20 SARIMA(1,1,1)(1,0,1,12) 月度 GMV 预测（未来 6 个月）")
    ax.set_xlabel("月份"); ax.set_ylabel("GMV（万雷亚尔）")
    ax.legend(frameon=False); ax.grid(alpha=0.3)
    save(fig, "fig20_SARIMA销量预测含置信区间.png")


def fig21_sarima_bt(t):
    """模型图6·SARIMA 回测：实际 vs 预测"""
    bt = t["sarima_回测"]
    x = np.arange(len(bt)); w = 0.38
    mape = bt["绝对误差率%"].mean()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(x - w / 2, bt["实际GMV"] / 1e4, width=w, color=C_MAIN, alpha=0.9, label="实际 GMV")
    ax.bar(x + w / 2, bt["预测GMV"] / 1e4, width=w, color=C_ACC, alpha=0.9, label="回测预测 GMV")
    for i, r in bt.iterrows():
        ax.text(i + w / 2, r["预测GMV"] / 1e4 + 1.2, f"{r['绝对误差率%']:.1f}%",
                ha="center", fontsize=8.5, color=C_RED)
    ax.set_xticks(x); ax.set_xticklabels(bt["月份"])
    ax.set_title(f"图21 SARIMA 回测对比（最近 6 个月，MAPE = {mape:.2f}%）")
    ax.set_ylabel("GMV（万雷亚尔）"); ax.legend(frameon=False); ax.grid(axis="y", alpha=0.3)
    save(fig, "fig21_SARIMA回测对比图.png")


def fig22_rules(t):
    """模型图7·关联规则散点：支持度 × 置信度，气泡/颜色 = 提升度"""
    r = t["apriori_关联规则"]
    fig, ax = plt.subplots(figsize=(9, 5.4))
    sc = ax.scatter(r["support"] * 100, r["confidence"] * 100,
                    s=r["lift"] * 120, c=r["lift"], cmap="RdYlGn",
                    alpha=0.75, edgecolors="white")
    for _, row in r.head(8).iterrows():
        ax.annotate(f"{cn(row['antecedents'])}→{cn(row['consequents'])}",
                    (row["support"] * 100, row["confidence"] * 100),
                    fontsize=8, xytext=(6, 5), textcoords="offset points")
    fig.colorbar(sc, ax=ax, label="提升度 Lift")
    ax.set_xlabel("支持度 Support（%，多品类订单子集）")
    ax.set_ylabel("置信度 Confidence（%）")
    ax.set_title("图22 跨品类关联规则分布（气泡大小 = Lift）")
    ax.grid(alpha=0.25)
    save(fig, "fig22_关联规则分布图.png")


def fig23_abc(t):
    """模型图8·客户价值 ABC / 洛伦兹累计曲线"""
    rfm = t["rfm_客户明细"].sort_values("M_累计消费金额", ascending=False).reset_index(drop=True)
    cum = rfm["M_累计消费金额"].cumsum() / rfm["M_累计消费金额"].sum() * 100
    xpct = (np.arange(len(rfm)) + 1) / len(rfm) * 100
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.plot(xpct, cum.values, color=C_MAIN, lw=2.2, label="客户价值累计曲线")
    ax.plot([0, 100], [0, 100], color=C_GRAY, ls="--", lw=1.2, label="绝对平均线")
    for p, tag in [(20, "前 20%"), (45, "前 45%")]:
        v = np.interp(p, xpct, cum.values)
        ax.scatter([p], [v], color=C_RED, zorder=5)
        ax.annotate(f"{tag}客户贡献 {v:.1f}% GMV", (p, v),
                    xytext=(p + 6, v - 12), fontsize=9.5, color=C_RED,
                    arrowprops=dict(arrowstyle="->", color=C_RED))
    ax.fill_between(xpct, cum.values, xpct, alpha=0.10, color=C_MAIN)
    ax.set_xlabel("客户累计占比（%，按消费金额降序）")
    ax.set_ylabel("GMV 累计占比（%）")
    ax.set_title("图23 客户价值 ABC 分类累计曲线（帕累托视角）")
    ax.legend(frameon=False, loc="lower right"); ax.grid(alpha=0.3)
    save(fig, "fig23_客户价值ABC累计曲线.png")


def main():
    apply_style()
    d, orders, t = load_all()
    # 模板复现 15 张
    fig01_line(d); fig02_bar_line(d); fig03_pareto(d); fig04_donut(d)
    fig05_stacked_area(d); fig06_scatter(d); fig07_hist(d); fig08_hbar(d)
    fig09_rose(d); fig10_funnel(orders); fig11_waterfall(d); fig12_radar(d)
    fig13_heatmap(d); fig14_kpi(d, orders); fig15_box(d)
    # 业务模型图 8 张
    fig16_rfm_bubble(t); fig17_rfm_seg(t); fig18_cohort(t); fig19_bcg(t)
    fig20_sarima_fc(t); fig21_sarima_bt(t); fig22_rules(t); fig23_abc(t)
    print(f"[完成] 共 23 张图表 -> {FIG_DIR}")


if __name__ == "__main__":
    main()
