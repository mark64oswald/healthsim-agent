"""Profile and Journey tools for HealthSim Agent.

Provides profile and journey management:
- Profiles: Reusable generation specifications
- Journeys: Multi-step cross-product workflows

Uses the ConnectionManager's close-before-write pattern for DuckDB operations.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4
import json

from .base import ToolResult, ok, err
from .connection import get_manager


# =============================================================================
# Table Setup
# =============================================================================

_tables_ensured = False


def _ensure_tables() -> None:
    """Ensure profile and journey tables exist."""
    global _tables_ensured
    if _tables_ensured:
        return
    
    with get_manager().write_connection() as conn:
        # Create sequence for auto-increment IDs
        conn.execute("CREATE SEQUENCE IF NOT EXISTS profile_exec_seq START 1")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS journey_exec_seq START 1")
        
        # Profile tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id              VARCHAR PRIMARY KEY,
                name            VARCHAR NOT NULL UNIQUE,
                description     VARCHAR,
                version         INTEGER DEFAULT 1,
                profile_spec    JSON NOT NULL,
                product         VARCHAR,
                tags            JSON,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata        JSON
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profile_executions (
                id              INTEGER DEFAULT nextval('profile_exec_seq') PRIMARY KEY,
                profile_id      VARCHAR NOT NULL,
                cohort_id       VARCHAR,
                executed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                seed            INTEGER,
                count           INTEGER,
                duration_ms     INTEGER,
                status          VARCHAR DEFAULT 'completed',
                error_message   VARCHAR,
                metadata        JSON
            )
        """)
        
        # Journey tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS journeys (
                id              VARCHAR PRIMARY KEY,
                name            VARCHAR NOT NULL UNIQUE,
                description     VARCHAR,
                version         INTEGER DEFAULT 1,
                steps           JSON NOT NULL,
                products        JSON,
                tags            JSON,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_builtin      BOOLEAN DEFAULT FALSE,
                metadata        JSON
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS journey_executions (
                id              INTEGER DEFAULT nextval('journey_exec_seq') PRIMARY KEY,
                journey_id      VARCHAR NOT NULL,
                cohort_id       VARCHAR,
                executed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                seed            INTEGER,
                total_entities  INTEGER,
                duration_ms     INTEGER,
                status          VARCHAR DEFAULT 'completed',
                steps_completed INTEGER,
                steps_total     INTEGER,
                error_message   VARCHAR,
                step_results    JSON,
                metadata        JSON
            )
        """)
    
    _tables_ensured = True


# =============================================================================
# Profile Tools
# =============================================================================

def list_profiles(
    product: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    limit: int = 50,
) -> ToolResult:
    """List saved profile specifications.
    
    Args:
        product: Filter by product (patientsim, membersim, etc.)
        tag: Filter by tag
        search: Search in name/description
        limit: Maximum results (default 50)
    
    Returns:
        ToolResult with list of profile summaries
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        sql = """
            SELECT 
                p.id,
                p.name,
                p.description,
                p.version,
                p.product,
                p.tags,
                p.created_at,
                p.updated_at,
                COUNT(pe.id) as execution_count,
                MAX(pe.executed_at) as last_executed
            FROM profiles p
            LEFT JOIN profile_executions pe ON p.id = pe.profile_id
            WHERE 1=1
        """
        params = []
        
        if product:
            sql += " AND p.product = ?"
            params.append(product)
        
        if tag:
            sql += " AND p.tags::VARCHAR LIKE ?"
            params.append(f'%"{tag}"%')
        
        if search:
            sql += " AND (p.name ILIKE ? OR p.description ILIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        sql += " GROUP BY p.id, p.name, p.description, p.version, p.product, p.tags, p.created_at, p.updated_at"
        sql += " ORDER BY p.updated_at DESC"
        sql += f" LIMIT {min(limit, 200)}"
        
        rows = conn.execute(sql, params).fetchall()
        
        profiles = []
        for row in rows:
            tags = json.loads(row[5]) if row[5] else []
            profiles.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "version": row[3],
                "product": row[4],
                "tags": tags,
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None,
                "execution_count": row[8] or 0,
                "last_executed": row[9].isoformat() if row[9] else None,
            })
        
        return ok(
            data={"profiles": profiles, "count": len(profiles)},
            message=f"Found {len(profiles)} profiles"
        )
        
    except Exception as e:
        return err(f"Failed to list profiles: {str(e)}")


