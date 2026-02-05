import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# Page Configuration - Standard Professional
st.set_page_config(
    page_title="Superstore Analytics | Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Minimalist CSS (No Gradients/Emojis)
st.markdown("""
<style>
    /* Clean white background */
    .section-main.css-10trblm {background-color: #ffffff;}
    .main {background-color: #ffffff;}
    
    /* Subtle Metric Cards - "Tableau Style" */
    .stMetric {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 5px;
        box-shadow: none;
    }
    
    /* Standard Headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', Roboto, sans-serif;
        color: #2c3e50;
    }
    
    h1 { font-size: 2.2rem; font-weight: 600; }
    h3 { font-size: 1.1rem; font-weight: 500; color: #555; }
    
    /* Highlight color for metrics */
    [data-testid="stMetricValue"] {
        color: #2c3e50 !important;
        font-size: 1.8rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Data Loading - Robust Error Handling
@st.cache_data
def load_data_sql():
    try:
        conn = sqlite3.connect("superstore.db")
        query = "SELECT * FROM orders"
        df = pd.read_sql(query, conn)
        df['Order_Date'] = pd.to_datetime(df['Order_Date'])
        conn.close()
        return df
    except Exception as e:
        return None

df = load_data_sql()

if df is None:
    st.error("⚠️ Database connection failed. Please run `setup_database.py` to initialize the data layer.")
    st.stop()

# Simpler Sidebar - Clean Filters
st.sidebar.title("Filters")
st.sidebar.caption("Refine your analysis scope")

date_range = st.sidebar.date_input(
    "Date Range",
    [df['Order_Date'].min().date(), df['Order_Date'].max().date()]
)

region = st.sidebar.multiselect(
    "Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

categories = st.sidebar.multiselect(
    "Category",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Apply Filters
mask = (
    (df['Order_Date'].dt.date >= date_range[0]) & 
    (df['Order_Date'].dt.date <= date_range[1]) & 
    (df['Region'].isin(region)) &
    (df['Category'].isin(categories))
)
f_df = df[mask]

if st.sidebar.button("Reset All Filters"):
    st.rerun()

# Main Header
st.title("Superstore Executive Overview")
st.caption(f"Reporting Period: {date_range[0]} to {date_range[1]}")
st.markdown("---")

# Clean KPI Row (No Emojis)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Revenue", f"${f_df['Sales'].sum():,.0f}")

with col2:
    profit = f_df['Profit'].sum()
    margin = (profit / f_df['Sales'].sum()) * 100 if f_df['Sales'].sum() > 0 else 0
    st.metric("Net Profit", f"${profit:,.0f}", f"{margin:.1f}% Margin")

with col3:
    st.metric("Active Customers", f"{f_df['Customer_ID'].nunique():,}")

with col4:
    avg_disc = f_df['Discount'].mean() * 100
    st.metric("Avg Discount", f"{avg_disc:.1f}%", f"{len(f_df[f_df['Discount']>0.2])} High Disc Orders", delta_color="inverse")

st.markdown("---")

# Tabs - Standard Professional Labels
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Profitability", "Trends", "What-If Analysis"])

with tab1:
    st.subheader("Sales Performance by Segment")
    
    # Standard Bar Chart (Tableau Blue)
    fig = px.bar(
        f_df.groupby('Segment')['Sales'].sum().reset_index(),
        x='Segment',
        y='Sales',
        text_auto='.2s',
        title="Revenue by Customer Segment",
        color_discrete_sequence=['#4c78a8'] # Standard Professional Blue
    )
    fig.update_layout(plot_bgcolor="white", height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Simple Data Table
    st.subheader("Top Customers (Recent & High Value)")
    snapshot_date = f_df['Order_Date'].max() + pd.Timedelta(days=1)
    rfm = f_df.groupby(['Customer_ID', 'Customer_Name']).agg({
        'Order_Date': lambda x: (snapshot_date - x.max()).days,
        'Order_ID': 'count',
        'Sales': 'sum'
    }).reset_index()
    rfm.columns = ['ID', 'Customer', 'Recency (Days)', 'Orders', 'Total Sales']
    
    st.dataframe(
        rfm.sort_values('Total Sales', ascending=False).head(10),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Profit by Sub-Category")
        prof_by_cat = f_df.groupby('Sub_Category')['Profit'].sum().sort_values()
        
        # Red/Green Diverging for Profit/Loss
        fig = px.bar(
            prof_by_cat,
            orientation='h',
            title="Profit Leaders & Losers",
            color=prof_by_cat.values,
            color_continuous_scale=['#d62728', '#e7ba52', '#2ca02c'] # Red -> Yellow -> Green
        )
        fig.update_layout(plot_bgcolor="white", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
    with col_b:
        st.subheader("Discount vs. Profit Matrix")
        fig = px.scatter(
            f_df,
            x='Discount',
            y='Profit',
            color='Category',
            opacity=0.6,
            title="Impact of Discounts on Profitability"
        )
        fig.update_layout(plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Sales Trend (Monthly)")
    monthly = f_df.set_index('Order_Date')['Sales'].resample('MS').sum().reset_index()
    
    fig = px.line(
        monthly,
        x='Order_Date',
        y='Sales',
        title="Monthly Revenue Trajectory",
        markers=True
    )
    fig.update_traces(line_color='#4c78a8', line_width=2)
    fig.update_layout(plot_bgcolor="white", xaxis_gridcolor="#eee", yaxis_gridcolor="#eee")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Strategic ROI Simulator")
    
    col_input, col_metric = st.columns([1, 2])
    
    with col_input:
        st.write("### Strategy Controls")
        cap = st.slider("Max Allowed Discount", 0, 50, 20, format="%d%%") / 100
        st.info("Adjust the slider to simulate capping excessive discounts.")

    # Logic
    sim_df = f_df.copy()
    mask_cap = sim_df['Discount'] > cap
    
    # Elasticity Logic 0.5
    discount_reduction = sim_df.loc[mask_cap, 'Discount'] - cap
    vol_loss = discount_reduction * 0.5
    
    sim_df.loc[mask_cap, 'New_Sales'] = sim_df.loc[mask_cap, 'Sales'] * (1 - vol_loss)
    sim_df['New_Sales'].fillna(sim_df['Sales'], inplace=True)
    
    # Recalculate Profit
    # Profit = Sales - Cost => Cost = Sales - Profit
    cost = sim_df['Sales'] - sim_df['Profit']
    sim_df['New_Profit'] = sim_df['New_Sales'] - cost
    
    orig_profit = sim_df['Profit'].sum()
    new_profit = sim_df['New_Profit'].sum()
    diff = new_profit - orig_profit
    
    with col_metric:
        st.write("### Projected Impact")
        c1, c2 = st.columns(2)
        c1.metric("Projected Annual Profit", f"${new_profit:,.0f}", f"${diff:,.0f} Improvement")
        
        if diff > 0:
            st.success(f"Recommendation: A **{cap*100:.0f}% cap** is projected to add **${diff:,.0f}** to the bottom line.")
        else:
            st.warning("This cap is too restrictive and may reduce overall profit volume.")

# Footer
st.markdown("---")
st.caption("Superstore Analytics | Confidential | Generated via Enterprise SQL Pipeline")
