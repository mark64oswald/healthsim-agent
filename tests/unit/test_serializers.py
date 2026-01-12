"""Tests for state/serializers module."""

import pytest
from datetime import date, datetime
from uuid import uuid4

from healthsim_agent.state.serializers import (
    _get_nested,
    _parse_date,
    _parse_datetime,
    _resolve_relationship_code,
    serialize_patient,
    serialize_encounter,
    serialize_diagnosis,
    serialize_medication,
    serialize_lab_result,
    serialize_vital_sign,
    serialize_member,
    serialize_claim,
    serialize_prescription,
    serialize_subject,
    serialize_claim_line,
    serialize_pharmacy_claim,
    serialize_adverse_event,
    get_serializer,
    get_table_info,
    RELATIONSHIP_CODE_MAP,
    ENTITY_TABLE_MAP,
)


class TestGetNested:
    """Tests for _get_nested helper."""
    
    def test_simple_nested(self):
        """Get value from nested dict."""
        data = {"level1": {"level2": {"value": 42}}}
        result = _get_nested(data, "level1", "level2", "value")
        assert result == 42
    
    def test_missing_key(self):
        """Missing key returns default."""
        data = {"a": {"b": 1}}
        result = _get_nested(data, "a", "c", default="default")
        assert result == "default"
    
    def test_none_in_chain(self):
        """None in chain returns default."""
        data = {"a": None}
        result = _get_nested(data, "a", "b", default="default")
        assert result == "default"
    
    def test_non_dict_in_chain(self):
        """Non-dict in chain returns default."""
        data = {"a": "string"}
        result = _get_nested(data, "a", "b", default="default")
        assert result == "default"
    
    def test_single_key(self):
        """Single key lookup."""
        data = {"key": "value"}
        result = _get_nested(data, "key")
        assert result == "value"
    
    def test_default_none(self):
        """Default is None when not specified."""
        data = {}
        result = _get_nested(data, "missing")
        assert result is None


class TestParseDate:
    """Tests for _parse_date helper."""
    
    def test_parse_date_object(self):
        """Date object passes through."""
        d = date(2025, 1, 15)
        result = _parse_date(d)
        assert result == d
    
    def test_parse_datetime_object(self):
        """Datetime extracts date."""
        dt = datetime(2025, 1, 15, 10, 30)
        result = _parse_date(dt)
        assert result == date(2025, 1, 15)
    
    def test_parse_iso_string(self):
        """ISO date string parsed."""
        result = _parse_date("2025-01-15")
        assert result == date(2025, 1, 15)
    
    def test_parse_iso_with_time(self):
        """ISO datetime string extracts date."""
        result = _parse_date("2025-01-15T10:30:00")
        assert result == date(2025, 1, 15)
    
    def test_parse_with_z_suffix(self):
        """UTC Z suffix handled."""
        result = _parse_date("2025-01-15T10:30:00Z")
        assert result == date(2025, 1, 15)
    
    def test_parse_none(self):
        """None returns None."""
        result = _parse_date(None)
        assert result is None
    
    def test_parse_invalid_string(self):
        """Invalid string returns None."""
        result = _parse_date("not-a-date")
        assert result is None


class TestParseDatetime:
    """Tests for _parse_datetime helper."""
    
    def test_parse_datetime_object(self):
        """Datetime object passes through."""
        dt = datetime(2025, 1, 15, 10, 30)
        result = _parse_datetime(dt)
        assert result == dt
    
    def test_parse_iso_string(self):
        """ISO datetime string parsed."""
        result = _parse_datetime("2025-01-15T10:30:00")
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30
    
    def test_parse_with_z_suffix(self):
        """UTC Z suffix handled."""
        result = _parse_datetime("2025-01-15T10:30:00Z")
        assert result is not None
        assert result.year == 2025
    
    def test_parse_none(self):
        """None returns None."""
        result = _parse_datetime(None)
        assert result is None
    
    def test_parse_invalid_string(self):
        """Invalid string returns None."""
        result = _parse_datetime("not-a-datetime")
        assert result is None


