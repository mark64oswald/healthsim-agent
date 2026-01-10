"""Legacy JSON compatibility for HealthSim Agent.

Provides export/import functions for JSON-based cohort storage,
enabling backwards compatibility with older file-based workflows
and data sharing with external tools.

Ported from: healthsim-workspace/packages/core/src/healthsim/state/legacy.py
"""

from datetime import datetime, date
from pathlib import Path
from typing import Any
import json
import os


# Default paths for legacy storage
LEGACY_COHORTS_PATH = Path("data/cohorts")
LEGACY_WORKSPACES_PATH = Path("data/workspaces")


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def export_to_json(
    cohort_id: str,
    output_path: str | Path | None = None,
    include_entities: bool = True,
    pretty: bool = True,
    connection=None,
) -> Path:
    """Export a cohort to JSON file.
    
    Args:
        cohort_id: Cohort ID or name to export
        output_path: Output file path (defaults to data/cohorts/{cohort_id}.json)
        include_entities: Whether to include full entity data
        pretty: Whether to format JSON with indentation
        connection: Optional database connection
        
    Returns:
        Path to exported file
        
    Raises:
        ValueError: If cohort not found
    """
    from healthsim_agent.state.summary import get_cohort_by_name
    from healthsim_agent.state.auto_persist import get_auto_persist_service
    
    if connection is None:
        from healthsim_agent.database import DatabaseConnection
        connection = DatabaseConnection("data/healthsim-reference.duckdb")
    
    # Get cohort
    cohort = get_cohort_by_name(cohort_id, connection)
    if not cohort:
        raise ValueError(f"Cohort not found: {cohort_id}")
    
    # Build export data
    export_data = {
        "version": "2.0",
        "exported_at": datetime.now().isoformat(),
        "cohort": {
            "id": cohort["id"],
            "name": cohort["name"],
            "description": cohort.get("description"),
            "created_at": cohort["created_at"].isoformat() if cohort.get("created_at") else None,
            "updated_at": cohort["updated_at"].isoformat() if cohort.get("updated_at") else None,
        }
    }
    
    if include_entities:
        service = get_auto_persist_service(connection)
        
        # Get entity counts
        summary = service.get_cohort_summary(cohort["id"])
        export_data["entity_counts"] = summary.entity_counts
        
        # Export each entity type
        export_data["entities"] = {}
        for entity_type in summary.entity_counts.keys():
            if summary.entity_counts[entity_type] > 0:
                # Query all entities of this type
                result = service.query_cohort(
                    cohort_id=cohort["id"],
                    query=f"SELECT * FROM {entity_type}",
                    page_size=10000  # Get all
                )
                export_data["entities"][entity_type] = result.results
    
    # Determine output path
    if output_path is None:
        LEGACY_COHORTS_PATH.mkdir(parents=True, exist_ok=True)
        output_path = LEGACY_COHORTS_PATH / f"{cohort['name']}.json"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    with open(output_path, "w") as f:
        json.dump(
            export_data,
            f,
            cls=DateTimeEncoder,
            indent=2 if pretty else None
        )
    
    return output_path


def import_from_json(
    input_path: str | Path,
    cohort_name: str | None = None,
    connection=None,
) -> str:
    """Import a cohort from JSON file.
    
    Args:
        input_path: Path to JSON file
        cohort_name: Override cohort name (optional)
        connection: Optional database connection
        
    Returns:
        Imported cohort ID
        
    Raises:
        FileNotFoundError: If file not found
        ValueError: If invalid JSON format
    """
    from healthsim_agent.state.auto_persist import get_auto_persist_service
    
    if connection is None:
        from healthsim_agent.database import DatabaseConnection
        connection = DatabaseConnection("data/healthsim-reference.duckdb")
    
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    
    with open(input_path) as f:
        data = json.load(f)
    
    # Validate format
    if "cohort" not in data:
        raise ValueError("Invalid cohort JSON: missing 'cohort' key")
    
    service = get_auto_persist_service(connection)
    
    # Determine cohort name
    name = cohort_name or data["cohort"].get("name") or input_path.stem
    
    # Import entities
    cohort_id = None
    if "entities" in data:
        for entity_type, entities in data["entities"].items():
            if entities:
                result = service.persist_entities(
                    entities=entities,
                    entity_type=entity_type,
                    cohort_name=name if cohort_id is None else None,
                    cohort_id=cohort_id
                )
                if cohort_id is None:
                    cohort_id = result.cohort_id
    
    return cohort_id or ""