def save_profile(
    name: str,
    profile_spec: dict[str, Any],
    description: str | None = None,
    product: str | None = None,
    tags: list[str] | None = None,
) -> ToolResult:
    """Save a new profile specification.
    
    Args:
        name: Unique profile name
        profile_spec: Profile specification dictionary
        description: Human-readable description
        product: Product type (patientsim, membersim, trialsim, rxmembersim)
        tags: List of tags for filtering
    
    Returns:
        ToolResult with saved profile ID
    """
    try:
        _ensure_tables()
        
        profile_id = f"profile-{uuid4().hex[:8]}"
        now = datetime.now()
        
        with get_manager().write_connection() as conn:
            conn.execute("""
                INSERT INTO profiles (id, name, description, profile_spec, product, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                profile_id,
                name,
                description,
                json.dumps(profile_spec),
                product,
                json.dumps(tags or []),
                now,
                now,
            ])
        
        return ok(
            data={"profile_id": profile_id, "name": name},
            message=f"Saved profile '{name}' as {profile_id}"
        )
        
    except Exception as e:
        if "unique" in str(e).lower():
            return err(f"Profile with name '{name}' already exists")
        return err(f"Failed to save profile: {str(e)}")


def load_profile(name_or_id: str) -> ToolResult:
    """Load a profile specification by name or ID.
    
    Args:
        name_or_id: Profile name or ID
    
    Returns:
        ToolResult with full profile specification
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        row = conn.execute("""
            SELECT id, name, description, version, profile_spec, product, tags, created_at, updated_at, metadata
            FROM profiles
            WHERE id = ? OR name = ?
        """, [name_or_id, name_or_id]).fetchone()
        
        if not row:
            return err(f"Profile not found: {name_or_id}")
        
        return ok(
            data={
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "version": row[3],
                "profile_spec": json.loads(row[4]) if row[4] else {},
                "product": row[5],
                "tags": json.loads(row[6]) if row[6] else [],
                "created_at": row[7].isoformat() if row[7] else None,
                "updated_at": row[8].isoformat() if row[8] else None,
                "metadata": json.loads(row[9]) if row[9] else None,
            },
            message=f"Loaded profile: {row[1]}"
        )
        
    except Exception as e:
        return err(f"Failed to load profile: {str(e)}")


def delete_profile(name_or_id: str) -> ToolResult:
    """Delete a profile by name or ID.
    
    Args:
        name_or_id: Profile name or ID
    
    Returns:
        ToolResult confirming deletion
    """
    try:
        _ensure_tables()
        
        # First check it exists
        conn = get_manager().get_read_connection()
        row = conn.execute("""
            SELECT id, name FROM profiles WHERE id = ? OR name = ?
        """, [name_or_id, name_or_id]).fetchone()
        
        if not row:
            return err(f"Profile not found: {name_or_id}")
        
        profile_id, profile_name = row
        
        with get_manager().write_connection() as conn:
            conn.execute("DELETE FROM profile_executions WHERE profile_id = ?", [profile_id])
            conn.execute("DELETE FROM profiles WHERE id = ?", [profile_id])
        
        return ok(
            data={"deleted_id": profile_id, "deleted_name": profile_name},
            message=f"Deleted profile: {profile_name}"
        )
        
    except Exception as e:
        return err(f"Failed to delete profile: {str(e)}")


def execute_profile(
    name_or_id: str,
    count: int | None = None,
    seed: int | None = None,
    save_to_cohort: str | None = None,
) -> ToolResult:
    """Execute a saved profile to generate entities.
    
    Args:
        name_or_id: Profile name or ID to execute
        count: Override count from profile spec
        seed: Random seed for reproducibility
        save_to_cohort: Save results to this cohort name
    
    Returns:
        ToolResult with generated entities
    """
    try:
        _ensure_tables()
        
        # Load the profile
        load_result = load_profile(name_or_id)
        if not load_result.success:
            return load_result
        
        profile = load_result.data
        profile_spec = profile["profile_spec"]
        product = profile.get("product", "patientsim")
        
        # Override count if specified
        if count:
            profile_spec["count"] = count
        
        actual_count = profile_spec.get("count", 10)
        
        # Generate based on product type
        start_time = datetime.now()
        
        from healthsim_agent.tools.generation_tools import (
            generate_patients, generate_members, generate_subjects, generate_rx_members
        )
        
        if product == "patientsim":
            result = generate_patients(count=actual_count, seed=seed)
        elif product == "membersim":
            result = generate_members(count=actual_count, seed=seed)
        elif product == "trialsim":
            result = generate_subjects(count=actual_count, seed=seed)
        elif product == "rxmembersim":
            result = generate_rx_members(count=actual_count, seed=seed)
        else:
            return err(f"Unknown product type: {product}")
        
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Record execution
        with get_manager().write_connection() as conn:
            conn.execute("""
                INSERT INTO profile_executions (profile_id, seed, count, duration_ms, status)
                VALUES (?, ?, ?, ?, 'completed')
            """, [profile["id"], seed, actual_count, duration_ms])
        
        if result.success:
            result.metadata["profile_id"] = profile["id"]
            result.metadata["profile_name"] = profile["name"]
            result.metadata["duration_ms"] = duration_ms
        
        return result
        
    except Exception as e:
        return err(f"Failed to execute profile: {str(e)}")


# =============================================================================
# Journey Tools
# =============================================================================

def list_journeys(
    product: str | None = None,
    tag: str | None = None,
    include_builtin: bool = True,
    limit: int = 50,
) -> ToolResult:
    """List saved journey definitions.
    
    Args:
        product: Filter by product involvement
        tag: Filter by tag
        include_builtin: Include built-in journeys (default True)
        limit: Maximum results
    
    Returns:
        ToolResult with list of journey summaries
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        sql = """
            SELECT 
                j.id,
                j.name,
                j.description,
                j.version,
                j.products,
                j.tags,
                j.is_builtin,
                j.steps,
                j.created_at,
                j.updated_at,
                COUNT(je.id) as execution_count,
                MAX(je.executed_at) as last_executed
            FROM journeys j
            LEFT JOIN journey_executions je ON j.id = je.journey_id
            WHERE 1=1
        """
        params = []
        
        if not include_builtin:
            sql += " AND j.is_builtin = FALSE"
        
        if product:
            sql += " AND j.products::VARCHAR LIKE ?"
            params.append(f'%"{product}"%')
        
        if tag:
            sql += " AND j.tags::VARCHAR LIKE ?"
            params.append(f'%"{tag}"%')
        
        sql += " GROUP BY j.id, j.name, j.description, j.version, j.products, j.tags, j.is_builtin, j.steps, j.created_at, j.updated_at"
        sql += " ORDER BY j.updated_at DESC"
        sql += f" LIMIT {min(limit, 200)}"
        
        rows = conn.execute(sql, params).fetchall()
        
        journeys = []
        for row in rows:
            products = json.loads(row[4]) if row[4] else []
            tags = json.loads(row[5]) if row[5] else []
            steps = json.loads(row[7]) if row[7] else []
            
            journeys.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "version": row[3],
                "products": products,
                "tags": tags,
                "is_builtin": row[6],
                "steps_count": len(steps),
                "created_at": row[8].isoformat() if row[8] else None,
                "updated_at": row[9].isoformat() if row[9] else None,
                "execution_count": row[10] or 0,
                "last_executed": row[11].isoformat() if row[11] else None,
            })
        
        return ok(
            data={"journeys": journeys, "count": len(journeys)},
            message=f"Found {len(journeys)} journeys"
        )
        
    except Exception as e:
        return err(f"Failed to list journeys: {str(e)}")


def save_journey(
    name: str,
    steps: list[dict[str, Any]],
    description: str | None = None,
    tags: list[str] | None = None,
) -> ToolResult:
    """Save a new journey definition.
    
    Args:
        name: Unique journey name
        steps: List of journey steps, each with:
            - name: Step name
            - product: patientsim, membersim, trialsim, rxmembersim
            - profile_ref: Reference to saved profile (optional)
            - profile_spec: Inline profile spec (optional)
            - depends_on: List of step names this depends on
            - entity_mapping: How to map entities from previous steps
        description: Human-readable description
        tags: List of tags for filtering
    
    Returns:
        ToolResult with saved journey ID
    """
    try:
        _ensure_tables()
        
        # Extract products from steps
        products = list(set(step.get("product", "patientsim") for step in steps))
        
        journey_id = f"journey-{uuid4().hex[:8]}"
        now = datetime.now()
        
        with get_manager().write_connection() as conn:
            conn.execute("""
                INSERT INTO journeys (id, name, description, steps, products, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                journey_id,
                name,
                description,
                json.dumps(steps),
                json.dumps(products),
                json.dumps(tags or []),
                now,
                now,
            ])
        
        return ok(
            data={"journey_id": journey_id, "name": name, "steps_count": len(steps)},
            message=f"Saved journey '{name}' with {len(steps)} steps"
        )
        
    except Exception as e:
        if "unique" in str(e).lower():
            return err(f"Journey with name '{name}' already exists")
        return err(f"Failed to save journey: {str(e)}")


