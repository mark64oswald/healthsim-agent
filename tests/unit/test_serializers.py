"""
Comprehensive tests for serializers module.

Tests cover:
- Helper functions (_get_nested, _parse_date, _parse_datetime)
- Relationship code resolution
- Entity serializers (patient, encounter, diagnosis, member, claim, prescription, subject)
- Registry functions (get_serializer, get_table_info)
"""

import pytest
from datetime import date, datetime


class TestGetNested:
    """Tests for _get_nested helper function."""
    
    def test_single_key(self):
        """Test getting single key value."""
        from healthsim_agent.state.serializers import _get_nested
        
        obj = {'name': 'Test'}
        assert _get_nested(obj, 'name') == 'Test'
    
    def test_nested_keys(self):
        """Test getting nested value."""
        from healthsim_agent.state.serializers import _get_nested
        
        obj = {'person': {'name': {'first': 'John'}}}
        assert _get_nested(obj, 'person', 'name', 'first') == 'John'
    
    def test_missing_key_returns_default(self):
        """Test missing key returns default."""
        from healthsim_agent.state.serializers import _get_nested
        
        obj = {'name': 'Test'}
        assert _get_nested(obj, 'missing') is None
        assert _get_nested(obj, 'missing', default='default') == 'default'
    
    def test_none_obj_returns_default(self):
        """Test None object returns default."""
        from healthsim_agent.state.serializers import _get_nested
        
        assert _get_nested(None, 'key') is None
        assert _get_nested(None, 'key', default='x') == 'x'
    
    def test_intermediate_none_returns_default(self):
        """Test None intermediate value returns default."""
        from healthsim_agent.state.serializers import _get_nested
        
        obj = {'person': None}
        assert _get_nested(obj, 'person', 'name') is None


class TestParseDate:
    """Tests for _parse_date helper function."""
    
    def test_date_passthrough(self):
        """Test date object passes through."""
        from healthsim_agent.state.serializers import _parse_date
        
        d = date(2025, 1, 15)
        assert _parse_date(d) == d
    
    def test_datetime_extracts_date(self):
        """Test datetime extracts date portion."""
        from healthsim_agent.state.serializers import _parse_date
        
        dt = datetime(2025, 1, 15, 10, 30, 0)
        assert _parse_date(dt) == date(2025, 1, 15)
    
    def test_iso_string(self):
        """Test ISO format string parsing."""
        from healthsim_agent.state.serializers import _parse_date
        
        assert _parse_date('2025-01-15') == date(2025, 1, 15)
    
    def test_iso_string_with_time(self):
        """Test ISO format with time."""
        from healthsim_agent.state.serializers import _parse_date
        
        assert _parse_date('2025-01-15T10:30:00') == date(2025, 1, 15)
    
    def test_iso_string_with_z(self):
        """Test ISO format with Z timezone."""
        from healthsim_agent.state.serializers import _parse_date
        
        assert _parse_date('2025-01-15T10:30:00Z') == date(2025, 1, 15)
    
    def test_none_returns_none(self):
        """Test None returns None."""
        from healthsim_agent.state.serializers import _parse_date
        
        assert _parse_date(None) is None
    
    def test_invalid_string_returns_none(self):
        """Test invalid string returns None."""
        from healthsim_agent.state.serializers import _parse_date
        
        assert _parse_date('not-a-date') is None


class TestParseDatetime:
    """Tests for _parse_datetime helper function."""
    
    def test_datetime_passthrough(self):
        """Test datetime object passes through."""
        from healthsim_agent.state.serializers import _parse_datetime
        
        dt = datetime(2025, 1, 15, 10, 30, 0)
        assert _parse_datetime(dt) == dt
    
    def test_iso_string(self):
        """Test ISO format string parsing."""
        from healthsim_agent.state.serializers import _parse_datetime
        
        result = _parse_datetime('2025-01-15T10:30:00')
        assert result == datetime(2025, 1, 15, 10, 30, 0)
    
    def test_iso_string_with_z(self):
        """Test ISO format with Z timezone."""
        from healthsim_agent.state.serializers import _parse_datetime
        
        result = _parse_datetime('2025-01-15T10:30:00Z')
        assert result is not None
        assert result.year == 2025
    
    def test_none_returns_none(self):
        """Test None returns None."""
        from healthsim_agent.state.serializers import _parse_datetime
        
        assert _parse_datetime(None) is None
    
    def test_invalid_string_returns_none(self):
        """Test invalid string returns None."""
        from healthsim_agent.state.serializers import _parse_datetime
        
        assert _parse_datetime('not-a-datetime') is None


