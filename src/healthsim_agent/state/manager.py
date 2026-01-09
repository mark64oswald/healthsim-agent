"""
HealthSim Agent - State Manager

Manages cohort persistence, entity tracking, and session state.

The StateManager provides:
- Cohort creation and management
- Entity registration (patients, claims, etc.)
- State serialization for export
- Query capabilities over generated data

Ported from: healthsim-workspace/packages/core/src/healthsim/state/manager.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4
import json


@dataclass
class EntityReference:
    """Reference to a generated entity."""
    entity_type: str
    entity_id: str
    cohort_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Cohort:
    """
    A cohort is a named collection of generated entities.
    
    Cohorts provide:
    - Organization for generated data
    - Export/import capabilities
    - Query scoping
    """
    id: str
    name: str
    description: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Entity storage by type
    entities: dict[str, list[dict]] = field(default_factory=dict)
    
    def add_entity(self, entity_type: str, entity: dict) -> None:
        """Add an entity to the cohort."""
        if entity_type not in self.entities:
            self.entities[entity_type] = []
        self.entities[entity_type].append(entity)
        self.updated_at = datetime.now()
    
    def get_entities(self, entity_type: str) -> list[dict]:
        """Get all entities of a type."""
        return self.entities.get(entity_type, [])
    
    def count_by_type(self) -> dict[str, int]:
        """Get entity counts by type."""
        return {k: len(v) for k, v in self.entities.items()}
    
    def total_entities(self) -> int:
        """Get total entity count."""
        return sum(len(v) for v in self.entities.values())
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize cohort to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata,
            "entities": self.entities,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Cohort":
        """Deserialize cohort from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            entities=data.get("entities", {}),
        )


@dataclass
class CohortSummary:
    """
    Token-efficient summary of a cohort.
    
    Used to provide context without loading full entity data.
    Typical token cost: ~500 tokens (vs 10K+ for full data)
    """
    id: str
    name: str
    description: str | None
    created_at: datetime
    entity_counts: dict[str, int]
    tags: list[str]
    sample_entities: dict[str, list[dict]] = field(default_factory=dict)
    
    def total_entities(self) -> int:
        """Get total entity count."""
        return sum(self.entity_counts.values())
    
    def token_estimate(self) -> int:
        """Estimate token usage for this summary."""
        base = 200  # Metadata
        per_type = 50 * len(self.entity_counts)
        samples = sum(len(json.dumps(s)) // 4 for s in self.sample_entities.values())
        return base + per_type + samples
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "entity_counts": self.entity_counts,
            "total_entities": self.total_entities(),
            "tags": self.tags,
            "sample_entities": self.sample_entities,
            "token_estimate": self.token_estimate(),
        }