def load_journey(name_or_id: str) -> ToolResult:
    """Load a journey definition by name or ID.
    
    Args:
        name_or_id: Journey name or ID
    
    Returns:
        ToolResult with full journey definition
    """
    try:
        _ensure_tables()
        conn = get_manager().get_read_connection()
        
        row = conn.execute("""
            SELECT id, name, description, version, steps, products, tags, is_builtin, created_at, updated_at, metadata
            FROM journeys
            WHERE id = ? OR name = ?
        """, [name_or_id, name_or_id]).fetchone()
        
        if not row:
            return err(f"Journey not found: {name_or_id}")
        
        return ok(
            data={
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "version": row[3],
                "steps": json.loads(row[4]) if row[4] else [],
                "products": json.loads(row[5]) if row[5] else [],
                "tags": json.loads(row[6]) if row[6] else [],
                "is_builtin": row[7],
                "created_at": row[8].isoformat() if row[8] else None,
                "updated_at": row[9].isoformat() if row[9] else None,
                "metadata": json.loads(row[10]) if row[10] else None,
            },
            message=f"Loaded journey: {row[1]}"
        )
        
    except Exception as e:
        return err(f"Failed to load journey: {str(e)}")


def delete_journey(name_or_id: str) -> ToolResult:
    """Delete a journey by name or ID.
    
    Args:
        name_or_id: Journey name or ID
    
    Returns:
        ToolResult confirming deletion
    """
    try:
        _ensure_tables()
        
        conn = get_manager().get_read_connection()
        row = conn.execute("""
            SELECT id, name, is_builtin FROM journeys WHERE id = ? OR name = ?
        """, [name_or_id, name_or_id]).fetchone()
        
        if not row:
            return err(f"Journey not found: {name_or_id}")
        
        journey_id, journey_name, is_builtin = row
        
        if is_builtin:
            return err(f"Cannot delete built-in journey: {journey_name}")
        
        with get_manager().write_connection() as conn:
            conn.execute("DELETE FROM journey_executions WHERE journey_id = ?", [journey_id])
            conn.execute("DELETE FROM journeys WHERE id = ?", [journey_id])
        
        return ok(
            data={"deleted_id": journey_id, "deleted_name": journey_name},
            message=f"Deleted journey: {journey_name}"
        )
        
    except Exception as e:
        return err(f"Failed to delete journey: {str(e)}")


