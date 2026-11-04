# -*- coding: utf-8 -*-
"""
05_dashboard.py —— Olist 交互式商业分析大屏（Pyecharts，全 Python 实现）
=======================================================================
页面结构：总标题 / 6 项 KPI / 经营总览 / 品类与交易结构 / 客户价值 / 预测与决策。
共 14 个分析组件：13 个 Pyecharts 图表 + 1 个 RFM 明细表。
交互能力：悬停提示、图例筛选、区域缩放、季度时间轴联动、品类点击下钻。
输出：outputs/fig24_交互式可视化大屏.html
"""
import json
import os

import numpy as np
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import (
    Bar, Calendar, Funnel, Gauge, HeatMap, Line, Liquid, Pie, Scatter, Timeline,
)
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_DIR = os.path.join(BASE_DIR, "data", "clean")
TABLES_DIR = os.path.join(BASE_DIR, "outputs", "tables")
OUT = os.path.join(BASE_DIR, "outputs", "fig24_交互式可视化大屏.html")

CAT_CN = {
    "health_beauty": "健康美妆", "watches_gifts": "腕表礼品",
    "bed_bath_table": "床浴桌台", "sports_leisure": "运动休闲",
    "computers_accessories": "电脑配件", "furniture_decor": "家具装饰",
    "housewares": "家居用品", "auto": "汽车配件", "cool_stuff": "酷玩好物",
    "toys": "玩具", "baby": "母婴用品", "garden_tools": "园艺工具",
    "home_confort": "家居舒适", "perfumery": "香氛",
}
PAY_CN = {
    "credit_card": "信用卡", "boleto": "银行票据",
    "debit_card": "借记卡", "voucher": "代金券", "not_defined": "未定义",
}
MINT = "#00d9a3"
GOLD = "#ffca34"
BLUE = "#69a7ff"
RED = "#ff6b6b"
TEXT = "#f3f5f4"
MUTED = "#9ca3af"
GRID = "#2b3433"
PALETTE = [MINT, GOLD, BLUE, RED, "#a78bfa", "#55c1e8", "#a3d635", "#f59e62"]
THEME = ThemeType.DARK


def cn(x):
    return CAT_CN.get(x, x)


def init(chart, height="390px"):
    # Pyecharts 6 在构造函数中展开 InitOpts；此处直接更新实例属性。
    chart.width = "100%"
    chart.height = height
    chart.theme = THEME
    chart.bg_color = "rgba(0,0,0,0)"
    chart.options["backgroundColor"] = chart.bg_color
    chart.options["animation"] = False
    return chart


def text_style(size=12, color=MUTED):
    return opts.TextStyleOpts(color=color, font_size=size, font_family="Microsoft YaHei")


def tooltip(trigger="item"):
    return opts.TooltipOpts(
        trigger=trigger, background_color="#17201f", border_color="#38504a",
        textstyle_opts=text_style(12, TEXT),
    )


def axis(name=None, type_=None):
    return opts.AxisOpts(
        name=name, type_=type_, name_textstyle_opts=text_style(),
        axislabel_opts=opts.LabelOpts(color=MUTED, font_size=11),
        axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#52605d")),
        splitline_opts=opts.SplitLineOpts(
            is_show=True, linestyle_opts=opts.LineStyleOpts(color=GRID, opacity=0.65)
        ),
    )


def kpi_gauges(good, rep):
    g = init(Gauge(), "310px").add(
        "好评率", [("好评率", good)], min_=0, max_=100, radius="76%",
        center=["50%", "58%"],
        detail_label_opts=opts.GaugeDetailOpts(
            formatter="{value}%", font_size=28, color=MINT, font_weight="bold"
        ),
        title_label_opts=opts.GaugeTitleOpts(font_size=13, color=MUTED, offset_center=[0, "85%"]),
    ).set_global_opts(
        legend_opts=opts.LegendOpts(is_show=False), tooltip_opts=tooltip(),
    ).set_series_opts(
        axisline_opts=opts.AxisLineOpts(
            linestyle_opts=opts.LineStyleOpts(color=[[0.6, GOLD], [0.8, MINT], [1, BLUE]], width=12)
        ),
        pointer_opts=opts.GaugePointerOpts(is_show=True, length="62%", width=5),
    )
    l = init(Liquid(), "310px").add(
        "复购率", [rep / 100, min(rep / 100 + 0.025, 1)], center=["50%", "56%"],
        color=[MINT, BLUE], is_outline_show=True,
        background_color="#17201f", is_animation=False,
        outline_itemstyle_opts=opts.ItemStyleOpts(color=MINT, border_color=MINT, border_width=2),
        label_opts=opts.LabelOpts(font_size=28, color=MINT, font_weight="bold"),
    ).set_global_opts(tooltip_opts=tooltip())
    return g, l


