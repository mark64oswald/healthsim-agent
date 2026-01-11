"""Base classes and utilities for HealthSim Agent tools.

This module provides the foundational types and helpers for all agent tools:
- ToolResult: Standard response container
- ok/err: Helper functions for creating results
- Entity type taxonomy for validation
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import json


# =============================================================================
# Entity Type Taxonomy - Defines what can be stored in cohorts
# =============================================================================

# SCENARIO DATA: Synthetic PHI entities that are generated per-cohort
# These are the ONLY entity types that should be stored in cohort_entities
# Includes canonical names AND semantic aliases the LLM might generate
SCENARIO_ENTITY_TYPES: Set[str] = {
    # PatientSim - Core
    "patients",
    "encounters", "visits", "appointments",  # visits/appointments → encounters
    "diagnoses", "conditions",  # conditions → diagnoses
    "medications", "drugs",  # drugs → medications
    "lab_results", "labs", "tests",  # labs/tests → lab_results
    "vital_signs", "vitals",  # vitals → vital_signs
    
    # MemberSim - Core
    "members", "enrollments", "subscribers", "dependents", "coverages",  # All → members
    "claims",
    "claim_lines",
    
    # RxMemberSim - Core
    "prescriptions", "rxs",  # rxs → prescriptions
    "pharmacy_claims", "rx_claims", "fills", "refills",  # All → pharmacy_claims
    
    # TrialSim - Core
    "subjects", "participants", "trial_subjects",  # All → subjects
    "adverse_events", "aes", "side_effects",  # All → adverse_events
}

# RELATIONSHIP ENTITIES: Link cohort data to reference data via IDs/NPIs
# These store relationships, not copies of reference data
RELATIONSHIP_ENTITY_TYPES: Set[str] = {
    "pcp_assignments",      # member_id → provider_npi
    "network_contracts",    # plan_id → provider_npi  
    "authorizations",       # member_id → service → provider_npi
    "referrals",            # member_id → from_npi → to_npi
    "facility_assignments", # member_id → facility_npi
}

# REFERENCE DATA: Real-world data that should NEVER be copied into cohorts
# These exist in shared reference tables (network.providers, population.*, etc.)
REFERENCE_ENTITY_TYPES: Set[str] = {
    "providers",    # → Query network.providers (8.9M NPPES records)
    "facilities",   # → Query network.providers with entity_type=2
    "pharmacies",   # → Query network.providers with taxonomy LIKE '333600%'
    "hospitals",    # → Query network.providers with taxonomy LIKE '282N%'
    "organizations",# → Query network.providers with entity_type=2
}

# Combined set of allowed types for validation
ALLOWED_ENTITY_TYPES: Set[str] = SCENARIO_ENTITY_TYPES | RELATIONSHIP_ENTITY_TYPES


# =============================================================================
# ToolResult - Standard Response Container
# =============================================================================

@dataclass
class ToolResult:
    """Standard result container for all tools.
    
    All agent tools return a ToolResult to ensure consistent response format.
    
    Attributes:
        success: Whether the operation completed successfully
        data: The result data (only present on success)
        error: Error message (only present on failure)
        metadata: Additional context (timestamps, counts, warnings, etc.)
    
    Example:
        >>> result = ok({"patients": [...]}, count=5)
        >>> result.success
        True
        >>> result.to_json()
        '{"status": "success", "data": {"patients": [...]}, "metadata": {"count": 5}}'
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string for agent response.
        
        Args:
            indent: JSON indentation level (default 2)
            
        Returns:
            JSON string representation
        """
        result: Dict[str, Any] = {}
        
        if self.success:
            result["status"] = "success"
            if self.data is not None:
                result["data"] = self.data
        else:
            result["status"] = "error"
            result["error"] = self.error or "Unknown error"
        
        if self.metadata:
            result["metadata"] = self.metadata
        
        return json.dumps(result, indent=indent, default=str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }
    
    def __bool__(self) -> bool:
        """Allow using ToolResult in boolean context."""
        return self.success


def ok(data: Any = None, **metadata) -> ToolResult:
    """Create a successful result.
    
    Args:
        data: The result data
        **metadata: Additional metadata key-value pairs
        
    Returns:
        ToolResult with success=True
        
    Example:
        >>> result = ok({"cohort_id": "abc123"}, count=10)
        >>> result.success
        True
    """
    return ToolResult(
        success=True, 
        data=data, 
        metadata=metadata if metadata else None
    )


def err(error: str, **metadata) -> ToolResult:
    """Create an error result.
    
    Args:
        error: Error message describing what went wrong
        **metadata: Additional metadata key-value pairs
        
    Returns:
        ToolResult with success=False
        
    Example:
        >>> result = err("Cohort not found", cohort_id="abc123")
        >>> result.success
        False
    """
    return ToolResult(
        success=False, 
        error=error, 
        metadata=metadata if metadata else None
    )


# =============================================================================
# Entity Type Validation
# =============================================================================

def normalize_entity_type(entity_type: str) -> str:
    """Normalize entity type to lowercase plural form.
    
    Handles common irregular plurals in healthcare domain.
    
    Args:
        entity_type: Raw entity type string
        
    Returns:
        Normalized entity type (lowercase, plural)
        
    Example:
        >>> normalize_entity_type("Patient")
        'patients'
        >>> normalize_entity_type("diagnosis")
        'diagnoses'
        >>> normalize_entity_type("claims")
        'claims'
    """
    normalized = entity_type.lower().strip()
    
    # Handle irregular plurals FIRST (before checking if ends with 's')
    # Words ending in -is → -es (Greek/Latin origin, common in medicine)
    if normalized.endswith('is') and not normalized.endswith('es'):
        return normalized[:-2] + 'es'  # diagnosis → diagnoses, analysis → analyses
    
    # Already plural - return as-is
    if normalized.endswith('s'):
        return normalized
    
    # Words ending in -y after consonant → -ies
    if normalized.endswith('y') and len(normalized) > 1 and normalized[-2] not in 'aeiou':
        return normalized[:-1] + 'ies'  # pharmacy → pharmacies, study → studies
    
    # Standard pluralization - add 's'
    return normalized + 's'


def validate_entity_types(
    entities: Dict[str, List[Dict[str, Any]]], 
    allow_reference: bool = False
) -> Optional[str]:
    """Validate that entity types are appropriate for cohort storage.
    
    Args:
        entities: Dict of entity_type -> list of entities
        allow_reference: If True, allows reference types with a warning
        
    Returns:
        None if valid, or an error message string if invalid.
        
    Example:
        >>> validate_entity_types({"patients": [...]})
        None
        >>> validate_entity_types({"providers": [...]})
        "⚠️ 'providers' is typically REFERENCE DATA..."
    """
    for entity_type in entities.keys():
        normalized = normalize_entity_type(entity_type)
        
        # Check if it's reference data (should NOT be stored in cohorts by default)
        if normalized in REFERENCE_ENTITY_TYPES:
            if allow_reference:
                # User explicitly requested synthetic reference data - allow
                continue
            else:
                # Default: suggest using real data instead
                return (
                    f"⚠️ '{entity_type}' is typically REFERENCE DATA that exists in shared tables.\n\n"
                    f"RECOMMENDED: Use real data from network.providers (8.9M+ records):\n"
                    f"  → search_providers(state='CA', specialty='Family Medicine')\n"
                    f"  → Then store relationships via 'pcp_assignments' or 'network_contracts'\n\n"
                    f"TO OVERRIDE: If you intentionally need synthetic {entity_type} for testing/demos,\n"
                    f"set allow_reference_entities=True in your request."
                )
        
        # Check if it's an allowed type
        if normalized not in ALLOWED_ENTITY_TYPES and normalized not in REFERENCE_ENTITY_TYPES:
            return (
                f"⚠️ Unknown entity type: '{entity_type}'\n\n"
                f"Allowed cohort entity types:\n"
                f"  Scenario data: {sorted(SCENARIO_ENTITY_TYPES)}\n"
                f"  Relationships: {sorted(RELATIONSHIP_ENTITY_TYPES)}\n"
                f"  Reference (with override): {sorted(REFERENCE_ENTITY_TYPES)}\n\n"
                f"If this is a new valid entity type, add it to the taxonomy in tools/base.py"
            )
    
    return None  # Valid
