"""
Auto-persist service for HealthSim Agent.

Implements the Structured RAG pattern:
- Summary in context (~500 tokens)
- Samples for consistency (~3000 tokens)
- Data stays in DuckDB
- Paginated queries for retrieval

This service is the primary interface for the auto-persist feature,
coordinating between auto-naming, summary generation, and database operations.

Ported from: healthsim-workspace/packages/core/src/healthsim/state/auto_persist.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4
import re
import json

from .summary import CohortSummary, generate_summary, get_cohort_by_name
from .auto_naming import generate_cohort_name, sanitize_name
from .serializers import get_serializer, get_table_info, ENTITY_TABLE_MAP


@dataclass
class PersistResult:
    """Result of a persist operation."""
    
    cohort_id: str
    cohort_name: str
    entity_type: str
    entities_persisted: int
    entity_ids: list[str]
    summary: CohortSummary | None
    is_new_cohort: bool
    batch_number: int | None = None
    total_batches: int | None = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cohort_id': self.cohort_id,
            'cohort_name': self.cohort_name,
            'entity_type': self.entity_type,
            'entities_persisted': self.entities_persisted,
            'entity_ids': self.entity_ids,
            'is_new_cohort': self.is_new_cohort,
            'batch_number': self.batch_number,
            'total_batches': self.total_batches,
            'summary': self.summary.to_dict() if self.summary else None,
        }


@dataclass
class QueryResult:
    """Result of a paginated query."""
    
    results: list[dict]
    total_count: int
    page: int
    page_size: int
    has_more: bool
    query_executed: str
    
    @property
    def offset(self) -> int:
        """Get current offset."""
        return self.page * self.page_size
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'results': self.results,
            'total_count': self.total_count,
            'page': self.page,
            'page_size': self.page_size,
            'has_more': self.has_more,
            'query_executed': self.query_executed,
        }


@dataclass
class CohortBrief:
    """Brief cohort info for listing."""
    
    cohort_id: str
    name: str
    description: str | None
    entity_count: int
    created_at: datetime | None
    updated_at: datetime | None
    tags: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cohort_id': self.cohort_id,
            'name': self.name,
            'description': self.description,
            'entity_count': self.entity_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': self.tags,
        }


@dataclass
class CloneResult:
    """Result of a clone operation."""
    
    source_cohort_id: str
    source_cohort_name: str
    new_cohort_id: str
    new_cohort_name: str
    entities_cloned: dict[str, int]
    total_entities: int
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source_cohort_id': self.source_cohort_id,
            'source_cohort_name': self.source_cohort_name,
            'new_cohort_id': self.new_cohort_id,
            'new_cohort_name': self.new_cohort_name,
            'entities_cloned': self.entities_cloned,
            'total_entities': self.total_entities,
        }


@dataclass
class MergeResult:
    """Result of a merge operation."""
    
    source_cohort_ids: list[str]
    source_cohort_names: list[str]
    target_cohort_id: str
    target_cohort_name: str
    entities_merged: dict[str, int]
    total_entities: int
    conflicts_resolved: int
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source_cohort_ids': self.source_cohort_ids,
            'source_cohort_names': self.source_cohort_names,
            'target_cohort_id': self.target_cohort_id,
            'target_cohort_name': self.target_cohort_name,
            'entities_merged': self.entities_merged,
            'total_entities': self.total_entities,
            'conflicts_resolved': self.conflicts_resolved,
        }


@dataclass
class ExportResult:
    """Result of an export operation."""
    
    cohort_id: str
    cohort_name: str
    format: str
    file_path: str
    entities_exported: dict[str, int]
    total_entities: int
    file_size_bytes: int
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cohort_id': self.cohort_id,
            'cohort_name': self.cohort_name,
            'format': self.format,
            'file_path': self.file_path,
            'entities_exported': self.entities_exported,
            'total_entities': self.total_entities,
            'file_size_bytes': self.file_size_bytes,
        }


# SQL patterns that are NOT allowed in queries
DISALLOWED_SQL_PATTERNS = [
    r'\bINSERT\b',
    r'\bUPDATE\b',
    r'\bDELETE\b',
    r'\bDROP\b',
    r'\bCREATE\b',
    r'\bALTER\b',
    r'\bTRUNCATE\b',
    r'\bGRANT\b',
    r'\bREVOKE\b',
    r'\bEXEC\b',
    r'\bEXECUTE\b',
    r'--',  # SQL comments
    r';.*\S',  # Multiple statements
]

# Tables that contain entity data (for cloning/merging/export)
CANONICAL_TABLES = [
    # Core
    ('persons', 'person_id'),
    ('providers', 'provider_id'),
    ('facilities', 'facility_id'),
    # PatientSim
    ('patients', 'id'),
    ('encounters', 'encounter_id'),
    ('diagnoses', 'id'),
    ('procedures', 'id'),
    ('lab_results', 'id'),
    ('medications', 'id'),
    ('allergies', 'id'),
    ('vitals', 'id'),
    # MemberSim
    ('members', 'member_id'),
    ('accumulators', 'id'),
    ('claims', 'claim_id'),
    ('claim_lines', 'id'),
    ('authorizations', 'id'),
    # RxMemberSim
    ('rx_members', 'rx_member_id'),
    ('prescriptions', 'prescription_id'),
    ('pharmacy_claims', 'pharmacy_claim_id'),
    ('dur_alerts', 'id'),
    ('pharmacies', 'pharmacy_id'),
    # TrialSim
    ('studies', 'study_id'),
    ('sites', 'site_id'),
    ('treatment_arms', 'arm_id'),
    ('subjects', 'subject_id'),
    ('adverse_events', 'ae_id'),
    ('visit_schedule', 'scheduled_visit_id'),
    ('actual_visits', 'actual_visit_id'),
    ('disposition_events', 'disposition_id'),
    # PopulationSim
    ('geographic_entities', 'geo_id'),
    ('population_profiles', 'profile_id'),
    ('health_indicators', 'indicator_id'),
    ('sdoh_indices', 'sdoh_id'),
    ('cohort_specifications', 'cohort_id'),
    # NetworkSim
    ('networks', 'network_id'),
    ('network_providers', 'network_provider_id'),
    ('network_facilities', 'network_facility_id'),
    ('provider_specialties', 'specialty_id'),
]


def _validate_query(query: str) -> bool:
    """
    Validate that a query is SELECT-only.
    
    Args:
        query: SQL query string
        
    Returns:
        True if query is safe
        
    Raises:
        ValueError: If query contains disallowed patterns
    """
    query_upper = query.upper().strip()
    
    # Must start with SELECT or WITH (for CTEs)
    if not (query_upper.startswith('SELECT') or query_upper.startswith('WITH')):
        raise ValueError("Query must be a SELECT statement")
    
    # Check for disallowed patterns
    for pattern in DISALLOWED_SQL_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValueError(f"Query contains disallowed pattern: {pattern}")
    
    return True


def _ensure_unique_name(name: str, connection) -> str:
    """Ensure cohort name is unique by adding suffix if needed."""
    base_name = name
    counter = 1
    
    while True:
        result = connection.execute("""
            SELECT COUNT(*) FROM cohorts WHERE name = ?
        """, [name])
        
        if result.rows and result.rows[0][0] == 0:
            return name
        
        counter += 1
        name = f"{base_name}-{counter}"


class AutoPersistService:
    """
    Service for auto-persisting generated entities.
    
    Implements the core Structured RAG pattern:
    1. Persist entities to DuckDB immediately after generation
    2. Return summary (not full data) to context
    3. Provide paginated queries for data retrieval
    
    Also provides:
    - Tag management for cohort organization
    - Scenario cloning for creating variations
    - Export utilities for data portability
    
    Usage:
        service = AutoPersistService(connection)
        
        # Persist entities
        result = service.persist_entities(
            entities=[...],
            entity_type='patient',
            context_keywords=['diabetes', 'elderly']
        )
        
        # Query data
        query_result = service.query_cohort(
            cohort_id=result.cohort_id,
            query="SELECT * FROM patients WHERE gender = 'F'"
        )
        
        # Tag management
        service.add_tag(cohort_id, 'training')
    """
    
    def __init__(self, connection=None):
        """
        Initialize the service.
        
        Args:
            connection: Database connection (lazy loaded if not provided)
        """
        self._conn = connection
    
    @property
    def conn(self):
        """Get database connection."""
        if self._conn is None:
            from healthsim_agent.database import DatabaseConnection
            self._conn = DatabaseConnection("data/healthsim-reference.duckdb")
        return self._conn
    
    # ========================================================================
    # Core Scenario Management
    # ========================================================================
    
    def _create_cohort(
        self,
        name: str,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """
        Create a new cohort.
        
        Args:
            name: Scenario name
            description: Optional description
            tags: Optional list of tags
            
        Returns:
            New cohort ID
        """
        cohort_id = str(uuid4())
        now = datetime.utcnow()
        
        self.conn.execute("""
            INSERT INTO cohorts (id, name, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, [cohort_id, name, description, now, now])
        
        # Add tags
        if tags:
            for tag in tags:
                self.conn.execute("""
                    INSERT INTO cohort_tags (cohort_id, tag)
                    VALUES (?, ?)
                """, [cohort_id, tag.lower()])
        
        return cohort_id
    
    def _update_cohort_timestamp(self, cohort_id: str):
        """Update cohort's updated_at timestamp."""
        self.conn.execute("""
            UPDATE cohorts SET updated_at = ? WHERE id = ?
        """, [datetime.utcnow(), cohort_id])
    
    def _get_cohort_info(self, cohort_id: str) -> dict[str, Any] | None:
        """Get cohort metadata."""
        result = self.conn.execute("""
            SELECT id, name, description, created_at, updated_at
            FROM cohorts WHERE id = ?
        """, [cohort_id])
        
        if not result.rows:
            return None
        
        row = result.rows[0]
        return {
            'cohort_id': row[0],
            'name': row[1],
            'description': row[2],
            'created_at': row[3],
            'updated_at': row[4],
        }
    
    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        try:
            result = self.conn.execute("""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_name = ?
            """, [table_name])
            return result.rows[0][0] > 0 if result.rows else False
        except Exception:
            return False
    
    def persist_entities(
        self,
        entities: list[dict],
        entity_type: str,
        cohort_id: str | None = None,
        cohort_name: str | None = None,
        cohort_description: str | None = None,
        context_keywords: list[str] | None = None,
        tags: list[str] | None = None,
        batch_number: int | None = None,
        total_batches: int | None = None,
    ) -> PersistResult:
        """
        Persist entities to DuckDB and return summary.
        
        If no cohort_id provided:
        - Creates new cohort with auto-generated name
        - Uses context_keywords for naming if available
        
        Args:
            entities: List of entity dictionaries to persist
            entity_type: Type of entities (patient, claim, etc.)
            cohort_id: Existing cohort ID to add to (optional)
            cohort_name: Name for new cohort (optional, auto-generated if not provided)
            cohort_description: Description for cohort (optional)
            context_keywords: Keywords from generation context for auto-naming
            tags: Tags for the cohort
            batch_number: Current batch number (for progress tracking)
            total_batches: Total number of batches (for progress tracking)
            
        Returns:
            PersistResult with summary (NOT full entity data)
        """
        if not entities:
            raise ValueError("No entities to persist")
        
        # Normalize entity type
        entity_type = entity_type.lower().rstrip('s') + 's'  # Ensure plural
        
        # Get table info
        table_info = get_table_info(entity_type)
        if not table_info:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        table_name, id_column = table_info
        
        # Get serializer
        serializer = get_serializer(entity_type)
        
        # Create or use existing cohort
        is_new_cohort = False
        if not cohort_id:
            is_new_cohort = True
            
            # Generate name if not provided
            if not cohort_name:
                cohort_name = generate_cohort_name(
                    keywords=context_keywords,
                    entity_type=entity_type,
                )
            else:
                cohort_name = _ensure_unique_name(
                    sanitize_name(cohort_name),
                    self.conn,
                )
            
            cohort_id = self._create_cohort(
                name=cohort_name,
                description=cohort_description,
                tags=tags,
            )
        else:
            # Get existing cohort name
            result = self.conn.execute("""
                SELECT name FROM cohorts WHERE id = ?
            """, [cohort_id])
            
            if not result.rows:
                raise ValueError(f"Cohort not found: {cohort_id}")
            
            cohort_name = result.rows[0][0]
        
        # Persist entities
        entity_ids = []
        
        for entity in entities:
            # Serialize entity
            if serializer:
                serialized = serializer(entity)
            else:
                serialized = entity.copy()
            
            # Add cohort_id (database column)
            serialized['cohort_id'] = cohort_id
            
            # Get or generate entity ID
            entity_id = serialized.get(id_column) or str(uuid4())
            serialized[id_column] = entity_id
            entity_ids.append(entity_id)
            
            # Build insert statement
            columns = list(serialized.keys())
            placeholders = ', '.join(['?' for _ in columns])
            column_str = ', '.join(columns)
            
            try:
                self.conn.execute(f"""
                    INSERT INTO {table_name} ({column_str})
                    VALUES ({placeholders})
                """, list(serialized.values()))
            except Exception as e:
                # Handle duplicate key by updating
                if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
                    set_clause = ', '.join([f"{col} = ?" for col in columns if col != id_column])
                    values = [v for k, v in serialized.items() if k != id_column]
                    values.append(entity_id)
                    
                    self.conn.execute(f"""
                        UPDATE {table_name}
                        SET {set_clause}
                        WHERE {id_column} = ?
                    """, values)
                else:
                    raise
        
        # Update cohort timestamp
        self._update_cohort_timestamp(cohort_id)
        
        # Generate summary
        try:
            summary = generate_summary(
                cohort_id=cohort_id,
                include_samples=True,
                samples_per_type=3,
                connection=self.conn,
            )
        except Exception:
            summary = None
        
        return PersistResult(
            cohort_id=cohort_id,
            cohort_name=cohort_name,
            entity_type=entity_type,
            entities_persisted=len(entities),
            entity_ids=entity_ids,
            summary=summary,
            is_new_cohort=is_new_cohort,
            batch_number=batch_number,
            total_batches=total_batches,
        )
    
    def get_cohort_summary(
        self,
        cohort_id: str | None = None,
        cohort_name: str | None = None,
        include_samples: bool = True,
        samples_per_type: int = 3,
    ) -> CohortSummary:
        """
        Get cohort summary for loading into context.
        
        IMPORTANT: Never loads full entity data!
        Returns summary (~500 tokens) + samples (~3000 tokens)
        
        Args:
            cohort_id: Scenario UUID (optional if name provided)
            cohort_name: Scenario name for fuzzy lookup (optional if ID provided)
            include_samples: Whether to include sample entities
            samples_per_type: Number of samples per entity type
            
        Returns:
            CohortSummary with counts, statistics, and samples
        """
        # Resolve cohort ID
        if not cohort_id:
            if not cohort_name:
                raise ValueError("Either cohort_id or cohort_name required")
            
            cohort_id = get_cohort_by_name(cohort_name, self.conn)
            if not cohort_id:
                raise ValueError(f"Cohort not found: {cohort_name}")
        
        return generate_summary(
            cohort_id=cohort_id,
            include_samples=include_samples,
            samples_per_type=samples_per_type,
            connection=self.conn,
        )
    
    def query_cohort(
        self,
        cohort_id: str,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> QueryResult:
        """
        Execute paginated query against cohort data.
        
        Args:
            cohort_id: Scenario to query
            query: SQL SELECT query
            limit: Results per page (default 20, max 100)
            offset: Starting offset
            
        Returns:
            QueryResult with paginated results
            
        Raises:
            ValueError: If query is not SELECT-only
        """
        # Validate query
        _validate_query(query)
        
        # Enforce limits
        limit = min(limit, 100)
        
        # Modify query to add pagination and cohort filter
        query_lower = query.lower().strip()
        
        # Add cohort_id filter if not already present
        if 'cohort_id' not in query_lower:
            if ' where ' in query_lower:
                where_idx = query_lower.index(' where ') + 7
                query = query[:where_idx] + f"cohort_id = '{cohort_id}' AND " + query[where_idx:]
            else:
                from_match = re.search(r'\bFROM\s+(\w+)', query, re.IGNORECASE)
                if from_match:
                    table_end = from_match.end()
                    query = query[:table_end] + f" WHERE cohort_id = '{cohort_id}'" + query[table_end:]
        
        # Remove any existing LIMIT/OFFSET
        query = re.sub(r'\bLIMIT\s+\d+', '', query, flags=re.IGNORECASE)
        query = re.sub(r'\bOFFSET\s+\d+', '', query, flags=re.IGNORECASE)
        
        # Get total count first
        count_query = f"SELECT COUNT(*) FROM ({query}) AS subquery"
        try:
            result = self.conn.execute(count_query)
            total_count = result.rows[0][0] if result.rows else 0
        except Exception:
            total_count = 0
        
        # Add pagination
        paginated_query = f"{query} LIMIT {limit} OFFSET {offset}"
        
        # Execute query
        try:
            result = self.conn.execute(paginated_query)
            columns = result.columns
            
            results = []
            for row in result.rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[col] = value
                results.append(row_dict)
        except Exception as e:
            raise ValueError(f"Query error: {str(e)}")
        
        page = offset // limit if limit > 0 else 0
        has_more = (offset + len(results)) < total_count
        
        return QueryResult(
            results=results,
            total_count=total_count,
            page=page,
            page_size=limit,
            has_more=has_more,
            query_executed=paginated_query,
        )
    
    def list_cohorts(
        self,
        filter_pattern: str | None = None,
        tag: str | None = None,
        limit: int = 20,
        sort_by: str = "updated_at",
    ) -> list[CohortBrief]:
        """
        List available cohorts with brief stats.
        
        Args:
            filter_pattern: Filter by name pattern (case-insensitive)
            tag: Filter by tag
            limit: Maximum results
            sort_by: Sort field (updated_at, created_at, name)
            
        Returns:
            List of CohortBrief objects
        """
        query = """
            SELECT 
                s.id,
                s.name,
                s.description,
                s.created_at,
                s.updated_at
            FROM cohorts s
        """
        
        params = []
        conditions = []
        
        if filter_pattern:
            conditions.append("LOWER(s.name) LIKE LOWER(?)")
            params.append(f"%{filter_pattern}%")
        
        if tag:
            query += " JOIN cohort_tags t ON s.id = t.cohort_id"
            conditions.append("LOWER(t.tag) = LOWER(?)")
            params.append(tag)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Sort
        sort_map = {
            'updated_at': 's.updated_at DESC',
            'created_at': 's.created_at DESC',
            'name': 's.name ASC',
        }
        query += f" ORDER BY {sort_map.get(sort_by, 's.updated_at DESC')}"
        query += f" LIMIT {limit}"
        
        result = self.conn.execute(query, params)
        
        cohorts = []
        for row in result.rows:
            cohort_id = str(row[0])
            
            # Get entity count
            count = 0
            for table in ['patients', 'members', 'subjects', 'claims', 'prescriptions']:
                try:
                    cnt_result = self.conn.execute(f"""
                        SELECT COUNT(*) FROM {table} WHERE cohort_id = ?
                    """, [cohort_id])
                    count += cnt_result.rows[0][0] if cnt_result.rows else 0
                except Exception:
                    pass
            
            # Get tags
            tags_result = self.conn.execute("""
                SELECT tag FROM cohort_tags WHERE cohort_id = ?
            """, [cohort_id])
            tags = [t[0] for t in tags_result.rows] if tags_result.rows else []
            
            cohorts.append(CohortBrief(
                cohort_id=cohort_id,
                name=row[1],
                description=row[2],
                entity_count=count,
                created_at=row[3],
                updated_at=row[4],
                tags=tags,
            ))
        
        return cohorts
    
    def rename_cohort(self, cohort_id: str, new_name: str) -> tuple[str, str]:
        """
        Rename a cohort.
        
        Args:
            cohort_id: Cohort to rename
            new_name: New name for the cohort
            
        Returns:
            Tuple of (old_name, new_name)
        """
        result = self.conn.execute("""
            SELECT name FROM cohorts WHERE id = ?
        """, [cohort_id])
        
        if not result.rows:
            raise ValueError(f"Cohort not found: {cohort_id}")
        
        old_name = result.rows[0][0]
        new_name = _ensure_unique_name(sanitize_name(new_name), self.conn)
        
        self.conn.execute("""
            UPDATE cohorts SET name = ?, updated_at = ?
            WHERE id = ?
        """, [new_name, datetime.utcnow(), cohort_id])
        
        return (old_name, new_name)
    
    def delete_cohort(self, cohort_id: str, confirm: bool = False) -> dict[str, Any]:
        """
        Delete cohort and all linked entities.
        
        Args:
            cohort_id: Scenario to delete
            confirm: Must be True to proceed with deletion
            
        Returns:
            Dict with deleted cohort info
        """
        if not confirm:
            raise ValueError("Deletion requires confirm=True")
        
        result = self.conn.execute("""
            SELECT name, description FROM cohorts WHERE id = ?
        """, [cohort_id])
        
        if not result.rows:
            raise ValueError(f"Cohort not found: {cohort_id}")
        
        name = result.rows[0][0]
        description = result.rows[0][1]
        
        # Count entities before deletion
        entity_count = 0
        for table_name, _ in CANONICAL_TABLES:
            if self._table_exists(table_name):
                try:
                    cnt = self.conn.execute(f"""
                        SELECT COUNT(*) FROM {table_name} WHERE cohort_id = ?
                    """, [cohort_id])
                    entity_count += cnt.rows[0][0] if cnt.rows else 0
                except Exception:
                    pass
        
        # Delete entities from all tables
        for table_name, _ in CANONICAL_TABLES:
            if self._table_exists(table_name):
                try:
                    self.conn.execute(f"""
                        DELETE FROM {table_name} WHERE cohort_id = ?
                    """, [cohort_id])
                except Exception:
                    pass
        
        # Delete tags
        self.conn.execute("""
            DELETE FROM cohort_tags WHERE cohort_id = ?
        """, [cohort_id])
        
        # Delete cohort
        self.conn.execute("""
            DELETE FROM cohorts WHERE id = ?
        """, [cohort_id])
        
        return {
            'cohort_id': cohort_id,
            'name': name,
            'description': description,
            'entity_count': entity_count,
        }
    
    # ========================================================================
    # Tag Management
    # ========================================================================
    
    def add_tag(self, cohort_id: str, tag: str) -> list[str]:
        """Add a tag to a cohort."""
        if not self._get_cohort_info(cohort_id):
            raise ValueError(f"Cohort not found: {cohort_id}")
        
        tag = tag.lower().strip()
        if not tag:
            raise ValueError("Tag cannot be empty")
        
        # Check if tag already exists
        existing = self.conn.execute("""
            SELECT COUNT(*) FROM cohort_tags
            WHERE cohort_id = ? AND tag = ?
        """, [cohort_id, tag])
        
        if existing.rows[0][0] == 0:
            self.conn.execute("""
                INSERT INTO cohort_tags (cohort_id, tag)
                VALUES (?, ?)
            """, [cohort_id, tag])
            self._update_cohort_timestamp(cohort_id)
        
        return self.get_tags(cohort_id)
    
    def remove_tag(self, cohort_id: str, tag: str) -> list[str]:
        """Remove a tag from a cohort."""
        if not self._get_cohort_info(cohort_id):
            raise ValueError(f"Cohort not found: {cohort_id}")
        
        tag = tag.lower().strip()
        
        self.conn.execute("""
            DELETE FROM cohort_tags
            WHERE cohort_id = ? AND tag = ?
        """, [cohort_id, tag])
        
        self._update_cohort_timestamp(cohort_id)
        return self.get_tags(cohort_id)
    
    def get_tags(self, cohort_id: str) -> list[str]:
        """Get all tags for a cohort."""
        result = self.conn.execute("""
            SELECT tag FROM cohort_tags
            WHERE cohort_id = ?
            ORDER BY tag
        """, [cohort_id])
        
        return [row[0] for row in result.rows] if result.rows else []
    
    def list_all_tags(self) -> list[dict[str, Any]]:
        """List all tags in use with counts."""
        result = self.conn.execute("""
            SELECT tag, COUNT(*) as count
            FROM cohort_tags
            GROUP BY tag
            ORDER BY count DESC, tag ASC
        """)
        
        return [{'tag': row[0], 'count': row[1]} for row in result.rows] if result.rows else []
    
    # ========================================================================
    # Entity Samples
    # ========================================================================
    
    def get_entity_samples(
        self,
        cohort_id: str,
        entity_type: str,
        count: int = 3,
        strategy: str = "diverse",
    ) -> list[dict]:
        """
        Get sample entities for pattern consistency.
        
        Args:
            cohort_id: Scenario to get samples from
            entity_type: Type of entities to sample
            count: Number of samples (default 3)
            strategy: Sampling strategy ("diverse", "random", "recent")
                
        Returns:
            List of sample entity dictionaries
        """
        # Normalize entity type
        entity_type = entity_type.lower()
        if not entity_type.endswith('s'):
            entity_type = entity_type + 's'
        
        table_info = get_table_info(entity_type)
        if not table_info:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        table_name, id_column = table_info
        
        # Build query based on strategy
        if strategy == "random":
            order_clause = "ORDER BY RANDOM()"
        elif strategy == "recent":
            order_clause = "ORDER BY created_at DESC"
        else:
            order_clause = "ORDER BY created_at"
        
        try:
            result = self.conn.execute(f"""
                SELECT * FROM {table_name}
                WHERE cohort_id = ?
                {order_clause}
            """, [cohort_id])
            
            if not result.rows:
                return []
            
            columns = result.columns
            
            # For diverse sampling, take evenly spaced samples
            if strategy == "diverse" and len(result.rows) > count:
                step = len(result.rows) / count
                indices = [int(i * step) for i in range(count)]
                selected = [result.rows[i] for i in indices]
            else:
                selected = result.rows[:count]
            
            # Convert to dicts
            samples = []
            for row in selected:
                sample = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    # Skip internal columns
                    if col not in ('cohort_id', 'generation_seed'):
                        sample[col] = value
                samples.append(sample)
            
            return samples
            
        except Exception as e:
            raise ValueError(f"Error fetching samples: {str(e)}")


# Module-level convenience function
_default_service: AutoPersistService | None = None


def get_auto_persist_service(connection=None) -> AutoPersistService:
    """Get or create the default auto-persist service."""
    global _default_service
    
    if connection is not None:
        return AutoPersistService(connection)
    
    if _default_service is None:
        _default_service = AutoPersistService()
    
    return _default_service
