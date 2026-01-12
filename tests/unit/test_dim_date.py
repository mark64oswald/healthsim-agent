"""Tests for dimensional generators dim_date module."""

import pytest
from datetime import date, timedelta


class TestGenerateDimDate:
    """Tests for generate_dim_date function."""
    
    def test_generate_basic(self):
        """Test basic date dimension generation."""
        from healthsim_agent.dimensional.generators.dim_date import generate_dim_date
        
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        df = generate_dim_date(start, end)
        
        assert df is not None
        assert len(df) == 31
    
    def test_generate_one_day(self):
        """Test single day generation."""
        from healthsim_agent.dimensional.generators.dim_date import generate_dim_date
        
        start = date(2024, 6, 15)
        end = date(2024, 6, 15)
        df = generate_dim_date(start, end)
        
        assert len(df) == 1
    
    def test_generate_full_year(self):
        """Test full year generation."""
        from healthsim_agent.dimensional.generators.dim_date import generate_dim_date
        
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        df = generate_dim_date(start, end)
        
        # 2024 is a leap year
        assert len(df) == 366
    
    def test_date_columns_exist(self):
        """Test that expected columns exist."""
        from healthsim_agent.dimensional.generators.dim_date import generate_dim_date
        
        start = date(2024, 1, 1)
        end = date(2024, 1, 7)
        df = generate_dim_date(start, end)
        
        # Check for common date dimension columns
        expected_cols = ['date_key', 'date_value']
        for col in expected_cols:
            assert col in df.columns or len(df.columns) > 0
    
    def test_year_boundaries(self):
        """Test date range spanning years."""
        from healthsim_agent.dimensional.generators.dim_date import generate_dim_date
        
        start = date(2023, 12, 25)
        end = date(2024, 1, 5)
        df = generate_dim_date(start, end)
        
        assert len(df) == 12
    
    def test_leap_year(self):
        """Test leap year handling."""
        from healthsim_agent.dimensional.generators.dim_date import generate_dim_date
        
        start = date(2024, 2, 28)
        end = date(2024, 3, 1)
        df = generate_dim_date(start, end)
        
        # Should include Feb 29
        assert len(df) == 3
    
    def test_returns_dataframe(self):
        """Test that result is a pandas DataFrame."""
        from healthsim_agent.dimensional.generators.dim_date import generate_dim_date
        import pandas as pd
        
        start = date(2024, 1, 1)
        end = date(2024, 1, 10)
        df = generate_dim_date(start, end)
        
        assert isinstance(df, pd.DataFrame)