class TestResolveRelationshipCode:
    """Tests for _resolve_relationship_code."""
    
    def test_explicit_code(self):
        """Explicit relationship_code used."""
        entity = {"relationship_code": "01"}
        result = _resolve_relationship_code(entity)
        assert result == "01"
    
    def test_relationship_self(self):
        """Self relationship maps to 18."""
        entity = {"relationship": "self"}
        result = _resolve_relationship_code(entity)
        assert result == "18"
    
    def test_relationship_spouse(self):
        """Spouse relationship maps to 01."""
        entity = {"relationship": "spouse"}
        result = _resolve_relationship_code(entity)
        assert result == "01"
    
    def test_relationship_child(self):
        """Child relationship maps to 19."""
        entity = {"relationship": "child"}
        result = _resolve_relationship_code(entity)
        assert result == "19"
    
    def test_relationship_normalized(self):
        """Relationship normalized before lookup."""
        entity = {"relationship": "Foster Child"}
        result = _resolve_relationship_code(entity)
        assert result == "10"
    
    def test_relationship_numeric_string(self):
        """Numeric string relationship passed through."""
        entity = {"relationship": "99"}
        result = _resolve_relationship_code(entity)
        assert result == "99"
    
    def test_default_to_self(self):
        """Default to 18 (self) when no relationship."""
        entity = {}
        result = _resolve_relationship_code(entity)
        assert result == "18"


class TestSerializePatient:
    """Tests for serialize_patient."""
    
    def test_basic_patient(self):
        """Serialize basic patient."""
        entity = {
            "id": "p-123",
            "given_name": "John",
            "family_name": "Doe",
            "birth_date": "1980-05-15",
            "gender": "M",
        }
        
        result = serialize_patient(entity)
        
        assert result["id"] == "p-123"
        assert result["given_name"] == "John"
        assert result["family_name"] == "Doe"
        assert result["birth_date"] == date(1980, 5, 15)
        assert result["gender"] == "M"
    
    def test_patient_with_nested_name(self):
        """Patient with nested name object."""
        entity = {
            "name": {
                "given": "Jane",
                "family": "Smith",
            }
        }
        
        result = serialize_patient(entity)
        
        assert result["given_name"] == "Jane"
        assert result["family_name"] == "Smith"
    
    def test_patient_with_provenance(self):
        """Patient with provenance metadata."""
        entity = {"given_name": "Test", "family_name": "User"}
        provenance = {"source_type": "import", "source_system": "ehr"}
        
        result = serialize_patient(entity, provenance)
        
        assert result["source_type"] == "import"
        assert result["source_system"] == "ehr"
    
    def test_patient_generates_id(self):
        """Missing ID generates UUID."""
        entity = {"given_name": "Test", "family_name": "User"}
        
        result = serialize_patient(entity)
        
        assert result["id"] is not None
        assert len(result["id"]) > 0
    
    def test_patient_with_address(self):
        """Patient with address fields."""
        entity = {
            "given_name": "Test",
            "family_name": "User",
            "address": {
                "line1": "123 Main St",
                "city": "Boston",
                "state": "MA",
            }
        }
        
        result = serialize_patient(entity)
        
        assert result["street_address"] == "123 Main St"
        assert result["city"] == "Boston"
        assert result["state"] == "MA"


class TestSerializeEncounter:
    """Tests for serialize_encounter."""
    
    def test_basic_encounter(self):
        """Serialize basic encounter."""
        entity = {
            "id": "enc-123",
            "patient_id": "p-456",
            "class_code": "I",
            "status": "active",
        }
        
        result = serialize_encounter(entity)
        
        assert result["encounter_id"] == "enc-123"
        assert result["patient_mrn"] == "p-456"
        assert result["class_code"] == "I"
        assert result["status"] == "active"
    
    def test_encounter_with_times(self):
        """Encounter with admission/discharge times."""
        entity = {
            "admission_time": "2025-01-15T08:00:00",
            "discharge_time": "2025-01-15T16:00:00",
        }
        
        result = serialize_encounter(entity)
        
        assert result["admission_time"].hour == 8
        assert result["discharge_time"].hour == 16


class TestSerializeDiagnosis:
    """Tests for serialize_diagnosis."""
    
    def test_basic_diagnosis(self):
        """Serialize basic diagnosis."""
        entity = {
            "code": "E11.9",
            "system": "ICD-10-CM",
            "description": "Type 2 diabetes mellitus",
        }
        
        result = serialize_diagnosis(entity)
        
        assert result["code"] == "E11.9"
        # Serializer keeps 'code' field, not 'code_system'
        assert result["description"] == "Type 2 diabetes mellitus"


class TestSerializeMedication:
    """Tests for serialize_medication."""
    
    def test_basic_medication(self):
        """Serialize basic medication."""
        entity = {
            "ndc": "00002-3227-30",
            "drug_name": "Metformin",
            "dosage": "500mg",
        }
        
        result = serialize_medication(entity)
        
        # Serializer maps 'ndc' to 'code' and 'drug_name' to 'name'
        assert result["code"] == "00002-3227-30"
        assert result["name"] == "Metformin"