def execute_journey(
    name_or_id: str,
    seed: int | None = None,
    save_to_cohort: str | None = None,
) -> ToolResult:
    """Execute a saved journey to generate entities across products.
    
    Args:
        name_or_id: Journey name or ID to execute
        seed: Random seed for reproducibility
        save_to_cohort: Save all results to this cohort name
    
    Returns:
        ToolResult with generated entities from all steps
    """
    try:
        _ensure_tables()
        
        # Load the journey
        load_result = load_journey(name_or_id)
        if not load_result.success:
            return load_result
        
        journey = load_result.data
        steps = journey["steps"]
        
        if not steps:
            return err(f"Journey has no steps: {journey['name']}")
        
        start_time = datetime.now()
        step_results = {}
        all_entities = {}
        total_entities = 0
        
        from healthsim_agent.tools.generation_tools import (
            generate_patients, generate_members, generate_subjects, generate_rx_members
        )
        
        generators = {
            "patientsim": generate_patients,
            "membersim": generate_members,
            "trialsim": generate_subjects,
            "rxmembersim": generate_rx_members,
        }
        
        for i, step in enumerate(steps):
            step_name = step.get("name", f"step_{i}")
            product = step.get("product", "patientsim")
            profile_spec = step.get("profile_spec", {})
            count = profile_spec.get("count", 10)
            
            generator = generators.get(product)
            if not generator:
                step_results[step_name] = {"status": "skipped", "reason": f"Unknown product: {product}"}
                continue
            
            # Execute the step
            result = generator(count=count, seed=seed)
            
            if result.success:
                step_results[step_name] = {
                    "status": "completed",
                    "entity_count": len(result.data.get(list(result.data.keys())[0], [])) if result.data else 0,
                }
                # Merge entities
                for key, entities in result.data.items():
                    if key not in all_entities:
                        all_entities[key] = []
                    all_entities[key].extend(entities)
                    total_entities += len(entities)
            else:
                step_results[step_name] = {"status": "failed", "error": result.error}
        
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        steps_completed = sum(1 for r in step_results.values() if r.get("status") == "completed")
        
        # Record execution
        with get_manager().write_connection() as conn:
            conn.execute("""
                INSERT INTO journey_executions 
                (journey_id, seed, total_entities, duration_ms, status, steps_completed, steps_total, step_results)
                VALUES (?, ?, ?, ?, 'completed', ?, ?, ?)
            """, [journey["id"], seed, total_entities, duration_ms, steps_completed, len(steps), json.dumps(step_results)])
        
        return ok(
            data={
                "journey_id": journey["id"],
                "journey_name": journey["name"],
                "entities": all_entities,
                "step_results": step_results,
                "total_entities": total_entities,
                "steps_completed": steps_completed,
                "steps_total": len(steps),
                "duration_ms": duration_ms,
            },
            message=f"Executed journey '{journey['name']}': {steps_completed}/{len(steps)} steps, {total_entities} entities"
        )
        
    except Exception as e:
        return err(f"Failed to execute journey: {str(e)}")


