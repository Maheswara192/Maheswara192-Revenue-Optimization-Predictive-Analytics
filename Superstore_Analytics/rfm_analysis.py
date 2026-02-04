import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.io as pio

# 1. Connect to SQL Data Layer
def load_data():
    conn = sqlite3.connect("superstore.db")
    df = pd.read_sql("SELECT * FROM orders", conn)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])
    conn.close()
    return df

# 2. RFM Calculation Logic
def calculate_rfm(df):
    print("🚀 Running SQL-backed RFM Analysis...")
    snapshot_date = df['Order_Date'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('Customer_ID').agg({
        'Order_Date': lambda x: (snapshot_date - x.max()).days, # Recency
        'Order_ID': 'count',                                   # Frequency
        'Sales': 'sum'                                         # Monetary
    })
    
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    # Scoring (1-5)
    rfm['R'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['M'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
    
    def segment_map(x):
        r, f = int(x['R']), int(x['F'])
        if r >= 4 and f >= 4: return 'Champions'
        if r >= 3 and f >= 3: return 'Loyalists'
        if r <= 2 and f >= 4: return 'At Risk'
        if r <= 1: return 'Hibernating'
        return 'Regular'
        
    rfm['Segment'] = rfm.apply(segment_map, axis=1)
    return rfm

# 3. Visualization & Reporting
def generate_reports(rfm):
    # Interactive Tree Map (Professional Visual)
    fig = px.treemap(rfm.reset_index(), path=['Segment', 'Customer_ID'], values='Monetary',
                     title='RFM Customer Segmentation: Executive View',
                     color='Monetary', color_continuous_scale='RdYlGn')
    
    pio.write_html(fig, file='rfm_interactive_report.html', auto_open=False)
    rfm.to_csv('Superstore_RFM_Analysis_Advanced.csv')
    print("✅ Analysis Complete.")
    print("- CSV saved: Superstore_RFM_Analysis_Advanced.csv")
    print("- Interactive HTML report: rfm_interactive_report.html")

if __name__ == "__main__":
    try:
        data = load_data()
        results = calculate_rfm(data)
        generate_reports(results)
    except Exception as e:
        print(f"❌ Error: {e}. Please ensure 'setup_database.py' was run.")
