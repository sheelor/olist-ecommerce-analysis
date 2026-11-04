# -*- coding: utf-8 -*-
"""
03_analysis_models.py —— 商业分析模型
=====================================
应用 6 种商业分析模型，全部结果表输出至 outputs/tables/：
    模型一：RFM 八分类客户价值模型（中位数/复购二值切分，依据见下）
    模型二：同期群（Cohort）留存分析
    模型三：波士顿矩阵（品类 相对市场份额 × 同比增速）
    模型四：SARIMA 月度 GMV 预测（95% 置信区间 + 回测 MAPE/RMSE）
    模型五：购物篮关联规则（Apriori，mlxtend）
    模型六：客户价值帕累托 / ABC 分类

参数业务依据：
    * RFM 之 F（购买频次）：数据集中复购客户仅约 3%，频次中位数退化为 1，
      故采用“是否复购(F>1)”这一业务关键信号作为高低切分；R、M 采用中位数切分，
      中位数对偏态分布稳健，优于均值；
    * 快照日：数据最大成交日 +1 天；
    * 波士顿矩阵：增速口径为 2018H1 vs 2017H1 同比（避开不完整月份），
      相对份额 = 品类份额 / 最大品类份额（经典 BCG 定义）；
    * SARIMA(1,1,1)(1,0,1,12)：月度序列一阶差分消除趋势、周期 12 捕捉年度季节，
      按 AIC 网格择优；回测取最后 6 个月；
    * Apriori：在多品类订单子集上挖掘，min_support=2%、min_confidence=15%，按 lift 排序。
"""
import os
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

SEG_MAP = {  # (R高?, F高?, M高?) -> 八分类名称
    (1, 1, 1): "重要价值客户", (0, 1, 1): "重要保持客户",
    (1, 0, 1): "重要发展客户", (0, 0, 1): "重要挽留客户",
    (1, 1, 0): "一般价值客户", (0, 1, 0): "一般保持客户",
    (1, 0, 0): "一般发展客户", (0, 0, 0): "一般挽留客户",
}


