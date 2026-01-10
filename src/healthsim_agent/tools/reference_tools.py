"""Reference data tools for HealthSim Agent.

These tools query real-world reference data:
- query_reference: Query PopulationSim data (CDC PLACES, SVI, ADI)
- search_providers: Search NPPES provider data (8.9M records)
"""

from typing import Any, Dict, List, Optional

from .base import ToolResult, ok, err
from .connection import get_manager


# =============================================================================
# Reference Table Configuration
# =============================================================================

# Map short names to full schema-qualified table names
REFERENCE_TABLE_MAP = {
    "places_county": "population.places_county",
    "places_tract": "population.places_tract",
    "svi_county": "population.svi_county",
    "svi_tract": "population.svi_tract",
    "adi_blockgroup": "population.adi_blockgroup",
}

# Map table names to their state column
STATE_COLUMN_MAP = {
    "places_county": "stateabbr",
    "places_tract": "stateabbr", 
    "svi_county": "st_abbr",
    "svi_tract": "st_abbr",
    "adi_blockgroup": "fips",  # ADI uses FIPS codes
}

# Map table names to their county column
COUNTY_COLUMN_MAP = {
    "places_county": "countyname",
    "places_tract": "countyname",
    "svi_county": "county",
    "svi_tract": "county",
    "adi_blockgroup": "fips",  # No county name in ADI
}

# State abbreviation to FIPS mapping
STATE_FIPS = {
    "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
    "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13",
    "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
    "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24",
    "MA": "25", "MI": "26", "MN": "27", "MS": "28", "MO": "29",
    "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34",
    "NM": "35", "NY": "36", "NC": "37", "ND": "38", "OH": "39",
    "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45",
    "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50",
    "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56",
    "DC": "11", "PR": "72",
}


# =============================================================================
# Query Reference Data
# =============================================================================

def query_reference(
    table: str,
    state: Optional[str] = None,
    county: Optional[str] = None,
    limit: int = 20
) -> ToolResult:
    """Query PopulationSim reference data tables.
    
    Available tables:
    - places_county: CDC PLACES county-level health indicators (3,143 rows)
    - places_tract: CDC PLACES tract-level health indicators (83,522 rows)
    - svi_county: Social Vulnerability Index by county (3,144 rows)
    - svi_tract: Social Vulnerability Index by tract (84,120 rows)
    - adi_blockgroup: Area Deprivation Index by block group (242,336 rows)
    
    Args:
        table: Reference table name (see available tables above)
        state: Filter by state abbreviation (e.g., 'CA')
        county: Filter by county name (partial match)
        limit: Maximum rows to return (1-100, default 20)
        
    Returns:
        ToolResult with columns and filtered rows
        
    Example:
        >>> result = query_reference("places_county", state="CA", limit=5)
        >>> result.data["rows"][0]["countyname"]
        "Alameda"
    """
    # Validate table name
    table_lower = table.lower().strip()
    full_table = REFERENCE_TABLE_MAP.get(table_lower)
    
    if not full_table:
        return err(
            f"Unknown table: {table}",
            available=list(REFERENCE_TABLE_MAP.keys())
        )
    
    # Clamp limit
    limit = max(1, min(limit, 100))
    
    try:
        conn = get_manager().get_read_connection()
        
        # Build query with filters
        conditions = []
        query_params = []
        
        state_col = STATE_COLUMN_MAP.get(table_lower, "stateabbr")
        county_col = COUNTY_COLUMN_MAP.get(table_lower, "countyname")
        
        if state:
            state = state.upper().strip()
            
            if table_lower == "adi_blockgroup":
                # ADI uses FIPS codes - filter by first 2 chars of fips column
                state_fips = STATE_FIPS.get(state, state)
                conditions.append(f"SUBSTRING({state_col}, 1, 2) = ?")
                query_params.append(state_fips)
            else:
                conditions.append(f"{state_col} = ?")
                query_params.append(state)
        
        if county:
            if table_lower == "adi_blockgroup":
                # ADI doesn't have county name - skip this filter
                pass
            else:
                conditions.append(f"{county_col} ILIKE ?")
                query_params.append(f"%{county}%")
        
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        sql = f"SELECT * FROM {full_table}{where_clause} LIMIT {limit}"
        
        result = conn.execute(sql, query_params).fetchall()
        columns = [desc[0] for desc in conn.description]
        
        rows = []
        for row in result:
            rows.append({col: val for col, val in zip(columns, row)})
        
        return ok({
            "table": full_table,
            "columns": columns,
            "row_count": len(rows),
            "rows": rows,
        })
        
    except Exception as e:
        return err(f"Query failed: {str(e)}")


