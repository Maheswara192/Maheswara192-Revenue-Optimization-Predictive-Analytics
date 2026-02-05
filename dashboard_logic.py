"""
Business Logic Module for Superstore Analytics Dashboard
Contains all core calculation functions without test dependencies
"""

import pandas as pd
import numpy as np


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
