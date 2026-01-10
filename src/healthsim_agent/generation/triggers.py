"""Cross-product trigger system for event coordination.

This module handles the dispatch and coordination of events across
different HealthSim products (PatientSim, MemberSim, RxMemberSim, etc.).

The trigger system enables scenarios like:
- Patient diagnosis (PatientSim) triggers a claim (MemberSim)
- Medication order (PatientSim) triggers a fill (RxMemberSim)
- Quality gap (MemberSim) triggers an outreach event (PatientSim)

Ported from: healthsim-workspace/packages/core/src/healthsim/generation/triggers.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable
from enum import Enum
import logging

from healthsim_agent.generation.journey_engine import (
    DelaySpec,
    EventCondition,
    Timeline,
    JourneyTimelineEvent,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Trigger Registry
# =============================================================================

class TriggerPriority(Enum):
    """Priority levels for trigger execution."""
    IMMEDIATE = 0  # Execute same day
    HIGH = 1       # Execute within 1-3 days
    NORMAL = 2     # Execute per delay spec
    LOW = 3        # Execute when convenient


@dataclass
class RegisteredTrigger:
    """A registered cross-product trigger."""
    
    source_product: str
    source_event_type: str
    target_product: str
    target_event_type: str
    
    delay: DelaySpec = field(default_factory=DelaySpec)
    priority: TriggerPriority = TriggerPriority.NORMAL
    condition: EventCondition | None = None
    
    parameter_map: dict[str, str] = field(default_factory=dict)
    handler: Callable | None = None


class TriggerRegistry:
    """Registry of cross-product triggers."""
    
    def __init__(self):
        self._triggers: dict[tuple[str, str], list[RegisteredTrigger]] = {}
        self._target_handlers: dict[str, Callable] = {}
    
    def register(
        self,
        source_product: str,
        source_event_type: str,
        target_product: str,
        target_event_type: str,
        delay: DelaySpec | None = None,
        priority: TriggerPriority = TriggerPriority.NORMAL,
        condition: EventCondition | None = None,
        parameter_map: dict[str, str] | None = None,
        handler: Callable | None = None,
    ) -> None:
        """Register a cross-product trigger."""
        key = (source_product, source_event_type)
        
        trigger = RegisteredTrigger(
            source_product=source_product,
            source_event_type=source_event_type,
            target_product=target_product,
            target_event_type=target_event_type,
            delay=delay or DelaySpec(),
            priority=priority,
            condition=condition,
            parameter_map=parameter_map or {},
            handler=handler,
        )
        
        if key not in self._triggers:
            self._triggers[key] = []
        self._triggers[key].append(trigger)
    
    def register_target_handler(
        self,
        product: str,
        handler: Callable[[str, JourneyTimelineEvent, dict], None]
    ) -> None:
        """Register a handler for receiving triggers in a product."""
        self._target_handlers[product] = handler
    
    def get_triggers(
        self,
        source_product: str,
        source_event_type: str
    ) -> list[RegisteredTrigger]:
        """Get triggers for a source event."""
        return self._triggers.get((source_product, source_event_type), [])
    
    def fire_triggers(
        self,
        source_event: JourneyTimelineEvent,
        source_result: dict[str, Any],
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Fire all triggers for a source event."""
        triggered = []
        triggers = self.get_triggers(source_event.product, source_event.event_type)
        
        for trigger in triggers:
            if trigger.condition and not trigger.condition.evaluate(context):
                continue
            
            target_date = source_event.scheduled_date + trigger.delay.to_timedelta()
            
            target_params = {}
            for target_key, source_key in trigger.parameter_map.items():
                if source_key in source_result:
                    target_params[target_key] = source_result[source_key]
                elif source_key in context:
                    target_params[target_key] = context[source_key]
            
            if trigger.target_product in self._target_handlers:
                handler = self._target_handlers[trigger.target_product]
                try:
                    handler(trigger.target_event_type, source_event, {
                        "target_date": target_date,
                        "parameters": target_params,
                        "source_event_id": source_event.timeline_event_id,
                    })
                except Exception as e:
                    logger.error(f"Trigger handler failed: {e}")
            
            triggered.append({
                "source_event_id": source_event.timeline_event_id,
                "target_product": trigger.target_product,
                "target_event_type": trigger.target_event_type,
                "target_date": target_date.isoformat(),
                "priority": trigger.priority.name,
            })
        
        return triggered


# =============================================================================
# Cross-Product Coordinator
# =============================================================================

@dataclass
class LinkedEntity:
    """An entity with cross-product linkage."""
    
    core_id: str
    
    patient_id: str | None = None
    member_id: str | None = None
    rx_member_id: str | None = None
    trial_subject_id: str | None = None
    
    timelines: dict[str, Timeline] = field(default_factory=dict)


