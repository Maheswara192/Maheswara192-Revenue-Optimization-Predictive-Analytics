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
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium, User-Friendly Look
st.markdown("""
<style>
    .main { 
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    
    /* Enhanced Metric Card Styling */
    .stMetric { 
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        padding: 25px; 
        border-radius: 15px; 
        box-shadow: 0 8px 16px rgba(0,0,0,0.1); 
        border-left: 5px solid #1f77b4;
        transition: transform 0.2s;
    }
    
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.15);
    }
    
    /* Make metric values highly visible */
    [data-testid="stMetricValue"] {
        color: #0e1117 !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    
    /* Make metric labels visible */
    [data-testid="stMetricLabel"] {
        color: #31333F !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Make delta values visible */
    [data-testid="stMetricDelta"] {
        color: #09ab3b !important;
        font-weight: 600 !important;
    }
    
    /* Enhanced Headers */
    h1 { 
        color: #1a1a2e; 
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    h2, h3 { 
        color: #0e1117; 
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    .highlight { 
        color: #ff4b4b; 
        font-weight: bold; 
        background-color: #fff3cd;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #17a2b8;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f77b4 0%, #0d47a1 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(90deg, #1f77b4, #0d47a1);
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 16px rgba(31, 119, 180, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Data Loading via SQL
@st.cache_data
def load_data_sql():
    conn = sqlite3.connect("superstore.db")
    query = "SELECT * FROM orders"
    df = pd.read_sql(query, conn)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    conn.close()
    return df

try:
    df = load_data_sql()
except Exception as e:
    st.error(f"⚠️ Database not found! Please run 'setup_database.py' first. Error: {e}")
    st.info("💡 **Quick Fix**: Run `python setup_database.py` in your terminal to initialize the database.")
    st.stop()

# Welcome Screen (First-time user experience)
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True

if st.session_state.first_visit:
    st.balloons()
    with st.container():
        # Hero section with visual appeal
        st.markdown("""
        <div style='text-align: center; padding: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; color: white;'>
            <h1 style='font-size: 3rem; margin-bottom: 10px;'>👋 Welcome to Your BI Hub!</h1>
            <p style='font-size: 1.3rem; opacity: 0.9;'>Transform Data into Actionable Insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Feature cards with icons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='font-size: 3rem;'>📊</div>
                <h3 style='color: #1f77b4;'>Customer Segmentation</h3>
                <p style='color: #666;'>RFM Analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='font-size: 3rem;'>💰</div>
                <h3 style='color: #2ca02c;'>Profit Diagnostics</h3>
                <p style='color: #666;'>Find Money Pits</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='font-size: 3rem;'>📈</div>
                <h3 style='color: #ff7f0e;'>Trend Analysis</h3>
                <p style='color: #666;'>Historical Patterns</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <div style='font-size: 3rem;'>🚀</div>
                <h3 style='color: #d62728;'>ROI Simulator</h3>
                <p style='color: #666;'>Prescriptive Analytics</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.info("""
        ### 🎯 Quick Start Guide:
        1. **Sidebar Filters** → Select your analysis period and regions
        2. **Navigate Tabs** → Explore different insights
        3. **ROI Simulator** → See how discount caps affect profitability
        """)
        
        if st.button("🚀 Let's Get Started!", use_container_width=True):
            st.session_state.first_visit = False
            st.rerun()
    st.stop()

# Sidebar - Enhanced with Help
st.sidebar.title("🎛️ Control Panel")
st.sidebar.markdown("---")

with st.sidebar.expander("ℹ️ How to Use This Dashboard"):
    st.markdown("""
    **Filters:**
    - **Date Range**: Select the time period for analysis
    - **Region**: Choose specific regions or view all
    
    **Navigation:**
    - Use tabs to switch between different analyses
    - Hover over charts for detailed information
    - Download data using export buttons
    """)

st.sidebar.markdown("### 📅 Time Period")
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['Order_Date'].min().date(), df['Order_Date'].max().date()],
    help="Choose the start and end dates for your analysis"
)

