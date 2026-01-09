"""
Query helpers for HealthSim Agent.

Provides convenience functions for querying:
- Reference data (NPPES providers, CDC PLACES, Census demographics)
- Canonical tables (patients, claims, etc.)
- Cohort management

Reference database is read-only; generated data goes to session state.
"""

from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class QueryResult:
    """Result from a database query."""
    columns: list[str]
    data: list[list[Any]]
    row_count: int
    error: str | None = None
    
    def to_dicts(self) -> list[dict[str, Any]]:
        """Convert rows to list of dictionaries."""
        return [dict(zip(self.columns, row)) for row in self.data]
    
    def first(self) -> dict[str, Any] | None:
        """Get first row as dictionary, or None."""
        if self.data:
            return dict(zip(self.columns, self.data[0]))
        return None


class ReferenceQueries:
    """
    Query helpers for reference data.
    
    The reference database contains:
    - NPPES: ~8.9M healthcare providers
    - CDC PLACES: Health indicators by geography
    - Census/SVI: Demographics and social vulnerability
    - ADI: Area Deprivation Index
    """
    
    def __init__(self, connection):
        """
        Initialize with database connection.
        
        Args:
            connection: DatabaseConnection instance
        """
        self.conn = connection
    
    # =========================================================================
    # NPPES Provider Queries
    # =========================================================================
    
    def search_providers(
        self,
        specialty: str | None = None,
        state: str | None = None,
        city: str | None = None,
        zip_code: str | None = None,
        name: str | None = None,
        limit: int = 20,
    ) -> QueryResult:
        """
        Search NPPES providers by various criteria.
        
        Args:
            specialty: Taxonomy description to search (partial match)
            state: Two-letter state code
            city: City name (partial match)
            zip_code: ZIP code (5 or 9 digit)
            name: Provider name (partial match)
            limit: Max results (default 20)
            
        Returns:
            QueryResult with matching providers
            
        Example:
            results = queries.search_providers(
                specialty="cardiology",
                state="TX",
                city="Austin"
            )
        """
        conditions = []
        
        if specialty:
            conditions.append(f"primary_taxonomy_desc ILIKE '%{specialty}%'")
        if state:
            conditions.append(f"state = '{state.upper()}'")
        if city:
            conditions.append(f"city ILIKE '%{city}%'")
        if zip_code:
            conditions.append(f"zip LIKE '{zip_code[:5]}%'")
        if name:
            conditions.append(f"provider_name ILIKE '%{name}%'")
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT 
            npi,
            provider_name,
            provider_type,
            primary_taxonomy_code,
            primary_taxonomy_desc,
            address,
            city,
            state,
            zip,
            phone
        FROM nppes_providers
        WHERE {where}
        LIMIT {limit}
        """
        
        return self.conn.execute_query(query, limit=limit)
    
    def get_provider_by_npi(self, npi: str) -> QueryResult:
        """
        Get a specific provider by NPI.
        
        Args:
            npi: 10-digit NPI number
            
        Returns:
            QueryResult with provider details
        """
        query = f"""
        SELECT *
        FROM nppes_providers
        WHERE npi = '{npi}'
        """
        return self.conn.execute_query(query, limit=1)
    
    def count_providers_by_specialty(
        self,
        state: str | None = None,
        limit: int = 20
    ) -> QueryResult:
        """
        Get provider counts by specialty.
        
        Args:
            state: Optional state filter
            limit: Max specialties to return
            
        Returns:
            QueryResult with specialty counts
        """
        where = f"WHERE state = '{state.upper()}'" if state else ""
        
        query = f"""
        SELECT 
            primary_taxonomy_desc as specialty,
            COUNT(*) as provider_count
        FROM nppes_providers
        {where}
        GROUP BY primary_taxonomy_desc
        ORDER BY provider_count DESC
        LIMIT {limit}
        """
        return self.conn.execute_query(query, limit=limit)
    
    # =========================================================================
    # Demographics Queries (Census/SVI)
    # =========================================================================
    
    def get_demographics_by_geography(
        self,
        state: str | None = None,
        county: str | None = None,
        zip_code: str | None = None,
        limit: int = 20,
    ) -> QueryResult:
        """
        Get demographic data by geography.
        
        Args:
            state: Two-letter state code
            county: County name (partial match)
            zip_code: ZIP code
            limit: Max results
            
        Returns:
            QueryResult with demographic data
        """
        conditions = []
        
        if state:
            conditions.append(f"state_abbr = '{state.upper()}'")
        if county:
            conditions.append(f"county_name ILIKE '%{county}%'")
        if zip_code:
            conditions.append(f"zcta = '{zip_code}'")
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        # Try the SVI table first (more comprehensive)
        query = f"""
        SELECT 
            state_abbr,
            county_name,
            fips,
            e_totpop as population,
            e_pov150 as poverty_count,
            e_nohsdp as no_hs_diploma,
            e_age65 as age_65_plus,
            rpl_themes as svi_score
        FROM svi_county
        WHERE {where}
        LIMIT {limit}
        """
        return self.conn.execute_query(query, limit=limit)
    
    def get_population_by_age_gender(
        self,
        state: str,
        county: str | None = None,
    ) -> QueryResult:
        """
        Get population breakdown by age and gender.
        
        Args:
            state: Two-letter state code
            county: Optional county name
            
        Returns:
            QueryResult with age/gender distribution
        """
        conditions = [f"state_abbr = '{state.upper()}'"]
        if county:
            conditions.append(f"county_name ILIKE '%{county}%'")
        
        where = " AND ".join(conditions)
        
        query = f"""
        SELECT 
            county_name,
            e_totpop as total_pop,
            e_male as male,
            e_female as female,
            e_age17 as under_18,
            e_age65 as over_65
        FROM svi_county
        WHERE {where}
        """
        return self.conn.execute_query(query, limit=100)
    
    # =========================================================================
    # Health Indicator Queries (CDC PLACES)
    # =========================================================================
    
    def get_health_indicators(
        self,
        state: str | None = None,
        county: str | None = None,
        measure: str | None = None,
        limit: int = 50,
    ) -> QueryResult:
        """
        Get CDC PLACES health indicators.
        
        Args:
            state: Two-letter state code
            county: County name (partial match)
            measure: Health measure name (e.g., 'diabetes', 'obesity')
            limit: Max results
            
        Returns:
            QueryResult with health indicators
        """
        conditions = []
        
        if state:
            conditions.append(f"state_abbr = '{state.upper()}'")
        if county:
            conditions.append(f"county_name ILIKE '%{county}%'")
        if measure:
            conditions.append(f"measure ILIKE '%{measure}%'")
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT 
            state_abbr,
            county_name,
            measure,
            data_value,
            data_value_unit,
            low_confidence_limit,
            high_confidence_limit
        FROM cdc_places_county
        WHERE {where}
        LIMIT {limit}
        """
        return self.conn.execute_query(query, limit=limit)
    
    def get_disease_prevalence(
        self,
        disease: str,
        state: str | None = None,
    ) -> QueryResult:
        """
        Get disease prevalence rates.
        
        Args:
            disease: Disease name (e.g., 'diabetes', 'hypertension')
            state: Optional state filter
            
        Returns:
            QueryResult with prevalence by geography
        """
        conditions = [f"measure ILIKE '%{disease}%'"]
        if state:
            conditions.append(f"state_abbr = '{state.upper()}'")
        
        where = " AND ".join(conditions)
        
        query = f"""
        SELECT 
            state_abbr,
            county_name,
            measure,
            data_value as prevalence_pct,
            total_population
        FROM cdc_places_county
        WHERE {where}
        ORDER BY data_value DESC
        LIMIT 50
        """
        return self.conn.execute_query(query, limit=50)
    
    # =========================================================================
    # Area Deprivation Index (ADI) Queries
    # =========================================================================
    
    def get_adi_by_geography(
        self,
        state: str | None = None,
        zip_code: str | None = None,
        limit: int = 20,
    ) -> QueryResult:
        """
        Get Area Deprivation Index data.
        
        ADI provides neighborhood-level socioeconomic measures.
        
        Args:
            state: Two-letter state code
            zip_code: ZIP code
            limit: Max results
            
        Returns:
            QueryResult with ADI scores
        """
        conditions = []
        
        if state:
            conditions.append(f"state = '{state.upper()}'")
        if zip_code:
            conditions.append(f"zipcode = '{zip_code}'")
        
        where = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT 
            state,
            zipcode,
            adi_natrank as national_rank,
            adi_staternk as state_rank
        FROM adi_zipcode
        WHERE {where}
        LIMIT {limit}
        """
        return self.conn.execute_query(query, limit=limit)
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def list_available_tables(self) -> list[str]:
        """List all tables in the reference database."""
        return self.conn.list_tables()
    
    def describe_table(self, table_name: str) -> QueryResult:
        """Get column information for a table."""
        return self.conn.get_table_info(table_name)
    
    def count_table(self, table_name: str) -> int:
        """Get row count for a table."""
        return self.conn.count_rows(table_name)
    
    def execute_custom(
        self,
        query: str,
        limit: int = 100,
    ) -> QueryResult:
        """
        Execute a custom SQL query.
        
        Args:
            query: SQL query string
            limit: Max rows to return
            
        Returns:
            QueryResult with query results
        """
        return self.conn.execute_query(query, limit=limit)