class CrossProductCoordinator:
    """Coordinates events across multiple HealthSim products."""
    
    def __init__(self):
        self._linked_entities: dict[str, LinkedEntity] = {}
        self._product_engines: dict[str, Any] = {}
        self._trigger_registry = TriggerRegistry()
        
        self._register_default_triggers()
    
    def create_linked_entity(
        self,
        core_id: str,
        product_ids: dict[str, str] | None = None,
    ) -> LinkedEntity:
        """Create a new linked entity."""
        linked = LinkedEntity(core_id=core_id)
        
        if product_ids:
            if "patient_id" in product_ids:
                linked.patient_id = product_ids["patient_id"]
            if "member_id" in product_ids:
                linked.member_id = product_ids["member_id"]
            if "rx_member_id" in product_ids:
                linked.rx_member_id = product_ids["rx_member_id"]
            if "trial_subject_id" in product_ids:
                linked.trial_subject_id = product_ids["trial_subject_id"]
        
        self._linked_entities[core_id] = linked
        return linked
    
    def register_product_engine(self, product: str, engine: Any) -> None:
        """Register a product's journey engine."""
        self._product_engines[product] = engine
    
    def get_linked_entity(self, core_id: str) -> LinkedEntity | None:
        """Get a linked entity by core ID."""
        return self._linked_entities.get(core_id)
    
    def add_timeline(
        self,
        linked: LinkedEntity,
        product: str,
        timeline: Timeline
    ) -> None:
        """Add a timeline to a linked entity."""
        linked.timelines[product] = timeline
        
        for other_product, other_timeline in linked.timelines.items():
            if other_product != product:
                timeline.linked_timelines[other_product] = other_timeline.entity_id
                other_timeline.linked_timelines[product] = timeline.entity_id
    
    def execute_coordinated(
        self,
        linked: LinkedEntity,
        up_to_date: date,
    ) -> dict[str, list[dict]]:
        """Execute all pending events across products."""
        results: dict[str, list[dict]] = {}
        
        all_events: list[tuple[str, Timeline, JourneyTimelineEvent]] = []
        
        for product, timeline in linked.timelines.items():
            for event in timeline.get_events_up_to(up_to_date):
                all_events.append((product, timeline, event))
        
        all_events.sort(key=lambda x: x[2].scheduled_date)
        
        for product, timeline, event in all_events:
            if product not in results:
                results[product] = []
            
            engine = self._product_engines.get(product)
            if not engine:
                results[product].append({
                    "event_id": event.timeline_event_id,
                    "status": "skipped",
                    "reason": f"No engine registered for {product}"
                })
                continue
            
            entity = self._get_product_entity(linked, product)
            
            result = engine.execute_event(timeline, event, entity)
            results[product].append({
                "event_id": event.timeline_event_id,
                "event_type": event.event_type,
                "scheduled_date": event.scheduled_date.isoformat(),
                **result
            })
            
            if result.get("status") == "executed":
                triggered = self._trigger_registry.fire_triggers(
                    event, 
                    result.get("outputs", {}),
                    {"linked_entity": linked}
                )
                if triggered:
                    results[product][-1]["triggered"] = triggered
        
        return results
    
    def _get_product_entity(self, linked: LinkedEntity, product: str) -> dict:
        """Get entity dict for a specific product."""
        if product == "patientsim":
            return {"patient_id": linked.patient_id, "core_id": linked.core_id}
        elif product == "membersim":
            return {"member_id": linked.member_id, "core_id": linked.core_id}
        elif product == "rxmembersim":
            return {"rx_member_id": linked.rx_member_id, "core_id": linked.core_id}
        elif product == "trialsim":
            return {"subject_id": linked.trial_subject_id, "core_id": linked.core_id}
        return {"core_id": linked.core_id}
    
    def _register_default_triggers(self) -> None:
        """Register standard healthcare cross-product triggers."""
        
        self._trigger_registry.register(
            source_product="patientsim",
            source_event_type="diagnosis",
            target_product="membersim",
            target_event_type="claim_professional",
            delay=DelaySpec(days=3, days_min=1, days_max=7, distribution="uniform"),
            parameter_map={"diagnosis_code": "icd10"},
        )
        
        self._trigger_registry.register(
            source_product="patientsim",
            source_event_type="medication_order",
            target_product="membersim",
            target_event_type="claim_pharmacy",
            delay=DelaySpec(days=1, days_min=0, days_max=3, distribution="uniform"),
            parameter_map={"ndc": "rxnorm"},
        )
        
        self._trigger_registry.register(
            source_product="patientsim",
            source_event_type="medication_order",
            target_product="rxmembersim",
            target_event_type="fill",
            delay=DelaySpec(days=1, days_min=0, days_max=3, distribution="uniform"),
            parameter_map={"ndc": "rxnorm", "quantity": "quantity"},
        )
        
        self._trigger_registry.register(
            source_product="patientsim",
            source_event_type="lab_order",
            target_product="patientsim",
            target_event_type="lab_result",
            delay=DelaySpec(days=2, days_min=1, days_max=5, distribution="uniform"),
            parameter_map={"loinc": "loinc", "order_id": "order_id"},
        )
        
        self._trigger_registry.register(
            source_product="membersim",
            source_event_type="gap_identified",
            target_product="patientsim",
            target_event_type="care_plan_update",
            delay=DelaySpec(days=7, days_min=3, days_max=14, distribution="uniform"),
            parameter_map={"measure": "measure", "gap_id": "gap_id"},
        )


# =============================================================================
# Convenience Functions
# =============================================================================

def create_coordinator() -> CrossProductCoordinator:
    """Create a cross-product coordinator with default configuration."""
    return CrossProductCoordinator()
