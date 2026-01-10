"""HealthSim Agent - State Management Package

Provides session and cohort management:
- SessionState: Conversation history and context
- StateManager: Cohort persistence and entity tracking
- Cohort: Named collection of generated entities
- CohortSummary: Token-efficient cohort overview
- Provenance: Entity lineage tracking
- Serializers: Entity serialization for database
- AutoNaming: Intelligent cohort naming
- AutoPersist: Structured RAG pattern implementation
"""

from healthsim_agent.state.session import (
    GeneratedItem,
    Message,
    SessionState,
)
from healthsim_agent.state.manager import (
    Cohort,
    CohortSummary,
    EntityReference,
    StateManager,
)
from healthsim_agent.state.provenance import (
    Provenance,
    ProvenanceSummary,
    SourceType,
)
from healthsim_agent.state.entity import EntityWithProvenance
from healthsim_agent.state.auto_naming import (
    extract_keywords,
    generate_cohort_name,
    parse_cohort_name,
    sanitize_name,
)
from healthsim_agent.state.serializers import (
    get_serializer,
    get_table_info,
    serialize_claim,
    serialize_diagnosis,
    serialize_encounter,
    serialize_member,
    serialize_patient,
    serialize_prescription,
    serialize_subject,
    ENTITY_TABLE_MAP,
)
from healthsim_agent.state.summary import (
    CohortSummary as DetailedCohortSummary,
    SummaryGenerator,
    ENTITY_COUNT_TABLES,
    generate_summary,
    get_cohort_by_name,
)
from healthsim_agent.state.auto_persist import (
    AutoPersistService,
    PersistResult,
    QueryResult,
    CohortBrief,
    CloneResult,
    MergeResult,
    ExportResult,
    CANONICAL_TABLES,
    get_auto_persist_service,
)
from healthsim_agent.state.profile_manager import (
    ProfileManager,
    ProfileRecord,
    ProfileSummary,
    ExecutionRecord,
    get_profile_manager,
)
from healthsim_agent.state.journey_manager import (
    JourneyManager,
    JourneyRecord,
    JourneyStep,
    JourneySummary,
    JourneyExecutionRecord,
    get_journey_manager,
)
from healthsim_agent.state.legacy import (
    export_to_json,
    import_from_json,
    list_legacy_cohorts,
    migrate_legacy_cohort,
    migrate_all_legacy_cohorts,
    export_cohort_for_sharing,
    LEGACY_COHORTS_PATH,
    LEGACY_WORKSPACES_PATH,
)
from healthsim_agent.state.workspace import (
    Workspace,
    WorkspaceMetadata,
    WORKSPACES_DIR,
)

__all__ = [
    # Session management
    "SessionState",
    "Message",
    "GeneratedItem",
    # Cohort management
    "StateManager",
    "Cohort",
    "CohortSummary",
    "EntityReference",
    # Provenance
    "Provenance",
    "ProvenanceSummary",
    "SourceType",
    "EntityWithProvenance",
    # Auto naming
    "extract_keywords",
    "generate_cohort_name",
    "parse_cohort_name",
    "sanitize_name",
    # Serializers
    "get_serializer",
    "get_table_info",
    "serialize_patient",
    "serialize_encounter",
    "serialize_diagnosis",
    "serialize_member",
    "serialize_claim",
    "serialize_prescription",
    "serialize_subject",
    "ENTITY_TABLE_MAP",
    # Summary generation
    "DetailedCohortSummary",
    "SummaryGenerator",
    "ENTITY_COUNT_TABLES",
    "generate_summary",
    "get_cohort_by_name",
    # Auto persist (Structured RAG)
    "AutoPersistService",
    "PersistResult",
    "QueryResult",
    "CohortBrief",
    "CloneResult",
    "MergeResult",
    "ExportResult",
    "CANONICAL_TABLES",
    "get_auto_persist_service",
    # Profile management
    "ProfileManager",
    "ProfileRecord",
    "ProfileSummary",
    "ExecutionRecord",
    "get_profile_manager",
    # Journey management
    "JourneyManager",
    "JourneyRecord",
    "JourneyStep",
    "JourneySummary",
    "JourneyExecutionRecord",
    "get_journey_manager",
    # Legacy JSON support
    "export_to_json",
    "import_from_json",
    "list_legacy_cohorts",
    "migrate_legacy_cohort",
    "migrate_all_legacy_cohorts",
    "export_cohort_for_sharing",
    "LEGACY_COHORTS_PATH",
    "LEGACY_WORKSPACES_PATH",
    # Workspace (file-based)
    "Workspace",
    "WorkspaceMetadata",
    "WORKSPACES_DIR",
]
