"""HealthSim Agent Tools - Database and generation operations.

This module provides all tools for the HealthSim Agent:
- Base: ToolResult, ok, err helpers
- Connection: ConnectionManager with close-before-write pattern
- Cohort tools: list, load, save, add_entities, delete
- Query tools: query, get_summary, list_tables
- Reference tools: query_reference, search_providers
- Format tools: transform_to_fhir, transform_to_x12, etc.
- Validation tools: validate_data, fix_validation_issues

Example:
    >>> from healthsim_agent.tools import list_cohorts, search_providers, validate_data
    >>> 
    >>> result = list_cohorts()
    >>> if result.success:
    ...     print(f"Found {len(result.data)} cohorts")
    >>> 
    >>> result = search_providers(state="CA", specialty="Family Medicine")
    >>> if result.success:
    ...     print(f"Found {result.data['result_count']} providers")
    >>>
    >>> result = validate_data([{"id": "P001", "birth_date": "1980-01-15", "gender": "M"}], "patient")
    >>> print(f"Valid: {result.data['valid']}")
"""

from .base import (
    # Result container
    ToolResult,
    ok,
    err,
    # Entity type validation
    validate_entity_types,
    normalize_entity_type,
    SCENARIO_ENTITY_TYPES,
    RELATIONSHIP_ENTITY_TYPES,
    REFERENCE_ENTITY_TYPES,
    ALLOWED_ENTITY_TYPES,
)

from .connection import (
    ConnectionManager,
    get_manager,
    reset_manager,
    get_db_path,
    DEFAULT_DB_PATH,
)

from .cohort_tools import (
    list_cohorts,
    load_cohort,
    save_cohort,
    add_entities,
    delete_cohort,
)

from .query_tools import (
    query,
    get_summary,
    list_tables,
)

from .reference_tools import (
    query_reference,
    search_providers,
)

from .format_tools import (
    transform_to_fhir,
    transform_to_ccda,
    transform_to_hl7v2,
    transform_to_x12,
    transform_to_ncpdp,
    transform_to_mimic,
    list_output_formats,
)

from .validation_tools import (
    validate_data,
    fix_validation_issues,
)

from .skill_tools import (
    # Index and search
    index_skills,
    search_skills,
    get_skill,
    list_skill_products,
    # CRUD operations
    save_skill,
    update_skill,
    delete_skill,
    # Validation
    validate_skill,
    # Versioning
    get_skill_versions,
    restore_skill_version,
    # Templates and creation
    get_skill_template,
    create_skill_from_spec,
    # Statistics
    get_skill_stats,
)


__all__ = [
    # Base
    "ToolResult",
    "ok",
    "err",
    "validate_entity_types",
    "normalize_entity_type",
    "SCENARIO_ENTITY_TYPES",
    "RELATIONSHIP_ENTITY_TYPES", 
    "REFERENCE_ENTITY_TYPES",
    "ALLOWED_ENTITY_TYPES",
    # Connection
    "ConnectionManager",
    "get_manager",
    "reset_manager",
    "get_db_path",
    "DEFAULT_DB_PATH",
    # Cohort tools
    "list_cohorts",
    "load_cohort",
    "save_cohort",
    "add_entities",
    "delete_cohort",
    # Query tools
    "query",
    "get_summary",
    "list_tables",
    # Reference tools
    "query_reference",
    "search_providers",
    # Format tools
    "transform_to_fhir",
    "transform_to_ccda",
    "transform_to_hl7v2",
    "transform_to_x12",
    "transform_to_ncpdp",
    "transform_to_mimic",
    "list_output_formats",
    # Validation tools
    "validate_data",
    "fix_validation_issues",
    # Skill tools
    "index_skills",
    "search_skills",
    "get_skill",
    "list_skill_products",
    "save_skill",
    "update_skill",
    "delete_skill",
    "validate_skill",
    "get_skill_versions",
    "restore_skill_version",
    "get_skill_template",
    "create_skill_from_spec",
    "get_skill_stats",
]
