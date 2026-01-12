"""
Tests for db/queries.py - QueryResult and ReferenceQueries.

Covers:
- QueryResult dataclass methods
- ReferenceQueries provider search methods
- Demographics queries
- Health indicator queries  
- ADI queries
- Utility methods
"""

import pytest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass

from healthsim_agent.db.queries import QueryResult, ReferenceQueries


class TestQueryResultDataclass:
    """Tests for QueryResult dataclass."""
    
    def test_create_query_result(self):
        """Test creating a basic QueryResult."""
        result = QueryResult(
            columns=["id", "name"],
            data=[["1", "Alice"], ["2", "Bob"]],
            row_count=2
        )
        
        assert result.columns == ["id", "name"]
        assert len(result.data) == 2
        assert result.row_count == 2
        assert result.error is None
    
    def test_create_query_result_with_error(self):
        """Test QueryResult with error."""
        result = QueryResult(
            columns=[],
            data=[],
            row_count=0,
            error="Table not found"
        )
        
        assert result.error == "Table not found"
        assert result.row_count == 0


class TestQueryResultToDicts:
    """Tests for QueryResult.to_dicts method."""
    
    def test_to_dicts_basic(self):
        """Test converting rows to dictionaries."""
        result = QueryResult(
            columns=["id", "name", "age"],
            data=[
                ["1", "Alice", 30],
                ["2", "Bob", 25]
            ],
            row_count=2
        )
        
        dicts = result.to_dicts()
        
        assert len(dicts) == 2
        assert dicts[0] == {"id": "1", "name": "Alice", "age": 30}
        assert dicts[1] == {"id": "2", "name": "Bob", "age": 25}
    
    def test_to_dicts_empty(self):
        """Test to_dicts with empty data."""
        result = QueryResult(
            columns=["id", "name"],
            data=[],
            row_count=0
        )
        
        dicts = result.to_dicts()
        
        assert dicts == []
    
    def test_to_dicts_single_row(self):
        """Test to_dicts with single row."""
        result = QueryResult(
            columns=["npi", "provider_name"],
            data=[["1234567890", "Dr. Smith"]],
            row_count=1
        )
        
        dicts = result.to_dicts()
        
        assert len(dicts) == 1
        assert dicts[0]["npi"] == "1234567890"


class TestQueryResultFirst:
    """Tests for QueryResult.first method."""
    
    def test_first_returns_dict(self):
        """Test first returns first row as dict."""
        result = QueryResult(
            columns=["id", "name"],
            data=[
                ["1", "First"],
                ["2", "Second"]
            ],
            row_count=2
        )
        
        first = result.first()
        
        assert first == {"id": "1", "name": "First"}
    
    def test_first_empty_returns_none(self):
        """Test first returns None for empty result."""
        result = QueryResult(
            columns=["id"],
            data=[],
            row_count=0
        )
        
        first = result.first()
        
        assert first is None


class TestReferenceQueriesInit:
    """Tests for ReferenceQueries initialization."""
    
    def test_init_with_connection(self):
        """Test initialization stores connection."""
        mock_conn = MagicMock()
        
        queries = ReferenceQueries(mock_conn)
        
        assert queries.conn is mock_conn


