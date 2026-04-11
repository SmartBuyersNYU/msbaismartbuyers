"""
Model Outputs Dashboard
=======================
Streamlit app showcasing three model outputs:
  1. CII 2026 Final Model
  2. OOS Elasticity Final Model
  3. Price Momentum Final Model

Run with:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Model Outputs Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ───────────────────────────────────────────────────────────────────
COLORS = {
    "primary": "#4F46E5",
    "success": "#10B981",
    "warning": "#F59E0B",
    "danger": "#EF4444",
    "neutral": "#6B7280",
    "bg": "#F9FAFB",
}

RISK_COLORS = {
    "Low": "#10B981",
    "Moderate": "#F59E0B",
    "Elevated": "#F97316",
    "High": "#EF4444",
}

COMPETITION_COLORS = {
    "Low Competition": "#10B981",
    "Moderate Competition": "#F59E0B",
    "High Competition": "#F97316",
    "Very High Competition": "#EF4444",
}

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    .main {background-color: #F9FAFB;}
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        border-left: 4px solid #4F46E5;
        margin-bottom: 1rem;
    }
    .metric-card h3 {margin: 0; font-size: 0.85rem; color: #6B7280; font-weight: 500;}
    .metric-card p {margin: 0; font-size: 1.7rem; font-weight: 700; color: #111827;}
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
        border-bottom: 2px solid #E5E7EB;
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {gap: 8px;}
    div[data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Search the script directory AND a data/ subfolder inside it
    search_dirs = [
        script_dir,
        os.path.join(script_dir, "data"),
        ".",
        os.path.join(".", "data"),
    ]
    files = {
        "cii": "CII_2026_Final_Model.csv",
        "oos": "OOS_Elasticity_Final_Model.csv",
        "pm": "Price_Momentum_Final_Model.csv",
    }
    dfs = {}
    for key, fname in files.items():
        for d in search_dirs:
            path = os.path.join(d, fname)
            if os.path.exists(path):
                dfs[key] = pd.read_csv(path)
                break
        if key not in dfs:
            st.error(
                f"Could not find **{fname}**.\n\n"
                "Make sure the CSV files are either:\n"
                "- In the same folder as `app.py`, or\n"
                "- In a `data/` subfolder next to `app.py`"
            )
            st.stop()
    return dfs["cii"], dfs["oos"], dfs["pm"]


df_cii, df_oos, df_pm = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Single_apple.png/240px-Single_apple.png",
        width=60,
    )
    st.title("Model Dashboard")
    st.caption("Analytics & Model Outputs")
    st.divider()

    active_tab = st.radio(
        "Navigate to",
        ["🏠 Overview", "📈 CII 2026", "📦 OOS Elasticity", "💰 Price Momentum"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(
        f"**Data summary**\n\n"
        f"CII rows: {len(df_cii):,}\n\n"
        f"OOS rows: {len(df_oos):,}\n\n"
        f"Price Momentum rows: {len(df_pm):,}"
    )

# ── Helper: metric card ───────────────────────────────────────────────────────
def metric(label, value, border_color=None):
    color = border_color or COLORS["primary"]
    st.markdown(
        f"""<div class="metric-card" style="border-left-color:{color};">
        <h3>{label}</h3>
        <p>{value}</p>
        </div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW TAB
