import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Superstore Business Intelligence",
    page_icon="🕴️",
    layout="wide",
)

# Custom CSS for Premium Look with Enhanced Visibility
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    
    /* Enhanced Metric Card Styling */
    .stMetric { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        border-left: 4px solid #1f77b4;
    }
    
    /* Make metric values highly visible */
    [data-testid="stMetricValue"] {
        color: #0e1117 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    /* Make metric labels visible */
    [data-testid="stMetricLabel"] {
        color: #31333F !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    
    /* Make delta values visible */
    [data-testid="stMetricDelta"] {
        color: #09ab3b !important;
        font-weight: 600 !important;
    }
    
    h1, h2, h3 { color: #0e1117; font-family: 'Inter', sans-serif; }
    .highlight { color: #ff4b4b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Data Loading via SQL
@st.cache_data
def load_data_sql():
    conn = sqlite3.connect("superstore.db")
    # Using SQL to pull data - this is what recruiters want to see!
    query = "SELECT * FROM orders"
    df = pd.read_sql(query, conn)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    conn.close()
    return df

try:
    df = load_data_sql()
except Exception as e:
    st.error(f"Please run 'setup_database.py' first! Error: {e}")
    st.stop()

# Sidebar Filters
st.sidebar.title("🎛️ BI Controller")
date_range = st.sidebar.date_input("Analysis Period", [df['Order_Date'].min().date(), df['Order_Date'].max().date()])
region = st.sidebar.multiselect("Region", options=df['Region'].unique(), default=df['Region'].unique())

# Filter Data
mask = (df['Order_Date'].dt.date >= date_range[0]) & (df['Order_Date'].dt.date <= date_range[1]) & (df['Region'].isin(region))
f_df = df[mask]

# Title
st.title("🕴️ Executive Business Intelligence Hub")
st.caption("Powered by SQLite & Prescriptive Analytics")
st.markdown("---")

# Key Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Revenue", f"${f_df['Sales'].sum():,.0f}")
m2.metric("Net Profit", f"${f_df['Profit'].sum():,.0f}", delta=f"{(f_df['Profit'].sum()/f_df['Sales'].sum())*100:.1f}% Margin")
m3.metric("Customer Base", f"{f_df['Customer_ID'].nunique():,}")
m4.metric("Avg Discount", f"{f_df['Discount'].mean()*100:.1f}%")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Segmentation", "💰 Profit Analysis", "📈 Trends", "🚀 ROI SIMULATOR"])

with tab1:
    st.header("Strategic Customer Segmentation")
    # (Existing RFM Logic updated for underscore columns)
    snapshot_date = f_df['Order_Date'].max() + pd.Timedelta(days=1)
    rfm = f_df.groupby('Customer_ID').agg({'Order_Date': lambda x: (snapshot_date - x.max()).days, 'Order_ID': 'count', 'Sales': 'sum'})
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    for col, labels in zip(['Recency', 'Frequency', 'Monetary'], [[5,4,3,2,1], [1,2,3,4,5], [1,2,3,4,5]]):
        rfm[col[0]] = pd.qcut(rfm[col].rank(method='first'), 5, labels=labels)
    
    def segment(x):
        r, f = int(x['R']), int(x['F'])
        if r >= 4 and f >= 4: return 'Champions'
        if r <= 2 and f >= 4: return 'At Risk'
        return 'Regular'
    rfm['Segment'] = rfm.apply(segment, axis=1)
    st.plotly_chart(px.treemap(rfm.reset_index(), path=['Segment'], values='Monetary', title="Revenue by Segment"), use_container_width=True)

with tab2:
    st.header("Profitability Diagnostics")
    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(px.scatter(f_df, x='Discount', y='Profit', color='Category', trendline="ols"), use_container_width=True)
    with col_b:
        st.plotly_chart(px.bar(f_df.groupby('Sub_Category')['Profit'].sum().sort_values(), orientation='h', title="Cumulative Profit"), use_container_width=True)

with tab3:
    st.header("Market Trend Analysis")
    st.plotly_chart(px.line(f_df.set_index('Order_Date')['Sales'].resample('MS').sum().reset_index(), x='Order_Date', y='Sales', markers=True), use_container_width=True)

with tab4:
    st.header("🚀 Strategic ROI Simulator (Prescriptive)")
    st.info("What if we capped discounts to optimize profit? Use the slider to simulate business strategy changes.")
    
    cap = st.slider("Set Maximum Discount Cap (%)", 0, 50, 20) / 100
    
    # Simulation Logic
    sim_df = f_df.copy()
    
    # 1. Identify rows over the cap
    over_cap_mask = sim_df['Discount'] > cap
    
    # 2. Estimate "Price Elasticity" - if we lower discount, we might lose some sales volume
    # Assuming for every 10% discount reduced, we lose 5% of sales volume (Simple Elasticity Model)
    reduction = sim_df.loc[over_cap_mask, 'Discount'] - cap
    sim_df['Vol_Loss'] = 0.0
    sim_df.loc[over_cap_mask, 'Vol_Loss'] = reduction * 0.5 # 0.5 elasticity factor
    
    # 3. Calculate New Sales and New Profit
    sim_df['New_Sales'] = sim_df['Sales'] * (1 - sim_df['Vol_Loss'])
    # Simplification: Unit Cost remains same. Original Profit = Sales - Cost. 
    # Original Cost = Sales - Profit.
    sim_df['Unit_Cost'] = sim_df['Sales'] - sim_df['Profit']
    sim_df['New_Profit'] = sim_df['New_Sales'] - sim_df['Unit_Cost']
    
    # Results
    orig_p = f_df['Profit'].sum()
    new_p = sim_df['New_Profit'].sum()
    gain = new_p - orig_p
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Simulated Net Profit", f"${new_p:,.0f}", delta=f"${gain:,.0f} Impact")
    c2.metric("Est. Revenue Risk", f"-${(sim_df['Sales'].sum() - sim_df['New_Sales'].sum()):,.0f}", delta_color="inverse")
    c3.metric("Profit Optimization ROI", f"{(gain/orig_p)*100:.1f}%")
    
    st.markdown(f"""
    ### 📝 Executive Recommendation:
    By capping discounts at <span class='highlight'>{cap*100:.0f}%</span>, the business could potentially increase profit by 
    <span class='highlight'>${gain:,.0f}</span> while risking a revenue drop of <span class='highlight'>${(sim_df['Sales'].sum() - sim_df['New_Sales'].sum()):,.0f}</span>.
    
    **Conclusion:** The trade-off is {'highly favorable' if gain > 0 else 'unfavorable'}. 
    This simulate provides a **Data-Driven Decision Support System** for the CEO.
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("💡 *Technical Highlights for Recruiters: SQLite Backend | Price Elasticity Modeling | Prescriptive Analytics*")