class StateManager:
    """
    Manages cohort persistence and entity tracking.
    
    The StateManager is the central hub for:
    - Creating and managing cohorts
    - Tracking generated entities
    - Providing query capabilities
    - Exporting/importing state
    
    Usage:
        manager = StateManager()
        
        # Create a cohort
        cohort = manager.create_cohort(
            name='diabetes-study',
            description='Diabetic patients for testing'
        )
        
        # Add entities
        manager.add_entities(cohort.id, 'patients', patient_list)
        
        # Get summary (token-efficient)
        summary = manager.get_summary(cohort.id)
        
        # Export
        data = manager.export_cohort(cohort.id)
    """
    
    def __init__(self):
        """Initialize state manager."""
        self._cohorts: dict[str, Cohort] = {}
        self._active_cohort_id: str | None = None
    
    # =========================================================================
    # Cohort Management
    # =========================================================================
    
    def create_cohort(
        self,
        name: str,
        description: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Cohort:
        """
        Create a new cohort.
        
        Args:
            name: Unique cohort name
            description: Optional description
            tags: Optional tags for organization
            metadata: Optional metadata
            
        Returns:
            The created Cohort
            
        Raises:
            ValueError: If name already exists
        """
        # Check for duplicate name
        for cohort in self._cohorts.values():
            if cohort.name == name:
                raise ValueError(f"Cohort with name '{name}' already exists")
        
        cohort = Cohort(
            id=str(uuid4()),
            name=name,
            description=description,
            tags=tags or [],
            metadata=metadata or {},
        )
        
        self._cohorts[cohort.id] = cohort
        self._active_cohort_id = cohort.id
        
        return cohort
    
    def get_cohort(self, cohort_id: str) -> Cohort | None:
        """Get cohort by ID."""
        return self._cohorts.get(cohort_id)
    
    def get_cohort_by_name(self, name: str) -> Cohort | None:
        """Get cohort by name."""
        for cohort in self._cohorts.values():
            if cohort.name == name:
                return cohort
        return None
    
    def list_cohorts(self) -> list[Cohort]:
        """List all cohorts."""
        return list(self._cohorts.values())
    
    def delete_cohort(self, cohort_id: str) -> bool:
        """
        Delete a cohort.
        
        Args:
            cohort_id: Cohort ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        if cohort_id in self._cohorts:
            del self._cohorts[cohort_id]
            if self._active_cohort_id == cohort_id:
                self._active_cohort_id = None
            return True
        return False
    
    @property
    def active_cohort(self) -> Cohort | None:
        """Get the currently active cohort."""
        if self._active_cohort_id:
            return self._cohorts.get(self._active_cohort_id)
        return None
    
    def set_active_cohort(self, cohort_id: str) -> bool:
        """Set the active cohort."""
        if cohort_id in self._cohorts:
            self._active_cohort_id = cohort_id
            return True
        return False
    
    # =========================================================================
    # Entity Management
    # =========================================================================
    
    def add_entities(
        self,
        cohort_id: str,
        entity_type: str,
        entities: list[dict],
    ) -> int:
        """
        Add entities to a cohort.
        
        Args:
            cohort_id: Target cohort ID
            entity_type: Type of entities (patients, claims, etc.)
            entities: List of entity dictionaries
            
        Returns:
            Number of entities added
            
        Raises:
            ValueError: If cohort not found
        """
        cohort = self._cohorts.get(cohort_id)
        if not cohort:
            raise ValueError(f"Cohort not found: {cohort_id}")
        
        for entity in entities:
            cohort.add_entity(entity_type, entity)
        
        return len(entities)
    
    def add_entity(
        self,
        cohort_id: str,
        entity_type: str,
        entity: dict,
    ) -> None:
        """Add a single entity to a cohort."""
        self.add_entities(cohort_id, entity_type, [entity])
    
    def get_entities(
        self,
        cohort_id: str,
        entity_type: str,
    ) -> list[dict]:
        """Get all entities of a type from a cohort."""
        cohort = self._cohorts.get(cohort_id)
        if not cohort:
            return []
        return cohort.get_entities(entity_type)
    
    # =========================================================================
    # Summaries (Token-Efficient)
    # =========================================================================
    
    def get_summary(
        self,
        cohort_id: str,
        include_samples: bool = True,
        samples_per_type: int = 2,
    ) -> CohortSummary | None:
        """
        Get a token-efficient summary of a cohort.
        
        Args:
            cohort_id: Cohort ID
            include_samples: Whether to include sample entities
            samples_per_type: Number of samples per entity type
            
        Returns:
            CohortSummary or None if not found
        """
        cohort = self._cohorts.get(cohort_id)
        if not cohort:
            return None
        
        samples = {}
        if include_samples:
            for entity_type, entities in cohort.entities.items():
                samples[entity_type] = entities[:samples_per_type]
        
        return CohortSummary(
            id=cohort.id,
            name=cohort.name,
            description=cohort.description,
            created_at=cohort.created_at,
            entity_counts=cohort.count_by_type(),
            tags=cohort.tags,
            sample_entities=samples,
        )
    
    # =========================================================================
    # Export/Import
    # =========================================================================
    
    def export_cohort(self, cohort_id: str) -> dict[str, Any] | None:
        """
        Export a cohort to a dictionary.
        
        Args:
            cohort_id: Cohort ID to export
            
        Returns:
            Cohort dictionary or None if not found
        """
        cohort = self._cohorts.get(cohort_id)
        if not cohort:
            return None
        return cohort.to_dict()
    
    def export_cohort_json(self, cohort_id: str, indent: int = 2) -> str | None:
        """
        Export a cohort to JSON string.
        
        Args:
            cohort_id: Cohort ID to export
            indent: JSON indentation
            
        Returns:
            JSON string or None if not found
        """
        data = self.export_cohort(cohort_id)
        if data:
            return json.dumps(data, indent=indent, default=str)
        return None
    
    def import_cohort(self, data: dict[str, Any]) -> Cohort:
        """
        Import a cohort from a dictionary.
        
        Args:
            data: Cohort dictionary
            
        Returns:
            The imported Cohort
        """
        cohort = Cohort.from_dict(data)
        self._cohorts[cohort.id] = cohort
        return cohort
    
    def import_cohort_json(self, json_str: str) -> Cohort:
        """
        Import a cohort from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            The imported Cohort
        """
        data = json.loads(json_str)
        return self.import_cohort(data)
    
    # =========================================================================
    # Statistics
    # =========================================================================
    
    def get_statistics(self) -> dict[str, Any]:
        """
        Get overall state statistics.
        
        Returns:
            Dictionary with counts and metadata
        """
        total_entities = 0
        entities_by_type: dict[str, int] = {}
        
        for cohort in self._cohorts.values():
            for entity_type, entities in cohort.entities.items():
                count = len(entities)
                total_entities += count
                entities_by_type[entity_type] = entities_by_type.get(entity_type, 0) + count
        
        return {
            "cohort_count": len(self._cohorts),
            "total_entities": total_entities,
            "entities_by_type": entities_by_type,
            "active_cohort": self._active_cohort_id,
        }
    
    def clear(self) -> None:
        """Clear all state."""
        self._cohorts.clear()
        self._active_cohort_id = None
