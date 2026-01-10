"""Journey persistence for HealthSim Agent.

Provides save/load/list/delete operations for journey definitions,
enabling reusable cross-product data generation workflows.

Journeys define multi-step entity generation across products, such as:
- Creating a patient, then generating claims for that patient
- Creating trial subjects with associated pharmacy records
- Building complete member profiles with encounters and prescriptions

Ported from: healthsim-workspace/packages/core/src/healthsim/state/journey_manager.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4
import json


@dataclass
class JourneyStep:
    """A single step in a journey."""
    id: str
    name: str
    product: str
    profile_ref: str | None  # Reference to saved profile
    profile_spec: dict[str, Any] | None  # Inline profile spec
    depends_on: list[str] = field(default_factory=list)  # Step IDs this depends on
    entity_mapping: dict[str, str] | None = None  # Map entities from previous steps
    count_expression: str | None = None  # Expression for count (e.g., "parent.count * 3")
    condition: str | None = None  # Condition for execution
    metadata: dict[str, Any] | None = None


@dataclass
class JourneyRecord:
    """A saved journey definition."""
    id: str
    name: str
    description: str | None
    version: int
    steps: list[JourneyStep]
    products: list[str]  # Products involved in this journey
    tags: list[str]
    created_at: datetime
    updated_at: datetime
    is_builtin: bool = False
    metadata: dict[str, Any] | None = None


@dataclass
class JourneyExecutionRecord:
    """Record of a journey execution."""
    id: int
    journey_id: str
    cohort_id: str | None
    executed_at: datetime
    seed: int | None
    total_entities: int
    duration_ms: int
    status: str
    steps_completed: int
    steps_total: int
    error_message: str | None = None
    step_results: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class JourneySummary:
    """Summary of a journey for listing."""
    id: str
    name: str
    description: str | None
    version: int
    products: list[str]
    tags: list[str]
    steps_count: int
    created_at: datetime
    is_builtin: bool
    execution_count: int = 0
    last_executed: datetime | None = None


class JourneyManager:
    """Manages journey persistence in DuckDB.
    
    Journeys are multi-step workflows that generate related entities
    across products. They define the order and dependencies between
    generation steps.
    
    Usage:
        manager = JourneyManager(connection)
        
        # Save a journey
        journey_id = manager.save_journey(
            name='diabetic-member-journey',
            steps=[
                JourneyStep(
                    id='create-patient',
                    name='Create Patient',
                    product='patientsim',
                    profile_ref='harris-diabetic'
                ),
                JourneyStep(
                    id='create-claims',
                    name='Generate Claims',
                    product='membersim',
                    profile_spec={...},
                    depends_on=['create-patient'],
                    entity_mapping={'member_id': 'patient.id'}
                )
            ],
            description='Complete diabetic member with claims',
            tags=['diabetes', 'member-journey']
        )
        
        # Load and execute
        journey = manager.load_journey('diabetic-member-journey')
        
        # List journeys
        journeys = manager.list_journeys(products=['patientsim', 'membersim'])
    """
    
    def __init__(self, connection=None):
        """Initialize journey manager.
        
        Args:
            connection: Database connection (lazy loaded if not provided)
        """
        self._conn = connection
        self._tables_ensured = False
    
    @property
    def conn(self):
        """Get database connection."""
        if self._conn is None:
            from healthsim_agent.database import DatabaseConnection
            self._conn = DatabaseConnection("data/healthsim-reference.duckdb")
        return self._conn
    
    def _ensure_tables(self) -> None:
        """Ensure journey tables exist."""
        if self._tables_ensured:
            return
        
        # Check if journeys table exists
        result = self.conn.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'journeys'
        """)
        
        if result.rows and result.rows[0][0] == 0:
            # Create sequence and tables
            self.conn.execute("""
                CREATE SEQUENCE IF NOT EXISTS journeys_seq START 1
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS journeys (
                    id              VARCHAR PRIMARY KEY,
                    name            VARCHAR NOT NULL UNIQUE,
                    description     VARCHAR,
                    version         INTEGER DEFAULT 1,
                    steps           JSON NOT NULL,
                    products        JSON NOT NULL,
                    tags            JSON,
                    is_builtin      BOOLEAN DEFAULT FALSE,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata        JSON
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS journey_executions (
                    id              INTEGER PRIMARY KEY DEFAULT nextval('journeys_seq'),
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
        
        self._tables_ensured = True
    
    def _step_to_dict(self, step: JourneyStep) -> dict[str, Any]:
        """Convert JourneyStep to dictionary for storage."""
        return {
            "id": step.id,
            "name": step.name,
            "product": step.product,
            "profile_ref": step.profile_ref,
            "profile_spec": step.profile_spec,
            "depends_on": step.depends_on,
            "entity_mapping": step.entity_mapping,
            "count_expression": step.count_expression,
            "condition": step.condition,
            "metadata": step.metadata
        }
    
    def _dict_to_step(self, d: dict[str, Any]) -> JourneyStep:
        """Convert dictionary to JourneyStep."""
        return JourneyStep(
            id=d["id"],
            name=d["name"],
            product=d["product"],
            profile_ref=d.get("profile_ref"),
            profile_spec=d.get("profile_spec"),
            depends_on=d.get("depends_on", []),
            entity_mapping=d.get("entity_mapping"),
            count_expression=d.get("count_expression"),
            condition=d.get("condition"),
            metadata=d.get("metadata")
        )
    
    # =========================================================================
    # Journey CRUD Operations
    # =========================================================================
    
    def save_journey(
        self,
        name: str,
        steps: list[JourneyStep],
        description: str | None = None,
        tags: list[str] | None = None,
        is_builtin: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Save a new journey definition.
        
        Args:
            name: Unique journey name
            steps: List of JourneyStep definitions
            description: Human-readable description
            tags: List of tags for filtering
            is_builtin: Whether this is a built-in journey
            metadata: Additional metadata
            
        Returns:
            Journey ID
            
        Raises:
            ValueError: If journey with name already exists
        """
        self._ensure_tables()
        
        journey_id = f"journey-{uuid4().hex[:8]}"
        
        # Check for existing journey with same name
        existing = self.conn.execute(
            "SELECT id FROM journeys WHERE name = ?",
            [name]
        )
        
        if existing.rows:
            raise ValueError(f"Journey with name '{name}' already exists. Use update_journey() or delete first.")
        
        # Extract unique products from steps
        products = list(set(step.product for step in steps))
        
        # Convert steps to JSON
        steps_json = [self._step_to_dict(step) for step in steps]
        
        self.conn.execute("""
            INSERT INTO journeys (id, name, description, version, steps, products, tags, is_builtin, metadata)
            VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?)
        """, [
            journey_id,
            name,
            description,
            json.dumps(steps_json),
            json.dumps(products),
            json.dumps(tags or []),
            is_builtin,
            json.dumps(metadata) if metadata else None
        ])
        
        return journey_id
    
    def load_journey(self, name_or_id: str) -> JourneyRecord:
        """Load a journey by name or ID.
        
        Args:
            name_or_id: Journey name or ID
            
        Returns:
            JourneyRecord with full definition
            
        Raises:
            ValueError: If journey not found
        """
        self._ensure_tables()
        
        result = self.conn.execute("""
            SELECT id, name, description, version, steps, products, tags, 
                   is_builtin, created_at, updated_at, metadata
            FROM journeys
            WHERE name = ? OR id = ?
        """, [name_or_id, name_or_id])
        
        if not result.rows:
            raise ValueError(f"Journey not found: {name_or_id}")
        
        row = result.rows[0]
        steps_data = json.loads(row[4]) if isinstance(row[4], str) else row[4]
        
        return JourneyRecord(
            id=row[0],
            name=row[1],
            description=row[2],
            version=row[3],
            steps=[self._dict_to_step(s) for s in steps_data],
            products=json.loads(row[5]) if isinstance(row[5], str) else row[5],
            tags=json.loads(row[6]) if isinstance(row[6], str) else (row[6] or []),
            is_builtin=row[7],
            created_at=row[8],
            updated_at=row[9],
            metadata=json.loads(row[10]) if row[10] and isinstance(row[10], str) else row[10]
        )
    
    def update_journey(
        self,
        name_or_id: str,
        steps: list[JourneyStep] | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        bump_version: bool = True,
    ) -> JourneyRecord:
        """Update an existing journey.
        
        Args:
            name_or_id: Journey name or ID
            steps: New step definitions (optional)
            description: New description (optional)
            tags: New tags (optional)
            metadata: New metadata (optional)
            bump_version: Whether to increment version number
            
        Returns:
            Updated JourneyRecord
            
        Raises:
            ValueError: If journey not found
        """
        existing = self.load_journey(name_or_id)
        
        new_version = existing.version + 1 if bump_version else existing.version
        new_steps = steps if steps is not None else existing.steps
        new_desc = description if description is not None else existing.description
        new_tags = tags if tags is not None else existing.tags
        new_metadata = metadata if metadata is not None else existing.metadata
        
        # Extract products from steps
        products = list(set(step.product for step in new_steps))
        steps_json = [self._step_to_dict(step) for step in new_steps]
        
        self.conn.execute("""
            UPDATE journeys
            SET steps = ?,
                products = ?,
                description = ?,
                version = ?,
                tags = ?,
                metadata = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, [
            json.dumps(steps_json),
            json.dumps(products),
            new_desc,
            new_version,
            json.dumps(new_tags),
            json.dumps(new_metadata) if new_metadata else None,
            existing.id
        ])
        
        return self.load_journey(existing.id)
    
    def delete_journey(self, name_or_id: str, delete_executions: bool = True) -> bool:
        """Delete a journey.
        
        Args:
            name_or_id: Journey name or ID
            delete_executions: Whether to delete execution history
            
        Returns:
            True if deleted, False if not found
        """
        self._ensure_tables()
        
        result = self.conn.execute("""
            SELECT id FROM journeys WHERE name = ? OR id = ?
        """, [name_or_id, name_or_id])
        
        if not result.rows:
            return False
        
        journey_id = result.rows[0][0]
        
        if delete_executions:
            self.conn.execute(
                "DELETE FROM journey_executions WHERE journey_id = ?",
                [journey_id]
            )
        
        self.conn.execute("DELETE FROM journeys WHERE id = ?", [journey_id])
        return True
    
    def list_journeys(
        self,
        products: list[str] | None = None,
        tags: list[str] | None = None,
        search: str | None = None,
        include_builtin: bool = True,
        limit: int = 50,
    ) -> list[JourneySummary]:
        """List journeys with optional filtering.
        
        Args:
            products: Filter by products (any match)
            tags: Filter by tags (any match)
            search: Search in name and description
            include_builtin: Whether to include built-in journeys
            limit: Maximum results
            
        Returns:
            List of JourneySummary objects
        """
        self._ensure_tables()
        
        query = """
            SELECT j.id, j.name, j.description, j.version, j.products, j.tags, 
                   j.steps, j.is_builtin, j.created_at,
                   COUNT(e.id) as exec_count,
                   MAX(e.executed_at) as last_exec
            FROM journeys j
            LEFT JOIN journey_executions e ON j.id = e.journey_id
            WHERE 1=1
        """
        params = []
        
        if not include_builtin:
            query += " AND j.is_builtin = FALSE"
        
        if search:
            query += " AND (j.name ILIKE ? OR j.description ILIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        
        query += " GROUP BY j.id, j.name, j.description, j.version, j.products, j.tags, j.steps, j.is_builtin, j.created_at, j.updated_at"
        query += " ORDER BY j.updated_at DESC"
        query += f" LIMIT {limit}"
        
        result = self.conn.execute(query, params)
        
        summaries = []
        for row in result.rows:
            journey_products = json.loads(row[4]) if isinstance(row[4], str) else row[4]
            journey_tags = json.loads(row[5]) if isinstance(row[5], str) else (row[5] or [])
            steps_data = json.loads(row[6]) if isinstance(row[6], str) else row[6]
            
            # Filter by products if requested
            if products:
                if not any(p in journey_products for p in products):
                    continue
            
            # Filter by tags if requested
            if tags:
                if not any(t in journey_tags for t in tags):
                    continue
            
            summaries.append(JourneySummary(
                id=row[0],
                name=row[1],
                description=row[2],
                version=row[3],
                products=journey_products,
                tags=journey_tags,
                steps_count=len(steps_data),
                is_builtin=row[7],
                created_at=row[8],
                execution_count=row[9] or 0,
                last_executed=row[10]
            ))
        
        return summaries
    
    def journey_exists(self, name_or_id: str) -> bool:
        """Check if a journey exists.
        
        Args:
            name_or_id: Journey name or ID
            
        Returns:
            True if journey exists
        """
        self._ensure_tables()
        
        result = self.conn.execute("""
            SELECT COUNT(*) FROM journeys WHERE name = ? OR id = ?
        """, [name_or_id, name_or_id])
        return result.rows[0][0] > 0 if result.rows else False
    
    # =========================================================================
    # Execution History
    # =========================================================================
    
    def record_execution(
        self,
        journey_id: str,
        cohort_id: str | None = None,
        seed: int | None = None,
        total_entities: int = 0,
        duration_ms: int = 0,
        status: str = "completed",
        steps_completed: int = 0,
        steps_total: int = 0,
        error_message: str | None = None,
        step_results: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Record a journey execution.
        
        Args:
            journey_id: Journey that was executed
            cohort_id: Cohort that was created (if any)
            seed: Random seed used
            total_entities: Total entities generated across all steps
            duration_ms: Execution time in milliseconds
            status: 'completed', 'failed', or 'partial'
            steps_completed: Number of steps completed
            steps_total: Total number of steps
            error_message: Error details if failed
            step_results: Per-step execution results
            metadata: Additional execution metadata
            
        Returns:
            Execution ID
        """
        self._ensure_tables()
        
        result = self.conn.execute("""
            INSERT INTO journey_executions 
            (journey_id, cohort_id, seed, total_entities, duration_ms, status, 
             steps_completed, steps_total, error_message, step_results, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """, [
            journey_id,
            cohort_id,
            seed,
            total_entities,
            duration_ms,
            status,
            steps_completed,
            steps_total,
            error_message,
            json.dumps(step_results) if step_results else None,
            json.dumps(metadata) if metadata else None
        ])
        
        return result.rows[0][0] if result.rows else 0
    
    def get_executions(
        self,
        journey_id: str,
        limit: int = 20,
    ) -> list[JourneyExecutionRecord]:
        """Get execution history for a journey.
        
        Args:
            journey_id: Journey ID or name
            limit: Maximum executions to return
            
        Returns:
            List of JourneyExecutionRecords, newest first
        """
        journey = self.load_journey(journey_id)
        
        result = self.conn.execute("""
            SELECT id, journey_id, cohort_id, executed_at, seed, total_entities,
                   duration_ms, status, steps_completed, steps_total, 
                   error_message, step_results, metadata
            FROM journey_executions
            WHERE journey_id = ?
            ORDER BY executed_at DESC
            LIMIT ?
        """, [journey.id, limit])
        
        return [
            JourneyExecutionRecord(
                id=row[0],
                journey_id=row[1],
                cohort_id=row[2],
                executed_at=row[3],
                seed=row[4],
                total_entities=row[5],
                duration_ms=row[6],
                status=row[7],
                steps_completed=row[8],
                steps_total=row[9],
                error_message=row[10],
                step_results=json.loads(row[11]) if row[11] and isinstance(row[11], str) else row[11],
                metadata=json.loads(row[12]) if row[12] and isinstance(row[12], str) else row[12]
            )
            for row in result.rows
        ]
    
    def get_entity_journeys(self, entity_id: str) -> list[JourneyRecord]:
        """Get journeys that have generated a specific entity.
        
        Args:
            entity_id: Entity ID to search for
            
        Returns:
            List of JourneyRecords
        """
        self._ensure_tables()
        
        # Search step_results for entity_id
        result = self.conn.execute("""
            SELECT DISTINCT j.id
            FROM journeys j
            JOIN journey_executions e ON j.id = e.journey_id
            WHERE e.step_results::VARCHAR LIKE ?
        """, [f"%{entity_id}%"])
        
        journeys = []
        for row in result.rows:
            try:
                journeys.append(self.load_journey(row[0]))
            except ValueError:
                pass
        
        return journeys
    
    # =========================================================================
    # Built-in Journeys
    # =========================================================================
    
    def import_builtin_journeys(self) -> int:
        """Import built-in journeys from auto_journeys and skill_journeys.
        
        Returns:
            Number of journeys imported
        """
        self._ensure_tables()
        
        builtin_journeys = self._get_builtin_journey_definitions()
        imported = 0
        
        for journey_def in builtin_journeys:
            if not self.journey_exists(journey_def["name"]):
                steps = [
                    JourneyStep(
                        id=s["id"],
                        name=s["name"],
                        product=s["product"],
                        profile_ref=s.get("profile_ref"),
                        profile_spec=s.get("profile_spec"),
                        depends_on=s.get("depends_on", []),
                        entity_mapping=s.get("entity_mapping"),
                        count_expression=s.get("count_expression"),
                        condition=s.get("condition")
                    )
                    for s in journey_def["steps"]
                ]
                
                self.save_journey(
                    name=journey_def["name"],
                    steps=steps,
                    description=journey_def.get("description"),
                    tags=journey_def.get("tags", []),
                    is_builtin=True
                )
                imported += 1
        
        return imported
    
    def _get_builtin_journey_definitions(self) -> list[dict[str, Any]]:
        """Get built-in journey definitions.
        
        Returns:
            List of journey definition dictionaries
        """
        return [
            {
                "name": "patient-to-member",
                "description": "Create a patient and generate associated member claims",
                "tags": ["cross-product", "patient", "member"],
                "steps": [
                    {
                        "id": "create-patient",
                        "name": "Create Patient",
                        "product": "patientsim",
                        "profile_spec": {
                            "profile": {
                                "product": "patientsim",
                                "generation": {"count": 1}
                            }
                        }
                    },
                    {
                        "id": "create-member",
                        "name": "Create Member Profile",
                        "product": "membersim",
                        "depends_on": ["create-patient"],
                        "entity_mapping": {"person_id": "patient.person_id"},
                        "profile_spec": {
                            "profile": {
                                "product": "membersim",
                                "generation": {"count": 1}
                            }
                        }
                    }
                ]
            },
            {
                "name": "member-with-pharmacy",
                "description": "Create member with pharmacy benefit claims",
                "tags": ["cross-product", "member", "pharmacy"],
                "steps": [
                    {
                        "id": "create-member",
                        "name": "Create Member",
                        "product": "membersim",
                        "profile_spec": {
                            "profile": {
                                "product": "membersim",
                                "generation": {"count": 1}
                            }
                        }
                    },
                    {
                        "id": "create-rx-claims",
                        "name": "Generate Pharmacy Claims",
                        "product": "rxmembersim",
                        "depends_on": ["create-member"],
                        "entity_mapping": {"member_id": "member.member_id"},
                        "count_expression": "random(3, 12)",
                        "profile_spec": {
                            "profile": {
                                "product": "rxmembersim"
                            }
                        }
                    }
                ]
            },
            {
                "name": "trial-subject-complete",
                "description": "Create trial subject with full clinical history",
                "tags": ["cross-product", "trial", "patient"],
                "steps": [
                    {
                        "id": "create-patient",
                        "name": "Create Base Patient",
                        "product": "patientsim",
                        "profile_spec": {
                            "profile": {
                                "product": "patientsim",
                                "generation": {"count": 1}
                            }
                        }
                    },
                    {
                        "id": "create-subject",
                        "name": "Enroll as Trial Subject",
                        "product": "trialsim",
                        "depends_on": ["create-patient"],
                        "entity_mapping": {"person_id": "patient.person_id"},
                        "profile_spec": {
                            "profile": {
                                "product": "trialsim",
                                "trial": {"phase": "phase3"}
                            }
                        }
                    }
                ]
            },
            {
                "name": "complete-healthcare-journey",
                "description": "Full patient journey across all products",
                "tags": ["cross-product", "complete", "demo"],
                "steps": [
                    {
                        "id": "create-patient",
                        "name": "Create Patient",
                        "product": "patientsim",
                        "profile_spec": {
                            "profile": {
                                "product": "patientsim",
                                "generation": {"count": 1}
                            }
                        }
                    },
                    {
                        "id": "create-member",
                        "name": "Create Member Profile",
                        "product": "membersim",
                        "depends_on": ["create-patient"],
                        "entity_mapping": {"person_id": "patient.person_id"}
                    },
                    {
                        "id": "create-pharmacy",
                        "name": "Add Pharmacy Benefits",
                        "product": "rxmembersim",
                        "depends_on": ["create-member"],
                        "entity_mapping": {"member_id": "member.member_id"}
                    },
                    {
                        "id": "enroll-trial",
                        "name": "Trial Enrollment",
                        "product": "trialsim",
                        "depends_on": ["create-patient"],
                        "entity_mapping": {"person_id": "patient.person_id"},
                        "condition": "patient.age >= 18"
                    }
                ]
            }
        ]


def get_journey_manager(connection=None) -> JourneyManager:
    """Get a JourneyManager instance.
    
    Args:
        connection: Optional database connection
        
    Returns:
        JourneyManager instance
    """
    return JourneyManager(connection)
