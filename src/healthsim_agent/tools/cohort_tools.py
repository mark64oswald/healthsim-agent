"""Cohort management tools for HealthSim Agent.

These tools manage cohorts (collections of synthetic healthcare entities):
- list_cohorts: List all saved cohorts
- load_cohort: Load a cohort by name or ID
- save_cohort: Save a new cohort (full replacement)
- add_entities: Add entities incrementally (RECOMMENDED)
- delete_cohort: Delete a cohort

All operations work directly with DuckDB for persistence.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json

from .base import (
    ToolResult, ok, err,
    validate_entity_types, normalize_entity_type,
)
from .connection import get_manager


# =============================================================================
# List Cohorts
# =============================================================================

def list_cohorts(
    tag: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50
) -> ToolResult:
    """List all saved cohorts in the HealthSim database.
    
    Args:
        tag: Filter by tag (optional)
        search: Search in name/description (optional)
        limit: Maximum results (default 50, max 200)
        
    Returns:
        ToolResult with list of cohort summaries containing:
        cohort_id, name, description, created_at, updated_at, entity_count, tags
    """
    try:
        limit = min(limit, 200)
        conn = get_manager().get_read_connection()
        
        # Build query
        sql = """
            SELECT 
                c.id as cohort_id,
                c.name,
                c.description,
                c.created_at,
                c.updated_at,
                COUNT(ce.id) as entity_count
            FROM cohorts c
            LEFT JOIN cohort_entities ce ON c.id = ce.cohort_id
        """
        
        conditions = []
        params = []
        
        if search:
            conditions.append("(c.name ILIKE ? OR c.description ILIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if tag:
            sql += " JOIN cohort_tags ct ON c.id = ct.cohort_id"
            conditions.append("ct.tag = ?")
            params.append(tag.lower())
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " GROUP BY c.id, c.name, c.description, c.created_at, c.updated_at"
        sql += f" ORDER BY c.updated_at DESC LIMIT {limit}"
        
        rows = conn.execute(sql, params).fetchall()
        columns = ["cohort_id", "name", "description", "created_at", "updated_at", "entity_count"]
        
        # Get tags for each cohort
        result = []
        for row in rows:
            cohort_dict = dict(zip(columns, row))
            cohort_dict["created_at"] = str(cohort_dict["created_at"])
            cohort_dict["updated_at"] = str(cohort_dict["updated_at"])
            
            # Get tags
            tags_result = conn.execute(
                "SELECT tag FROM cohort_tags WHERE cohort_id = ?",
                [cohort_dict["cohort_id"]]
            ).fetchall()
            cohort_dict["tags"] = [t[0] for t in tags_result]
            
            result.append(cohort_dict)
        
        return ok(result, count=len(result))
        
    except Exception as e:
        return err(f"Failed to list cohorts: {str(e)}")


# =============================================================================
# Load Cohort
# =============================================================================

def load_cohort(
    cohort_id: str,
    include_entities: bool = True
) -> ToolResult:
    """Load a cohort by name or ID.
    
    Args:
        cohort_id: Cohort name or UUID (parameter name matches tool schema)
        include_entities: Whether to include full entity data (default True)
        
    Returns:
        ToolResult with cohort data including metadata and optionally entities
    """
    if not cohort_id or not cohort_id.strip():
        return err("Cohort name or ID is required")
    
    cohort_id_clean = cohort_id.strip()
    
    try:
        conn = get_manager().get_read_connection()
        
        # Try to find by ID or name
        row = conn.execute(
            "SELECT id, name, description, created_at, updated_at FROM cohorts WHERE id = ? OR name = ?",
            [cohort_id_clean, cohort_id_clean]
        ).fetchone()
        
        if not row:
            return err(f"Cohort not found: {cohort_id_clean}")
        
        cohort = {
            "cohort_id": row[0],
            "name": row[1],
            "description": row[2],
            "created_at": str(row[3]),
            "updated_at": str(row[4]),
        }
        
        # Get tags
        tags_result = conn.execute(
            "SELECT tag FROM cohort_tags WHERE cohort_id = ?",
            [cohort["cohort_id"]]
        ).fetchall()
        cohort["tags"] = [t[0] for t in tags_result]
        
        if include_entities:
            # Get entities grouped by type
            entities_result = conn.execute(
                "SELECT entity_type, entity_id, entity_data FROM cohort_entities WHERE cohort_id = ?",
                [cohort["cohort_id"]]
            ).fetchall()
            
            entities: Dict[str, List[Dict]] = {}
            for entity_type, entity_id, entity_data in entities_result:
                if entity_type not in entities:
                    entities[entity_type] = []
                try:
                    data = json.loads(entity_data) if isinstance(entity_data, str) else entity_data
                except json.JSONDecodeError:
                    data = {"_raw": entity_data, "_entity_id": entity_id}
                entities[entity_type].append(data)
            
            cohort["entities"] = entities
            cohort["entity_counts"] = {k: len(v) for k, v in entities.items()}
        
        return ok(cohort)
        
    except Exception as e:
        return err(f"Failed to load cohort: {str(e)}")


# =============================================================================
# Save Cohort
# =============================================================================

def save_cohort(
    name: str,
    entities: Dict[str, List[Dict[str, Any]]],
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    overwrite: bool = False,
    allow_reference_entities: bool = False
) -> ToolResult:
    """Save a cohort to the HealthSim database.
    
    ⚠️ USE add_entities() INSTEAD when:
    - Total entity count exceeds 50 (to avoid token limit truncation)
    - Building cohorts incrementally across multiple calls
    - Adding entities to an existing cohort
    
    This tool REPLACES ALL entities in one atomic operation.
    """
    # Validate inputs
    if not name or not name.strip():
        return err("Cohort name is required")
    
    name = name.strip()
    if len(name) > 200:
        return err("Cohort name must be 200 characters or less")
    
    if not entities:
        return err("Entities dict is required")
    
    # Validate entity types
    validation_error = validate_entity_types(entities, allow_reference=allow_reference_entities)
    if validation_error:
        return err(validation_error)
    
    try:
        with get_manager().write_connection() as conn:
            # Check if exists
            existing = conn.execute(
                "SELECT id FROM cohorts WHERE name = ?", [name]
            ).fetchone()
            
            if existing and not overwrite:
                return err(f"Cohort '{name}' already exists. Set overwrite=True to replace.")
            
            if existing:
                cohort_id = existing[0]
                # Delete existing entities
                conn.execute("DELETE FROM cohort_entities WHERE cohort_id = ?", [cohort_id])
                conn.execute("DELETE FROM cohort_tags WHERE cohort_id = ?", [cohort_id])
                # Update metadata
                conn.execute(
                    "UPDATE cohorts SET description = ?, updated_at = ? WHERE id = ?",
                    [description, datetime.utcnow(), cohort_id]
                )
            else:
                cohort_id = str(uuid4())
                now = datetime.utcnow()
                conn.execute(
                    "INSERT INTO cohorts (id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    [cohort_id, name, description, now, now]
                )
            
            # Add tags
            if tags:
                for tag in tags:
                    conn.execute(
                        "INSERT INTO cohort_tags (id, cohort_id, tag) VALUES (nextval('cohort_tags_seq'), ?, ?)",
                        [cohort_id, tag.lower()]
                    )
            
            # Add entities
            for entity_type, entity_list in entities.items():
                normalized = normalize_entity_type(entity_type)
                for entity in entity_list:
                    entity_id = (
                        entity.get('id') or 
                        entity.get(f'{normalized[:-1]}_id') or
                        entity.get('patient_id') or
                        entity.get('member_id') or
                        str(uuid4())
                    )
                    entity_json = json.dumps(entity, default=str)
                    conn.execute(
                        "INSERT INTO cohort_entities VALUES (nextval('cohort_entities_seq'), ?, ?, ?, ?, ?)",
                        [cohort_id, normalized, entity_id, entity_json, datetime.utcnow()]
                    )
        
        # Calculate entity counts
        entity_counts = {normalize_entity_type(k): len(v) for k, v in entities.items()}
        
        return ok({
            "cohort_id": cohort_id,
            "name": name,
            "entity_counts": entity_counts,
            "total_entities": sum(entity_counts.values()),
        }, status="saved")
        
    except Exception as e:
        return err(f"Failed to save cohort: {str(e)}")


# =============================================================================
# Add Entities (Incremental)
# =============================================================================

def add_entities(
    entities: Dict[str, List[Dict[str, Any]]],
    cohort_id: Optional[str] = None,
    cohort_name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    batch_number: Optional[int] = None,
    total_batches: Optional[int] = None,
    allow_reference_entities: bool = False
) -> ToolResult:
    """Add entities incrementally to a cohort (RECOMMENDED for most use cases).
    
    This tool uses UPSERT logic:
    - Adds new entities
    - Updates existing entities (matched by entity_id)
    - NEVER deletes entities not in the current payload
    """
    # Validate inputs
    if not entities:
        return err("Entities dict is required")
    
    if not cohort_id and not cohort_name:
        return err("Must provide cohort_id (to add to existing) or cohort_name (to create new)")
    
    # Validate entity types
    validation_error = validate_entity_types(entities, allow_reference=allow_reference_entities)
    if validation_error:
        return err(validation_error)
    
    try:
        with get_manager().write_connection() as conn:
            is_new_cohort = False
            
            if cohort_id:
                # Verify cohort exists
                existing = conn.execute(
                    "SELECT name FROM cohorts WHERE id = ?", [cohort_id]
                ).fetchone()
                
                if not existing:
                    return err(f"Cohort not found: {cohort_id}")
                
                cohort_name = existing[0]
            else:
                # Check if cohort exists by name
                existing = conn.execute(
                    "SELECT id FROM cohorts WHERE name = ?", [cohort_name]
                ).fetchone()
                
                if existing:
                    cohort_id = existing[0]
                else:
                    # Create new cohort
                    is_new_cohort = True
                    cohort_id = str(uuid4())
                    now = datetime.utcnow()
                    
                    conn.execute(
                        "INSERT INTO cohorts (id, name, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                        [cohort_id, cohort_name, description, now, now]
                    )
                    
                    # Add tags if provided
                    if tags:
                        for tag in tags:
                            conn.execute(
                                "INSERT INTO cohort_tags (id, cohort_id, tag) VALUES (nextval('cohort_tags_seq'), ?, ?)",
                                [cohort_id, tag.lower()]
                            )
            
            # Add entities
            entity_counts = {}
            sample_ids = {}
            
            for entity_type, entity_list in entities.items():
                if not entity_list:
                    continue
                
                normalized = normalize_entity_type(entity_type)
                added_ids = []
                
                for entity in entity_list:
                    entity_id = (
                        entity.get('id') or 
                        entity.get(f'{normalized[:-1]}_id') or
                        entity.get('patient_id') or
                        entity.get('member_id') or
                        str(uuid4())
                    )
                    
                    entity_json = json.dumps(entity, default=str)
                    
                    # Upsert: check if exists
                    existing_entity = conn.execute(
                        "SELECT id FROM cohort_entities WHERE cohort_id = ? AND entity_type = ? AND entity_id = ?",
                        [cohort_id, normalized, entity_id]
                    ).fetchone()
                    
                    if existing_entity:
                        conn.execute(
                            "UPDATE cohort_entities SET entity_data = ?, created_at = ? WHERE cohort_id = ? AND entity_type = ? AND entity_id = ?",
                            [entity_json, datetime.utcnow(), cohort_id, normalized, entity_id]
                        )
                    else:
                        conn.execute(
                            "INSERT INTO cohort_entities VALUES (nextval('cohort_entities_seq'), ?, ?, ?, ?, ?)",
                            [cohort_id, normalized, entity_id, entity_json, datetime.utcnow()]
                        )
                    
                    added_ids.append(entity_id)
                
                entity_counts[normalized] = len(added_ids)
                sample_ids[normalized] = added_ids[:5]
            
            # Update cohort timestamp
            conn.execute(
                "UPDATE cohorts SET updated_at = ? WHERE id = ?",
                [datetime.utcnow(), cohort_id]
            )
            
            # Get totals
            total_result = conn.execute(
                "SELECT entity_type, COUNT(*) FROM cohort_entities WHERE cohort_id = ? GROUP BY entity_type",
                [cohort_id]
            ).fetchall()
            
            totals_by_type = {row[0]: row[1] for row in total_result}
            total_entities = sum(totals_by_type.values())
        
        # Build response
        result = {
            "cohort_id": cohort_id,
            "cohort_name": cohort_name,
            "is_new_cohort": is_new_cohort,
            "entities_added_this_batch": entity_counts,
            "sample_ids": sample_ids,
            "cohort_totals": {
                "by_type": totals_by_type,
                "total_entities": total_entities,
            },
        }
        
        if batch_number is not None:
            result["batch_number"] = batch_number
        if total_batches is not None:
            result["total_batches"] = total_batches
            if batch_number is not None:
                result["batches_remaining"] = total_batches - batch_number
        
        return ok(result, status="added")
        
    except Exception as e:
        return err(f"Failed to add entities: {str(e)}")


# =============================================================================
# Delete Cohort
# =============================================================================

def delete_cohort(
    cohort_id: str,
    confirm: bool = False
) -> ToolResult:
    """Delete a cohort from the database.
    
    CAUTION: This permanently removes the cohort and all linked entities.
    You must set confirm=True to actually delete.
    
    Args:
        cohort_id: Cohort name or UUID (parameter name matches tool schema)
        confirm: Must be True to actually delete
    """
    if not cohort_id or not cohort_id.strip():
        return err("Cohort name or ID is required")
    
    if not confirm:
        return err(
            "Must set confirm=True to delete. This action is permanent.",
            cohort=cohort_id
        )
    
    cohort_id_clean = cohort_id.strip()
    
    try:
        with get_manager().write_connection() as conn:
            # Find cohort by ID or name
            row = conn.execute(
                "SELECT id FROM cohorts WHERE id = ? OR name = ?",
                [cohort_id_clean, cohort_id_clean]
            ).fetchone()
            
            if not row:
                return err(f"Cohort not found: {cohort_id_clean}")
            
            actual_cohort_id = row[0]
            
            # Delete entities, tags, and cohort
            conn.execute("DELETE FROM cohort_entities WHERE cohort_id = ?", [actual_cohort_id])
            conn.execute("DELETE FROM cohort_tags WHERE cohort_id = ?", [actual_cohort_id])
            conn.execute("DELETE FROM cohorts WHERE id = ?", [actual_cohort_id])
        
        return ok({"cohort": cohort_id_clean}, status="deleted")
        
    except Exception as e:
        return err(f"Failed to delete cohort: {str(e)}")
