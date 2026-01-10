"""Reference data loader utilities.

Ported from: healthsim-workspace/packages/core/src/healthsim/db/reference/loader.py
"""

from typing import Any

import duckdb

from healthsim_agent.db.reference.populationsim import (
    import_adi_blockgroup,
    import_places_county,
    import_places_tract,
    import_svi_county,
    import_svi_tract,
)

# Reference tables with expected minimum row counts
REFERENCE_TABLES = {
    "places_tract": {"min_rows": 80000, "description": "CDC PLACES tract-level health indicators", "schema": "population"},
    "places_county": {"min_rows": 3000, "description": "CDC PLACES county-level health indicators", "schema": "population"},
    "svi_tract": {"min_rows": 80000, "description": "Social Vulnerability Index tract-level", "schema": "population"},
    "svi_county": {"min_rows": 3000, "description": "Social Vulnerability Index county-level", "schema": "population"},
    "adi_blockgroup": {"min_rows": 200000, "description": "Area Deprivation Index block group", "schema": "population"},
}


def import_all_reference_data(
    conn: duckdb.DuckDBPyConnection,
    replace: bool = False,
    verbose: bool = True,
    schema: str = "population",
) -> dict[str, int]:
    """Import all PopulationSim reference datasets."""
    results = {}

    importers = [
        ("places_tract", import_places_tract),
        ("places_county", import_places_county),
        ("svi_tract", import_svi_tract),
        ("svi_county", import_svi_county),
        ("adi_blockgroup", import_adi_blockgroup),
    ]

    for table_name, importer in importers:
        if verbose:
            print(f"  Importing {table_name}...", end=" ", flush=True)
        try:
            count = importer(conn, replace=replace, schema=schema)
            results[table_name] = count
            if verbose:
                print(f"{count:,} rows")
        except Exception as e:
            results[table_name] = -1
            if verbose:
                print(f"ERROR: {e}")

    return results


def get_reference_status(
    conn: duckdb.DuckDBPyConnection,
    schema: str = "population",
) -> dict[str, dict[str, Any]]:
    """Get status of all reference tables."""
    status = {}

    for table_name, info in REFERENCE_TABLES.items():
        full_table = f"{schema}.{table_name}"
        
        exists_result = conn.execute(f"""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema = '{schema}' AND table_name = '{table_name}'
        """).fetchone()
        exists = exists_result[0] > 0 if exists_result else False

        row_count = 0
        if exists:
            row_count = conn.execute(f"SELECT count(*) FROM {full_table}").fetchone()[0]

        status[table_name] = {
            "exists": exists,
            "row_count": row_count,
            "healthy": row_count >= info["min_rows"],
            "description": info["description"],
            "min_expected": info["min_rows"],
            "schema": schema,
        }

    return status


def is_reference_data_loaded(
    conn: duckdb.DuckDBPyConnection,
    schema: str = "population",
) -> bool:
    """Check if all reference data is loaded and healthy."""
    status = get_reference_status(conn, schema=schema)
    return all(info["healthy"] for info in status.values())


__all__ = [
    "import_all_reference_data",
    "get_reference_status",
    "is_reference_data_loaded",
    "REFERENCE_TABLES",
]