class TestRelationshipCodeMap:
    """Tests for RELATIONSHIP_CODE_MAP constant."""
    
    def test_constant_exists(self):
        """Test constant exists."""
        from healthsim_agent.state.serializers import RELATIONSHIP_CODE_MAP
        
        assert isinstance(RELATIONSHIP_CODE_MAP, dict)
    
    def test_self_maps_to_18(self):
        """Test 'self' maps to subscriber code '18'."""
        from healthsim_agent.state.serializers import RELATIONSHIP_CODE_MAP
        
        assert RELATIONSHIP_CODE_MAP['self'] == '18'
        assert RELATIONSHIP_CODE_MAP['subscriber'] == '18'
    
    def test_spouse_maps_to_01(self):
        """Test 'spouse' maps to code '01'."""
        from healthsim_agent.state.serializers import RELATIONSHIP_CODE_MAP
        
        assert RELATIONSHIP_CODE_MAP['spouse'] == '01'
    
    def test_child_maps_to_19(self):
        """Test 'child' maps to code '19'."""
        from healthsim_agent.state.serializers import RELATIONSHIP_CODE_MAP
        
        assert RELATIONSHIP_CODE_MAP['child'] == '19'


class TestResolveRelationshipCode:
    """Tests for _resolve_relationship_code function."""
    
    def test_explicit_code(self):
        """Test explicit code is used."""
        from healthsim_agent.state.serializers import _resolve_relationship_code
        
        entity = {'relationship_code': '01'}
        assert _resolve_relationship_code(entity) == '01'
    
    def test_relationship_string(self):
        """Test relationship string is mapped."""
        from healthsim_agent.state.serializers import _resolve_relationship_code
        
        entity = {'relationship': 'spouse'}
        assert _resolve_relationship_code(entity) == '01'
    
    def test_relationship_with_spaces(self):
        """Test relationship with spaces."""
        from healthsim_agent.state.serializers import _resolve_relationship_code
        
        entity = {'relationship': 'life partner'}
        assert _resolve_relationship_code(entity) == '53'
    
    def test_digit_relationship(self):
        """Test numeric relationship string."""
        from healthsim_agent.state.serializers import _resolve_relationship_code
        
        entity = {'relationship': '32'}
        assert _resolve_relationship_code(entity) == '32'
    
    def test_default_to_self(self):
        """Test defaults to '18' (self)."""
        from healthsim_agent.state.serializers import _resolve_relationship_code
        
        entity = {}
        assert _resolve_relationship_code(entity) == '18'


class TestSerializePatient:
    """Tests for serialize_patient function."""
    
    def test_basic_patient(self):
        """Test serializing basic patient."""
        from healthsim_agent.state.serializers import serialize_patient
        
        entity = {
            'patient_id': 'p-123',
            'given_name': 'John',
            'family_name': 'Doe',
            'birth_date': '1980-05-15',
            'gender': 'M',
        }
        
        result = serialize_patient(entity)
        
        assert result['id'] == 'p-123'
        assert result['given_name'] == 'John'
        assert result['family_name'] == 'Doe'
        assert result['birth_date'] == date(1980, 5, 15)
        assert result['gender'] == 'M'
    
    def test_nested_name(self):
        """Test patient with nested name object."""
        from healthsim_agent.state.serializers import serialize_patient
        
        entity = {
            'name': {
                'given': 'Jane',
                'family': 'Smith',
            }
        }
        
        result = serialize_patient(entity)
        
        assert result['given_name'] == 'Jane'
        assert result['family_name'] == 'Smith'
    
    def test_alternative_field_names(self):
        """Test alternative field names."""
        from healthsim_agent.state.serializers import serialize_patient
        
        entity = {
            'first_name': 'Bob',
            'last_name': 'Jones',
            'date_of_birth': '1990-03-20',
            'sex': 'M',
        }
        
        result = serialize_patient(entity)
        
        assert result['given_name'] == 'Bob'
        assert result['family_name'] == 'Jones'
        assert result['birth_date'] == date(1990, 3, 20)
        assert result['gender'] == 'M'
    
    def test_provenance(self):
        """Test provenance is included."""
        from healthsim_agent.state.serializers import serialize_patient
        
        entity = {'given_name': 'Test', 'family_name': 'User'}
        provenance = {
            'source_type': 'imported',
            'source_system': 'ehr',
            'skill_used': 'import-skill',
        }
        
        result = serialize_patient(entity, provenance)
        
        assert result['source_type'] == 'imported'
        assert result['source_system'] == 'ehr'
        assert result['skill_used'] == 'import-skill'
    
    def test_generates_id_if_missing(self):
        """Test UUID is generated if no ID provided."""
        from healthsim_agent.state.serializers import serialize_patient
        
        entity = {'given_name': 'Test', 'family_name': 'User'}
        
        result = serialize_patient(entity)
        
        assert result['id'] is not None
        assert len(result['id']) == 36  # UUID length


