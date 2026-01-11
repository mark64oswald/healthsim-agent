"""Tests for entity and provenance modules.

Tests entity wrapping and provenance tracking across HealthSim products.
"""

from datetime import datetime
from typing import Any

import pytest
from pydantic import BaseModel

from healthsim_agent.state.entity import EntityWithProvenance
from healthsim_agent.state.provenance import Provenance, ProvenanceSummary, SourceType


class TestSourceType:
    """Tests for SourceType enum."""

    def test_source_type_values(self):
        """Test source type values."""
        assert SourceType.LOADED.value == "loaded"
        assert SourceType.GENERATED.value == "generated"
        assert SourceType.DERIVED.value == "derived"

    def test_source_type_is_string_enum(self):
        """Test that SourceType is a string enum."""
        assert isinstance(SourceType.LOADED, str)
        assert SourceType.LOADED == "loaded"


class TestProvenance:
    """Tests for Provenance class."""

    def test_generated_provenance(self):
        """Test creating generated provenance."""
        prov = Provenance.generated()
        assert prov.source_type == SourceType.GENERATED
        assert prov.skill_used is None
        assert prov.generation_params == {}

    def test_generated_with_skill(self):
        """Test generated provenance with skill name."""
        prov = Provenance.generated(skill_used="patientsim/demographics")
        assert prov.skill_used == "patientsim/demographics"

    def test_generated_with_params(self):
        """Test generated provenance with generation params."""
        prov = Provenance.generated(skill_used="test", age=45, gender="male")
        assert prov.generation_params == {"age": 45, "gender": "male"}

    def test_loaded_provenance(self):
        """Test creating loaded provenance."""
        prov = Provenance.loaded("CMS_SYNTHETIC_DATA")
        assert prov.source_type == SourceType.LOADED
        assert prov.source_system == "CMS_SYNTHETIC_DATA"

    def test_derived_provenance(self):
        """Test creating derived provenance."""
        source_ids = ["patient_001", "patient_002"]
        prov = Provenance.derived(source_ids)
        assert prov.source_type == SourceType.DERIVED
        assert prov.derived_from == source_ids

    def test_created_at_default(self):
        """Test that created_at is set by default."""
        before = datetime.now()
        prov = Provenance.generated()
        after = datetime.now()
        assert before <= prov.created_at <= after

    def test_default_values(self):
        """Test provenance default values."""
        prov = Provenance(source_type=SourceType.GENERATED)
        assert prov.source_system is None
        assert prov.skill_used is None
        assert prov.derived_from == []
        assert prov.generation_params == {}


class TestEntityWithProvenance:
    """Tests for EntityWithProvenance class."""

    def test_create_basic_entity(self):
        """Test creating basic entity with provenance."""
        entity = EntityWithProvenance(
            entity_id="patient_001",
            entity_type="Patient",
            data={"name": "John Doe", "age": 45},
        )
        assert entity.entity_id == "patient_001"
        assert entity.entity_type == "Patient"
        assert entity.data["name"] == "John Doe"
        assert entity.provenance.source_type == SourceType.GENERATED

    def test_create_with_custom_provenance(self):
        """Test creating entity with custom provenance."""
        prov = Provenance.loaded("external_ehr")
        entity = EntityWithProvenance(
            entity_id="member_001",
            entity_type="Member",
            data={"member_number": "123456789"},
            provenance=prov,
        )
        assert entity.provenance.source_type == SourceType.LOADED
        assert entity.provenance.source_system == "external_ehr"


class TestEntityFromModel:
    """Tests for EntityWithProvenance.from_model() method."""

    def test_from_pydantic_model(self):
        """Test creating entity from Pydantic model."""

        class PatientModel(BaseModel):
            name: str
            age: int
            gender: str

        patient = PatientModel(name="Jane Smith", age=30, gender="female")
        entity = EntityWithProvenance.from_model(
            model=patient,
            entity_id="patient_002",
            entity_type="Patient",
        )

        assert entity.entity_id == "patient_002"
        assert entity.entity_type == "Patient"
        assert entity.data["name"] == "Jane Smith"
        assert entity.data["age"] == 30
        assert entity.data["gender"] == "female"

    def test_from_model_with_provenance(self):
        """Test from_model with custom provenance."""

        class SimpleModel(BaseModel):
            value: int

        model = SimpleModel(value=42)
        prov = Provenance.derived(["source_1", "source_2"])

        entity = EntityWithProvenance.from_model(
            model=model,
            entity_id="derived_001",
            entity_type="Computed",
            provenance=prov,
        )

        assert entity.provenance.source_type == SourceType.DERIVED
        assert entity.provenance.derived_from == ["source_1", "source_2"]

    def test_from_dict(self):
        """Test creating entity from regular dict."""
        data = {"key1": "value1", "key2": 123}
        entity = EntityWithProvenance.from_model(
            model=data,
            entity_id="dict_001",
            entity_type="GenericData",
        )

        assert entity.data == data

    def test_from_non_iterable(self):
        """Test creating entity from non-dict, non-model value."""
        value = 12345
        entity = EntityWithProvenance.from_model(
            model=value,
            entity_id="simple_001",
            entity_type="SimpleValue",
        )

        assert entity.data == {"value": value}