def trend_line(d):
    s = d[d["purchase_month"] >= "2017-01"].groupby("purchase_month")["item_gmv"].sum() / 1e4
    ln = init(Line(), "410px").add_xaxis(list(s.index)).add_yaxis(
        "月度 GMV（万雷亚尔）", [round(v, 1) for v in s.values], is_smooth=True,
        color=MINT, symbol="circle", symbol_size=7,
        linestyle_opts=opts.LineStyleOpts(width=3),
        label_opts=opts.LabelOpts(is_show=True, position="top", color=TEXT, font_size=10),
        markpoint_opts=opts.MarkPointOpts(
            data=[opts.MarkPointItem(type_="max", name="峰值")],
            symbol_size=48, label_opts=opts.LabelOpts(color="#10201c", font_size=10),
        ),
        markline_opts=opts.MarkLineOpts(
            data=[opts.MarkLineItem(type_="average", name="均值")],
            linestyle_opts=opts.LineStyleOpts(color=GOLD, type_="dashed"),
            label_opts=opts.LabelOpts(color=GOLD),
        ),
    ).set_global_opts(
        title_opts=opts.TitleOpts(is_show=False),
        datazoom_opts=[opts.DataZoomOpts(type_="slider", pos_bottom="3%", range_start=0, range_end=100),
                       opts.DataZoomOpts(type_="inside", range_start=0, range_end=100)],
        tooltip_opts=tooltip("axis"),
        legend_opts=opts.LegendOpts(pos_top="2%", textstyle_opts=text_style()),
        xaxis_opts=axis(), yaxis_opts=axis("万雷亚尔"),
    )
    return ln


def top10_bar(d):
    s = d.groupby("category_english")["item_gmv"].sum().nlargest(10).sort_values() / 1e4
    bar = init(Bar(), "430px").add_xaxis([cn(c) for c in s.index]).add_yaxis(
        "GMV（万雷亚尔）", [round(v, 1) for v in s.values], color=MINT, bar_width="54%",
        label_opts=opts.LabelOpts(position="right", color=TEXT, font_size=11),
    ).reversal_axis().set_global_opts(
        title_opts=opts.TitleOpts(is_show=False), tooltip_opts=tooltip("axis"),
        legend_opts=opts.LegendOpts(is_show=False),
        xaxis_opts=axis("万雷亚尔"),
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color=TEXT, font_size=11)),
    )
    return bar


def pay_pie(d):
    s = d.drop_duplicates("order_id").groupby("payment_type")["payment_value"].sum() / 1e4
    pie = init(Pie(), "310px").set_colors(PALETTE).add(
        "支付金额", [(PAY_CN.get(k, k), round(v, 1)) for k, v in s.items()],
        radius=["42%", "69%"], center=["53%", "53%"],
    ).set_global_opts(
        title_opts=opts.TitleOpts(is_show=False), tooltip_opts=tooltip(),
        legend_opts=opts.LegendOpts(
            orient="vertical", pos_left="2%", pos_top="middle", textstyle_opts=text_style()
        ),
    ).set_series_opts(label_opts=opts.LabelOpts(formatter="{b}\n{d}%", color=TEXT, font_size=11))
    return pie


def calendar_heat(d):
    s = d[d["purchase_month"] >= "2018-01"].groupby(
        d["order_purchase_timestamp"].dt.strftime("%Y-%m-%d")
    )["order_id"].nunique()
    cal = init(Calendar(), "390px").add(
        "日订单量", [[k, int(v)] for k, v in s.items()],
        calendar_opts=opts.CalendarOpts(
            range_="2018", pos_top="18%", pos_left="8%", pos_right="5%",
            cell_size=[22, 22], yearlabel_opts=opts.CalendarYearLabelOpts(is_show=False),
            daylabel_opts=opts.CalendarDayLabelOpts(name_map="ZH", label_color=MUTED),
            monthlabel_opts=opts.CalendarMonthLabelOpts(name_map="ZH", label_color=MUTED),
            splitline_opts=opts.SplitLineOpts(linestyle_opts=opts.LineStyleOpts(color="#52605d")),
        ),
    ).set_global_opts(
        title_opts=opts.TitleOpts(is_show=False), tooltip_opts=tooltip(),
        legend_opts=opts.LegendOpts(is_show=False),
        visualmap_opts=opts.VisualMapOpts(
            min_=0, max_=int(s.max()), orient="horizontal", pos_top="2%", pos_left="center",
            range_color=["#18332e", MINT, GOLD], textstyle_opts=text_style(),
        ),
    )
    return cal


def funnel_chart(orders):
    stages = [("全部下单", len(orders)),
              ("支付批准", int(orders["order_approved_at"].notna().sum())),
              ("卖家发货", int(orders["order_delivered_carrier_date"].notna().sum())),
              ("买家签收", int(orders["order_delivered_customer_date"].notna().sum()))]
    fu = init(Funnel(), "390px").set_colors(PALETTE).add(
        "订单数", stages, pos_left="8%", pos_right="8%", pos_top="12%", pos_bottom="8%",
        label_opts=opts.LabelOpts(formatter="{b}  {c}", position="inside", color=TEXT, font_size=12),
        sort_="descending", gap=4,
    ).set_global_opts(
        title_opts=opts.TitleOpts(is_show=False), legend_opts=opts.LegendOpts(is_show=False),
        tooltip_opts=tooltip(),
    )
    return fu