# ══════════════════════════════════════════════════════════════════════════════
if active_tab == "🏠 Overview":
    st.title("📊 Model Outputs Overview")
    st.markdown(
        "High-level summary of all three models. Use the sidebar to drill into each."
    )
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric("CII Subcategories", df_cii["subcategory"].nunique(), COLORS["primary"])
    with col2:
        metric("Avg CII Score (2026)", f"{df_cii['cii'].mean():.2f}", COLORS["primary"])
    with col3:
        metric("OOS Products", f"{len(df_oos):,}", COLORS["warning"])
    with col4:
        metric("Price Momentum ASINs", f"{len(df_pm):,}", COLORS["success"])

    st.markdown("---")
    col_a, col_b, col_c = st.columns(3)

    # CII mini chart
    with col_a:
        st.markdown('<div class="section-header">CII 2026 — Avg by Quarter</div>', unsafe_allow_html=True)
        cii_q = df_cii.groupby("quarter")["cii"].mean().reset_index()
        fig = px.bar(
            cii_q, x="quarter", y="cii",
            color="cii", color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
            labels={"cii": "Avg CII", "quarter": ""},
            height=280,
        )
        fig.update_layout(margin=dict(t=10, b=10), showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # OOS Risk mini donut
    with col_b:
        st.markdown('<div class="section-header">OOS Risk Level Distribution</div>', unsafe_allow_html=True)
        oos_risk = df_oos["OOS_Risk_Level"].value_counts().reset_index()
        oos_risk.columns = ["Risk Level", "Count"]
        fig = px.pie(
            oos_risk, names="Risk Level", values="Count",
            color="Risk Level", color_discrete_map=RISK_COLORS,
            hole=0.55, height=280,
        )
        fig.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

    # PM Signal mini donut
    with col_c:
        st.markdown('<div class="section-header">Price Momentum Signal Mix</div>', unsafe_allow_html=True)
        pm_sig = df_pm["Price_Momentum_Signal"].value_counts().reset_index()
        pm_sig.columns = ["Signal", "Count"]
        fig = px.pie(
            pm_sig, names="Signal", values="Count",
            hole=0.55, height=280,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h", y=-0.3))
        st.plotly_chart(fig, use_container_width=True)

    # Demand-Price quadrant heatmap
    st.markdown("---")
    st.markdown('<div class="section-header">Price Momentum — Demand-Price Quadrant × Momentum Signal</div>', unsafe_allow_html=True)
    heat = (
        df_pm.groupby(["Demand_Price_Quadrant", "Price_Momentum_Signal"])
        .size()
        .reset_index(name="Count")
    )
    pivot = heat.pivot(index="Demand_Price_Quadrant", columns="Price_Momentum_Signal", values="Count").fillna(0)
    fig = px.imshow(
        pivot,
        color_continuous_scale="Blues",
        labels=dict(x="Momentum Signal", y="Demand-Price Quadrant", color="Count"),
        aspect="auto",
        height=300,
        text_auto=True,
    )
    fig.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# CII 2026 TAB
# ══════════════════════════════════════════════════════════════════════════════
elif active_tab == "📈 CII 2026":
    st.title("📈 Category Intensity Index (CII) 2026")
    st.caption("Quarterly competitive intensity forecast by subcategory.")
    st.divider()

    # Filters
    col_f1, col_f2 = st.columns([2, 2])
    with col_f1:
        selected_quarters = st.multiselect(
            "Quarter", df_cii["quarter"].unique().tolist(),
            default=df_cii["quarter"].unique().tolist(),
        )
    with col_f2:
        selected_comp = st.multiselect(
            "Competition Level", df_cii["competition_level"].unique().tolist(),
            default=df_cii["competition_level"].unique().tolist(),
        )

    filtered = df_cii[
        df_cii["quarter"].isin(selected_quarters) &
        df_cii["competition_level"].isin(selected_comp)
    ]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric("Subcategories", filtered["subcategory"].nunique())
    with c2:
        metric("Avg CII", f"{filtered['cii'].mean():.3f}", COLORS["primary"])
    with c3:
        metric("Max CII", f"{filtered['cii'].max():.3f}", COLORS["danger"])
    with c4:
        metric("Min CII", f"{filtered['cii'].min():.3f}", COLORS["success"])

    st.divider()

    # CII by subcategory heatmap (quarters as columns)
    st.markdown('<div class="section-header">CII Heat Map — Subcategory × Quarter</div>', unsafe_allow_html=True)
    pivot_cii = filtered.pivot_table(index="subcategory", columns="quarter", values="cii", aggfunc="mean")
    fig_heat = px.imshow(
        pivot_cii,
        color_continuous_scale=["#EF4444", "#FFFFFF", "#10B981"],
        color_continuous_midpoint=0,
        aspect="auto",
        height=500,
        labels=dict(x="Quarter", y="Subcategory", color="CII"),
        text_auto=".2f",
    )
    fig_heat.update_layout(margin=dict(t=20, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

    # CII trend lines
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown('<div class="section-header">CII Trend by Quarter</div>', unsafe_allow_html=True)
        trend = filtered.groupby(["quarter", "competition_level"])["cii"].mean().reset_index()
        fig_trend = px.line(
            trend, x="quarter", y="cii", color="competition_level",
            color_discrete_map=COMPETITION_COLORS,
            markers=True,
            labels={"cii": "Avg CII", "quarter": "", "competition_level": "Competition"},
            height=320,
        )
        fig_trend.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Competition Level Mix per Quarter</div>', unsafe_allow_html=True)
        comp_mix = (
            filtered.groupby(["quarter", "competition_level"])
            .size()
            .reset_index(name="count")
        )
        fig_bar = px.bar(
            comp_mix, x="quarter", y="count", color="competition_level",
            barmode="stack",
            color_discrete_map=COMPETITION_COLORS,
            labels={"count": "# Subcategories", "quarter": "", "competition_level": ""},
            height=320,
        )
        fig_bar.update_layout(margin=dict(t=20, b=20), legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig_bar, use_container_width=True)

    # Top/bottom subcategories
    st.markdown('<div class="section-header">Top 10 Highest CII Subcategories (Avg across selected quarters)</div>', unsafe_allow_html=True)
    top10 = (
        filtered.groupby("subcategory")["cii"].mean()
        .sort_values(ascending=False).head(10).reset_index()
    )
    fig_top = px.bar(
        top10, x="cii", y="subcategory", orientation="h",
        color="cii", color_continuous_scale=["#F59E0B", "#EF4444"],
        labels={"cii": "Avg CII", "subcategory": ""},
        height=340,
    )
    fig_top.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig_top, use_container_width=True)

    with st.expander("📄 View Raw Data"):
        st.dataframe(filtered.sort_values("cii", ascending=False), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# OOS ELASTICITY TAB
# ══════════════════════════════════════════════════════════════════════════════
elif active_tab == "📦 OOS Elasticity":
    st.title("📦 OOS Elasticity Model")
    st.caption("Out-of-stock risk scoring and elasticity signal analysis per ASIN.")
    st.divider()

    # Sidebar filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        risk_filter = st.multiselect(
            "OOS Risk Level",
            df_oos["OOS_Risk_Level"].unique().tolist(),
            default=df_oos["OOS_Risk_Level"].unique().tolist(),
        )
    with col_f2:
        elastic_filter = st.multiselect(
            "Elasticity Signal",
            df_oos["Elasticity_Signal"].unique().tolist(),
            default=df_oos["Elasticity_Signal"].unique().tolist(),
        )
    with col_f3:
        brand_search = st.text_input("Brand filter (partial match)", "")

    filt_oos = df_oos[
        df_oos["OOS_Risk_Level"].isin(risk_filter) &
        df_oos["Elasticity_Signal"].isin(elastic_filter)
    ]
    if brand_search:
        filt_oos = filt_oos[filt_oos["brand"].str.contains(brand_search, case=False, na=False)]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric("ASINs in View", f"{len(filt_oos):,}", COLORS["primary"])
    with c2:
        pct_high = (filt_oos["OOS_Risk_Level"] == "High").mean() * 100
        metric("% High Risk", f"{pct_high:.1f}%", COLORS["danger"])
    with c3:
        metric("Avg OOS Rate", f"{filt_oos['OOS_Rate'].mean():.2%}", COLORS["warning"])
    with c4:
        metric("Avg Risk Score (GB)", f"{filt_oos['OOS_Risk_Score_GB'].mean():.3f}", COLORS["primary"])

    st.divider()

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">OOS Risk Level Distribution</div>', unsafe_allow_html=True)
        rc = filt_oos["OOS_Risk_Level"].value_counts().reset_index()
        rc.columns = ["Risk Level", "Count"]
        fig_rc = px.bar(
            rc, x="Risk Level", y="Count",
            color="Risk Level", color_discrete_map=RISK_COLORS,
            text_auto=True, height=300,
        )
        fig_rc.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig_rc, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Elasticity Signal Distribution</div>', unsafe_allow_html=True)
        ec = filt_oos["Elasticity_Signal"].value_counts().reset_index()
        ec.columns = ["Signal", "Count"]
        fig_ec = px.bar(
            ec, x="Count", y="Signal", orientation="h",
            color="Count", color_continuous_scale="Blues",
            text_auto=True, height=300,
        )
        fig_ec.update_layout(showlegend=False, margin=dict(t=10, b=10), coloraxis_showscale=False,
                             yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_ec, use_container_width=True)

    # Scatter: OOS Risk Score vs Elasticity Proxy Mean
    st.markdown('<div class="section-header">OOS Risk Score vs. Elasticity Proxy Mean</div>', unsafe_allow_html=True)
    scatter_df = filt_oos.dropna(subset=["OOS_Risk_Score_GB", "Elasticity_Proxy_Mean"])
    if len(scatter_df) > 0:
        fig_sc = px.scatter(
            scatter_df,
            x="OOS_Risk_Score_GB",
            y="Elasticity_Proxy_Mean",
            color="OOS_Risk_Level",
            color_discrete_map=RISK_COLORS,
            hover_data=["asin", "brand", "Elasticity_Signal"],
            opacity=0.65,
            labels={
                "OOS_Risk_Score_GB": "OOS Risk Score (GB)",
                "Elasticity_Proxy_Mean": "Elasticity Proxy Mean",
                "OOS_Risk_Level": "Risk Level",
            },
            height=380,
        )
        fig_sc.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig_sc, use_container_width=True)
    else:
        st.info("No data with both risk score and elasticity for current filters.")

    # OOS Rate histogram
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown('<div class="section-header">OOS Rate Distribution</div>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            filt_oos, x="OOS_Rate", color="OOS_Risk_Level",
            color_discrete_map=RISK_COLORS,
            nbins=40, barmode="overlay", opacity=0.75,
            labels={"OOS_Rate": "OOS Rate", "OOS_Risk_Level": "Risk"},
            height=280,
        )
        fig_hist.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_h2:
        st.markdown('<div class="section-header">Max OOS Streak by Risk Level</div>', unsafe_allow_html=True)
        box_df = filt_oos.dropna(subset=["Max_OOS_Streak"])
        fig_box = px.box(
            box_df, x="OOS_Risk_Level", y="Max_OOS_Streak",
            color="OOS_Risk_Level", color_discrete_map=RISK_COLORS,
            labels={"Max_OOS_Streak": "Max OOS Streak (periods)", "OOS_Risk_Level": ""},
            height=280,
        )
        fig_box.update_layout(showlegend=False, margin=dict(t=10, b=10))
        st.plotly_chart(fig_box, use_container_width=True)

    # Risk × Elasticity cross-table
    st.markdown('<div class="section-header">Risk × Elasticity Signal Cross-Table</div>', unsafe_allow_html=True)
    cross = pd.crosstab(filt_oos["OOS_Risk_Level"], filt_oos["Elasticity_Signal"])
    fig_cross = px.imshow(
        cross, text_auto=True, aspect="auto",
        color_continuous_scale="OrRd", height=300,
    )
    fig_cross.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig_cross, use_container_width=True)

    # Top high-risk brands
    st.markdown('<div class="section-header">Top 15 Brands by High-Risk ASIN Count</div>', unsafe_allow_html=True)
    brand_risk = (
        filt_oos[filt_oos["OOS_Risk_Level"] == "High"]
        .groupby("brand").size()
        .sort_values(ascending=False).head(15).reset_index()
    )
    brand_risk.columns = ["Brand", "High Risk ASINs"]
    fig_brand = px.bar(
        brand_risk, x="High Risk ASINs", y="Brand", orientation="h",
        color="High Risk ASINs", color_continuous_scale="Reds",
        height=380, text_auto=True,
    )
    fig_brand.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig_brand, use_container_width=True)

    with st.expander("📄 View Raw Data"):
        show_cols = ["asin", "brand", "buy_box_current", "OOS_Rate", "Max_OOS_Streak",
                     "OOS_Risk_Score_GB", "OOS_Risk_Level", "Elasticity_Signal", "Elasticity_Proxy_Mean"]
        st.dataframe(filt_oos[show_cols].sort_values("OOS_Risk_Score_GB", ascending=False), use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PRICE MOMENTUM TAB
# ══════════════════════════════════════════════════════════════════════════════
elif active_tab == "💰 Price Momentum":
    st.title("💰 Price Momentum Model")
    st.caption("Price momentum signals, competition dynamics, and demand-price quadrant analysis.")
    st.divider()

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        period_filter = st.multiselect(
            "Period", sorted(df_pm["Period"].unique().tolist()),
            default=sorted(df_pm["Period"].unique().tolist()),
        )
    with col_f2:
        signal_filter = st.multiselect(
            "Momentum Signal",
            df_pm["Price_Momentum_Signal"].unique().tolist(),
            default=df_pm["Price_Momentum_Signal"].unique().tolist(),
        )
    with col_f3:
        margin_filter = st.multiselect(
            "Margin Gate",
            df_pm["Margin_Gate"].dropna().unique().tolist(),
            default=df_pm["Margin_Gate"].dropna().unique().tolist(),
        )

    filt_pm = df_pm[
        df_pm["Period"].isin(period_filter) &
        df_pm["Price_Momentum_Signal"].isin(signal_filter) &
        df_pm["Margin_Gate"].isin(margin_filter)
    ]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric("ASINs in View", f"{len(filt_pm):,}", COLORS["primary"])
    with c2:
        pct_pos = (filt_pm["Momentum_Direction"] == "Positive").mean() * 100
        metric("% Positive Momentum", f"{pct_pos:.1f}%", COLORS["success"])
    with c3:
        avg_mom = filt_pm["Price_Momentum_Pct"].mean()
        metric("Avg Momentum %", f"{avg_mom:.2f}%", COLORS["primary"])
    with c4:
        avg_margin = filt_pm["Margin_Proxy"].mean()
        metric("Avg Margin Proxy", f"${avg_margin:.2f}", COLORS["success"])

    st.divider()

    # Momentum signal bar + direction pie
    col_l, col_r = st.columns([3, 2])
    with col_l:
        st.markdown('<div class="section-header">Price Momentum Signal Distribution</div>', unsafe_allow_html=True)
        sig_cnt = filt_pm["Price_Momentum_Signal"].value_counts().reset_index()
        sig_cnt.columns = ["Signal", "Count"]
        SIGNAL_COLORS = {
            "Strong Positive": "#10B981",
            "Positive (Low Confidence)": "#6EE7B7",
            "Neutral": "#9CA3AF",
            "Negative (Noisy)": "#FCA5A5",
            "Negative (Confirmed)": "#EF4444",
            "Strong Negative": "#991B1B",
            "Insufficient Data": "#D1D5DB",
            "AVOID (Margin Fail)": "#7F1D1D",
        }
        fig_sig = px.bar(
            sig_cnt, x="Count", y="Signal", orientation="h",
            color="Signal", color_discrete_map=SIGNAL_COLORS,
            text_auto=True, height=320,
        )
        fig_sig.update_layout(showlegend=False, margin=dict(t=10, b=10),
                              yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_sig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-header">Momentum Direction</div>', unsafe_allow_html=True)
        dir_cnt = filt_pm["Momentum_Direction"].value_counts().reset_index()
        dir_cnt.columns = ["Direction", "Count"]
        DIR_COLORS = {"Positive": "#10B981", "Neutral": "#9CA3AF", "Negative": "#EF4444"}
        fig_dir = px.pie(
            dir_cnt, names="Direction", values="Count",
            color="Direction", color_discrete_map=DIR_COLORS,
            hole=0.5, height=320,
        )
        fig_dir.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_dir, use_container_width=True)

    # Demand-Price quadrant
    st.markdown('<div class="section-header">Demand-Price Quadrant Analysis</div>', unsafe_allow_html=True)
    quad_cnt = filt_pm["Demand_Price_Quadrant"].value_counts().reset_index()
    quad_cnt.columns = ["Quadrant", "Count"]
    QUAD_COLORS = {
        "Rising Demand + Rising Price": "#10B981",
        "Rising Demand + Falling Price": "#F59E0B",
        "Falling Demand + Rising Price": "#F97316",
        "Falling Demand + Falling Price": "#EF4444",
    }
    fig_quad = px.bar(
        quad_cnt, x="Quadrant", y="Count",
        color="Quadrant", color_discrete_map=QUAD_COLORS,
        text_auto=True, height=320,
    )
    fig_quad.update_layout(showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig_quad, use_container_width=True)

    # Price momentum % histogram + scatter
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown('<div class="section-header">Price Momentum % Distribution</div>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            filt_pm.dropna(subset=["Price_Momentum_Pct"]),
            x="Price_Momentum_Pct", nbins=50,
            color_discrete_sequence=[COLORS["primary"]],
            labels={"Price_Momentum_Pct": "Price Momentum %"},
            height=300,
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="red", opacity=0.6)
        fig_hist.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_h2:
        st.markdown('<div class="section-header">BuyBox Current vs. 90-Day Avg</div>', unsafe_allow_html=True)
        bb_df = filt_pm.dropna(subset=["BuyBox_Current", "BuyBox_90d_Avg"]).sample(min(800, len(filt_pm)), random_state=42)
        fig_bb = px.scatter(
            bb_df, x="BuyBox_90d_Avg", y="BuyBox_Current",
            color="Momentum_Direction",
            color_discrete_map=DIR_COLORS,
            opacity=0.5,
            labels={"BuyBox_90d_Avg": "90-Day Avg Price ($)", "BuyBox_Current": "Current Price ($)"},
            height=300,
        )
        # Diagonal reference line
        max_val = max(bb_df["BuyBox_90d_Avg"].max(), bb_df["BuyBox_Current"].max())
        fig_bb.add_trace(
            go.Scatter(x=[0, max_val], y=[0, max_val], mode="lines",
                       line=dict(dash="dot", color="gray"), name="No change", showlegend=True)
        )
        fig_bb.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig_bb, use_container_width=True)

    # Momentum over periods
    st.markdown('<div class="section-header">Avg Price Momentum % by Period</div>', unsafe_allow_html=True)
    period_order = sorted(filt_pm["Period"].unique())
    period_mom = (
        filt_pm.groupby("Period")["Price_Momentum_Pct"].mean()
        .reindex(period_order).reset_index()
    )
    period_mom.columns = ["Period", "Avg Momentum %"]
    fig_per = px.line(
        period_mom, x="Period", y="Avg Momentum %",
        markers=True, height=300,
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig_per.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    fig_per.update_layout(margin=dict(t=10, b=10))
    st.plotly_chart(fig_per, use_container_width=True)

    # Competition risk
    col_cr1, col_cr2 = st.columns(2)
    with col_cr1:
        st.markdown('<div class="section-header">Competition Risk Distribution</div>', unsafe_allow_html=True)
        cr_cnt = filt_pm["Competition_Risk"].value_counts().reset_index()
        cr_cnt.columns = ["Competition Risk", "Count"]
        fig_cr = px.pie(cr_cnt, names="Competition Risk", values="Count",
                        hole=0.5, height=280,
                        color_discrete_sequence=px.colors.sequential.Oranges_r)
        fig_cr.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_cr, use_container_width=True)

    with col_cr2:
        st.markdown('<div class="section-header">Signal Confidence Distribution</div>', unsafe_allow_html=True)
        sc_cnt = filt_pm["Signal_Confidence"].value_counts().reset_index()
        sc_cnt.columns = ["Confidence", "Count"]
        fig_sc = px.bar(sc_cnt, x="Confidence", y="Count", text_auto=True,
                        color="Count", color_continuous_scale="Blues",
                        height=280)
        fig_sc.update_layout(margin=dict(t=10, b=10), coloraxis_showscale=False)
        st.plotly_chart(fig_sc, use_container_width=True)

    # Top subcategories by avg momentum
    st.markdown('<div class="section-header">Top 15 Subcategories by Avg Price Momentum %</div>', unsafe_allow_html=True)
    sub_mom = (
        filt_pm.groupby("Subcategory")["Price_Momentum_Pct"].mean()
        .sort_values(ascending=False).head(15).reset_index()
    )
    sub_mom.columns = ["Subcategory", "Avg Momentum %"]
    fig_sub = px.bar(
        sub_mom, x="Avg Momentum %", y="Subcategory", orientation="h",
        color="Avg Momentum %",
        color_continuous_scale=["#EF4444", "#F9FAFB", "#10B981"],
        color_continuous_midpoint=0,
        text_auto=".1f", height=420,
    )
    fig_sub.update_layout(yaxis=dict(autorange="reversed"), margin=dict(t=10, b=10), coloraxis_showscale=False)
    st.plotly_chart(fig_sub, use_container_width=True)

    with st.expander("📄 View Raw Data"):
        show_cols = ["ASIN", "Brand", "Subcategory", "Period", "BuyBox_Current",
                     "Price_Momentum_Pct", "Momentum_Direction", "Price_Momentum_Signal",
                     "Demand_Price_Quadrant", "Margin_Proxy", "Margin_Gate"]
        st.dataframe(filt_pm[show_cols].sort_values("Price_Momentum_Pct", ascending=False), use_container_width=True)
