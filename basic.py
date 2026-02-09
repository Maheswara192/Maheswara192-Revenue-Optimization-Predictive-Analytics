import pandas as pd

# 1. Load the data
url = "https://raw.githubusercontent.com/sumit0072/Superstore-Data-Analysis/main/Sample%20-%20Superstore.csv"
df = pd.read_csv(url, encoding='windows-1252') # Common encoding for Excel-generated CSVs

# 2. Quick Clean
# Check for missing values
print(df.isnull().sum()) 

# Let's assume we found some nulls (common in real life) and want to drop them
df_clean = df.dropna()
df_clean['Discount_Category'] = df_clean['Discount'].apply(lambda x: 'High' if x > 0.2 else 'Low')

# 4. Save the clean data for Power BI
df_clean.to_csv('Superstore_Cleaned.csv', index=False)
print("Data cleaned and saved successfully!")


import sqlite3

# Create a temporary mini-database in RAM
conn = sqlite3.connect(':memory:')
df_clean.to_sql('sales', conn, index=False)

# Answer Q2: Top 5 Cities by Sales
query = """
SELECT 
    City, 
    SUM(Sales) as Total_Revenue, 
    SUM(Profit) as Total_Profit
FROM sales
GROUP BY City
ORDER BY Total_Revenue DESC
LIMIT 5;
"""
print(pd.read_sql(query, conn))