st.sidebar.markdown("### 🗺️ Geographic Filter")
region = st.sidebar.multiselect(
    "Select Regions",
    options=df['Region'].unique(),
    default=df['Region'].unique(),
    help="Filter data by specific regions. Select multiple regions to compare."
)

# Category filter (NEW)
st.sidebar.markdown("### 📦 Product Filter")
categories = st.sidebar.multiselect(
    "Select Categories",
    options=df['Category'].unique(),
    default=df['Category'].unique(),
    help="Filter by product categories"
)

# Filter Data
mask = (
    (df['Order_Date'].dt.date >= date_range[0]) & 
    (df['Order_Date'].dt.date <= date_range[1]) & 
    (df['Region'].isin(region)) &
    (df['Category'].isin(categories))
)
f_df = df[mask]

# Data quality indicator
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Summary")
st.sidebar.info(f"""
**Filtered Records:** {len(f_df):,} / {len(df):,}  
**Date Range:** {f_df['Order_Date'].min().date()} to {f_df['Order_Date'].max().date()}  
**Regions:** {len(region)} selected
""")

# Reset filters button
if st.sidebar.button("🔄 Reset All Filters"):
    st.rerun()

# Main Dashboard
st.title("🕴️ Executive Business Intelligence Hub")
st.caption("Powered by SQLite & Prescriptive Analytics | Real-time Data Insights")
st.markdown("---")

# Key Metrics with enhanced descriptions
st.markdown("### 📊 Key Performance Indicators")
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("<div style='text-align: center; font-size: 2rem;'>💵</div>", unsafe_allow_html=True)
    st.metric(
        "Total Revenue", 
        f"${f_df['Sales'].sum():,.0f}",
        help="Total sales revenue for the selected period and filters"
    )

with m2:
    profit_margin = (f_df['Profit'].sum()/f_df['Sales'].sum())*100
    st.markdown("<div style='text-align: center; font-size: 2rem;'>💎</div>", unsafe_allow_html=True)
    st.metric(
        "Net Profit", 
        f"${f_df['Profit'].sum():,.0f}", 
        delta=f"{profit_margin:.1f}% Margin",
        help="Total profit and profit margin percentage"
    )

with m3:
    st.markdown("<div style='text-align: center; font-size: 2rem;'>👥</div>", unsafe_allow_html=True)
    st.metric(
        "Customer Base", 
        f"{f_df['Customer_ID'].nunique():,}",
        help="Number of unique customers in the selected period"
    )

with m4:
    st.markdown("<div style='text-align: center; font-size: 2rem;'>🏷️</div>", unsafe_allow_html=True)
    st.metric(
        "Avg Discount", 
        f"{f_df['Discount'].mean()*100:.1f}%",
        delta=f"{len(f_df[f_df['Discount'] > 0.2])} orders >20%",
        delta_color="inverse",
        help="Average discount rate across all transactions"
    )

st.markdown("---")

# Enhanced Tabs with icons and descriptions
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Customer Segmentation", 
    "💰 Profit Analysis", 
    "📈 Trends & Forecasting", 
    "🚀 ROI Simulator",
    "📥 Data Export"
])