# =============================================================================
# Export JSON Tool
# =============================================================================

def export_json(
    entities: dict[str, list[dict[str, Any]]],
    output_path: str | None = None,
    pretty: bool = True,
) -> ToolResult:
    """Export entities to JSON format.
    
    Args:
        entities: Dictionary of entity type -> list of entities
        output_path: Path to write JSON file (optional, returns string if not provided)
        pretty: Use pretty formatting (default True)
    
    Returns:
        ToolResult with JSON string or file path
    """
    try:
        indent = 2 if pretty else None
        json_str = json.dumps(entities, indent=indent, default=str)
        
        if output_path:
            from pathlib import Path
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json_str)
            return ok(
                data={"path": str(path), "size_bytes": len(json_str)},
                message=f"Exported to {path}"
            )
        else:
            return ok(
                data={"json": json_str, "size_bytes": len(json_str)},
                message=f"Exported {len(json_str)} bytes of JSON"
            )
        
    except Exception as e:
        return err(f"Failed to export JSON: {str(e)}")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Profile tools
    "list_profiles",
    "save_profile",
    "load_profile",
    "delete_profile",
    "execute_profile",
    # Journey tools
    "list_journeys",
    "save_journey",
    "load_journey",
    "delete_journey",
    "execute_journey",
    # Export tools
    "export_json",
]
