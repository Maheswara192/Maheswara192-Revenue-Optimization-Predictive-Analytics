"""
🏢 SUPERSTORE ENTERPRISE ANALYTICS MASTER SUITE
-----------------------------------------------
This master script orchestrates the entire data science pipeline,
from raw data migration to prescriptive ROI modeling and AI clustering.
"""

import os
import sys

# Add project root and current directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)
sys.path.append(script_dir)

def run_pipeline():
    print("="*60)
    print("🔥 STARTING ENTERPRISE ANALYTICS PIPELINE")
    print("="*60)
    
    try:
        # Step 0: Ensure Data Layer exists
        from setup_database import setup_db
        setup_db()
        
        # Step 1: RFM Analysis
        from Superstore_Analytics import rfm_analysis
        rfm_data = rfm_analysis.load_data()
        rfm_results = rfm_analysis.calculate_rfm(rfm_data)
        rfm_analysis.generate_reports(rfm_results)
        
        # Step 2: Profitability & ROI Simulation
        from Superstore_Analytics import profit_loss_analysis
        profit_data = profit_loss_analysis.get_analytical_data()
        profit_loss_analysis.analyze_leakage(profit_data)
        
        # Step 3: Advanced ML Clustering
        from Superstore_Analytics import customer_clustering
        customer_clustering.run_ml_segmentation()
        
        # Step 4: Forecasting
        # Note: forecasting script runs independently as a standalone module
        print("\n📈 Note: Run 'sales_forecasting.py' separately for time-series modeling.")
        
        print("\n" + "="*60)
        print("🏆 PIPELINE EXECUTED SUCCESSFULLY")
        print("Check for HTML reports and professional CSV results.")
        print("="*60)
        
    except ImportError as e:
        print(f"❌ Pipeline Failed: Missing modules. Run 'pip install -r requirements.txt'")
        print(f"Details: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    run_pipeline()