class TestSearchProviders:
    """Tests for search_providers method."""
    
    def test_search_providers_no_filters(self):
        """Test search_providers with no filters."""
        mock_conn = MagicMock()
        mock_result = QueryResult(
            columns=["npi", "provider_name"],
            data=[["1234567890", "Dr. Smith"]],
            row_count=1
        )
        mock_conn.execute_query.return_value = mock_result
        
        queries = ReferenceQueries(mock_conn)
        result = queries.search_providers()
        
        mock_conn.execute_query.assert_called_once()
        assert result.row_count == 1
    
    def test_search_providers_by_specialty(self):
        """Test search_providers with specialty filter."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.search_providers(specialty="cardiology")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "cardiology" in call_args.lower()
        assert "ILIKE" in call_args
    
    def test_search_providers_by_state(self):
        """Test search_providers with state filter."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.search_providers(state="TX")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "TX" in call_args
    
    def test_search_providers_by_city(self):
        """Test search_providers with city filter."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.search_providers(city="Austin")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "Austin" in call_args
    
    def test_search_providers_by_zip(self):
        """Test search_providers with zip filter."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.search_providers(zip_code="78701")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "78701" in call_args
    
    def test_search_providers_by_name(self):
        """Test search_providers with name filter."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.search_providers(name="Smith")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "Smith" in call_args
    
    def test_search_providers_with_limit(self):
        """Test search_providers respects limit."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.search_providers(limit=50)
        
        call_args = mock_conn.execute_query.call_args
        assert call_args[1]["limit"] == 50
    
    def test_search_providers_multiple_filters(self):
        """Test search_providers with multiple filters."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.search_providers(
            specialty="cardiology",
            state="CA",
            city="Los Angeles"
        )
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "cardiology" in call_args.lower()
        assert "CA" in call_args
        assert "Los Angeles" in call_args


class TestGetProviderByNpi:
    """Tests for get_provider_by_npi method."""
    
    def test_get_provider_by_npi(self):
        """Test getting provider by NPI."""
        mock_conn = MagicMock()
        mock_result = QueryResult(
            columns=["npi", "provider_name"],
            data=[["1234567890", "Dr. Jones"]],
            row_count=1
        )
        mock_conn.execute_query.return_value = mock_result
        
        queries = ReferenceQueries(mock_conn)
        result = queries.get_provider_by_npi("1234567890")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "1234567890" in call_args
        assert result.row_count == 1


class TestCountProvidersBySpecialty:
    """Tests for count_providers_by_specialty method."""
    
    def test_count_providers_no_state(self):
        """Test counting providers without state filter."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=["specialty", "provider_count"],
            data=[["Cardiology", 1000]],
            row_count=1
        )
        
        queries = ReferenceQueries(mock_conn)
        result = queries.count_providers_by_specialty()
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "GROUP BY" in call_args
        assert "COUNT(*)" in call_args
    
    def test_count_providers_with_state(self):
        """Test counting providers with state filter."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.count_providers_by_specialty(state="TX")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "TX" in call_args


class TestGetDemographicsByGeography:
    """Tests for get_demographics_by_geography method."""
    
    def test_get_demographics_by_state(self):
        """Test getting demographics by state."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=["state_abbr", "population"],
            data=[["TX", 29000000]],
            row_count=1
        )
        
        queries = ReferenceQueries(mock_conn)
        result = queries.get_demographics_by_geography(state="TX")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "TX" in call_args
    
    def test_get_demographics_by_county(self):
        """Test getting demographics by county."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.get_demographics_by_geography(county="Harris")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "Harris" in call_args
    
    def test_get_demographics_by_zip(self):
        """Test getting demographics by zip code."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.get_demographics_by_geography(zip_code="77001")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "77001" in call_args
    
    def test_get_demographics_no_filters(self):
        """Test getting demographics with no filters."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.get_demographics_by_geography()
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "1=1" in call_args


class TestGetPopulationByAgeGender:
    """Tests for get_population_by_age_gender method."""
    
    def test_get_population_state_only(self):
        """Test getting population by state."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=["county_name", "total_pop"],
            data=[["Harris", 4700000]],
            row_count=1
        )
        
        queries = ReferenceQueries(mock_conn)
        result = queries.get_population_by_age_gender(state="TX")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "TX" in call_args
    
    def test_get_population_with_county(self):
        """Test getting population by state and county."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.get_population_by_age_gender(state="TX", county="Harris")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "TX" in call_args
        assert "Harris" in call_args


class TestGetHealthIndicators:
    """Tests for get_health_indicators method."""
    
    def test_get_health_indicators_by_state(self):
        """Test getting health indicators by state."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=["state_abbr", "measure", "data_value"],
            data=[["TX", "Diabetes", 12.5]],
            row_count=1
        )
        
        queries = ReferenceQueries(mock_conn)
        result = queries.get_health_indicators(state="TX")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "TX" in call_args
    
    def test_get_health_indicators_by_measure(self):
        """Test getting health indicators by measure."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.get_health_indicators(measure="diabetes")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "diabetes" in call_args.lower()
    
    def test_get_health_indicators_no_filters(self):
        """Test getting health indicators with no filters."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.get_health_indicators()
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "1=1" in call_args


