"""PopulationSim reference data importer.

Ported from: healthsim-workspace/packages/core/src/healthsim/db/reference/populationsim.py

Note: In healthsim-agent, reference data is typically pre-loaded in the DuckDB database.
These functions support importing from CSV files if needed for data refresh.
"""

from pathlib import Path
from typing import Optional

import duckdb


def get_default_data_path() -> Path:
    """Get the default path to PopulationSim data directory."""
    # For healthsim-agent, data may be in a data/ subdirectory
    module_path = Path(__file__).resolve()
    # Navigate to project root and find data directory
    project_root = module_path.parent.parent.parent.parent
    return project_root / "data" / "populationsim"


def import_places_tract(
    conn: duckdb.DuckDBPyConnection,
    csv_path: Optional[Path] = None,
    replace: bool = False,
    schema: str = "population",
) -> int:
    """Import CDC PLACES tract-level data."""
    table_name = f"{schema}.places_tract" if schema else "places_tract"
    csv_path = csv_path or get_default_data_path() / "tract" / "places_tract_2024.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Check if table exists
    existing = conn.execute(f"""
        SELECT count(*) FROM information_schema.tables 
        WHERE table_schema = '{schema}' AND table_name = 'places_tract'
    """).fetchone()[0]

    if existing and not replace:
        return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]

    if replace and existing:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.execute(f"""
        CREATE TABLE {table_name} AS 
        SELECT * FROM read_csv_auto('{csv_path}', header=true, normalize_names=true)
    """)

    conn.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_places_tract_pk ON {table_name}(tractfips)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_places_tract_county ON {table_name}(countyfips)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_places_tract_state ON {table_name}(stateabbr)")

    return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]


def import_places_county(
    conn: duckdb.DuckDBPyConnection,
    csv_path: Optional[Path] = None,
    replace: bool = False,
    schema: str = "population",
) -> int:
    """Import CDC PLACES county-level data."""
    table_name = f"{schema}.places_county" if schema else "places_county"
    csv_path = csv_path or get_default_data_path() / "county" / "places_county_2024.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    existing = conn.execute(f"""
        SELECT count(*) FROM information_schema.tables 
        WHERE table_schema = '{schema}' AND table_name = 'places_county'
    """).fetchone()[0]

    if existing and not replace:
        return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]

    if replace and existing:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.execute(f"""
        CREATE TABLE {table_name} AS 
        SELECT * FROM read_csv_auto('{csv_path}', header=true, normalize_names=true)
    """)

    conn.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_places_county_pk ON {table_name}(countyfips)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_places_county_state ON {table_name}(stateabbr)")

    return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]


def import_svi_tract(
    conn: duckdb.DuckDBPyConnection,
    csv_path: Optional[Path] = None,
    replace: bool = False,
    schema: str = "population",
) -> int:
    """Import Social Vulnerability Index tract-level data."""
    table_name = f"{schema}.svi_tract" if schema else "svi_tract"
    csv_path = csv_path or get_default_data_path() / "tract" / "svi_tract_2022.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    existing = conn.execute(f"""
        SELECT count(*) FROM information_schema.tables 
        WHERE table_schema = '{schema}' AND table_name = 'svi_tract'
    """).fetchone()[0]

    if existing and not replace:
        return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]

    if replace and existing:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.execute(f"""
        CREATE TABLE {table_name} AS 
        SELECT * FROM read_csv_auto('{csv_path}', header=true, normalize_names=true)
    """)

    conn.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_svi_tract_pk ON {table_name}(fips)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_svi_tract_county ON {table_name}(stcnty)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_svi_tract_state ON {table_name}(st_abbr)")

    return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]


def import_svi_county(
    conn: duckdb.DuckDBPyConnection,
    csv_path: Optional[Path] = None,
    replace: bool = False,
    schema: str = "population",
) -> int:
    """Import Social Vulnerability Index county-level data."""
    table_name = f"{schema}.svi_county" if schema else "svi_county"
    csv_path = csv_path or get_default_data_path() / "county" / "svi_county_2022.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    existing = conn.execute(f"""
        SELECT count(*) FROM information_schema.tables 
        WHERE table_schema = '{schema}' AND table_name = 'svi_county'
    """).fetchone()[0]

    if existing and not replace:
        return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]

    if replace and existing:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.execute(f"""
        CREATE TABLE {table_name} AS 
        SELECT * FROM read_csv_auto('{csv_path}', header=true, normalize_names=true)
    """)

    conn.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_svi_county_pk ON {table_name}(stcnty)")
    conn.execute(f"CREATE INDEX IF NOT EXISTS idx_svi_county_state ON {table_name}(st_abbr)")

    return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]


def import_adi_blockgroup(
    conn: duckdb.DuckDBPyConnection,
    csv_path: Optional[Path] = None,
    replace: bool = False,
    schema: str = "population",
) -> int:
    """Import Area Deprivation Index block group data."""
    table_name = f"{schema}.adi_blockgroup" if schema else "adi_blockgroup"
    csv_path = csv_path or get_default_data_path() / "block_group" / "adi_blockgroup_2023.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    existing = conn.execute(f"""
        SELECT count(*) FROM information_schema.tables 
        WHERE table_schema = '{schema}' AND table_name = 'adi_blockgroup'
    """).fetchone()[0]

    if existing and not replace:
        return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]

    if replace and existing:
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    conn.execute(f"""
        CREATE TABLE {table_name} AS 
        SELECT * FROM read_csv_auto('{csv_path}', header=true, normalize_names=true)
    """)

    conn.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_adi_blockgroup_pk ON {table_name}(fips)")

    return conn.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]


__all__ = [
    "import_places_tract",
    "import_places_county",
    "import_svi_tract",
    "import_svi_county",
    "import_adi_blockgroup",
    "get_default_data_path",
]
