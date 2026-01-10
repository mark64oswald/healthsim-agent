"""Tests for healthsim_agent.tools.reference_tools module."""

import pytest
from pathlib import Path
import tempfile
import os

import duckdb

from healthsim_agent.tools import reset_manager
from healthsim_agent.tools.reference_tools import (
    query_reference,
    search_providers,
    REFERENCE_TABLE_MAP,
    STATE_FIPS,
    SPECIALTY_TAXONOMY_MAP,
)


@pytest.fixture
def temp_db_env(monkeypatch):
    """Create a temporary database with mock reference data."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name
    os.unlink(db_path)  # Delete empty file so DuckDB can create fresh
    
    conn = duckdb.connect(db_path)
    
    # Create population schema and tables
    conn.execute("CREATE SCHEMA IF NOT EXISTS population")
    conn.execute("""
        CREATE TABLE population.places_county (
            stateabbr VARCHAR,
            countyname VARCHAR,
            population INTEGER,
            obesity_crude FLOAT
        )
    """)
    conn.execute("""
        INSERT INTO population.places_county VALUES
        ('CA', 'Los Angeles', 10000000, 25.5),
        ('CA', 'San Francisco', 800000, 20.1),
        ('TX', 'Harris', 4500000, 28.3)
    """)
    
    conn.execute("""
        CREATE TABLE population.svi_county (
            st_abbr VARCHAR,
            county VARCHAR,
            svi_score FLOAT
        )
    """)
    conn.execute("""
        INSERT INTO population.svi_county VALUES
        ('CA', 'Los Angeles', 0.65),
        ('TX', 'Harris', 0.72)
    """)
    
    # Create network schema with providers
    conn.execute("CREATE SCHEMA IF NOT EXISTS network")
    conn.execute("""
        CREATE TABLE network.providers (
            npi VARCHAR PRIMARY KEY,
            entity_type_code INTEGER,
            first_name VARCHAR,
            last_name VARCHAR,
            organization_name VARCHAR,
            credential VARCHAR,
            taxonomy_1 VARCHAR,
            taxonomy_2 VARCHAR,
            taxonomy_3 VARCHAR,
            taxonomy_4 VARCHAR,
            practice_address_1 VARCHAR,
            practice_city VARCHAR,
            practice_state VARCHAR,
            practice_zip VARCHAR,
            county_fips VARCHAR,
            phone VARCHAR
        )
    """)
    conn.execute("""
        INSERT INTO network.providers VALUES
        ('1234567890', 1, 'John', 'Smith', NULL, 'MD', '207Q00000X', NULL, NULL, NULL, 
         '123 Main St', 'Los Angeles', 'CA', '90001', '06037', '555-1234'),
        ('0987654321', 1, 'Jane', 'Doe', NULL, 'NP', '363L00000X', NULL, NULL, NULL,
         '456 Oak Ave', 'San Francisco', 'CA', '94102', '06075', '555-5678'),
        ('1111111111', 2, NULL, NULL, 'General Hospital', NULL, '282N00000X', NULL, NULL, NULL,
         '789 Hospital Dr', 'Houston', 'TX', '77001', '48201', '555-9999')
    """)
    
    conn.close()
    
    monkeypatch.setenv("HEALTHSIM_DB_PATH", db_path)
    reset_manager()
    
    yield db_path
    
    reset_manager()
    try:
        os.unlink(db_path)
    except Exception:
        pass


class TestQueryReference:
    """Tests for query_reference function."""
    
    def test_query_places_county(self, temp_db_env):
        """Test querying CDC PLACES county data."""
        result = query_reference("places_county")
        assert result.success
        assert result.data["table"] == "population.places_county"
        assert len(result.data["rows"]) > 0
    
    def test_query_with_state_filter(self, temp_db_env):
        """Test filtering by state."""
        result = query_reference("places_county", state="CA")
        assert result.success
        for row in result.data["rows"]:
            assert row["stateabbr"] == "CA"
    
    def test_query_with_county_filter(self, temp_db_env):
        """Test filtering by county."""
        result = query_reference("places_county", county="Los Angeles")
        assert result.success
        assert len(result.data["rows"]) >= 1
        assert "Los Angeles" in result.data["rows"][0]["countyname"]
    
    def test_query_svi_county(self, temp_db_env):
        """Test querying SVI county data."""
        result = query_reference("svi_county", state="CA")
        assert result.success
        for row in result.data["rows"]:
            assert row["st_abbr"] == "CA"
    
    def test_unknown_table(self, temp_db_env):
        """Test unknown table is rejected."""
        result = query_reference("nonexistent_table")
        assert not result.success
        assert "Unknown table" in result.error
        assert "available" in str(result.metadata)
    
    def test_limit_applied(self, temp_db_env):
        """Test limit is respected."""
        result = query_reference("places_county", limit=1)
        assert result.success
        assert len(result.data["rows"]) <= 1
    
    def test_limit_clamped(self, temp_db_env):
        """Test limit is clamped to max."""
        result = query_reference("places_county", limit=999)
        # Should succeed with clamped limit
        assert result.success


class TestSearchProviders:
    """Tests for search_providers function."""
    
    def test_search_by_state(self, temp_db_env):
        """Test searching providers by state."""
        result = search_providers(state="CA")
        assert result.success
        assert result.data["result_count"] >= 1
        for provider in result.data["providers"]:
            assert provider["practice_state"] == "CA"
    
    def test_search_by_city(self, temp_db_env):
        """Test searching by city."""
        result = search_providers(state="CA", city="Los Angeles")
        assert result.success
        for provider in result.data["providers"]:
            assert "los angeles" in provider["practice_city"].lower()
    
    def test_search_individual_type(self, temp_db_env):
        """Test filtering by individual entity type."""
        result = search_providers(state="CA", entity_type="individual")
        assert result.success
        for provider in result.data["providers"]:
            assert provider["entity_type_code"] == 1
    
    def test_search_organization_type(self, temp_db_env):
        """Test filtering by organization entity type."""
        result = search_providers(state="TX", entity_type="organization")
        assert result.success
        for provider in result.data["providers"]:
            assert provider["entity_type_code"] == 2
    
    def test_search_by_taxonomy(self, temp_db_env):
        """Test searching by taxonomy code."""
        result = search_providers(state="CA", taxonomy_code="207Q00000X")
        assert result.success
        assert result.data["result_count"] >= 1
    
    def test_search_by_specialty_keyword(self, temp_db_env):
        """Test searching by specialty keyword."""
        result = search_providers(state="CA", specialty="nurse")
        assert result.success
        # Should find the NP
        npis = [p["npi"] for p in result.data["providers"]]
        assert "0987654321" in npis
    
    def test_state_required(self, temp_db_env):
        """Test that state is required."""
        result = search_providers(state="")
        assert not result.success
        assert "required" in result.error.lower()
    
    def test_state_format(self, temp_db_env):
        """Test state must be 2-letter abbreviation."""
        result = search_providers(state="California")
        assert not result.success
        assert "abbreviation" in result.error.lower()
    
    def test_result_includes_metadata(self, temp_db_env):
        """Test result includes source metadata."""
        result = search_providers(state="CA")
        assert result.success
        assert "NPPES" in result.data["source"]
        assert result.data["data_type"] == "REAL registered providers"


class TestReferenceDataConstants:
    """Tests for reference data constants."""
    
    def test_reference_table_map(self):
        """Test reference table map has expected tables."""
        assert "places_county" in REFERENCE_TABLE_MAP
        assert "svi_county" in REFERENCE_TABLE_MAP
        assert "adi_blockgroup" in REFERENCE_TABLE_MAP
    
    def test_state_fips_mapping(self):
        """Test state to FIPS mapping."""
        assert STATE_FIPS["CA"] == "06"
        assert STATE_FIPS["TX"] == "48"
        assert STATE_FIPS["NY"] == "36"
    
    def test_specialty_taxonomy_map(self):
        """Test specialty to taxonomy mapping."""
        assert "family" in SPECIALTY_TAXONOMY_MAP
        assert "nurse" in SPECIALTY_TAXONOMY_MAP
        assert "207Q%" in SPECIALTY_TAXONOMY_MAP["family"]