def list_legacy_cohorts(
    path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """List cohorts in legacy JSON format.
    
    Args:
        path: Path to cohorts directory (defaults to data/cohorts)
        
    Returns:
        List of cohort metadata dictionaries
    """
    cohorts_dir = Path(path) if path else LEGACY_COHORTS_PATH
    
    if not cohorts_dir.exists():
        return []
    
    cohorts = []
    for json_file in cohorts_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
            
            if "cohort" in data:
                cohorts.append({
                    "file": str(json_file),
                    "name": data["cohort"].get("name", json_file.stem),
                    "description": data["cohort"].get("description"),
                    "created_at": data["cohort"].get("created_at"),
                    "entity_counts": data.get("entity_counts", {}),
                    "version": data.get("version", "1.0")
                })
        except (json.JSONDecodeError, KeyError):
            # Skip invalid files
            continue
    
    return sorted(cohorts, key=lambda x: x.get("created_at") or "", reverse=True)


def migrate_legacy_cohort(
    json_path: str | Path,
    connection=None,
) -> str:
    """Migrate a single legacy JSON cohort to DuckDB.
    
    Args:
        json_path: Path to legacy JSON file
        connection: Optional database connection
        
    Returns:
        New cohort ID in DuckDB
    """
    return import_from_json(json_path, connection=connection)


def migrate_all_legacy_cohorts(
    source_dir: str | Path | None = None,
    connection=None,
) -> list[dict[str, Any]]:
    """Migrate all legacy JSON cohorts to DuckDB.
    
    Args:
        source_dir: Directory containing JSON files
        connection: Optional database connection
        
    Returns:
        List of migration results
    """
    source_dir = Path(source_dir) if source_dir else LEGACY_COHORTS_PATH
    
    if not source_dir.exists():
        return []
    
    results = []
    for json_file in source_dir.glob("*.json"):
        try:
            cohort_id = migrate_legacy_cohort(json_file, connection)
            results.append({
                "file": str(json_file),
                "cohort_id": cohort_id,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "file": str(json_file),
                "cohort_id": None,
                "status": "failed",
                "error": str(e)
            })
    
    return results


def export_cohort_for_sharing(
    cohort_id: str,
    output_dir: str | Path,
    include_metadata: bool = True,
    connection=None,
) -> dict[str, Path]:
    """Export cohort in shareable format with separate entity files.
    
    Creates a directory structure:
        {output_dir}/
            metadata.json
            patients.json
            encounters.json
            claims.json
            ...
    
    Args:
        cohort_id: Cohort to export
        output_dir: Output directory
        include_metadata: Whether to include metadata file
        connection: Optional database connection
        
    Returns:
        Dictionary mapping entity type to file path
    """
    from healthsim_agent.state.summary import get_cohort_by_name
    from healthsim_agent.state.auto_persist import get_auto_persist_service
    
    if connection is None:
        from healthsim_agent.database import DatabaseConnection
        connection = DatabaseConnection("data/healthsim-reference.duckdb")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cohort = get_cohort_by_name(cohort_id, connection)
    if not cohort:
        raise ValueError(f"Cohort not found: {cohort_id}")
    
    service = get_auto_persist_service(connection)
    summary = service.get_cohort_summary(cohort["id"])
    
    exported_files = {}
    
    # Export metadata
    if include_metadata:
        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump({
                "cohort": {
                    "id": cohort["id"],
                    "name": cohort["name"],
                    "description": cohort.get("description"),
                },
                "entity_counts": summary.entity_counts,
                "exported_at": datetime.now().isoformat()
            }, f, indent=2)
        exported_files["metadata"] = metadata_path
    
    # Export each entity type to separate file
    for entity_type, count in summary.entity_counts.items():
        if count > 0:
            result = service.query_cohort(
                cohort_id=cohort["id"],
                query=f"SELECT * FROM {entity_type}",
                page_size=10000
            )
            
            entity_file = output_dir / f"{entity_type}.json"
            with open(entity_file, "w") as f:
                json.dump(result.results, f, cls=DateTimeEncoder, indent=2)
            
            exported_files[entity_type] = entity_file
    
    return exported_files
