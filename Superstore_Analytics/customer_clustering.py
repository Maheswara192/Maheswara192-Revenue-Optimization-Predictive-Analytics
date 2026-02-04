import pandas as pd
import numpy as np
import sqlite3
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px

def run_ml_segmentation():
    print("🤖 Initializing Machine Learning Data Pipeline...")
    
    # 1. Fetch Data
    conn = sqlite3.connect("superstore.db")
    df = pd.read_sql("SELECT Customer_ID, Sales, Profit, Discount FROM orders", conn)
    conn.close()
    
    # 2. Feature Engineering (Aggregating to Customer Level)
    cust_data = df.groupby('Customer_ID').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Discount': 'mean'
    }).reset_index()
    
    # 3. Preprocessing
    features = ['Sales', 'Profit', 'Discount']
    X = cust_data[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 4. K-Means Clustering (K=4 for 4 distinct business segments)
    print("🧠 Training K-Means Clustering Model...")
    kmeans = KMeans(n_init=10, n_clusters=4, random_state=42)
    cust_data['ML_Cluster'] = kmeans.fit_predict(X_scaled)
    
    # 5. Labeling based on characteristics
    # Cluster 0, 1, 2, 3 might vary, so we'll just keep numbers for technical proof
    
    # 6. Visualization
    fig = px.scatter_3d(cust_data, x='Sales', y='Profit', z='Discount',
                        color='ML_Cluster', title='3D AI-Driven Customer Clustering',
                        hover_data=['Customer_ID'],
                        color_continuous_scale='Viridis')
    
    fig.write_html("customer_ml_clusters.html")
    cust_data.to_csv("AI_Customer_Segments.csv", index=False)
    
    print("✅ ML Segmentation Complete.")
    print("- 3D AI Visual: customer_ml_clusters.html")
    print("- Detailed CSV: AI_Customer_Segments.csv")

if __name__ == "__main__":
    try:
        run_ml_segmentation()
    except Exception as e:
        print(f"❌ ML Error: {e}")