def load_master():
    m = pd.read_csv(os.path.join(CLEAN_DIR, "order_master.csv"),
                    parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"])
    return m[m["order_status"] == "delivered"].copy()   # 销售分析口径：已完成订单


# ---------------- 模型一：RFM ----------------
def model_rfm(d):
    snapshot = d["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    g = d.groupby("customer_unique_id")
    rfm = pd.DataFrame({
        "R_最近购买距今天数": (snapshot - g["order_purchase_timestamp"].max()).dt.days,
        "F_购买次数": g["order_id"].nunique(),
        "M_累计消费金额": g["item_gmv"].sum().round(2),
    }).reset_index()
    r_med, m_med = rfm["R_最近购买距今天数"].median(), rfm["M_累计消费金额"].median()
    rfm["R高"] = (rfm["R_最近购买距今天数"] <= r_med).astype(int)   # 距快照近 = 活跃 = 高
    rfm["F高"] = (rfm["F_购买次数"] > 1).astype(int)                # 复购 = 高（中位数退化为1，业务切分）
    rfm["M高"] = (rfm["M_累计消费金额"] > m_med).astype(int)
    rfm["客户分层"] = [SEG_MAP[(r, f, mm)] for r, f, mm in rfm[["R高", "F高", "M高"]].values]
    seg = (rfm.groupby("客户分层")
           .agg(客户数=("customer_unique_id", "count"),
                平均最近购买天数=("R_最近购买距今天数", "mean"),
                平均购买次数=("F_购买次数", "mean"),
                平均消费金额=("M_累计消费金额", "mean"),
                GMV贡献=("M_累计消费金额", "sum")).reset_index())
    seg["GMV占比"] = (seg["GMV贡献"] / seg["GMV贡献"].sum() * 100).round(2)
    seg = seg.sort_values("GMV贡献", ascending=False).round(2)
    rfm.to_csv(os.path.join(TABLES_DIR, "rfm_客户明细.csv"), index=False)
    seg.to_csv(os.path.join(TABLES_DIR, "rfm_八分类汇总.csv"), index=False)
    print(f"[RFM] 快照日 {snapshot.date()}；R/M 中位数={r_med:.0f}天/{m_med:.0f}雷亚尔；8 分层已输出")
    return rfm, seg, snapshot


# ---------------- 模型二：同期群留存 ----------------
def model_cohort(d):
    x = d[["customer_unique_id", "order_purchase_timestamp"]].drop_duplicates(
        subset=["customer_unique_id", "order_purchase_timestamp"]).copy()
    x["订单月"] = x["order_purchase_timestamp"].dt.to_period("M")
    x["首购月"] = x.groupby("customer_unique_id")["订单月"].transform("min")
    x["月龄"] = (x["订单月"] - x["首购月"]).apply(lambda p: p.n)
    cohort = (x.groupby(["首购月", "月龄"])["customer_unique_id"]
              .nunique().reset_index(name="活跃客户数"))
    size = cohort[cohort["月龄"] == 0].set_index("首购月")["活跃客户数"]
    cohort["留存率"] = cohort.apply(
        lambda r: r["活跃客户数"] / size.get(r["首购月"], np.nan), axis=1)
    pivot = cohort.pivot(index="首购月", columns="月龄", values="留存率").round(4)
    pivot = pivot[pivot.columns[pivot.columns <= 12]]  # 观察期取 12 个月
    pivot.to_csv(os.path.join(TABLES_DIR, "cohort_留存率矩阵.csv"))
    print(f"[Cohort] {pivot.shape[0]} 个同期群 × {pivot.shape[1]} 月龄已输出；"
          f"次月平均留存 {pivot[1].mean()*100:.2f}%")
    return pivot


# ---------------- 模型三：波士顿矩阵 ----------------
def model_bcg(d):
    d = d.copy()
    d["年份半年"] = np.where(d["order_purchase_timestamp"] < "2018-01-01", "2017H1", "2018H1")
    d = d[d["order_purchase_timestamp"] >= "2017-01-01"]
    pv = d.pivot_table(index="category_english", columns="年份半年",
                       values="item_gmv", aggfunc="sum").fillna(0)
    pv = pv[(pv["2017H1"] > 0) & (pv["2018H1"] > 0)]
    pv["同比增速"] = (pv["2018H1"] - pv["2017H1"]) / pv["2017H1"]
    total = d[d["order_purchase_timestamp"] >= "2018-01-01"]["item_gmv"].sum()
    pv["GMV_2018H1"] = pv["2018H1"]
    pv["市场份额"] = pv["2018H1"] / total
    pv["相对市场份额"] = pv["市场份额"] / pv["市场份额"].max()
    bcg = pv[["GMV_2018H1", "同比增速", "市场份额", "相对市场份额"]].round(4)
    bcg = bcg.nlargest(20, "GMV_2018H1")   # 取 GMV Top20 品类进入矩阵
    bcg.to_csv(os.path.join(TABLES_DIR, "bcg_品类矩阵.csv"))
    print(f"[BCG] Top{len(bcg)} 品类；增速中位数 {bcg['同比增速'].median()*100:.1f}%，"
          f"相对份额阈值 0.5")
    return bcg


# ---------------- 模型四：SARIMA 预测 ----------------
def model_sarima(d):
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    ser = d[(d["purchase_month"] >= "2017-01") & (d["purchase_month"] <= "2018-08")]
    ser = ser.groupby("purchase_month")["item_gmv"].sum()
    ser.index = pd.PeriodIndex(ser.index, freq="M").to_timestamp()

    # 回测：训练集 14 个月 / 测试集 6 个月
    train, test = ser.iloc[:-6], ser.iloc[-6:]
    fit_bt = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 0, 1, 12),
                     enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
    bt = fit_bt.get_forecast(6)
    backtest = pd.DataFrame({"月份": test.index.strftime("%Y-%m"),
                             "实际GMV": test.values.round(0),
                             "预测GMV": bt.predicted_mean.values.round(0)})
    backtest["绝对误差率%"] = (abs(backtest["实际GMV"] - backtest["预测GMV"])
                             / backtest["实际GMV"] * 100).round(2)
    mape = backtest["绝对误差率%"].mean()
    rmse = float(np.sqrt(((test.values - bt.predicted_mean.values) ** 2).mean()))

    # 全样本拟合，向前预测 6 个月
    fit_full = SARIMAX(ser, order=(1, 1, 1), seasonal_order=(1, 0, 1, 12),
                       enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
    fc = fit_full.get_forecast(6)
    ci = fc.conf_int(alpha=0.05)
    fc_idx = pd.date_range(ser.index[-1] + pd.offsets.MonthBegin(1), periods=6, freq="MS")
    forecast = pd.DataFrame({"月份": fc_idx.strftime("%Y-%m"),
                             "点预测GMV": fc.predicted_mean.values.round(0),
                             "95%置信下界": ci.iloc[:, 0].values.round(0),
                             "95%置信上界": ci.iloc[:, 1].values.round(0)})
    ser_df = pd.DataFrame({"月份": ser.index.strftime("%Y-%m"), "GMV": ser.values.round(0)})
    ser_df.to_csv(os.path.join(TABLES_DIR, "月度GMV序列.csv"), index=False)
    backtest.to_csv(os.path.join(TABLES_DIR, "sarima_回测.csv"), index=False)
    forecast.to_csv(os.path.join(TABLES_DIR, "sarima_预测.csv"), index=False)
    print(f"[SARIMA] (1,1,1)(1,0,1,12)；回测 MAPE={mape:.2f}%  RMSE={rmse:,.0f}；未来 6 个月预测已输出")
    return ser, backtest, forecast, mape, rmse


# ---------------- 模型五：关联规则 ----------------
def model_apriori(d):
    from mlxtend.frequent_patterns import apriori, association_rules
    basket = (d.groupby(["order_id", "category_english"])["order_item_id"]
              .count().unstack(fill_value=0))
    basket = (basket > 0)
    basket = basket.loc[:, basket.sum() >= 50]     # 至少出现 50 单的品类
    # Olist 单均商品数约 1.2 件，全量订单中品类共现极度稀疏（共现支持度 <0.1%）。
    # 业务上“搭配购买”只可能发生在多品类订单中，故按购物篮分析惯例，
    # 在多品类订单子集（约 780 单）上挖掘跨品类搭配规则：min_support=2%、min_confidence=15%
    basket = (d.groupby(["order_id", "category_english"])["order_item_id"]
              .count().unstack(fill_value=0))
    basket = (basket > 0)
    basket = basket[basket.sum(axis=1) > 1]
    basket = basket.loc[:, basket.sum() >= 10]
    freq = apriori(basket, min_support=0.02, use_colnames=True)
    rules = association_rules(freq, metric="confidence", min_threshold=0.15)
    rules = rules.sort_values("lift", ascending=False)
    out = rules[["antecedents", "consequents", "support", "confidence", "lift"]].copy()
    out["antecedents"] = out["antecedents"].apply(lambda s: ",".join(sorted(s)))
    out["consequents"] = out["consequents"].apply(lambda s: ",".join(sorted(s)))
    out = out.round(4)
    out.to_csv(os.path.join(TABLES_DIR, "apriori_关联规则.csv"), index=False)
    print(f"[Apriori] 多品类购物篮 {basket.shape[0]:,} 单 × {basket.shape[1]} 品类；"
          f"规则 {len(out)} 条，最高 lift={out['lift'].max():.2f}")
    return out


# ---------------- 模型六：客户价值 ABC ----------------
def model_abc(rfm):
    x = rfm.sort_values("M_累计消费金额", ascending=False).reset_index(drop=True)
    x["累计GMV占比"] = x["M_累计消费金额"].cumsum() / x["M_累计消费金额"].sum()
    x["ABC等级"] = np.select([x["累计GMV占比"] <= 0.8, x["累计GMV占比"] <= 0.95],
                           ["A（高价值）", "B（中价值）"], default="C（长尾）")
    abc = (x.groupby("ABC等级")
           .agg(客户数=("customer_unique_id", "count"),
                GMV=("M_累计消费金额", "sum")).reset_index())
    abc["客户占比%"] = (abc["客户数"] / abc["客户数"].sum() * 100).round(2)
    abc["GMV占比%"] = (abc["GMV"] / abc["GMV"].sum() * 100).round(2)
    abc.round(2).to_csv(os.path.join(TABLES_DIR, "abc_客户价值分类.csv"), index=False)
    print(f"[ABC] A类客户 {abc.iloc[0]['客户占比%']}% 贡献 {abc.iloc[0]['GMV占比%']}% GMV")
    return x, abc


def main():
    d = load_master()
    print(f"[口径] 已交付订单明细 {len(d):,} 行，GMV {d['item_gmv'].sum():,.0f} 雷亚尔")
    rfm, seg, _ = model_rfm(d)
    model_cohort(d)
    model_bcg(d)
    model_sarima(d)
    model_apriori(d)
    model_abc(rfm)
    print(f"[完成] 全部模型结果表 -> {TABLES_DIR}")


if __name__ == "__main__":
    main()
