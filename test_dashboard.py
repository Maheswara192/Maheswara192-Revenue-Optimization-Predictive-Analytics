"""
Enterprise-Grade Dashboard Test Suite
Tests all business logic, edge cases, and performance benchmarks
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Business Logic Functions (will be extracted from dashboard)
def calculate_rfm(df, snapshot_date=None):
    """
    Calculate RFM (Recency, Frequency, Monetary) scores for customers
    
    Args:
        df: DataFrame with Order_Date, Customer_ID, Order_ID, Sales columns
        snapshot_date: Reference date for recency calculation (default: max date + 1 day)
    
    Returns:
        DataFrame with RFM scores and segments
    """
    if df.empty:
        return pd.DataFrame(columns=['Customer_ID', 'Recency', 'Frequency', 'Monetary', 'Segment'])
    
    if snapshot_date is None:
        snapshot_date = df['Order_Date'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('Customer_ID').agg({
        'Order_Date': lambda x: (snapshot_date - x.max()).days,
        'Order_ID': 'count',
        'Sales': 'sum'
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    # Assign quintile scores
    for col, labels in zip(['Recency', 'Frequency', 'Monetary'], [[5,4,3,2,1], [1,2,3,4,5], [1,2,3,4,5]]):
        try:
            rfm[col[0]] = pd.qcut(rfm[col].rank(method='first'), 5, labels=labels, duplicates='drop')
        except ValueError:
            # Handle case where we can't create 5 bins
            rfm[col[0]] = 3  # Default to middle score
    
    # Segment customers
    def segment(row):
        try:
            r, f = int(row['R']), int(row['F'])
            if r >= 4 and f >= 4:
                return 'Champions'
            elif r <= 2 and f >= 4:
                return 'At Risk'
            else:
                return 'Regular'
        except:
            return 'Regular'
    
    rfm['Segment'] = rfm.apply(segment, axis=1)
    return rfm.reset_index()


def calculate_roi_impact(df, discount_cap, elasticity=0.5):
    """
    Calculate ROI impact of implementing a discount cap
    
    Args:
        df: DataFrame with Discount, Sales, Profit columns
        discount_cap: Maximum allowed discount (0-1)
        elasticity: Price elasticity coefficient (default: 0.5)
    
    Returns:
        dict with original_profit, new_profit, profit_gain, revenue_risk
    """
    if df.empty:
        return {
            'original_profit': 0,
            'new_profit': 0,
            'profit_gain': 0,
            'revenue_risk': 0
        }
    
    sim_df = df.copy()
    mask_cap = sim_df['Discount'] > discount_cap
    
    # Calculate volume loss from elasticity
    discount_reduction = sim_df.loc[mask_cap, 'Discount'] - discount_cap
    vol_loss = discount_reduction * elasticity
    
    # Calculate new sales
    sim_df.loc[mask_cap, 'New_Sales'] = sim_df.loc[mask_cap, 'Sales'] * (1 - vol_loss)
    sim_df['New_Sales'].fillna(sim_df['Sales'], inplace=True)
    
    # Calculate new profit
    cost = sim_df['Sales'] - sim_df['Profit']
    sim_df['New_Profit'] = sim_df['New_Sales'] - cost
    
    return {
        'original_profit': sim_df['Profit'].sum(),
        'new_profit': sim_df['New_Profit'].sum(),
        'profit_gain': sim_df['New_Profit'].sum() - sim_df['Profit'].sum(),
        'revenue_risk': sim_df['Sales'].sum() - sim_df['New_Sales'].sum()
    }


def validate_data(df):
    """
    Validate that DataFrame has required columns and data quality
    
    Returns:
        dict with 'valid' boolean and 'errors' list
    """
    required_columns = ['Order_Date', 'Customer_ID', 'Order_ID', 'Sales', 'Profit', 'Discount', 'Region', 'Category', 'Segment']
    
    errors = []
    
    # Check for required columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
    
    if df.empty:
        errors.append("DataFrame is empty")
        return {'valid': False, 'errors': errors}
    
    # Check for null values in critical columns
    critical_cols = ['Order_Date', 'Customer_ID', 'Sales']
    for col in critical_cols:
        if col in df.columns and df[col].isnull().any():
            errors.append(f"Null values found in {col}")
    
    # Check data types
    if 'Order_Date' in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df['Order_Date']):
            errors.append("Order_Date must be datetime type")
    
    # Check for negative sales/profit (warning, not error)
    if 'Sales' in df.columns and (df['Sales'] < 0).any():
        errors.append("Warning: Negative sales values detected")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


# ============= UNIT TESTS =============

class TestRFMCalculation:
    """Test RFM calculation logic"""
    
    def test_rfm_basic(self):
        """Test RFM with normal data"""
        data = {
            'Order_Date': pd.date_range('2024-01-01', periods=10),
            'Customer_ID': ['C1', 'C1', 'C2', 'C2', 'C3', 'C3', 'C3', 'C4', 'C4', 'C4'],
            'Order_ID': range(10),
            'Sales': [100, 200, 150, 250, 300, 400, 500, 50, 75, 100]
        }
        df = pd.DataFrame(data)
        
        rfm = calculate_rfm(df)
        
        assert len(rfm) == 4  # 4 unique customers
        assert 'Segment' in rfm.columns
        assert rfm['Monetary'].sum() > 0
    
    def test_rfm_empty_data(self):
        """Test RFM with empty DataFrame"""
        df = pd.DataFrame(columns=['Order_Date', 'Customer_ID', 'Order_ID', 'Sales'])
        rfm = calculate_rfm(df)
        
        assert len(rfm) == 0
        assert 'Segment' in rfm.columns
    
    def test_rfm_single_customer(self):
        """Test RFM with only one customer"""
        data = {
            'Order_Date': pd.date_range('2024-01-01', periods=3),
            'Customer_ID': ['C1', 'C1', 'C1'],
            'Order_ID': range(3),
            'Sales': [100, 200, 300]
        }
        df = pd.DataFrame(data)
        
        rfm = calculate_rfm(df)
        
        assert len(rfm) == 1
        assert rfm.iloc[0]['Segment'] in ['Champions', 'At Risk', 'Regular']


class TestROICalculation:
    """Test ROI simulator logic"""
    
    def test_roi_no_cap_needed(self):
        """Test ROI when all discounts are below cap"""
        data = {
            'Discount': [0.1, 0.15, 0.05],
            'Sales': [1000, 2000, 1500],
            'Profit': [200, 400, 300]
        }
        df = pd.DataFrame(data)
        
        result = calculate_roi_impact(df, discount_cap=0.2)
        
        assert result['profit_gain'] == 0  # No change expected
        assert result['revenue_risk'] == 0
    
    def test_roi_with_cap(self):
        """Test ROI when discounts exceed cap"""
        data = {
            'Discount': [0.3, 0.4, 0.1],
            'Sales': [1000, 2000, 1500],
            'Profit': [100, 200, 300]
        }
        df = pd.DataFrame(data)
        
        result = calculate_roi_impact(df, discount_cap=0.2, elasticity=0.5)
        
        assert result['profit_gain'] != 0  # Should have impact
        assert result['revenue_risk'] > 0  # Should have some revenue risk
    
    def test_roi_empty_data(self):
        """Test ROI with empty DataFrame"""
        df = pd.DataFrame(columns=['Discount', 'Sales', 'Profit'])
        
        result = calculate_roi_impact(df, discount_cap=0.2)
        
        assert result['original_profit'] == 0
        assert result['new_profit'] == 0
    
    def test_roi_extreme_cap(self):
        """Test ROI with extreme discount cap (0%)"""
        data = {
            'Discount': [0.1, 0.2, 0.3],
            'Sales': [1000, 2000, 3000],
            'Profit': [200, 400, 600]
        }
        df = pd.DataFrame(data)
        
        result = calculate_roi_impact(df, discount_cap=0.0, elasticity=0.5)
        
        # All discounts exceed cap, should have significant impact
        assert result['revenue_risk'] > 0


class TestDataValidation:
    """Test data validation logic"""
    
    def test_valid_data(self):
        """Test validation with correct data"""
        data = {
            'Order_Date': pd.date_range('2024-01-01', periods=5),
            'Customer_ID': ['C1', 'C2', 'C3', 'C4', 'C5'],
            'Order_ID': range(5),
            'Sales': [100, 200, 300, 400, 500],
            'Profit': [20, 40, 60, 80, 100],
            'Discount': [0.1, 0.2, 0.15, 0.05, 0.1],
            'Region': ['East'] * 5,
            'Category': ['Furniture'] * 5,
            'Segment': ['Consumer'] * 5
        }
        df = pd.DataFrame(data)
        
        result = validate_data(df)
        
        assert result['valid'] == True
        assert len(result['errors']) == 0
    
    def test_missing_columns(self):
        """Test validation with missing columns"""
        df = pd.DataFrame({'Sales': [100, 200]})
        
        result = validate_data(df)
        
        assert result['valid'] == False
        assert len(result['errors']) > 0
    
    def test_empty_dataframe(self):
        """Test validation with empty DataFrame"""
        df = pd.DataFrame()
        
        result = validate_data(df)
        
        assert result['valid'] == False
        assert 'empty' in str(result['errors']).lower()
    
    def test_null_values(self):
        """Test validation with null values in critical columns"""
        data = {
            'Order_Date': pd.date_range('2024-01-01', periods=5),
            'Customer_ID': ['C1', None, 'C3', 'C4', 'C5'],
            'Order_ID': range(5),
            'Sales': [100, 200, None, 400, 500],
            'Profit': [20, 40, 60, 80, 100],
            'Discount': [0.1, 0.2, 0.15, 0.05, 0.1],
            'Region': ['East'] * 5,
            'Category': ['Furniture'] * 5,
            'Segment': ['Consumer'] * 5
        }
        df = pd.DataFrame(data)
        
        result = validate_data(df)
        
        assert result['valid'] == False
        assert any('Null values' in err for err in result['errors'])


# ============= INTEGRATION TESTS =============

class TestDatabaseIntegration:
    """Test database connection and queries"""
    
    def test_database_exists(self):
        """Test that database file exists"""
        import os
        assert os.path.exists('superstore.db'), "Database file not found. Run setup_database.py first."
    
    def test_database_connection(self):
        """Test database connection"""
        import sqlite3
        try:
            conn = sqlite3.connect('superstore.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            
            assert len(tables) > 0, "No tables found in database"
            assert ('orders',) in tables, "orders table not found"
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")
    
    def test_query_performance(self):
        """Test that basic query completes in reasonable time"""
        import sqlite3
        import time
        
        start = time.time()
        conn = sqlite3.connect('superstore.db')
        df = pd.read_sql("SELECT * FROM orders LIMIT 1000", conn)
        conn.close()
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Query took too long: {elapsed:.2f}s"
        assert len(df) > 0, "Query returned no results"


# ============= EDGE CASE TESTS =============

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_single_record(self):
        """Test with single record"""
        data = {
            'Order_Date': [pd.Timestamp('2024-01-01')],
            'Customer_ID': ['C1'],
            'Order_ID': [1],
            'Sales': [100]
        }
        df = pd.DataFrame(data)
        
        rfm = calculate_rfm(df)
        assert len(rfm) == 1
    
    def test_extreme_values(self):
        """Test with extreme values"""
        data = {
            'Discount': [0.99, 0.01, 0.5],
            'Sales': [1000000, 1, 5000],
            'Profit': [100000, 0.5, 1000]
        }
        df = pd.DataFrame(data)
        
        result = calculate_roi_impact(df, discount_cap=0.5)
        assert not np.isnan(result['profit_gain'])
        assert not np.isinf(result['profit_gain'])
    
    def test_all_zero_discounts(self):
        """Test with zero discounts"""
        data = {
            'Discount': [0.0, 0.0, 0.0],
            'Sales': [1000, 2000, 3000],
            'Profit': [200, 400, 600]
        }
        df = pd.DataFrame(data)
        
        result = calculate_roi_impact(df, discount_cap=0.2)
        assert result['profit_gain'] == 0


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
