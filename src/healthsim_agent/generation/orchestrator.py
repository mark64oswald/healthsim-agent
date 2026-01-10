"""Profile-to-Journey orchestrator for HealthSim.

This module bridges profile-based entity generation with journey-based
temporal event sequences.

Ported from: healthsim-workspace/packages/core/src/healthsim/generation/orchestrator.py
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from healthsim_agent.generation.journey_engine import (
    JourneyEngine,
    JourneySpecification,
    Timeline,
    JOURNEY_TEMPLATES,
)
from healthsim_agent.generation.profile_executor import (
    ProfileExecutor,
    GeneratedEntity,
    HierarchicalSeedManager,
)
from healthsim_agent.generation.profile import ProfileSpecification


@dataclass
class EntityWithTimeline:
    """An entity paired with its journey timeline."""
    
    entity: GeneratedEntity
    timeline: Timeline
    journey_ids: list[str] = field(default_factory=list)
    
    @property
    def pending_events(self) -> int:
        """Count of pending events on timeline."""
        return len(self.timeline.get_pending_events())
    
    @property
    def executed_events(self) -> int:
        """Count of executed events."""
        return len([e for e in self.timeline.events if e.status == "executed"])


@dataclass
class OrchestratorResult:
    """Result from orchestrator execution."""
    
    profile_id: str
    journey_ids: list[str]
    seed: int
    
    entities: list[EntityWithTimeline]
    
    duration_seconds: float = 0.0
    
    profile_name: str | None = None
    execution_id: int | None = None
    cohort_id: str | None = None
    
    @property
    def entity_count(self) -> int:
        """Number of entities generated."""
        return len(self.entities)
    
    @property
    def event_count(self) -> int:
        """Total events across all timelines."""
        return sum(len(e.timeline.events) for e in self.entities)
    
    @property
    def pending_events(self) -> int:
        """Total pending events."""
        return sum(e.pending_events for e in self.entities)
    
    def get_events_by_date(self, target_date: date) -> list[tuple[str, Any]]:
        """Get all events scheduled for a specific date."""
        results = []
        for ent in self.entities:
            for event in ent.timeline.get_events_by_date(target_date):
                results.append((ent.entity.identifiers.get("entity_id", str(ent.entity.index)), event))
        return results


class ProfileJourneyOrchestrator:
    """Orchestrate profile generation with journey assignment."""
    
    def __init__(
        self,
        seed: int | None = None,
        journey_engine: JourneyEngine | None = None,
    ):
        self.seed = seed or 42
        self.seed_manager = HierarchicalSeedManager(self.seed)
        self.journey_engine = journey_engine or JourneyEngine(seed=self.seed)
        
        self._profile_executors: dict[str, type] = {}
    
    def register_executor(self, product: str, executor_class: type) -> None:
        """Register a product-specific profile executor."""
        self._profile_executors[product] = executor_class
    
    def execute(
        self,
        profile: str | ProfileSpecification | dict,
        journey: str | JourneySpecification | dict | list | None = None,
        count: int | None = None,
        start_date: date | None = None,
        execute_events: bool = False,
        up_to_date: date | None = None,
    ) -> OrchestratorResult:
        """Execute profile generation with journey assignment."""
        start_time = time.time()
        
        profile_spec = self._resolve_profile(profile)
        profile_id = profile_spec.id
        
        journeys = self._resolve_journeys(journey) if journey else []
        journey_ids = [j.journey_id for j in journeys]
        
        if count:
            profile_spec.generation.count = count
        
        executor = ProfileExecutor(profile_spec, seed=self.seed)
        profile_result = executor.execute()
        
        timeline_start = start_date or date.today()
        entities_with_timelines = []
        
        for entity in profile_result.entities:
            entity_seed = self.seed_manager.get_entity_seed(entity.index)
            entity_context = self._build_entity_context(entity)
            
            combined_timeline = Timeline(
                entity_id=str(entity.index),
                entity_type=self._get_entity_type(profile_spec),
                journey_ids=journey_ids,
                start_date=timeline_start,
            )
            
            for journey_spec in journeys:
                timeline = self.journey_engine.create_timeline(
                    entity=entity_context,
                    entity_type=self._get_entity_type(profile_spec),
                    journey=journey_spec,
                    start_date=timeline_start,
                )
                for event in timeline.events:
                    combined_timeline.add_event(event)
            
            if execute_events and combined_timeline.events:
                exec_date = up_to_date or timeline_start
                self.journey_engine.execute_timeline(
                    combined_timeline,
                    entity_context,
                    up_to_date=exec_date,
                )
            
            entities_with_timelines.append(EntityWithTimeline(
                entity=entity,
                timeline=combined_timeline,
                journey_ids=journey_ids,
            ))
        
        duration = time.time() - start_time
        
        return OrchestratorResult(
            profile_id=profile_id,
            journey_ids=journey_ids,
            seed=self.seed,
            entities=entities_with_timelines,
            duration_seconds=duration,
        )
    
    def execute_with_persistence(
        self,
        profile: str | ProfileSpecification | dict,
        profile_name: str,
        journey: str | JourneySpecification | dict | list | None = None,
        count: int | None = None,
        start_date: date | None = None,
        execute_events: bool = False,
        up_to_date: date | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        persist_entities: bool = True,
    ) -> OrchestratorResult:
        """Execute profile with automatic persistence tracking."""
        from healthsim_agent.state.profile_manager import get_profile_manager
        from healthsim_agent.state.manager import get_manager, persist
        
        start_time = time.time()
        
        profile_spec = self._resolve_profile(profile)
        
        state_manager = get_manager()
        profile_manager = state_manager.profiles
        
        try:
            saved_profile = profile_manager.load_profile(profile_name)
            profile_id = saved_profile.id
        except ValueError:
            spec_dict = profile_spec.model_dump() if hasattr(profile_spec, 'model_dump') else {"profile": profile_spec.__dict__}
            profile_id = profile_manager.save_profile(
                name=profile_name,
                profile_spec=spec_dict,
                description=description,
                tags=tags,
            )
        
        result = self.execute(
            profile=profile,
            journey=journey,
            count=count,
            start_date=start_date,
            execute_events=execute_events,
            up_to_date=up_to_date,
        )
        
        cohort_id = None
        if persist_entities and result.entities:
            entity_dicts = [
                {"index": e.entity.index, **e.entity.attributes}
                for e in result.entities
            ]
            
            persist_result = persist(
                entities={"entities": entity_dicts},
                context=f"{profile_name} execution",
            )
            cohort_id = persist_result.cohort_id
        
        duration = time.time() - start_time
        duration_ms = int(duration * 1000)
        
        execution_id = profile_manager.record_execution(
            profile_id=profile_id,
            cohort_id=cohort_id,
            seed=self.seed,
            count=result.entity_count,
            duration_ms=duration_ms,
        )
        
        return OrchestratorResult(
            profile_id=result.profile_id,
            journey_ids=result.journey_ids,
            seed=result.seed,
            entities=result.entities,
            duration_seconds=duration,
            profile_name=profile_name,
            execution_id=execution_id,
            cohort_id=cohort_id,
        )
    
    def _resolve_profile(
        self,
        profile: str | ProfileSpecification | dict,
    ) -> ProfileSpecification:
        """Resolve profile to ProfileSpecification."""
        if isinstance(profile, str):
            return ProfileSpecification(
                id=profile,
                name=profile,
            )
        elif isinstance(profile, dict):
            return ProfileSpecification.model_validate(profile)
        return profile
    
    def _resolve_journeys(
        self,
        journey: str | JourneySpecification | dict | list,
    ) -> list[JourneySpecification]:
        """Resolve journey(s) to list of JourneySpecification."""
        if isinstance(journey, list):
            return [self._resolve_single_journey(j) for j in journey]
        return [self._resolve_single_journey(journey)]
    
    def _resolve_single_journey(
        self,
        journey: str | JourneySpecification | dict,
    ) -> JourneySpecification:
        """Resolve a single journey."""
        if isinstance(journey, str):
            if journey in JOURNEY_TEMPLATES:
                template = JOURNEY_TEMPLATES[journey]
                return JourneySpecification.model_validate(template)
            return JourneySpecification(
                journey_id=journey,
                name=journey,
            )
        elif isinstance(journey, dict):
            return JourneySpecification.model_validate(journey)
        return journey
    
    def _build_entity_context(self, entity: GeneratedEntity) -> dict[str, Any]:
        """Build context dict from generated entity."""
        return {
            "entity_id": str(entity.index),
            "age": entity.age,
            "gender": entity.gender,
            "conditions": entity.conditions,
            "coverage_type": entity.coverage_type,
            "attributes": entity.attributes,
            **entity.identifiers,
        }
    
    def _get_entity_type(self, profile: ProfileSpecification) -> str:
        """Determine entity type from profile."""
        products = profile.generation.products
        if "patientsim" in products:
            return "patient"
        elif "membersim" in products:
            return "member"
        elif "rxmembersim" in products:
            return "rx_member"
        elif "trialsim" in products:
            return "subject"
        return "entity"


# =============================================================================
# Convenience Functions
# =============================================================================

def orchestrate(
    profile: str | ProfileSpecification | dict,
    journey: str | JourneySpecification | dict | list | None = None,
    count: int | None = None,
    seed: int | None = None,
    start_date: date | None = None,
) -> OrchestratorResult:
    """Generate entities with journeys in one call."""
    orchestrator = ProfileJourneyOrchestrator(seed=seed)
    return orchestrator.execute(
        profile=profile,
        journey=journey,
        count=count,
        start_date=start_date,
    )


__all__ = [
    "ProfileJourneyOrchestrator",
    "EntityWithTimeline",
    "OrchestratorResult",
    "orchestrate",
]
