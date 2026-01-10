"""
Generation framework for synthetic healthcare data.

This package provides:
- Statistical distributions for realistic value generation
- Profile specifications for cohort definitions
- Entity generators for each product (Patient, Member, Subject, etc.)
- Event handlers for timeline-based data generation
- Journey orchestration for profile + journey integration
- Cross-domain synchronization for multi-product scenarios
- Skill reference resolution for dynamic parameter lookup
"""

# Distributions
from healthsim_agent.generation.distributions import (
    Distribution,
    WeightedChoice,
    NormalDistribution,
    UniformDistribution,
    LogNormalDistribution,
    CategoricalDistribution,
    AgeBandDistribution,
    ExplicitDistribution,
    AgeDistribution,
    ConditionalDistribution,
    create_distribution,
)

# Profile schema
from healthsim_agent.generation.profile import (
    DistributionType,
    DistributionSpec,
    GeographyReference,
    ProviderReference,
    FacilityReference,
    NetworkSimSpec,
    DemographicsSpec,
    ConditionSpec,
    ClinicalSpec,
    CoverageSpec,
    OutputSpec,
    GenerationSpec,
    JourneyReference,
    ProfileSpecification,
    PROFILE_TEMPLATES,
)

# Base generators
from healthsim_agent.generation.base import (
    BaseGenerator,
    PersonGenerator,
)

# Cohort generation
from healthsim_agent.generation.cohort import (
    CohortConstraints,
    CohortProgress,
    CohortGenerator,
)

# Entity generators
from healthsim_agent.generation.generators import (
    GeneratorConfig,
    PatientGenerator,
    MemberGenerator,
    ClaimGenerator,
    SubjectGenerator,
)

# Event handlers
from healthsim_agent.generation.handlers import (
    TimelineEvent,
    EventHandler,
    BaseEventHandler,
    PatientSimHandlers,
    MemberSimHandlers,
    RxMemberSimHandlers,
    TrialSimHandlers,
    HandlerRegistry,
)

# Profile executor
from healthsim_agent.generation.profile_executor import (
    HierarchicalSeedManager,
    GeneratedEntity,
    ExecutionResult,
    ValidationMetric,
    ValidationReport,
    ProfileExecutor,
    execute_profile,
)

# Journey engine
from healthsim_agent.generation.journey_engine import (
    BaseEventType,
    PatientEventType,
    MemberEventType,
    RxEventType,
    TrialEventType,
    DelaySpec,
    EventCondition,
    SkillRef,
    EventDefinition,
    TriggerSpec,
    JourneySpecification,
    JourneyTimelineEvent,
    Timeline,
    JourneyEngine,
    create_journey_engine,
    create_simple_journey,
    get_journey_template,
    JOURNEY_TEMPLATES,
)

# Journey validation
from healthsim_agent.generation.journey_validation import (
    ValidationSeverity,
    ValidationCategory,
    ValidationIssue,
    ValidationResult,
    JourneySpecValidator,
    TimelineValidator,
    CrossEventValidator,
    JourneyValidator,
    validate_journey_spec,
    validate_timeline,
    validate_events,
    create_journey_validator,
)

# Reference profiles (PopulationSim/NetworkSim integration)
from healthsim_agent.generation.reference_profiles import (
    GeographyLevel,
    RefGeographyReference,
    DemographicProfile,
    ReferenceProfileResolver,
    resolve_geography,
    list_counties,
    list_states,
    merge_profile_with_reference,
    create_hybrid_profile,
    resolve_provider_reference,
    resolve_facility_reference,
    create_hybrid_profile_with_network,
)

# Cross-domain synchronization
from healthsim_agent.generation.cross_domain_sync import (
    ProductType,
    TriggerType,
    CorrelatorType,
    PersonIdentity,
    IdentityRegistry,
    CrossTriggerSpec,
    TriggerResult,
    TriggerRegistry,
    SyncConfig,
    SyncReport,
    CrossDomainSync,
    create_cross_domain_sync,
    hash_ssn,
)

# Cross-product triggers
from healthsim_agent.generation.triggers import (
    TriggerPriority,
    RegisteredTrigger,
    TriggerRegistry as EventTriggerRegistry,
    LinkedEntity,
    CrossProductCoordinator,
    create_coordinator,
)

