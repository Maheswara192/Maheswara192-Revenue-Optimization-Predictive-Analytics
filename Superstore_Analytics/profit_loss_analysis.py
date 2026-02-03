import pandas as pd
import numpy as np

# 1. Load the data
url = "https://raw.githubusercontent.com/sumit0072/Superstore-Data-Analysis/main/Sample%20-%20Superstore.csv"
try:
    df = pd.read_csv(url, encoding='windows-1252')
except Exception as e:
    print(f"Error loading data: {e}")
    exit()

# 2. Basic Profitability Metrics
total_profit = df['Profit'].sum()
total_sales = df['Sales'].sum()
overall_margin = (total_profit / total_sales) * 100

print(f"Total Sales: ${total_sales:,.2f}")
print(f"Total Profit: ${total_profit:,.2f}")
print(f"Overall Profit Margin: {overall_margin:.2f}%")

# 3. Isolating Losses
losses = df[df['Profit'] < 0].copy()
num_loss_orders = len(losses)
total_loss_amount = losses['Profit'].sum()

print(f"\nOrders with Negative Profit: {num_loss_orders} ({(num_loss_orders/len(df))*100:.1f}% of total orders)")
print(f"Total Amount Lost: ${abs(total_loss_amount):,.2f}")

# 4. Root Cause Analysis: The Discount Factor
# Let's see how much discount is given on loss-making orders compared to profitable ones
avg_discount_loss = losses['Discount'].mean()
avg_discount_profit = df[df['Profit'] >= 0]['Discount'].mean()

print(f"\nAvg Discount (Loss Orders): {avg_discount_loss*100:.1f}%")
print(f"Avg Discount (Profitable Orders): {avg_discount_profit*100:.1f}%")

# 5. Identifying "Money Pits" (Category + Region)
money_pits = losses.groupby(['Category', 'Sub-Category', 'Region']).agg({
    'Profit': ['sum', 'count'],
    'Discount': 'mean'
}).reset_index()

money_pits.columns = ['Category', 'Sub-Category', 'Region', 'Total_Loss', 'Loss_Frequency', 'Avg_Discount']
money_pits = money_pits.sort_values(by='Total_Loss', ascending=True) # Biggest loss first

print("\nTop 5 Most Unprofitable Combinations (Money Pits):")
print(money_pits.head())

# 6. Recommendation: Safe Discount Threshold
# Find the discount level after which profit almost always becomes negative
bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]
df['Discount_Bin'] = pd.cut(df['Discount'], bins)
discount_impact = df.groupby('Discount_Bin')['Profit'].mean()

print("\nAverage Profit per Discount Level:")
print(discount_impact)

# 7. Save results
money_pits.to_csv('High_Loss_Segments.csv', index=False)
print(f"\nAnalysis complete! Segments causing major losses saved to 'High_Loss_Segments.csv'")
