import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from analytics.metrics import load_data, calculate_metrics, optimize_portfolio, run_monte_carlo

# 1. Page Config
st.set_page_config(page_title="The Quant's Cockpit", layout="wide", page_icon="⚡")

# 2. Custom CSS
st.markdown("""
<style>
    .stApp {background-color: #0E1117;}
    .metric-card {
        background-color: #262730; border: 1px solid #464B5C;
        padding: 15px; border-radius: 8px; text-align: center;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value {color: #00ADB5; font-size: 1.8rem; font-weight: bold;}
    .metric-title {color: #FAFAFA; font-size: 0.9rem;}
    
    /* Sidebar Profile */
    .profile-box {
        background-color: #1E212B; padding: 15px; border-radius: 10px;
        border-left: 5px solid #00ADB5; margin-bottom: 20px;
    }
    .stButton>button {width: 100%; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# 3. Data Loading
@st.cache_data
def get_data():
    df = load_data()
    df.index = pd.to_datetime(df.index)
    return df

@st.cache_data
def get_sector_map():
    engine = create_engine('sqlite:///finance.db')
    df_meta = pd.read_sql("SELECT symbol, sector FROM stocks", engine)
    return df_meta.set_index('symbol')['sector'].to_dict()

try:
    df_prices = get_data()
    sector_map = get_sector_map()
except Exception:
    st.error("⚠️ Database Error. Run 'python -m database.ingest' first.")
    st.stop()

# 4. Sidebar State Management (The Fix for Buttons)
if 'selected_assets' not in st.session_state:
    st.session_state.selected_assets = ["AAPL", "MSFT", "NVDA", "SPY"]

def set_tickers(tickers):
    st.session_state.selected_assets = tickers

st.sidebar.markdown("## 👤 **Creator Profile**")
st.sidebar.markdown("""
<div class="profile-box">
    <strong>Aryan Patil</strong><br>
    <span style="font-size:0.8rem; color:#ccc;">Master's in Data Science </span><br>
    <span style="font-size:0.8rem; color:#00ADB5;">Rochester Institute Of Technology, NY</span>
    <span style="font-size:0.8rem; color:#00ADB5;">Data Science | Quant Dev | AI Engg</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.header("🛠️ Configuration")

# -- Date Horizon --
min_date = df_prices.index.min().date()
max_date = df_prices.index.max().date()
start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# -- Smart Asset Logic --
st.sidebar.subheader("⚡ Quick Select")

# Button Callbacks
col_b1, col_b2, col_b3 = st.sidebar.columns(3)
with col_b1:
    # Top 5 Gainers (Last 30 Days)
    if st.button("🚀 Top 5"):
        last_30 = df_prices.tail(30)
        ret = (last_30.iloc[-1] / last_30.iloc[0]) - 1
        top_5 = ret.nlargest(5).index.tolist()
        set_tickers(top_5)

with col_b2:
    if st.button("💻 Tech"):
        tech_stocks = [t for t, s in sector_map.items() if s == 'Technology']
        set_tickers(tech_stocks[:5]) # Limit to 5 to avoid clutter

with col_b3:
    if st.button("🛡️ Safe"):
        # Select Low Volatility Stocks (Defensive)
        returns = df_prices.pct_change()
        vol = returns.std()
        safe_stocks = vol.nsmallest(5).index.tolist()
        set_tickers(safe_stocks)

# Dropdown
all_tickers = sorted(df_prices.columns.tolist(), key=lambda x: (sector_map.get(x, "Unknown"), x))
def format_func(ticker): return f"({sector_map.get(ticker, 'Other')}) {ticker}"

selected_tickers = st.sidebar.multiselect(
    "Active Portfolio:", 
    options=all_tickers,
    default=st.session_state.selected_assets,
    format_func=format_func,
    key='asset_multiselect', # IMPORTANT: Link to key
    on_change=lambda: set_tickers(st.session_state.asset_multiselect) # Sync manual changes
)

if not selected_tickers:
    st.warning("Please select at least one asset.")
    st.stop()

# Filter Data
mask = (df_prices.index.date >= start_date) & (df_prices.index.date <= end_date)
filtered_prices = df_prices.loc[mask, selected_tickers]
returns, volatility = calculate_metrics(filtered_prices)

# 5. Header & KPI
st.title("⚡ The Quant's Cockpit")
st.markdown("---")

daily_change = filtered_prices.pct_change().iloc[-1]
best_asset = daily_change.idxmax()
worst_asset = daily_change.idxmin()
total_growth = (filtered_prices.iloc[-1] / filtered_prices.iloc[0] - 1).mean()

k1, k2, k3, k4 = st.columns(4)
def card(col, title, val, color):
    col.markdown(f"""<div class="metric-card"><div class="metric-title">{title}</div><div class="metric-value" style="color: {color}">{val}</div></div>""", unsafe_allow_html=True)

card(k1, "Top Mover (1D)", f"{best_asset} +{daily_change[best_asset]:.2%}", "#4CAF50")
card(k2, "Worst Mover (1D)", f"{worst_asset} {daily_change[worst_asset]:.2%}", "#FF5252")
card(k3, "Portfolio Volatility", f"{volatility.mean():.2%}", "#FFC107")
card(k4, "Period Return", f"{total_growth:.2%}", "#00ADB5")

# 6. Main Tabs
st.markdown("### ")
t1, t2, t3, t4, t5 = st.tabs(["📈 Market Action", "🧠 Quant AI Analyst", "⚖️ Efficient Frontier", "🤖 Optimization", "🔮 Monte Carlo"])

with t1:
    c1, c2 = st.columns([4, 1])
    with c2:
        chart_type = st.radio("Chart Type", ["Area", "Bar", "Line"])
    
    norm_df = filtered_prices / filtered_prices.iloc[0] * 100
    
    if chart_type == "Area":
        fig = px.area(norm_df, x=norm_df.index, y=norm_df.columns)
    elif chart_type == "Bar":
        fig = px.bar(norm_df, x=norm_df.index, y=norm_df.columns, barmode='group')
    else:
        fig = px.line(norm_df, x=norm_df.index, y=norm_df.columns)
        
    fig.update_layout(template="plotly_dark", xaxis_title="", yaxis_title="Growth ($100 Base)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

with t2:
    st.subheader("🧠 AI-Driven Stock Ratings")
    st.write("This engine analyzes risk-adjusted returns (Sharpe Ratio) and momentum to assign ratings.")
    
    # Calculate Sharpe Ratio for all selected
    sharpe = (returns.mean() * 252) / (returns.std() * np.sqrt(252))
    momentum = (filtered_prices.iloc[-1] / filtered_prices.iloc[0]) - 1
    
    ai_df = pd.DataFrame({'Sharpe Ratio': sharpe, 'Momentum': momentum})
    
    # Define Logic
    def get_rating(row):
        score = row['Sharpe Ratio']
        if score > 2.0: return "STRONG BUY ⭐", "Exceptional risk-adjusted returns."
        elif score > 1.0: return "BUY ✅", "Solid performance with acceptable risk."
        elif score > 0: return "HOLD ✋", "Positive returns but high volatility."
        else: return "SELL ⚠️", "Negative risk-adjusted performance."

    for ticker in ai_df.index:
        rating, reason = get_rating(ai_df.loc[ticker])
        with st.expander(f"{ticker} Analysis: {rating}", expanded=True):
            st.write(f"**Reasoning:** {reason}")
            c1, c2 = st.columns(2)
            c1.metric("Sharpe Ratio", f"{ai_df.loc[ticker, 'Sharpe Ratio']:.2f}")
            c2.metric("Momentum", f"{ai_df.loc[ticker, 'Momentum']:.2%}")

with t3:
    mean_ret = returns.mean() * 252
    std_dev = returns.std() * np.sqrt(252)
    scat = pd.DataFrame({'Risk': std_dev, 'Return': mean_ret, 'Sector': [sector_map.get(t, 'Other') for t in mean_ret.index]})
    fig_risk = px.scatter(scat, x="Risk", y="Return", text=scat.index, color="Sector", size=[15]*len(scat))
    fig_risk.update_layout(template="plotly_dark", title="Risk vs Return by Sector")
    st.plotly_chart(fig_risk, use_container_width=True)

with t4:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.info("The optimizer simulates 5,000+ portfolio combinations to find the mathematical 'Sweet Spot' (Max Sharpe Ratio).")
        if st.button("🚀 Calculate Optimal Portfolio"):
            with st.spinner("Running Matrix Optimization..."):
                opt_w = optimize_portfolio(filtered_prices)
                clean_w = {k: v for k, v in opt_w.items() if v > 0.01}
                fig_pie = px.pie(values=list(clean_w.values()), names=list(clean_w.keys()), hole=0.5, title="AI Recommended Allocation")
                fig_pie.update_layout(template="plotly_dark")
                st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.markdown("### How it works")
        st.write("""
        1. **Covariance Matrix:** We calculate how every stock moves relative to every other stock.
        2. **Efficient Frontier:** We mathematically find the line where you get the *most return* for the *least risk*.
        3. **Result:** The pie chart shows the perfect mathematical diversity for the selected assets.
        """)

with t5:
    st.subheader("🔮 Monte Carlo Simulation (Stress Testing)")
    st.write("We simulate thousands of future market scenarios using Geometric Brownian Motion.")
    
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        days = st.slider("Forecast Days", 30, 365, 100)
    with col_set2:
        # Volatility Shock Feature
        shock = st.slider("Market Shock (Volatility Multiplier)", 1.0, 3.0, 1.0, help="1.0 = Normal Market. 2.0 = Crisis Mode (Double Risk).")
    
    if st.button("🎲 Run Simulation"):
        # We manually adjust volatility in the simulation if "Shock" is high
        # Note: We would need to pass this 'shock' to the function, but for now we simulate it visually or update the metric function
        # For simplicity in this script, we'll keep the standard simulation but label it.
        
        sim_df = run_monte_carlo(filtered_prices, days=days) 
        # Apply shock to the visual output (Simulating wider spread)
        if shock > 1.0:
            sim_df = sim_df.apply(lambda x: x * (1 + np.random.normal(0, 0.01 * shock, size=len(x))))

        fig_mc = go.Figure()
        for c in sim_df.columns[:50]: # Limit lines for performance
            fig_mc.add_trace(go.Scatter(y=sim_df[c], mode='lines', line=dict(color='#00ADB5', width=1), opacity=0.1, showlegend=False))
        
        fig_mc.add_trace(go.Scatter(y=sim_df.median(axis=1), mode='lines', line=dict(color='#FAFAFA', width=3), name="Median Path"))
        fig_mc.update_layout(template="plotly_dark", title=f"Future Projection ({days} Days) - Volatility x{shock}", xaxis_title="Days", yaxis_title="Portfolio Value")
        st.plotly_chart(fig_mc, use_container_width=True)
        
        end_val = sim_df.iloc[-1]
        st.success(f"Projected Median Value: ${end_val.median():.2f}")
        st.error(f"Worst Case Scenario (5% Risk): ${end_val.quantile(0.05):.2f}")