def quarterly_timeline(d):
    x = d[d["purchase_month"] >= "2017-01"].copy()
    x["季度"] = x["order_purchase_timestamp"].dt.to_period("Q").astype(str)
    tl = init(Timeline(), "430px")
    for q, sub in x.groupby("季度"):
        s = sub.groupby("category_english")["item_gmv"].sum().nlargest(8).sort_values() / 1e4
        bar = Bar().add_xaxis([cn(c) for c in s.index]).add_yaxis(
            "GMV（万雷亚尔）", [round(v, 1) for v in s.values], color=GOLD, bar_width="52%",
            label_opts=opts.LabelOpts(position="right", color=TEXT, font_size=10),
        ).reversal_axis().set_global_opts(
            title_opts=opts.TitleOpts(title=f"{q} 销售 Top8", title_textstyle_opts=text_style(15, TEXT)),
            legend_opts=opts.LegendOpts(is_show=False), tooltip_opts=tooltip("axis"),
            xaxis_opts=axis("万雷亚尔"),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color=TEXT, font_size=10)),
        )
        tl.add(bar, q)
    tl.add_schema(
        play_interval=1800, is_auto_play=False, pos_bottom="2%",
        label_opts=opts.LabelOpts(color=MUTED), checkpointstyle_opts=opts.TimelineCheckPointerStyle(color=MINT),
    )
    return tl


def rfm_bar(seg):
    s = seg.sort_values("GMV占比")
    bar = init(Bar(), "420px").add_xaxis(s["客户分层"].tolist()).add_yaxis(
        "GMV 占比", [round(v, 2) for v in s["GMV占比"]], color=MINT, bar_width="52%",
        label_opts=opts.LabelOpts(position="right", formatter="{c}%", color=TEXT),
    ).reversal_axis().set_global_opts(
        title_opts=opts.TitleOpts(is_show=False), tooltip_opts=tooltip("axis"),
        legend_opts=opts.LegendOpts(is_show=False), xaxis_opts=axis("GMV 占比（%）"),
        yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(color=TEXT, font_size=11)),
    )
    return bar


def cohort_heatmap(cohort):
    c = cohort[cohort["首购月"] >= "2017-01"].copy()
    months = [str(i) for i in range(13)]
    data = []
    for yi, (_, row) in enumerate(c.iterrows()):
        for xi, m in enumerate(months):
            v = row[m]
            if pd.notna(v):
                data.append([xi, yi, round(float(v) * 100, 2)])
    hm = init(HeatMap(), "480px").add_xaxis([f"M+{m}" for m in months]).add_yaxis(
        "留存率", c["首购月"].tolist(), data,
        label_opts=opts.LabelOpts(is_show=True, formatter=JsCode("function(p){return p.value[2].toFixed(1);}"), color=TEXT, font_size=9),
    ).set_global_opts(
        title_opts=opts.TitleOpts(is_show=False), tooltip_opts=tooltip(),
        legend_opts=opts.LegendOpts(is_show=False),
        xaxis_opts=axis(), yaxis_opts=axis(),
        visualmap_opts=opts.VisualMapOpts(
            min_=0, max_=12, is_calculable=True, orient="horizontal", pos_top="2%", pos_right="5%",
            range_color=["#17201f", "#126b59", MINT, GOLD], textstyle_opts=text_style(),
        ),
    )
    return hm


def bcg_scatter(bcg):
    data = []
    for _, r in bcg.iterrows():
        data.append({
            "name": cn(r["category_english"]),
            "value": [round(float(r["相对市场份额"]), 3), round(float(r["同比增速"]) * 100, 2),
                      round(float(r["GMV_2018H1"]) / 10000, 1)],
        })
    sc = init(Scatter(), "470px").add_xaxis([]).add_yaxis(
        "品类", data, color=MINT,
        symbol_size=JsCode("function(p){return Math.max(12, Math.min(48, Math.sqrt(p[2])*3.2));}"),
        label_opts=opts.LabelOpts(is_show=True, formatter="{b}", position="top", color=TEXT, font_size=10),
        markline_opts=opts.MarkLineOpts(
            is_silent=True, symbol="none",
            data=[opts.MarkLineItem(x=0.5), opts.MarkLineItem(y=0)],
            linestyle_opts=opts.LineStyleOpts(color=GOLD, type_="dashed"),
            label_opts=opts.LabelOpts(is_show=False),
        ),
    ).set_global_opts(
        title_opts=opts.TitleOpts(is_show=False), legend_opts=opts.LegendOpts(is_show=False),
        tooltip_opts=opts.TooltipOpts(
            formatter=JsCode("function(p){return p.name+'<br/>相对份额：'+p.value[0]+'<br/>同比增速：'+p.value[1]+'%<br/>GMV：'+p.value[2]+' 万雷亚尔';}"),
            background_color="#17201f", border_color="#38504a", textstyle_opts=text_style(12, TEXT),
        ),
        xaxis_opts=axis("相对市场份额", "value"), yaxis_opts=axis("同比增速（%）", "value"),
    )
    return sc


