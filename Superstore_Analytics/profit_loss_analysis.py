import pandas as pd
import numpy as np
import sqlite3

# 1. Data Retrieval
def get_analytical_data():
    conn = sqlite3.connect("superstore.db")
    df = pd.read_sql("SELECT * FROM orders", conn)
    conn.close()
    return df

# 2. Profit Leakage Analysis
def analyze_leakage(df):
    print("💰 Analyzing Profit Leakage & Discount Sensitivity...")
    
    # Identify Loss Makers
    loss_df = df[df['Profit'] < 0].copy()
    total_leaked = abs(loss_df['Profit'].sum())
    
    print(f"- Total Revenue Leakage Identified: ${total_leaked:,.2f}")
    
    # Prescriptive Simulation: ROI of Discount Caps
    def simulate_cap(cap_pct):
        temp = df.copy()
        temp['Unit_Cost'] = temp['Sales'] - temp['Profit']
        
        # Apply Cap
        mask = temp['Discount'] > cap_pct
        temp.loc[mask, 'New_Discount'] = cap_pct
        # Simplified assumption: Price goes up, Sales volume drops (Elasticity 0.5)
        reduction = temp.loc[mask, 'Discount'] - cap_pct
        temp['New_Sales'] = temp['Sales']
        temp.loc[mask, 'New_Sales'] = temp['Sales'] * (1 - (reduction * 0.5))
        
        temp['New_Profit'] = temp['New_Sales'] - temp['Unit_Cost']
        return temp['New_Profit'].sum()

    base_profit = df['Profit'].sum()
    cap_20 = simulate_cap(0.20)
    
    print(f"- Baseline Annual Profit: ${base_profit:,.2f}")
    print(f"- Simulated Profit with 20% Discount Cap: ${cap_20:,.2f}")
    print(f"- **Strategic Opportunity**: +${(cap_20 - base_profit):,.2f} incremental gain.")

    # Save to CSV
    loss_df.to_csv('Profit_Leakage_Deep_Dive.csv', index=False)
    print("✅ Detailed report saved: Profit_Leakage_Deep_Dive.csv")

if __name__ == "__main__":
    try:
        data = get_analytical_data()
        analyze_leakage(data)
    except Exception as e:
        print(f"❌ Error: {e}")
