import pandas as pd
import sqlite3
import os

# Database Path
DB_PATH = "superstore.db"
URL = "https://raw.githubusercontent.com/sumit0072/Superstore-Data-Analysis/main/Sample%20-%20Superstore.csv"

def setup_db():
    print("🚀 Initializing SQL Data Layer...")
    
    # 1. Load Data
    try:
        df = pd.read_csv(URL, encoding='windows-1252')
        # Clean column names for SQL (replace spaces with underscores)
        df.columns = [c.replace(' ', '_').replace('-', '_') for c in df.columns]
        
        # 2. Connect to SQLite
        conn = sqlite3.connect(DB_PATH)
        
        # 3. Write to SQL
        df.to_sql('orders', conn, if_exists='replace', index=False)
        
        # 4. Create an optimized index for performance
        conn.execute("CREATE INDEX idx_order_date ON orders(Order_Date)")
        conn.execute("CREATE INDEX idx_region ON orders(Region)")
        
        conn.close()
        print(f"✅ Success! Data migrated to {DB_PATH}")
        print("💡 Recruiters will now see that you use SQL instead of just CSVs.")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

if __name__ == "__main__":
    setup_db()