def apriori_scatter(rules):
    data = []
    for _, r in rules.iterrows():
        label = f"{cn(r['antecedents'])} → {cn(r['consequents'])}"
        data.append({
            "name": label,
            "value": [round(float(r["confidence"]) * 100, 1), round(float(r["lift"]), 2),
                      round(float(r["support"]) * 100, 2)],
        })
    sc = init(Scatter(), "430px").add_xaxis([]).add_yaxis(
        "关联规则", data, color=GOLD,
        symbol_size=JsCode("function(p){return Math.max(14, p[2]*2.8);}"),
        label_opts=opts.LabelOpts(is_show=False),
        markline_opts=opts.MarkLineOpts(
            is_silent=True, symbol="none", data=[opts.MarkLineItem(y=1, name="lift=1")],
            linestyle_opts=opts.LineStyleOpts(color=RED, type_="dashed"),
            label_opts=opts.LabelOpts(formatter="提升度=1", color=RED),
        ),
    ).set_global_opts(
        title_opts=opts.TitleOpts(is_show=False), legend_opts=opts.LegendOpts(is_show=False),
        tooltip_opts=opts.TooltipOpts(
            formatter=JsCode("function(p){return p.name+'<br/>置信度：'+p.value[0]+'%<br/>提升度：'+p.value[1]+'<br/>支持度：'+p.value[2]+'%';}"),
            background_color="#17201f", border_color="#38504a", textstyle_opts=text_style(12, TEXT),
        ),
        xaxis_opts=axis("置信度（%）", "value"), yaxis_opts=axis("提升度 Lift", "value"),
    )
    return sc


def sarima_chart(monthly, forecast):
    hist_x = monthly["月份"].tolist()
    fc_x = forecast["月份"].tolist()
    x = hist_x + fc_x
    hist = [round(v / 1e4, 1) for v in monthly["GMV"]] + [None] * len(fc_x)
    point = [None] * (len(hist_x) - 1) + [hist[len(hist_x) - 1]] + [round(v / 1e4, 1) for v in forecast["点预测GMV"]]
    lower = [None] * len(hist_x) + [round(v / 1e4, 1) for v in forecast["95%置信下界"]]
    band = [None] * len(hist_x) + [round((hi - lo) / 1e4, 1) for hi, lo in zip(forecast["95%置信上界"], forecast["95%置信下界"])]
    bf_value = round(float(forecast.loc[forecast["月份"] == "2018-11", "点预测GMV"].iloc[0]) / 1e4, 1)
    ln = init(Line(), "440px").add_xaxis(x).add_yaxis(
        "历史 GMV", hist, color=BLUE, symbol_size=6, linestyle_opts=opts.LineStyleOpts(width=2.5),
    ).add_yaxis(
        "点预测", point, color=MINT, symbol_size=7, linestyle_opts=opts.LineStyleOpts(width=3),
        markpoint_opts=opts.MarkPointOpts(
            data=[opts.MarkPointItem(coord=["2018-11", bf_value], name="黑五预测")],
            symbol_size=54, itemstyle_opts=opts.ItemStyleOpts(color=GOLD),
            label_opts=opts.LabelOpts(color="#17201f", font_size=10),
        ),
    ).add_yaxis(
        "95% 置信下界", lower, stack="confidence", color="#1b5d50", symbol="none",
        linestyle_opts=opts.LineStyleOpts(opacity=0), is_smooth=False,
    ).add_yaxis(
        "95% 置信区间", band, stack="confidence", color=MINT, symbol="none",
        linestyle_opts=opts.LineStyleOpts(opacity=0),
        areastyle_opts=opts.AreaStyleOpts(opacity=0.22),
    ).set_global_opts(
        title_opts=opts.TitleOpts(is_show=False), tooltip_opts=tooltip("axis"),
        legend_opts=opts.LegendOpts(pos_top="2%", textstyle_opts=text_style()),
        xaxis_opts=axis(), yaxis_opts=axis("万雷亚尔"),
        datazoom_opts=[opts.DataZoomOpts(type_="inside", range_start=0, range_end=100)],
    )
    return ln


def card(chart, title, subtitle, cls="half", tag="交互图表"):
    import re
    rendered = chart.render_embed()
    body = re.search(r"<body[^>]*>(.*?)</body>", rendered, re.S)
    embed = body.group(1) if body else rendered
    return f'''<article class="chart-card {cls}">
      <div class="card-head"><div><h3>{title}</h3><p>{subtitle}</p></div><span>{tag}</span></div>
      {embed}
    </article>'''