# =============================================================================
# Search Providers
# =============================================================================

# Common specialty keyword to taxonomy code mapping
SPECIALTY_TAXONOMY_MAP = {
    "family": ["207Q%"],  # Family Medicine
    "internal": ["207R%"],  # Internal Medicine
    "cardio": ["207RC%"],  # Cardiovascular Disease
    "neuro": ["2084N%"],  # Neurology
    "gastro": ["207RG%"],  # Gastroenterology
    "oncol": ["207RX%"],  # Medical Oncology
    "ortho": ["2086S%"],  # Orthopedic Surgery
    "nurse": ["363L%"],  # Nurse Practitioner
    "np": ["363L%"],  # Nurse Practitioner
    "physician assistant": ["363A%"],  # Physician Assistant
    "pa-c": ["363A%"],  # Physician Assistant
    "hospital": ["282N%"],  # Hospitals
    "urgent": ["261QU%"],  # Urgent Care
    "pediatric": ["208000%"],  # Pediatrics
    "ob": ["207V%"],  # OB/GYN
    "gyn": ["207V%"],  # OB/GYN
    "psychiatr": ["2084P%"],  # Psychiatry
    "dermat": ["207N%"],  # Dermatology
    "emergency": ["207P%"],  # Emergency Medicine
    "radiol": ["2085%"],  # Radiology
    "anesthes": ["207L%"],  # Anesthesiology
    "patholog": ["207Z%"],  # Pathology
    "surgery": ["208600%"],  # Surgery
    "physical therap": ["225100%"],  # Physical Therapy
    "occupational therap": ["225X%"],  # Occupational Therapy
    "speech": ["235Z%"],  # Speech-Language Pathology
    "pharmacy": ["183500%"],  # Pharmacy
    "dentist": ["1223%"],  # Dentistry
    "optom": ["152W%"],  # Optometry
    "chiropract": ["111N%"],  # Chiropractic
}


