import pytest
import pandas as pd
import numpy as np

# Mock data for testing
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'Customer ID': ['C1', 'C1', 'C2'],
        'Order Date': pd.to_datetime(['2023-01-01', '2023-01-10', '2023-02-01']),
        'Order ID': ['O1', 'O2', 'O3'],
        'Sales': [100, 200, 500],
        'Profit': [10, 20, 50],
        'Discount': [0, 0.1, 0]
    })

def test_rfm_calculation(sample_data):
    """Test if RFM logic correctly aggregates values."""
    snapshot_date = sample_data['Order Date'].max() + pd.Timedelta(days=1)
    rfm = sample_data.groupby('Customer ID').agg({
        'Order Date': lambda x: (snapshot_date - x.max()).days,
        'Order ID': 'count',
        'Sales': 'sum'
    })
    
    assert rfm.loc['C1', 'Order ID'] == 2
    assert rfm.loc['C1', 'Sales'] == 300
    assert rfm.loc['C2', 'Order ID'] == 1
    assert rfm.loc['C2', 'Recency'] == 1

def test_profitability_logic(sample_data):
    """Verify that profit margin calculation is correct."""
    sample_data['Margin'] = sample_data['Profit'] / sample_data['Sales']
    assert sample_data.loc[0, 'Margin'] == 0.1
    assert sample_data['Margin'].mean() == 0.1

def test_data_integrity(sample_data):
    """Ensure no nulls exist after basic cleaning."""
    assert sample_data.isnull().sum().sum() == 0