def rfm_table_html(seg):
    rows = []
    for _, r in seg.iterrows():
        important = str(r["客户分层"]).startswith("重要")
        rows.append(f'''<tr class="{'important' if important else ''}">
          <td>{r['客户分层']}</td><td>{int(r['客户数']):,}</td><td>{r['平均消费金额']:.2f}</td>
          <td><div class="table-value"><span>{r['GMV占比']:.2f}%</span><i style="width:{min(float(r['GMV占比']) * 2, 100):.1f}%"></i></div></td>
        </tr>''')
    return f'''<article class="chart-card full table-card">
      <div class="card-head"><div><h3>RFM 八分类客户分层明细</h3><p>重要发展 + 重要挽留客户贡献 78.02% GMV；表格按 GMV 贡献排序</p></div><span>明细表</span></div>
      <div class="table-wrap"><table><thead><tr><th>客户分层</th><th>客户数</th><th>人均消费（雷亚尔）</th><th>GMV 占比</th></tr></thead>
      <tbody>{''.join(rows)}</tbody></table></div></article>'''


CSS = r'''
:root{
  --p0:oklch(0.18 0.012 180); --p1:oklch(0.22 0.015 180); --p2:oklch(0.28 0.018 180);
  --mint:oklch(0.84 0.15 170); --gold:oklch(0.86 0.16 90);
  --text:oklch(0.96 0.008 170); --muted:oklch(0.72 0.018 180);
  --bg:var(--p0); --surface:var(--p1); --line:var(--p2); --accent:var(--mint);
}
*{box-sizing:border-box} html{scroll-behavior:smooth;scroll-padding-top:24px}
body{margin:0;background:var(--bg);color:var(--text);font-family:"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",sans-serif;font-size:16px;line-height:1.6}
a{color:inherit;text-decoration:none} a:focus-visible{outline:2px solid var(--gold);outline-offset:5px}
.shell{width:min(1560px,calc(100% - 48px));margin:0 auto;padding:32px 0 56px}
.hero{display:grid;grid-template-columns:1fr auto;gap:32px;align-items:end;padding:20px 0 28px;border-bottom:1px solid var(--line)}
.kicker{font-size:12px;letter-spacing:.18em;color:var(--mint);font-weight:700;margin:0 0 8px}
h1{font-size:clamp(30px,3.2vw,52px);line-height:1.15;letter-spacing:-.035em;margin:0;font-weight:750}
.subtitle{color:var(--muted);margin:14px 0 0;font-size:14px}.hero-meta{text-align:right;color:var(--muted);font-size:13px}
.status{display:inline-flex;gap:8px;align-items:center;color:var(--mint);font-weight:700;margin-bottom:8px}.status:before{content:"";width:8px;height:8px;border-radius:50%;background:var(--mint)}
.nav{display:flex;flex-wrap:wrap;gap:8px 24px;padding:18px 0 8px;font-size:14px;color:var(--muted)}.nav a{transition:color .18s ease}.nav a:hover{color:var(--mint)}
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:24px 0}.kpi{padding:20px 18px;background:var(--surface);border:1px solid var(--line);border-radius:10px}
.kpi .label{font-size:12px;color:var(--muted)}.kpi strong{display:block;font-size:clamp(23px,2vw,34px);line-height:1.25;letter-spacing:-.03em;margin:5px 0;font-variant-numeric:tabular-nums}.kpi small{font-size:12px;color:var(--muted)}
.kpi:nth-child(1) strong,.kpi:nth-child(5) strong{color:var(--mint)}.kpi:nth-child(6) strong{color:var(--gold)}
.insight-strip{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:4px 0 38px}.insight{padding:20px 24px}.insight+.insight{border-left:1px solid var(--line)}
.insight b{display:block;font-size:14px;margin-bottom:4px}.insight p{margin:0;color:var(--muted);font-size:13px}.insight b.mint{color:var(--mint)}.insight b.gold{color:var(--gold)}
.section{margin-top:38px}.section-head{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:16px}.section-head h2{font-size:24px;margin:0;letter-spacing:-.02em}.section-head p{margin:3px 0 0;color:var(--muted);font-size:13px}.section-head .index{color:var(--mint);font-size:12px;letter-spacing:.15em}
.grid{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:16px}.chart-card{background:var(--surface);border:1px solid var(--line);border-radius:10px;overflow:hidden;min-width:0}.full{grid-column:span 12}.wide{grid-column:span 8}.half{grid-column:span 6}.third{grid-column:span 4}
.card-head{display:flex;justify-content:space-between;gap:16px;align-items:start;padding:18px 20px 0}.card-head h3{font-size:16px;line-height:1.4;margin:0}.card-head p{font-size:12px;color:var(--muted);margin:5px 0 0}.card-head>span{font-size:11px;color:var(--mint);white-space:nowrap;border:1px solid var(--line);border-radius:4px;padding:2px 7px}
.chart-container{margin:0 auto}.table-wrap{overflow-x:auto;padding:16px 20px 22px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}th{color:var(--muted);font-weight:500}tr.important td:first-child{color:var(--mint);font-weight:700}.table-value{display:grid;grid-template-columns:58px 1fr;align-items:center;gap:10px}.table-value i{display:block;height:5px;background:var(--mint);border-radius:3px;max-width:100%}
.drilldown{margin-top:16px;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:20px}.drill-head{display:flex;align-items:center;justify-content:space-between;gap:16px}.drill-head h3{margin:0;font-size:16px}.drill-head p{margin:4px 0 0;color:var(--muted);font-size:12px}.drill-head span{color:var(--gold);font-size:12px}.drill-metrics{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-top:16px}.drill-metrics div{border-top:1px solid var(--line);padding-top:12px}.drill-metrics small{display:block;color:var(--muted);font-size:12px}.drill-metrics b{font-size:22px;font-variant-numeric:tabular-nums}
.decision-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:16px}.decision{border-top:2px solid var(--mint);padding:16px 4px}.decision:nth-child(2){border-color:var(--gold)}.decision h3{font-size:15px;margin:0 0 6px}.decision p{font-size:13px;color:var(--muted);margin:0}
.model-note{display:flex;gap:28px;flex-wrap:wrap;margin:16px 0 0;color:var(--muted);font-size:13px}.model-note b{color:var(--text);font-size:18px;margin-right:5px}.footer{display:flex;justify-content:space-between;gap:24px;border-top:1px solid var(--line);margin-top:42px;padding-top:22px;color:var(--muted);font-size:12px}.footer a{color:var(--mint)}
@media(max-width:1100px){.kpis{grid-template-columns:repeat(3,1fr)}.third{grid-column:span 6}.wide{grid-column:span 12}}
@media(max-width:720px){.shell{width:min(100% - 28px,1560px);padding-top:18px}.hero{grid-template-columns:1fr;gap:12px}.hero-meta{text-align:left}.kpis{grid-template-columns:repeat(2,1fr)}.insight-strip,.decision-grid{grid-template-columns:1fr}.insight+.insight{border-left:0;border-top:1px solid var(--line)}.half,.third,.wide,.full{grid-column:span 12}.drill-metrics{grid-template-columns:repeat(2,1fr)}.section-head{align-items:start;flex-direction:column;gap:4px}.footer{flex-direction:column}.card-head{padding:16px 14px 0}.card-head>span{display:none}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
'''


