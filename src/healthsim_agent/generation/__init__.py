"""
Generation framework for synthetic healthcare data.

This package provides:
- Statistical distributions for realistic value generation
- Profile specifications for cohort definitions
- Entity generators for each product (Patient, Member, Subject, etc.)
- Event handlers for timeline-based data generation

Usage:
    from healthsim_agent.generation import (
        PatientGenerator,
        MemberGenerator,
        ProfileSpecification,
        create_distribution,
    )
    
    # Generate patients
    gen = PatientGenerator()
    patients = gen.generate_batch(count=100)
    
    # Use profile specification
    profile = ProfileSpecification(
        id="test-cohort",
        name="Test Cohort",
        generation={"count": 50, "products": ["patientsim"]},
    )
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
    create_distribution,
)

# Profile schema
from healthsim_agent.generation.profile import (
    DistributionType,
    DistributionSpec,
    GeographyReference,
    ProviderReference,
    FacilityReference,
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
    "create_distribution",
    # Profile
    "DistributionType",
    "DistributionSpec",
    "GeographyReference",
    "ProviderReference",
    "FacilityReference",
    "DemographicsSpec",
    "ConditionSpec",
    "ClinicalSpec",
    "CoverageSpec",
    "OutputSpec",
    "GenerationSpec",
    "JourneyReference",
    "ProfileSpecification",
    "PROFILE_TEMPLATES",
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
]
