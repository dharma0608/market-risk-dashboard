import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import sys
import pathlib

page = st.sidebar.selectbox(
    "Navigate",
    ["🏠 Overview", "📊 Dashboard"]
)

trading_bg_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.pexels.com/photos/7887800/pexels-photo-7887800.jpeg");
    background-size: cover;
    background-position: center;
}
[data-testid="stHeader"] {
    background: rgba(0,0,0,0.0);
}
.block-container {
    background-color: rgba(0, 0, 0, 0.65);
    border-radius: 8px;
    padding: 1.5rem;
}
h1, h2, h3, h4, h5, h6, p, span {
    color: #f2f2f2 !important;
}
</style>
"""

st.markdown(trading_bg_css, unsafe_allow_html=True)


# Fix: Add project root to sys.path reliably
current_file = pathlib.Path(__file__)
project_root = current_file.parent.parent  # MarketRiskAgents/
sys.path.insert(0, str(project_root))

# Now import agents
try:
    from agents.data_agent import DataAgent
    from agents.model_agent import ModelAgent
    from agents.alert_agent import AlertAgent
except ImportError as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

from config import DATA_PATH, RISK_METRICS_PATH, ALERTS_PATH


 # === Page Setup ===
st.set_page_config(
    page_title="Market Risk Dashboard",
    page_icon="📊",
    layout="wide"
)


# === Title ===
st.title("📊 Market Risk Agent Dashboard")

if page == "🏠 Overview":
    st.title("📈 Market Risk AI Agent Suite")

    st.markdown("""
    Welcome to your **Market Risk AI Agent** project.

    This app uses multiple Python agents to:
    - Fetch real market data (AAPL, TSLA, SPY, GLD)
    - Compute portfolio risk (VaR, CVaR, volatility, drawdowns)
    - Generate automatic risk alerts

    Use the sidebar to switch to the **Dashboard** and explore the live risk metrics.
    """)
    st.subheader("Project Info")
    st.markdown("""
    Tech stack: Python, yfinance, pandas, NumPy, SciPy, Streamlit, Plotly.  
    Use case: Educational market risk dashboard with autonomous agents.  
    Author: Dharma - Financial Data Analysis student.
    """)

    # Optional: highlight features in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Agents", "3", "Data • Model • Alert")
    with col2:
        st.metric("Risk Metrics", "VaR / CVaR / Vol")
    with col3:
        st.metric("Universe", "Equities & Gold")

    st.subheader("How it works")
    st.markdown("""
    1. **Data Agent** downloads 1-year price history and builds portfolio returns.  
    2. **Model Agent** calculates 1-day VaR and CVaR at 95% and 99%.  
    3. **Alert Agent** checks thresholds and issues risk warnings.
    """)

if page == "📊 Dashboard":
    
    # === Run agents section ===
    st.header("1. Run Agents")

    if st.button("🚀 Run Data + Model + Alert pipeline"):
        with st.spinner("Running DataAgent..."):
            data_path = DataAgent().run()
            if data_path:
                st.success("✅ DataAgent done")

        with st.spinner("Running ModelAgent..."):
            metrics_path = ModelAgent().run()
            if metrics_path:
                st.success("✅ ModelAgent done")

        with st.spinner("Running AlertAgent..."):
            alerts_path = AlertAgent().run()
            if alerts_path:
                st.success("✅ AlertAgent done")

    # Always assume data exists
    data_path = DATA_PATH
    metrics_path = RISK_METRICS_PATH
    alerts_path = ALERTS_PATH

    # === Metrics section (KPIs) ===
    st.header("2. Current Market Risk Metrics")

    if os.path.exists(metrics_path):
        metrics_df = pd.read_csv(metrics_path)

        st.subheader("Value‑At‑Risk (1‑day)")

        # Show both 95% and 99%
        row = st.columns(2)

        row_95 = metrics_df[metrics_df['confidence'] == 0.95]
        if not row_95.empty:
            r = row_95.iloc[0]
            row[0].metric(
                "VaR (95%)",
                f"{r['parametric_VaR_1d']:.2f}%",
                help="Parametric 1‑day VaR (normal‑distribution assumption)"
            )
            row[0].metric(
                "CVaR (95%)",
                f"{r['parametric_CVaR_1d']:.2f}%",
                help="Average loss beyond VaR in the tail"
            )

        row_99 = metrics_df[metrics_df['confidence'] == 0.99]
        if not row_99.empty:
            r = row_99.iloc[0]
            row[1].metric(
                "VaR (99%)",
                f"{r['parametric_VaR_1d']:.2f}%",
                help="More extreme 1‑day VaR level"
            )
            row[1].metric(
                "CVaR (99%)",
                f"{r['parametric_CVaR_1d']:.2f}%",
                help="Average loss beyond VaR at 99% level"
            )
    else:
        st.warning("No risk metrics found. Run agents first.")


    # === Data loading ===
    st.header("3. Portfolio Returns & Volatility")

    if os.path.exists(data_path):
        returns_df = pd.read_csv(data_path, index_col='Date', parse_dates=True)

        # Charts as before...
        st.subheader("Portfolio daily returns over time")
        fig_returns = px.line(
            returns_df,
            x=returns_df.index,
            y='portfolio_returns',
            title="Daily Portfolio Returns",
            labels={'portfolio_returns': 'Return', 'Date': 'Date'}
        )
        st.plotly_chart(fig_returns, width="stretch")

        st.subheader("Rolling 20‑day volatility (annualized)")
        fig_vol = px.line(
            returns_df,
            x=returns_df.index,
            y='vol_20d',
            title="Rolling 20‑day annualized volatility",
            labels={'vol_20d': 'Volatility (%)', 'Date': 'Date'}
        )
        st.plotly_chart(fig_vol, width="stretch")

        # Max drawdown KPI
        returns_df['cum_return'] = (1 + returns_df['portfolio_returns']).cumprod()
        returns_df['drawdown'] = returns_df['cum_return'] / returns_df['cum_return'].cummax() - 1
        max_drawdown = returns_df['drawdown'].min()

        col1, col2, col3 = st.columns(3)
        col1.metric("Max Drawdown", f"{max_drawdown * 100:.2f}%")

    else:
        st.warning("No portfolio data found. Run DataAgent first.")


    # === Alerts section ===
    st.header("4. Risk Alerts")

    if os.path.exists(alerts_path):
        with open(alerts_path, 'r', encoding='utf-8') as f:
            alerts_lines = f.readlines()

        for line in alerts_lines:
            line = line.strip()
            if not line:
                continue

            if "CRITICAL RISK" in line:
                st.error(line)
            elif "HIGH RISK" in line:
                st.warning(line)
            elif "All clear" in line:
                st.success(line)
            else:
                st.write(line)
    else:
        st.warning("No alerts file found.")

    # == VaR / CVaR section ==
    st.header("5. VaR / CVaR Comparison")

    if os.path.exists(metrics_path):
        metrics_df = pd.read_csv(metrics_path)

        row_95 = metrics_df[metrics_df['confidence'] == 0.95]
        row_99 = metrics_df[metrics_df['confidence'] == 0.99]

        if not row_95.empty and not row_99.empty:
            r95 = row_95.iloc[0]
            r99 = row_99.iloc[0]

            bar_data = pd.DataFrame({
                "Metric": [
                    "Parametric VaR (95%)",
                    "Parametric VaR (99%)",
                    "Parametric CVaR (95%)",
                    "Parametric CVaR (99%)"
                ],
                "Value": [
                    r95['parametric_VaR_1d'],
                    r99['parametric_VaR_1d'],
                    r95['parametric_CVaR_1d'],
                    r99['parametric_CVaR_1d']
                ]
            })

            fig_bars = px.bar(
                bar_data,
                x="Metric",
                y="Value",
                title="VaR / CVaR Comparison",
                labels={"Value": "Loss % (1-day)"},
            )
            st.plotly_chart(fig_bars, width="stretch")
        else:
            st.warning("VaR data for 95% or 99% confidence not found.")
    else:
        st.warning("No risk metrics found. Run agents first.")

    #==volatility–returns section==
    st.header("6. Returns vs Volatility")

    if os.path.exists(data_path):
        # re‑use returns_df from earlier section
        returns_df_clean = returns_df.dropna()

        fig_scatter = px.scatter(
            returns_df_clean,
            x='vol_20d',
            y='portfolio_returns',
            title="Daily Returns vs Volatility",
            labels={"vol_20d": "20-day Volatility", "portfolio_returns": "Daily Return"}
        )
        st.plotly_chart(fig_scatter, width="stretch")
    else:
        st.warning("No portfolio data found. Run DataAgent first.")