def main():
    m = pd.read_csv(os.path.join(CLEAN_DIR, "order_master.csv"), parse_dates=["order_purchase_timestamp"])
    d = m[m["order_status"] == "delivered"].copy()
    orders = pd.read_csv(
        os.path.join(CLEAN_DIR, "orders_clean.csv"),
        parse_dates=["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date"],
    )
    seg = pd.read_csv(os.path.join(TABLES_DIR, "rfm_八分类汇总.csv"))
    cohort = pd.read_csv(os.path.join(TABLES_DIR, "cohort_留存率矩阵.csv"))
    bcg = pd.read_csv(os.path.join(TABLES_DIR, "bcg_品类矩阵.csv"))
    rules = pd.read_csv(os.path.join(TABLES_DIR, "apriori_关联规则.csv"))
    monthly = pd.read_csv(os.path.join(TABLES_DIR, "月度GMV序列.csv"))
    forecast = pd.read_csv(os.path.join(TABLES_DIR, "sarima_预测.csv"))
    backtest = pd.read_csv(os.path.join(TABLES_DIR, "sarima_回测.csv"))

    od = d.drop_duplicates("order_id")
    total_gmv = float(d["item_gmv"].sum())
    order_n = int(od["order_id"].nunique())
    customer_n = int(od["customer_unique_id"].nunique())
    aov = total_gmv / order_n
    good = round(float((od["review_score"] >= 4).mean() * 100), 1)
    rep = round(float((od.groupby("customer_unique_id")["order_id"].nunique() > 1).mean() * 100), 1)
    mape = float(backtest["绝对误差率%"].mean())
    rmse = float(np.sqrt(np.mean((backtest["实际GMV"] - backtest["预测GMV"]) ** 2)))
    black_friday = float(forecast.loc[forecast["月份"] == "2018-11", "点预测GMV"].iloc[0])
    start = d["order_purchase_timestamp"].min().strftime("%Y.%m")
    end = d["order_purchase_timestamp"].max().strftime("%Y.%m")

    gauge, liquid = kpi_gauges(good, rep)
    trend = trend_line(d)
    top10 = top10_bar(d)
    bcg_chart = bcg_scatter(bcg.head(12))

    # 品类下钻数据：点击 Top10 或 BCG 图表后更新同页指标，不跳转外部页面。
    drill = {}
    cat_all = d.groupby("category_english").agg(
        GMV=("item_gmv", "sum"), 订单数=("order_id", "nunique"),
        平均评分=("review_score", "mean"), 平均交付天数=("delivery_days", "mean"),
    )
    cat_all["排名"] = cat_all["GMV"].rank(ascending=False, method="min").astype(int)
    for cat, r in cat_all.iterrows():
        drill[cn(cat)] = {
            "gmv": round(float(r["GMV"]) / 10000, 1), "orders": int(r["订单数"]),
            "aov": round(float(r["GMV"]) / int(r["订单数"]), 1),
            "score": round(float(r["平均评分"]), 2) if pd.notna(r["平均评分"]) else None,
            "days": round(float(r["平均交付天数"]), 1) if pd.notna(r["平均交付天数"]) else None,
            "rank": int(r["排名"]),
        }
    default_cat = cn(d.groupby("category_english")["item_gmv"].sum().idxmax())

    cards = {
        "trend": card(trend, "月度 GMV 趋势", "2017.01—2018.08；拖动底部滑块或滚轮缩放，峰值与均值自动标注", "full", "缩放 / 提示"),
        "good": card(gauge, "服务体验：好评率", "4—5 星订单占已交付订单比例", "third", "体验指标"),
        "repeat": card(liquid, "客户经营：复购率", "购买 2 次及以上客户占独立客户比例", "third", "风险指标"),
        "pay": card(pay_pie(d), "支付方式结构", "按订单支付金额汇总；点击图例可筛选", "third", "图例筛选"),
        "calendar": card(calendar_heat(d), "2018 年日订单热力", "颜色越亮代表订单越多；悬停查看单日订单量", "half", "日期下钻"),
        "funnel": card(funnel_chart(orders), "订单履约转化漏斗", "从下单到签收的关键流程转化；悬停查看订单数", "half", "流程诊断"),
        "top10": card(top10, "Top10 品类 GMV", "点击条形可在下方查看品类订单、客单价、评分与交付时效", "half", "点击下钻"),
        "timeline": card(quarterly_timeline(d), "季度品类 Top8 时间轴", "点击播放或拖动时间轴，观察品类结构随季度变化", "half", "时间轴联动"),
        "bcg": card(bcg_chart, "BCG 品类增长—份额矩阵", "GMV Top12；横轴为相对市场份额，纵轴为 2018H1 同比增速；点击气泡可下钻", "half", "点击下钻"),
        "apriori": card(apriori_scatter(rules), "Apriori 品类关联规则", "气泡大小表示支持度；Lift > 1 表示正向关联", "half", "关联探索"),
        "rfm": card(rfm_bar(seg), "RFM 八分类 GMV 贡献", "八类客户价值结构；悬停查看各层 GMV 占比", "half", "客户分层"),
        "cohort": card(cohort_heatmap(cohort), "同期群留存热力图", "2017 年起首购客户在 M+0 至 M+12 的留存率（%）", "half", "留存追踪"),
        "forecast": card(sarima_chart(monthly, forecast), "SARIMA 月度 GMV 预测", "历史 20 个月 + 未来 6 个月；绿色阴影为 95% 置信区间", "full", "95% 置信区间"),
    }

    html = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%2300d9a3'/%3E%3Cpath d='M8 22V12m8 10V6m8 16v-7' stroke='%2317201f' stroke-width='4'/%3E%3C/svg%3E">