class TestSerializeEncounter:
    """Tests for serialize_encounter function."""
    
    def test_basic_encounter(self):
        """Test serializing basic encounter."""
        from healthsim_agent.state.serializers import serialize_encounter
        
        entity = {
            'encounter_id': 'e-123',
            'patient_mrn': 'MRN001',
            'class_code': 'IMP',
            'admission_time': '2025-01-10T08:00:00',
            'discharge_time': '2025-01-15T14:00:00',
        }
        
        result = serialize_encounter(entity)
        
        assert result['encounter_id'] == 'e-123'
        assert result['patient_mrn'] == 'MRN001'
        assert result['class_code'] == 'IMP'
        assert result['admission_time'] == datetime(2025, 1, 10, 8, 0, 0)


class TestSerializeMember:
    """Tests for serialize_member function."""
    
    def test_basic_member(self):
        """Test serializing basic member."""
        from healthsim_agent.state.serializers import serialize_member
        
        entity = {
            'member_id': 'm-123',
            'given_name': 'Alice',
            'family_name': 'Johnson',
            'relationship': 'self',
            'coverage_start': '2024-01-01',
        }
        
        result = serialize_member(entity)
        
        assert result['member_id'] == 'm-123'
        assert result['given_name'] == 'Alice'
        assert result['relationship_code'] == '18'
        assert result['coverage_start'] == date(2024, 1, 1)


class TestSerializePrescription:
    """Tests for serialize_prescription function."""
    
    def test_basic_prescription(self):
        """Test serializing basic prescription."""
        from healthsim_agent.state.serializers import serialize_prescription
        
        entity = {
            'prescription_id': 'rx-123',
            'drug_ndc': '12345-678-90',
            'drug_name': 'Metformin',
            'quantity': 90,
            'days_supply': 30,
        }
        
        result = serialize_prescription(entity)
        
        assert result['prescription_id'] == 'rx-123'
        assert result['drug_ndc'] == '12345-678-90'
        assert result['drug_name'] == 'Metformin'


class TestSerializerRegistry:
    """Tests for SERIALIZERS registry."""
    
    def test_registry_exists(self):
        """Test registry exists."""
        from healthsim_agent.state.serializers import SERIALIZERS
        
        assert isinstance(SERIALIZERS, dict)
    
    def test_patient_registered(self):
        """Test patient serializer registered."""
        from healthsim_agent.state.serializers import SERIALIZERS, serialize_patient
        
        assert SERIALIZERS['patient'] is serialize_patient
        assert SERIALIZERS['patients'] is serialize_patient
    
    def test_encounter_registered(self):
        """Test encounter serializer registered."""
        from healthsim_agent.state.serializers import SERIALIZERS, serialize_encounter
        
        assert SERIALIZERS['encounter'] is serialize_encounter


class TestGetSerializer:
    """Tests for get_serializer function."""
    
    def test_get_patient_serializer(self):
        """Test getting patient serializer."""
        from healthsim_agent.state.serializers import get_serializer, serialize_patient
        
        assert get_serializer('patient') is serialize_patient
    
    def test_get_unknown_returns_none(self):
        """Test unknown type returns None."""
        from healthsim_agent.state.serializers import get_serializer
        
        assert get_serializer('unknown_type') is None


class TestEntityTableMap:
    """Tests for ENTITY_TABLE_MAP constant."""
    
    def test_map_exists(self):
        """Test map exists."""
        from healthsim_agent.state.serializers import ENTITY_TABLE_MAP
        
        assert isinstance(ENTITY_TABLE_MAP, dict)
    
    def test_patient_mapping(self):
        """Test patient table mapping."""
        from healthsim_agent.state.serializers import ENTITY_TABLE_MAP
        
        assert ENTITY_TABLE_MAP['patient'] == ('patients', 'id')
        assert ENTITY_TABLE_MAP['patients'] == ('patients', 'id')
    
    def test_claim_mapping(self):
        """Test claim table mapping."""
        from healthsim_agent.state.serializers import ENTITY_TABLE_MAP
        
        assert ENTITY_TABLE_MAP['claim'] == ('claims', 'claim_id')


class TestGetTableInfo:
    """Tests for get_table_info function."""
    
    def test_get_patient_info(self):
        """Test getting patient table info."""
        from healthsim_agent.state.serializers import get_table_info
        
        table, id_col = get_table_info('patient')
        assert table == 'patients'
        assert id_col == 'id'
    
    def test_get_claim_info(self):
        """Test getting claim table info."""
        from healthsim_agent.state.serializers import get_table_info
        
        table, id_col = get_table_info('claim')
        assert table == 'claims'
        assert id_col == 'claim_id'
    
    def test_unknown_type_defaults(self):
        """Test unknown type gets default mapping."""
        from healthsim_agent.state.serializers import get_table_info
        
        table, id_col = get_table_info('widget')
        assert table == 'widgets'  # Pluralized
        assert id_col == 'id'  # Default