class TestGetDiseasePrevalence:
    """Tests for get_disease_prevalence method."""
    
    def test_get_disease_prevalence(self):
        """Test getting disease prevalence."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=["state_abbr", "county_name", "prevalence_pct"],
            data=[["TX", "Harris", 15.2]],
            row_count=1
        )
        
        queries = ReferenceQueries(mock_conn)
        result = queries.get_disease_prevalence("diabetes")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "diabetes" in call_args.lower()
        assert "ORDER BY" in call_args
    
    def test_get_disease_prevalence_with_state(self):
        """Test getting disease prevalence with state filter."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.get_disease_prevalence("hypertension", state="CA")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "hypertension" in call_args.lower()
        assert "CA" in call_args


class TestGetAdiByGeography:
    """Tests for get_adi_by_geography method."""
    
    def test_get_adi_by_state(self):
        """Test getting ADI by state."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=["state", "zipcode", "national_rank"],
            data=[["TX", "77001", 85]],
            row_count=1
        )
        
        queries = ReferenceQueries(mock_conn)
        result = queries.get_adi_by_geography(state="TX")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "TX" in call_args
    
    def test_get_adi_by_zip(self):
        """Test getting ADI by zip code."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.get_adi_by_geography(zip_code="77001")
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "77001" in call_args
    
    def test_get_adi_no_filters(self):
        """Test getting ADI with no filters."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.get_adi_by_geography()
        
        call_args = mock_conn.execute_query.call_args[0][0]
        assert "1=1" in call_args


class TestUtilityMethods:
    """Tests for utility methods."""
    
    def test_list_available_tables(self):
        """Test listing available tables."""
        mock_conn = MagicMock()
        mock_conn.list_tables.return_value = ["providers", "places"]
        
        queries = ReferenceQueries(mock_conn)
        tables = queries.list_available_tables()
        
        mock_conn.list_tables.assert_called_once()
        assert tables == ["providers", "places"]
    
    def test_describe_table(self):
        """Test describing a table."""
        mock_conn = MagicMock()
        mock_result = QueryResult(
            columns=["column_name", "data_type"],
            data=[["npi", "VARCHAR"]],
            row_count=1
        )
        mock_conn.get_table_info.return_value = mock_result
        
        queries = ReferenceQueries(mock_conn)
        result = queries.describe_table("providers")
        
        mock_conn.get_table_info.assert_called_once_with("providers")
    
    def test_count_table(self):
        """Test counting table rows."""
        mock_conn = MagicMock()
        mock_conn.count_rows.return_value = 1000000
        
        queries = ReferenceQueries(mock_conn)
        count = queries.count_table("providers")
        
        mock_conn.count_rows.assert_called_once_with("providers")
        assert count == 1000000
    
    def test_execute_custom(self):
        """Test executing custom query."""
        mock_conn = MagicMock()
        mock_result = QueryResult(
            columns=["count"],
            data=[[500]],
            row_count=1
        )
        mock_conn.execute_query.return_value = mock_result
        
        queries = ReferenceQueries(mock_conn)
        result = queries.execute_custom("SELECT COUNT(*) FROM providers")
        
        mock_conn.execute_query.assert_called_once()
        call_args = mock_conn.execute_query.call_args
        assert "SELECT COUNT(*)" in call_args[0][0]
    
    def test_execute_custom_with_limit(self):
        """Test executing custom query with limit."""
        mock_conn = MagicMock()
        mock_conn.execute_query.return_value = QueryResult(
            columns=[], data=[], row_count=0
        )
        
        queries = ReferenceQueries(mock_conn)
        queries.execute_custom("SELECT * FROM providers", limit=50)
        
        call_args = mock_conn.execute_query.call_args
        assert call_args[1]["limit"] == 50