def search_providers(
    state: str,
    city: Optional[str] = None,
    county_fips: Optional[str] = None,
    zip_code: Optional[str] = None,
    specialty: Optional[str] = None,
    taxonomy_code: Optional[str] = None,
    entity_type: Optional[str] = None,
    limit: int = 50
) -> ToolResult:
    """Search real healthcare providers from NPPES data (8.9M records).
    
    ⚠️ USE THIS TOOL FIRST when providers are needed for a cohort.
    Returns REAL, registered healthcare providers with valid NPIs.
    Only generate synthetic providers if real data is unavailable.
    
    Args:
        state: State abbreviation (REQUIRED, e.g., 'CA', 'TX')
        city: City name filter (optional, partial match)
        county_fips: 5-digit county FIPS code (optional)
        zip_code: ZIP code (5 digits, optional)
        specialty: Specialty keyword (e.g., 'Family Medicine', 'Cardiology')
        taxonomy_code: NUCC taxonomy code (e.g., '207Q00000X')
        entity_type: 'individual' (NPI-1) or 'organization' (NPI-2)
        limit: Maximum results (1-200, default 50)
        
    Returns:
        ToolResult with provider records including NPI, name, specialty, location
        
    Common taxonomy codes:
        - 207Q00000X: Family Medicine
        - 207R00000X: Internal Medicine
        - 208D00000X: General Practice
        - 363L00000X: Nurse Practitioner
        - 363A00000X: Physician Assistant
        - 207RC0000X: Cardiovascular Disease
        - 2084N0400X: Neurology
        
    Example:
        >>> result = search_providers(state="CA", specialty="Family Medicine", limit=10)
        >>> result.data["providers"][0]["npi"]
        "1234567890"
    """
    # Validate required state
    if not state or not state.strip():
        return err("State is required (e.g., 'CA', 'TX')")
    
    state = state.upper().strip()
    if len(state) != 2:
        return err("State must be 2-letter abbreviation (e.g., 'CA', 'TX')")
    
    # Clamp limit
    limit = max(1, min(limit, 200))
    
    try:
        conn = get_manager().get_read_connection()
        
        # Check if network.providers table exists
        try:
            table_check = conn.execute(
                "SELECT COUNT(*) FROM information_schema.tables "
                "WHERE table_schema = 'network' AND table_name = 'providers'"
            ).fetchone()
            
            if not table_check or table_check[0] == 0:
                return err(
                    "NPPES provider data not loaded",
                    hint="NetworkSim reference data may not be imported"
                )
        except Exception:
            return err(
                "network.providers table not available",
                hint="NPPES data may not be loaded in this database"
            )
        
        # Build query with filters
        conditions = ["1=1"]  # Base condition for easier AND chaining
        query_params = []
        
        # State is required
        conditions.append("practice_state = ?")
        query_params.append(state)
        
        # Optional filters
        if city:
            conditions.append("practice_city ILIKE ?")
            query_params.append(f"%{city.strip()}%")
        
        if county_fips:
            conditions.append("county_fips = ?")
            query_params.append(county_fips.strip())
        
        if zip_code:
            conditions.append("practice_zip LIKE ?")
            query_params.append(f"{zip_code.strip()[:5]}%")
        
        if taxonomy_code:
            # Search across all 4 taxonomy columns
            conditions.append(
                "(taxonomy_1 = ? OR taxonomy_2 = ? OR taxonomy_3 = ? OR taxonomy_4 = ?)"
            )
            query_params.extend([taxonomy_code.strip()] * 4)
            
        elif specialty:
            # Map specialty keyword to taxonomy patterns
            specialty_lower = specialty.lower().strip()
            taxonomy_patterns = []
            
            for keyword, patterns in SPECIALTY_TAXONOMY_MAP.items():
                if keyword in specialty_lower:
                    for pattern in patterns:
                        taxonomy_patterns.append(f"taxonomy_1 LIKE '{pattern}'")
            
            if taxonomy_patterns:
                conditions.append(f"({' OR '.join(taxonomy_patterns)})")
        
        if entity_type:
            entity_type_lower = entity_type.lower().strip()
            if entity_type_lower == 'individual':
                conditions.append("entity_type_code = 1")
            elif entity_type_lower == 'organization':
                conditions.append("entity_type_code = 2")
        
        where_clause = " AND ".join(conditions)
        
        sql = f"""
            SELECT 
                npi,
                entity_type_code,
                CASE WHEN entity_type_code = 1 
                     THEN first_name || ' ' || last_name
                     ELSE organization_name 
                END as name,
                credential,
                taxonomy_1 as primary_taxonomy,
                practice_address_1 as practice_address,
                practice_city,
                practice_state,
                practice_zip,
                county_fips,
                phone
            FROM network.providers
            WHERE {where_clause}
            LIMIT {limit}
        """
        
        result = conn.execute(sql, query_params).fetchall()
        columns = [desc[0] for desc in conn.description]
        
        rows = []
        for row in result:
            rows.append({col: val for col, val in zip(columns, row)})
        
        return ok({
            "source": "NPPES (National Plan and Provider Enumeration System)",
            "data_type": "REAL registered providers",
            "filters_applied": {
                "state": state,
                "city": city,
                "county_fips": county_fips,
                "zip_code": zip_code,
                "specialty": specialty,
                "taxonomy_code": taxonomy_code,
                "entity_type": entity_type,
            },
            "result_count": len(rows),
            "providers": rows,
        })
        
    except Exception as e:
        return err(f"Provider search failed: {str(e)}")