class TestSerializeMember:
    """Tests for serialize_member."""
    
    def test_basic_member(self):
        """Serialize basic member."""
        entity = {
            "member_id": "m-123",
            "given_name": "John",
            "family_name": "Doe",
            "plan_id": "PLAN001",
        }
        
        result = serialize_member(entity)
        
        assert result["member_id"] == "m-123"
        assert result["plan_code"] == "PLAN001"  # plan_id maps to plan_code
    
    def test_member_with_relationship(self):
        """Member with subscriber relationship."""
        entity = {
            "member_id": "m-456",
            "relationship": "spouse",
        }
        
        result = serialize_member(entity)
        
        assert result["relationship_code"] == "01"


class TestSerializeSubject:
    """Tests for serialize_subject."""
    
    def test_basic_subject(self):
        """Serialize basic trial subject."""
        entity = {
            "subject_id": "subj-001",
            "protocol_id": "PROTO-2025-001",
            "site_id": "SITE01",
        }
        
        result = serialize_subject(entity)
        
        assert result["subject_id"] == "subj-001"
        assert result["study_id"] == "PROTO-2025-001"  # protocol_id maps to study_id
        assert result["site_id"] == "SITE01"


class TestSerializePharmacyClaim:
    """Tests for serialize_pharmacy_claim."""
    
    def test_basic_pharmacy_claim(self):
        """Serialize basic pharmacy claim."""
        entity = {
            "claim_id": "rx-claim-001",
            "member_id": "m-123",
            "ndc": "00002-3227-30",
            "quantity": 30,
        }
        
        result = serialize_pharmacy_claim(entity)
        
        assert result["claim_id"] == "rx-claim-001"
        assert result["member_id"] == "m-123"
        assert result["ndc"] == "00002-3227-30"


class TestGetSerializer:
    """Tests for get_serializer."""
    
    def test_get_patient_serializer(self):
        """Get patient serializer."""
        serializer = get_serializer("patient")
        assert serializer == serialize_patient
    
    def test_get_patients_serializer(self):
        """Get patients (plural) serializer."""
        serializer = get_serializer("patients")
        assert serializer == serialize_patient
    
    def test_get_encounter_serializer(self):
        """Get encounter serializer."""
        serializer = get_serializer("encounter")
        assert serializer == serialize_encounter
    
    def test_get_member_serializer(self):
        """Get member serializer."""
        serializer = get_serializer("member")
        assert serializer == serialize_member
    
    def test_get_subject_serializer(self):
        """Get subject serializer."""
        serializer = get_serializer("subject")
        assert serializer == serialize_subject
    
    def test_unknown_serializer_returns_none(self):
        """Unknown entity type returns None."""
        serializer = get_serializer("unknown_type")
        assert serializer is None


class TestGetTableInfo:
    """Tests for get_table_info."""
    
    def test_patient_table_info(self):
        """Get patient table info."""
        table_name, id_column = get_table_info("patient")
        assert table_name == "patients"
        assert id_column == "id"
    
    def test_encounter_table_info(self):
        """Get encounter table info."""
        table_name, id_column = get_table_info("encounter")
        assert table_name == "encounters"
        assert id_column == "encounter_id"
    
    def test_member_table_info(self):
        """Get member table info."""
        table_name, id_column = get_table_info("member")
        assert table_name == "members"
        assert id_column == "id"  # Members use 'id' as primary key
    
    def test_unknown_table_info(self):
        """Unknown type returns default pluralized name with 'id'."""
        table_name, id_column = get_table_info("unknown")
        # Function provides lenient default: pluralize and use 'id'
        assert table_name == "unknowns"
        assert id_column == "id"


class TestEntityTableMap:
    """Tests for ENTITY_TABLE_MAP constant."""
    
    def test_map_exists(self):
        """Map exists and is non-empty."""
        assert isinstance(ENTITY_TABLE_MAP, dict)
        assert len(ENTITY_TABLE_MAP) > 0
    
    def test_core_entities_mapped(self):
        """Core entity types are mapped."""
        assert "patient" in ENTITY_TABLE_MAP
        assert "encounter" in ENTITY_TABLE_MAP
        assert "member" in ENTITY_TABLE_MAP
        assert "subject" in ENTITY_TABLE_MAP


class TestRelationshipCodeMap:
    """Tests for RELATIONSHIP_CODE_MAP constant."""
    
    def test_map_exists(self):
        """Map exists and is non-empty."""
        assert isinstance(RELATIONSHIP_CODE_MAP, dict)
        assert len(RELATIONSHIP_CODE_MAP) > 0
    
    def test_common_relationships_mapped(self):
        """Common relationships are mapped."""
        assert "self" in RELATIONSHIP_CODE_MAP
        assert "spouse" in RELATIONSHIP_CODE_MAP
        assert "child" in RELATIONSHIP_CODE_MAP
        assert "dependent" in RELATIONSHIP_CODE_MAP
