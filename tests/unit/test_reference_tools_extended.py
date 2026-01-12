"""Extended tests for reference_tools module."""

import pytest


class TestSearchProviders:
    """Tests for search_providers function."""
    
    def test_search_basic(self):
        """Test basic provider search."""
        from healthsim_agent.tools.reference_tools import search_providers
        
        result = search_providers(state="TX", specialty="Cardiology")
        assert result is not None
    
    def test_search_by_state(self):
        """Test search by state."""
        from healthsim_agent.tools.reference_tools import search_providers
        
        result = search_providers(state="TX")
        assert result is not None
    
    def test_search_by_city(self):
        """Test search by city."""
        from healthsim_agent.tools.reference_tools import search_providers
        
        result = search_providers(state="TX", city="Houston")
        assert result is not None
    
    def test_search_with_limit(self):
        """Test search with limit."""
        from healthsim_agent.tools.reference_tools import search_providers
        
        result = search_providers(state="CA", limit=5)
        assert result is not None
    
    def test_search_with_zip(self):
        """Test search with zip code."""
        from healthsim_agent.tools.reference_tools import search_providers
        
        result = search_providers(state="TX", zip_code="77001")
        assert result is not None
    
    def test_search_combined_filters(self):
        """Test search with multiple filters."""
        from healthsim_agent.tools.reference_tools import search_providers
        
        result = search_providers(
            state="CA",
            specialty="Internal Medicine",
            limit=10
        )
        assert result is not None


class TestQueryReference:
    """Tests for query_reference function."""
    
    def test_query_providers(self):
        """Test querying reference data."""
        from healthsim_agent.tools.reference_tools import query_reference
        
        result = query_reference("SELECT COUNT(*) FROM network.providers")
        assert result is not None
    
    def test_query_invalid(self):
        """Test invalid query."""
        from healthsim_agent.tools.reference_tools import query_reference
        
        result = query_reference("INVALID SQL")
        assert result.success is False
    
    def test_query_empty(self):
        """Test empty query."""
        from healthsim_agent.tools.reference_tools import query_reference
        
        result = query_reference("")
        assert result.success is False
