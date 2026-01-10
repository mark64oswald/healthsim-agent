"""Generic entity with provenance tracking.

Provides a wrapper that can hold any entity type (Patient, Member, RxMember, etc.)
along with its provenance metadata for serialization and lineage tracking.
"""

from typing import Any

from pydantic import BaseModel, Field

from healthsim_agent.state.provenance import Provenance


class EntityWithProvenance(BaseModel):
    """Wraps any entity with provenance metadata.

    This is a generic container for serializing entities across products.
    """

    entity_id: str
    entity_type: str
    data: dict[str, Any]
    provenance: Provenance = Field(default_factory=Provenance.generated)

    @classmethod
    def from_model(
        cls,
        model: Any,
        entity_id: str,
        entity_type: str,
        provenance: Provenance | None = None,
    ) -> "EntityWithProvenance":
        """Create from a Pydantic model."""
        if hasattr(model, "model_dump"):
            data = model.model_dump()
        elif hasattr(model, "dict"):
            data = model.dict()
        else:
            data = dict(model) if hasattr(model, "__iter__") else {"value": model}

        return cls(
            entity_id=entity_id,
            entity_type=entity_type,
            data=data,
            provenance=provenance or Provenance.generated(),
        )