# Profile-Journey orchestrator
from healthsim_agent.generation.orchestrator import (
    EntityWithTimeline,
    OrchestratorResult,
    ProfileJourneyOrchestrator,
    orchestrate,
)

# Skill registry
from healthsim_agent.generation.skill_registry import (
    SkillCapability,
    SkillCapabilityDeclaration,
    SkillRegistration,
    SkillRegistry,
    get_skill_registry,
    auto_resolve_parameters,
    register_skill,
)

# Skill reference resolution
from healthsim_agent.generation.skill_reference import (
    SkillReference,
    ResolvedParameters,
    SkillResolver,
    ParameterResolver,
    get_skill_resolver,
    get_parameter_resolver,
    resolve_skill_ref,
    get_skills_root,
)

# Skill-aware journey templates
from healthsim_agent.generation.skill_journeys import (
    SKILL_AWARE_TEMPLATES,
    DIABETIC_FIRST_YEAR_SKILL,
    CKD_MANAGEMENT_SKILL,
    HF_MANAGEMENT_SKILL,
    PHARMACY_ADHERENCE_SKILL,
    list_skill_aware_templates,
    get_skill_aware_template,
)

# Auto-resolution journey templates
from healthsim_agent.generation.auto_journeys import (
    AUTO_RESOLUTION_TEMPLATES,
    DIABETIC_CARE_AUTO,
    CKD_CARE_AUTO,
    HEART_FAILURE_AUTO,
    HYPERTENSION_AUTO,
    MULTI_CONDITION_AUTO,
    PHARMACY_DIABETES_AUTO,
    TRIAL_DIABETES_AUTO,
    list_auto_templates,
    get_auto_template,
)

# NetworkSim reference resolver
from healthsim_agent.generation.networksim_reference import (
    EntityType,
    FacilityType,
    Provider,
    Facility,
    ProviderSearchCriteria,
    FacilitySearchCriteria,
    TAXONOMY_MAP,
    FACILITY_TYPE_MAP,
    NetworkSimResolver,
    get_healthsim_db_path,
    get_networksim_db_path,
    get_providers_by_geography,
    get_facilities_by_geography,
    assign_provider_to_patient,
    assign_facility_to_patient,
)

# Geography-aware profile builder
from healthsim_agent.generation.geography_builder import (
    GeographyProfile,
    GeographyAwareProfileBuilder,
    create_geography_profile,
    build_cohort_with_geography,
    get_provider_for_entity,
    get_facility_for_entity,
)

# Reproducibility
from healthsim_agent.generation.reproducibility import SeedManager