with tab1:
    st.header("🎯 Strategic Customer Segmentation (RFM Analysis)")
    st.markdown("""
    **What is RFM?** RFM stands for **Recency**, **Frequency**, and **Monetary** value. 
    This analysis helps identify your most valuable customers and those at risk of churning.
    """)
    
    with st.expander("📖 Understanding the Segments"):
        st.markdown("""
        - **Champions**: Your best customers - recent, frequent, high-value purchases
        - **At Risk**: Previously valuable customers who haven't purchased recently
        - **Regular**: Average customers with moderate engagement
        """)
    
    snapshot_date = f_df['Order_Date'].max() + pd.Timedelta(days=1)
    rfm = f_df.groupby('Customer_ID').agg({
        'Order_Date': lambda x: (snapshot_date - x.max()).days,
        'Order_ID': 'count',
        'Sales': 'sum'
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    for col, labels in zip(['Recency', 'Frequency', 'Monetary'], [[5,4,3,2,1], [1,2,3,4,5], [1,2,3,4,5]]):
        rfm[col[0]] = pd.qcut(rfm[col].rank(method='first'), 5, labels=labels)
    
    def segment(x):
        r, f = int(x['R']), int(x['F'])
        if r >= 4 and f >= 4: return 'Champions'
        if r <= 2 and f >= 4: return 'At Risk'
        return 'Regular'
    
    rfm['Segment'] = rfm.apply(segment, axis=1)
    
    # Enhanced treemap
    fig = px.treemap(
        rfm.reset_index(), 
        path=['Segment'], 
        values='Monetary',
        title="Customer Revenue Distribution by Segment",
        color='Monetary',
        color_continuous_scale='RdYlGn'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Segment statistics
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📊 Segment Distribution")
        segment_counts = rfm['Segment'].value_counts()
        for seg, count in segment_counts.items():
            st.metric(seg, f"{count:,} customers", f"{(count/len(rfm)*100):.1f}%")
    
    with col2:
        st.markdown("#### 💵 Revenue by Segment")
        segment_revenue = rfm.groupby('Segment')['Monetary'].sum().sort_values(ascending=False)
        for seg, rev in segment_revenue.items():
            st.metric(seg, f"${rev:,.0f}", f"{(rev/segment_revenue.sum()*100):.1f}%")

with tab2:
    st.header("💰 Profitability Diagnostics")
    st.markdown("Identify which products and categories are driving profit vs. causing losses.")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 📉 Discount Impact on Profit")
        fig = px.scatter(
            f_df, 
            x='Discount', 
            y='Profit', 
            color='Category',
            trendline="ols",
            title="Correlation: Higher Discounts = Lower Profits",
            labels={'Discount': 'Discount Rate', 'Profit': 'Profit ($)'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.info("💡 **Insight**: Notice the negative trend? High discounts often lead to losses.")
    
    with col_b:
        st.markdown("#### 📊 Profit by Sub-Category")
        profit_by_sub = f_df.groupby('Sub_Category')['Profit'].sum().sort_values()
        fig = px.bar(
            profit_by_sub,
            orientation='h',
            title="Which Products Are Money Pits?",
            labels={'value': 'Total Profit ($)', 'index': 'Sub-Category'},
            color=profit_by_sub.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Highlight loss-makers
        loss_makers = profit_by_sub[profit_by_sub < 0]
        if len(loss_makers) > 0:
            st.warning(f"⚠️ **{len(loss_makers)} sub-categories** are operating at a loss!")

with tab3:
    st.header("📈 Market Trend Analysis")
    st.markdown("Visualize sales patterns over time to identify seasonality and growth trends.")
    
    # Monthly sales trend
    monthly_sales = f_df.set_index('Order_Date')['Sales'].resample('MS').sum().reset_index()
    fig = px.line(
        monthly_sales,
        x='Order_Date',
        y='Sales',
        markers=True,
        title="Monthly Sales Trend",
        labels={'Order_Date': 'Month', 'Sales': 'Total Sales ($)'}
    )
    fig.update_traces(line_color='#1f77b4', line_width=3)
    fig.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Growth metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        yoy_growth = ((f_df['Sales'].sum() / df['Sales'].sum()) - 1) * 100
        st.metric("Period Growth", f"{yoy_growth:.1f}%")
    with col2:
        avg_monthly = monthly_sales['Sales'].mean()
        st.metric("Avg Monthly Sales", f"${avg_monthly:,.0f}")
    with col3:
        peak_month = monthly_sales.loc[monthly_sales['Sales'].idxmax(), 'Order_Date'].strftime('%B %Y')
        st.metric("Peak Month", peak_month)

with tab4:
    st.header("🚀 Strategic ROI Simulator (Prescriptive Analytics)")
    st.markdown("""
    **What-If Analysis**: See how implementing a discount cap would affect your bottom line.
    This tool uses a **Price Elasticity Model** to estimate the trade-off between profit gains and potential revenue loss.
    """)
    
    with st.expander("🧮 How Does This Work?"):
        st.markdown("""
        1. **Select a discount cap** using the slider below
        2. The model calculates:
           - **Profit Gain**: From reducing excessive discounts
           - **Volume Loss**: Estimated customer drop-off (using elasticity = 0.5)
        3. **Net Impact**: Shows if the strategy is profitable
        
        **Elasticity Assumption**: For every 10% discount reduction, we assume 5% volume loss.
        """)
    
    cap = st.slider(
        "Set Maximum Discount Cap (%)",
        min_value=0,
        max_value=50,
        value=20,
        step=5,
        help="Move the slider to simulate different discount cap scenarios"
    ) / 100
    
    # Simulation Logic
    sim_df = f_df.copy()
    over_cap_mask = sim_df['Discount'] > cap
    reduction = sim_df.loc[over_cap_mask, 'Discount'] - cap
    sim_df['Vol_Loss'] = 0.0
    sim_df.loc[over_cap_mask, 'Vol_Loss'] = reduction * 0.5
    sim_df['New_Sales'] = sim_df['Sales'] * (1 - sim_df['Vol_Loss'])
    sim_df['Unit_Cost'] = sim_df['Sales'] - sim_df['Profit']
    sim_df['New_Profit'] = sim_df['New_Sales'] - sim_df['Unit_Cost']
    
    # Results
    orig_p = f_df['Profit'].sum()
    new_p = sim_df['New_Profit'].sum()
    gain = new_p - orig_p
    revenue_risk = sim_df['Sales'].sum() - sim_df['New_Sales'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Simulated Net Profit", f"${new_p:,.0f}", delta=f"${gain:,.0f} Impact")
    c2.metric("Est. Revenue Risk", f"-${revenue_risk:,.0f}", delta_color="inverse")
    c3.metric("Profit Optimization ROI", f"{(gain/orig_p)*100:.1f}%")
    
    # Visual recommendation
    if gain > 0:
        st.success(f"""
        ### ✅ Recommended Strategy
        Implementing a **{cap*100:.0f}% discount cap** could increase annual profit by **${gain:,.0f}**.
        
        **Action Items:**
        1. Phase in the discount cap over 3 months
        2. Focus on high-discount categories first
        3. Monitor customer retention closely
        """)
    else:
        st.warning(f"""
        ### ⚠️ Caution Required
        A **{cap*100:.0f}% discount cap** may reduce profit by **${abs(gain):,.0f}**.
        Consider a higher cap or targeted approach.
        """)

with tab5:
    st.header("📥 Data Export & Download")
    st.markdown("Download the filtered data for further analysis in Excel or other tools.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Filtered Transaction Data")
        csv = f_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name=f"superstore_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        st.info(f"**{len(f_df):,} records** ready for download")
    
    with col2:
        st.markdown("#### 🎯 RFM Segment Data")
        if 'rfm' in locals():
            rfm_csv = rfm.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Download RFM Analysis (CSV)",
                data=rfm_csv,
                file_name=f"rfm_segments_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            st.info(f"**{len(rfm):,} customers** segmented")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <strong>Technical Highlights for Recruiters:</strong> SQLite Backend | Price Elasticity Modeling | Prescriptive Analytics | Interactive Plotly Visualizations</p>
    <p>Built with ❤️ using Streamlit | Data refreshes in real-time from SQL database</p>
</div>
""", unsafe_allow_html=True)