<title>Olist 巴西电商经营分析大屏</title>
<script src="https://assets.pyecharts.org/assets/v6/echarts.min.js"></script>
<script src="https://assets.pyecharts.org/assets/v6/echarts-liquidfill.min.js"></script>
<style>{CSS}</style></head><body id="top"><main class="shell">
<header class="hero"><div><p class="kicker">COMMERCIAL DATA ANALYSIS · OLIST BRAZIL</p><h1>Olist 巴西电商经营分析大屏</h1>
<p class="subtitle">数据区间：{start}—{end}｜来源：Kaggle Olist 公开数据集｜口径：已交付订单｜全 Python 实现</p></div>
<div class="hero-meta"><div class="status">14 个分析组件 · 可交互</div><div>RFM / 同期群 / BCG / SARIMA / Apriori / ABC</div></div></header>
<nav class="nav" aria-label="页面分区"><a href="#overview">经营总览</a><a href="#category">品类与交易结构</a><a href="#customer">客户价值</a><a href="#forecast">预测与决策</a></nav>
<section class="kpis" aria-label="核心经营指标">
<div class="kpi"><span class="label">累计 GMV</span><strong>{total_gmv/1e4:,.1f} 万</strong><small>雷亚尔 · 已交付订单</small></div>
<div class="kpi"><span class="label">成交订单</span><strong>{order_n:,}</strong><small>去重订单数</small></div>
<div class="kpi"><span class="label">独立客户</span><strong>{customer_n:,}</strong><small>customer_unique_id 去重</small></div>
<div class="kpi"><span class="label">订单客单价</span><strong>{aov:,.1f}</strong><small>雷亚尔 / 订单</small></div>
<div class="kpi"><span class="label">好评率</span><strong>{good:.1f}%</strong><small>4—5 星评价占比</small></div>
<div class="kpi"><span class="label">复购率</span><strong>{rep:.1f}%</strong><small>客户留存是核心短板</small></div></section>
<section class="insight-strip" aria-label="管理摘要"><div class="insight"><b class="mint">增长：销售规模快速扩张</b><p>2017 年 GMV 持续上行，11 月大促形成显著峰值，趋势图支持缩放核验。</p></div>
<div class="insight"><b class="gold">风险：高增长伴随低留存</b><p>复购率仅 {rep:.1f}%，次月平均留存约 5.45%，获客成果尚未充分转化为长期价值。</p></div>
<div class="insight"><b>机会：客户召回与品类组合</b><p>重要发展及重要挽留客户贡献 78.02% GMV；健康美妆、家居搭配与黑五备货值得优先投入。</p></div></section>
<section class="section" id="overview"><div class="section-head"><div><h2>经营总览</h2><p>先看规模与趋势，再定位体验、复购和履约问题</p></div><span class="index">01 · OVERVIEW</span></div>
<div class="grid">{cards['trend']}{cards['good']}{cards['repeat']}{cards['pay']}{cards['calendar']}{cards['funnel']}</div></section>
<section class="section" id="category"><div class="section-head"><div><h2>品类与交易结构</h2><p>销售排行 × 季度迁移 × 增长份额 × 搭配购买</p></div><span class="index">02 · CATEGORY</span></div>
<div class="grid">{cards['top10']}{cards['timeline']}{cards['bcg']}{cards['apriori']}</div>
<aside class="drilldown" aria-live="polite"><div class="drill-head"><div><h3 id="drill-title">{default_cat} · 品类下钻</h3><p>点击上方 Top10 条形或 BCG 气泡切换品类</p></div><span id="drill-rank">GMV 排名第 1</span></div>
<div class="drill-metrics"><div><small>累计 GMV</small><b id="drill-gmv">—</b></div><div><small>成交订单</small><b id="drill-orders">—</b></div><div><small>品类客单价</small><b id="drill-aov">—</b></div><div><small>平均评分</small><b id="drill-score">—</b></div><div><small>平均交付天数</small><b id="drill-days">—</b></div></div></aside></section>
<section class="section" id="customer"><div class="section-head"><div><h2>客户价值</h2><p>识别高贡献客户、观察留存，并把分层结果落到运营名单</p></div><span class="index">03 · CUSTOMER</span></div>
<div class="grid">{cards['rfm']}{cards['cohort']}{rfm_table_html(seg)}</div></section>
<section class="section" id="forecast"><div class="section-head"><div><h2>预测与商业决策</h2><p>用回测误差约束预测解释，再把预测转化为备货与客户运营动作</p></div><span class="index">04 · FORECAST</span></div>
<div class="grid">{cards['forecast']}</div><div class="model-note"><span><b>{mape:.2f}%</b>最近 6 个月回测 MAPE</span><span><b>{rmse/1e4:.2f} 万</b>回测 RMSE（雷亚尔）</span><span><b>{black_friday/1e4:.1f} 万</b>2018 年 11 月点预测 GMV</span><span>模型：SARIMA (1,1,1)(1,0,1,12)</span></div>
<div class="decision-grid"><article class="decision"><h3>优先召回高贡献客户</h3><p>对重要挽留客户设置 30/60/90 天分层召回；对重要发展客户推动二单转化，优先解决低复购。</p></article>
<article class="decision"><h3>按品类角色配置资源</h3><p>健康美妆与腕表礼品守住份额，家居用品和汽车配件承接增长；搭配销售优先采用 Lift 较高的规则。</p></article>
<article class="decision"><h3>黑五采用区间备货</h3><p>11 月点预测约 {black_friday/1e4:.1f} 万雷亚尔，并结合 95% 置信区间设置安全库存与弹性履约能力。</p></article></div></section>
<footer class="footer"><span>商业数据分析期末项目 · 所有图表与页面由 Python 代码生成</span><span>数据仅用于课程学习 · <a href="#top">返回顶部</a></span></footer>
</main>
<script>
const CATEGORY_DATA = {json.dumps(drill, ensure_ascii=False)};
function updateCategory(name) {{
  const v = CATEGORY_DATA[name]; if (!v) return;
  document.getElementById('drill-title').textContent = name + ' · 品类下钻';
  document.getElementById('drill-rank').textContent = 'GMV 排名第 ' + v.rank;
  document.getElementById('drill-gmv').textContent = v.gmv.toLocaleString() + ' 万';
  document.getElementById('drill-orders').textContent = v.orders.toLocaleString();
  document.getElementById('drill-aov').textContent = v.aov.toLocaleString() + ' 雷亚尔';
  document.getElementById('drill-score').textContent = v.score === null ? '暂无' : v.score + ' / 5';
  document.getElementById('drill-days').textContent = v.days === null ? '暂无' : v.days + ' 天';
}}
chart_{top10.chart_id}.on('click', p => updateCategory(p.name));
chart_{bcg_chart.chart_id}.on('click', p => updateCategory(p.name));
updateCategory({json.dumps(default_cat, ensure_ascii=False)});
const charts = Object.keys(window).filter(k => k.startsWith('chart_')).map(k => window[k]).filter(v => v && typeof v.resize === 'function');
let resizeTimer; window.addEventListener('resize', () => {{ clearTimeout(resizeTimer); resizeTimer = setTimeout(() => charts.forEach(c => c.resize()), 120); }});
</script></body></html>'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[大屏] 14 个分析组件（13 图表 + 1 明细表）-> {OUT}")
    print("[大屏] 交互能力：悬停提示 / 区域缩放 / 图例筛选 / 季度时间轴联动 / 品类点击下钻")


if __name__ == "__main__":
    main()