__all__ = [
    # Distributions
    "Distribution",
    "WeightedChoice",
    "NormalDistribution",
    "UniformDistribution",
    "LogNormalDistribution",
    "CategoricalDistribution",
    "AgeBandDistribution",
    "ExplicitDistribution",
    "AgeDistribution",
    "ConditionalDistribution",
    "create_distribution",
    # Profile
    "DistributionType",
    "DistributionSpec",
    "GeographyReference",
    "ProviderReference",
    "FacilityReference",
    "NetworkSimSpec",
    "DemographicsSpec",
    "ConditionSpec",
    "ClinicalSpec",
    "CoverageSpec",
    "OutputSpec",
    "GenerationSpec",
    "JourneyReference",
    "ProfileSpecification",
    "PROFILE_TEMPLATES",
    # Base generators
    "BaseGenerator",
    "PersonGenerator",
    # Cohort generation
    "CohortConstraints",
    "CohortProgress",
    "CohortGenerator",
    # Generators
    "GeneratorConfig",
    "PatientGenerator",
    "MemberGenerator",
    "ClaimGenerator",
    "SubjectGenerator",
    # Handlers
    "TimelineEvent",
    "EventHandler",
    "BaseEventHandler",
    "PatientSimHandlers",
    "MemberSimHandlers",
    "RxMemberSimHandlers",
    "TrialSimHandlers",
    "HandlerRegistry",
    # Profile executor
    "HierarchicalSeedManager",
    "GeneratedEntity",
    "ExecutionResult",
    "ValidationMetric",
    "ValidationReport",
    "ProfileExecutor",
    "execute_profile",
    # Journey engine
    "BaseEventType",
    "PatientEventType",
    "MemberEventType",
    "RxEventType",
    "TrialEventType",
    "DelaySpec",
    "EventCondition",
    "SkillRef",
    "EventDefinition",
    "TriggerSpec",
    "JourneySpecification",
    "JourneyTimelineEvent",
    "Timeline",
    "JourneyEngine",
    "create_journey_engine",
    "create_simple_journey",
    "get_journey_template",
    "JOURNEY_TEMPLATES",
    # Journey validation
    "ValidationSeverity",
    "ValidationCategory",
    "ValidationIssue",
    "ValidationResult",
    "JourneySpecValidator",
    "TimelineValidator",
    "CrossEventValidator",
    "JourneyValidator",
    "validate_journey_spec",
    "validate_timeline",
    "validate_events",
    "create_journey_validator",
    # Reference profiles
    "GeographyLevel",
    "RefGeographyReference",
    "DemographicProfile",
    "ReferenceProfileResolver",
    "resolve_geography",
    "list_counties",
    "list_states",
    "merge_profile_with_reference",
    "create_hybrid_profile",
    "resolve_provider_reference",
    "resolve_facility_reference",
    "create_hybrid_profile_with_network",
    # Cross-domain sync
    "ProductType",
    "TriggerType",
    "CorrelatorType",
    "PersonIdentity",
    "IdentityRegistry",
    "CrossTriggerSpec",
    "TriggerResult",
    "TriggerRegistry",
    "SyncConfig",
    "SyncReport",
    "CrossDomainSync",
    "create_cross_domain_sync",
    "hash_ssn",
    # Triggers
    "TriggerPriority",
    "RegisteredTrigger",
    "EventTriggerRegistry",
    "LinkedEntity",
    "CrossProductCoordinator",
    "create_coordinator",
    # Orchestrator
    "EntityWithTimeline",
    "OrchestratorResult",
    "ProfileJourneyOrchestrator",
    "orchestrate",
    # Skill registry
    "SkillCapability",
    "SkillCapabilityDeclaration",
    "SkillRegistration",
    "SkillRegistry",
    "get_skill_registry",
    "auto_resolve_parameters",
    "register_skill",
    # Skill reference
    "SkillReference",
    "ResolvedParameters",
    "SkillResolver",
    "ParameterResolver",
    "get_skill_resolver",
    "get_parameter_resolver",
    "resolve_skill_ref",
    "get_skills_root",
    # Skill-aware templates
    "SKILL_AWARE_TEMPLATES",
    "DIABETIC_FIRST_YEAR_SKILL",
    "CKD_MANAGEMENT_SKILL",
    "HF_MANAGEMENT_SKILL",
    "PHARMACY_ADHERENCE_SKILL",
    "list_skill_aware_templates",
    "get_skill_aware_template",
    # Auto-resolution templates
    "AUTO_RESOLUTION_TEMPLATES",
    "DIABETIC_CARE_AUTO",
    "CKD_CARE_AUTO",
    "HEART_FAILURE_AUTO",
    "HYPERTENSION_AUTO",
    "MULTI_CONDITION_AUTO",
    "PHARMACY_DIABETES_AUTO",
    "TRIAL_DIABETES_AUTO",
    "list_auto_templates",
    "get_auto_template",
    # NetworkSim reference
    "EntityType",
    "FacilityType",
    "Provider",
    "Facility",
    "ProviderSearchCriteria",
    "FacilitySearchCriteria",
    "TAXONOMY_MAP",
    "FACILITY_TYPE_MAP",
    "NetworkSimResolver",
    "get_healthsim_db_path",
    "get_networksim_db_path",
    "get_providers_by_geography",
    "get_facilities_by_geography",
    "assign_provider_to_patient",
    "assign_facility_to_patient",
    # Geography builder
    "GeographyProfile",
    "GeographyAwareProfileBuilder",
    "create_geography_profile",
    "build_cohort_with_geography",
    "get_provider_for_entity",
    "get_facility_for_entity",
    # Reproducibility
    "SeedManager",
]