class TestProvenanceSummary:
    """Tests for ProvenanceSummary class."""

    def test_empty_summary(self):
        """Test empty provenance summary."""
        summary = ProvenanceSummary()
        assert summary.total_entities == 0
        assert summary.by_source_type == {}
        assert summary.source_systems == []
        assert summary.skills_used == []

    def test_from_entities_empty(self):
        """Test summary from empty entities dict."""
        summary = ProvenanceSummary.from_entities({})
        assert summary.total_entities == 0

    def test_from_entities_with_generated(self):
        """Test summary with generated entities."""
        entities = {
            "patients": [
                EntityWithProvenance(
                    entity_id="p1",
                    entity_type="Patient",
                    data={},
                    provenance=Provenance.generated(skill_used="patientsim/demographics"),
                ),
                EntityWithProvenance(
                    entity_id="p2",
                    entity_type="Patient",
                    data={},
                    provenance=Provenance.generated(skill_used="patientsim/conditions"),
                ),
            ]
        }

        summary = ProvenanceSummary.from_entities(entities)
        assert summary.total_entities == 2
        assert summary.by_source_type["generated"] == 2
        assert "patientsim/demographics" in summary.skills_used
        assert "patientsim/conditions" in summary.skills_used

    def test_from_entities_with_loaded(self):
        """Test summary with loaded entities."""
        entities = {
            "members": [
                EntityWithProvenance(
                    entity_id="m1",
                    entity_type="Member",
                    data={},
                    provenance=Provenance.loaded("CMS_DATA"),
                ),
                EntityWithProvenance(
                    entity_id="m2",
                    entity_type="Member",
                    data={},
                    provenance=Provenance.loaded("NPPES"),
                ),
            ]
        }

        summary = ProvenanceSummary.from_entities(entities)
        assert summary.total_entities == 2
        assert summary.by_source_type["loaded"] == 2
        assert "CMS_DATA" in summary.source_systems
        assert "NPPES" in summary.source_systems

    def test_from_entities_mixed_types(self):
        """Test summary with mixed source types."""
        entities = {
            "data": [
                EntityWithProvenance(
                    entity_id="e1",
                    entity_type="Type1",
                    data={},
                    provenance=Provenance.generated(skill_used="skill1"),
                ),
                EntityWithProvenance(
                    entity_id="e2",
                    entity_type="Type2",
                    data={},
                    provenance=Provenance.loaded("system1"),
                ),
                EntityWithProvenance(
                    entity_id="e3",
                    entity_type="Type3",
                    data={},
                    provenance=Provenance.derived(["e1", "e2"]),
                ),
            ]
        }

        summary = ProvenanceSummary.from_entities(entities)
        assert summary.total_entities == 3
        assert summary.by_source_type["generated"] == 1
        assert summary.by_source_type["loaded"] == 1
        assert summary.by_source_type["derived"] == 1
        assert summary.skills_used == ["skill1"]
        assert summary.source_systems == ["system1"]

    def test_from_entities_multiple_collections(self):
        """Test summary across multiple entity collections."""
        entities = {
            "patients": [
                EntityWithProvenance(
                    entity_id="p1",
                    entity_type="Patient",
                    data={},
                    provenance=Provenance.generated(),
                ),
            ],
            "members": [
                EntityWithProvenance(
                    entity_id="m1",
                    entity_type="Member",
                    data={},
                    provenance=Provenance.generated(),
                ),
            ],
            "claims": [
                EntityWithProvenance(
                    entity_id="c1",
                    entity_type="Claim",
                    data={},
                    provenance=Provenance.generated(),
                ),
            ],
        }

        summary = ProvenanceSummary.from_entities(entities)
        assert summary.total_entities == 3

    def test_from_entities_skips_non_entity(self):
        """Test that non-EntityWithProvenance items are skipped."""
        # Mix of valid entities and non-entities
        entities = {
            "mixed": [
                EntityWithProvenance(
                    entity_id="e1",
                    entity_type="Valid",
                    data={},
                    provenance=Provenance.generated(),
                ),
                {"not": "an entity"},  # This should be skipped
                "just a string",  # This should be skipped
            ]
        }

        summary = ProvenanceSummary.from_entities(entities)
        assert summary.total_entities == 1

    def test_source_systems_sorted(self):
        """Test that source systems are sorted alphabetically."""
        entities = {
            "data": [
                EntityWithProvenance(
                    entity_id="e1",
                    entity_type="T",
                    data={},
                    provenance=Provenance.loaded("Zebra"),
                ),
                EntityWithProvenance(
                    entity_id="e2",
                    entity_type="T",
                    data={},
                    provenance=Provenance.loaded("Apple"),
                ),
            ]
        }

        summary = ProvenanceSummary.from_entities(entities)
        assert summary.source_systems == ["Apple", "Zebra"]

    def test_skills_used_sorted(self):
        """Test that skills are sorted alphabetically."""
        entities = {
            "data": [
                EntityWithProvenance(
                    entity_id="e1",
                    entity_type="T",
                    data={},
                    provenance=Provenance.generated(skill_used="z_skill"),
                ),
                EntityWithProvenance(
                    entity_id="e2",
                    entity_type="T",
                    data={},
                    provenance=Provenance.generated(skill_used="a_skill"),
                ),
            ]
        }

        summary = ProvenanceSummary.from_entities(entities)
        assert summary.skills_used == ["a_skill", "z_skill"]

    def test_deduplicates_source_systems(self):
        """Test that duplicate source systems are deduplicated."""
        entities = {
            "data": [
                EntityWithProvenance(
                    entity_id="e1",
                    entity_type="T",
                    data={},
                    provenance=Provenance.loaded("SAME_SYSTEM"),
                ),
                EntityWithProvenance(
                    entity_id="e2",
                    entity_type="T",
                    data={},
                    provenance=Provenance.loaded("SAME_SYSTEM"),
                ),
            ]
        }

        summary = ProvenanceSummary.from_entities(entities)
        assert summary.source_systems == ["SAME_SYSTEM"]
        assert len(summary.source_systems) == 1
