"""Entity serialization between canonical models and database.

Handles the mapping between in-memory entity dicts and their database representations.
"""

from datetime import date, datetime
from typing import Any
from uuid import uuid4


def _get_nested(obj: dict, *keys, default=None) -> Any:
    """Safely get nested dictionary value."""
    for key in keys:
        if obj is None or not isinstance(obj, dict):
            return default
        obj = obj.get(key)
    return obj if obj is not None else default


def _parse_date(value: Any) -> date | None:
    """Parse date from various formats."""
    if value is None:
        return None
    # Check datetime BEFORE date (datetime is a subclass of date)
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        except ValueError:
            return None
    return None


def _parse_datetime(value: Any) -> datetime | None:
    """Parse datetime from various formats."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return None
    return None


# X12 270/271 Subscriber Relationship Codes
RELATIONSHIP_CODE_MAP = {
    'self': '18', 'subscriber': '18', 'spouse': '01', 'child': '19',
    'dependent': '19', 'parent': '32', 'grandparent': '04', 'grandchild': '05',
    'nephew_niece': '07', 'foster_child': '10', 'ward': '15', 'stepchild': '17',
    'employee': '20', 'other': '21', 'life_partner': '53', 'domestic_partner': '53',
}


def _resolve_relationship_code(entity: dict[str, Any]) -> str:
    """Resolve relationship code from various input formats."""
    code = entity.get('relationship_code')
    if code:
        return str(code)
    
    relationship = entity.get('relationship')
    if relationship:
        normalized = relationship.lower().strip().replace(' ', '_').replace('-', '_')
        if normalized in RELATIONSHIP_CODE_MAP:
            return RELATIONSHIP_CODE_MAP[normalized]
        if relationship.isdigit():
            return relationship
    
    return '18'


def serialize_patient(entity: dict[str, Any], provenance: dict | None = None) -> dict[str, Any]:
    """Prepare a patient entity for database insertion."""
    prov = provenance or entity.get('_provenance', {})
    
    given_name = (
        entity.get('given_name') or entity.get('first_name') or
        _get_nested(entity, 'name', 'given') or 'Unknown'
    )
    family_name = (
        entity.get('family_name') or entity.get('last_name') or
        _get_nested(entity, 'name', 'family') or 'Unknown'
    )
    
    return {
        'id': entity.get('patient_id') or entity.get('id') or str(uuid4()),
        'mrn': entity.get('mrn') or str(uuid4())[:8].upper(),
        'ssn': entity.get('ssn'),
        'given_name': given_name,
        'middle_name': entity.get('middle_name') or _get_nested(entity, 'name', 'middle'),
        'family_name': family_name,
        'suffix': entity.get('suffix') or _get_nested(entity, 'name', 'suffix'),
        'prefix': entity.get('prefix') or _get_nested(entity, 'name', 'prefix'),
        'birth_date': _parse_date(entity.get('birth_date') or entity.get('date_of_birth')),
        'gender': entity.get('gender') or entity.get('sex'),
        'race': entity.get('race'),
        'ethnicity': entity.get('ethnicity'),
        'language': entity.get('language', 'en'),
        'street_address': entity.get('street_address') or _get_nested(entity, 'address', 'line1'),
        'street_address_2': entity.get('street_address_2'),
        'city': entity.get('city') or _get_nested(entity, 'address', 'city'),
        'state': entity.get('state') or _get_nested(entity, 'address', 'state'),
        'postal_code': entity.get('postal_code') or entity.get('zip_code'),
        'country': entity.get('country', 'US'),
        'phone': entity.get('phone'),
        'phone_mobile': entity.get('phone_mobile'),
        'email': entity.get('email'),
        'deceased': entity.get('deceased', False),
        'death_date': _parse_date(entity.get('death_date')),
        'created_at': datetime.utcnow(),
        'source_type': prov.get('source_type', 'generated'),
        'source_system': prov.get('source_system', 'patientsim'),
        'skill_used': prov.get('skill_used'),
        'generation_seed': prov.get('seed'),
    }


def serialize_encounter(entity: dict[str, Any], provenance: dict | None = None) -> dict[str, Any]:
    """Prepare an encounter entity for database insertion."""
    prov = provenance or entity.get('_provenance', {})
    
    return {
        'encounter_id': entity.get('encounter_id') or entity.get('id') or str(uuid4()),
        'patient_mrn': entity.get('patient_mrn') or entity.get('patient_id'),
        'class_code': entity.get('class_code') or entity.get('class', 'O'),
        'status': entity.get('status', 'finished'),
        'admission_time': _parse_datetime(entity.get('admission_time')),
        'discharge_time': _parse_datetime(entity.get('discharge_time')),
        'facility': entity.get('facility'),
        'department': entity.get('department'),
        'room': entity.get('room'),
        'bed': entity.get('bed'),
        'chief_complaint': entity.get('chief_complaint'),
        'admitting_diagnosis': entity.get('admitting_diagnosis'),
        'discharge_disposition': entity.get('discharge_disposition'),
        'attending_physician': entity.get('attending_physician'),
        'admitting_physician': entity.get('admitting_physician'),
        'created_at': datetime.utcnow(),
        'source_type': prov.get('source_type', 'generated'),
        'source_system': prov.get('source_system', 'patientsim'),
        'skill_used': prov.get('skill_used'),
        'generation_seed': prov.get('seed'),
    }


def serialize_diagnosis(entity: dict[str, Any], provenance: dict | None = None) -> dict[str, Any]:
    """Prepare a diagnosis entity for database insertion."""
    prov = provenance or entity.get('_provenance', {})
    
    return {
        'id': entity.get('id') or str(uuid4()),
        'code': entity.get('code'),
        'description': entity.get('description') or entity.get('display'),
        'type': entity.get('type', 'final'),
        'patient_mrn': entity.get('patient_mrn') or entity.get('patient_id'),
        'encounter_id': entity.get('encounter_id'),
        'diagnosed_date': _parse_date(entity.get('diagnosed_date')),
        'resolved_date': _parse_date(entity.get('resolved_date')),
        'created_at': datetime.utcnow(),
        'source_type': prov.get('source_type', 'generated'),
        'source_system': prov.get('source_system', 'patientsim'),
        'skill_used': prov.get('skill_used'),
        'generation_seed': prov.get('seed'),
    }


def serialize_medication(entity: dict[str, Any], provenance: dict | None = None) -> dict[str, Any]:
    """Prepare a medication entity for database insertion."""
    prov = provenance or entity.get('_provenance', {})
    
    return {
        'id': entity.get('id') or str(uuid4()),
        'name': entity.get('name') or entity.get('drug_name'),
        'code': entity.get('code') or entity.get('ndc'),
        'dose': entity.get('dose') or entity.get('dosage'),
        'route': entity.get('route', 'oral'),
        'frequency': entity.get('frequency', 'daily'),
        'patient_mrn': entity.get('patient_mrn') or entity.get('patient_id'),
        'encounter_id': entity.get('encounter_id'),
        'start_date': _parse_datetime(entity.get('start_date')),
        'end_date': _parse_datetime(entity.get('end_date')),
        'status': entity.get('status', 'active'),
        'prescriber': entity.get('prescriber') or entity.get('prescriber_npi'),
        'indication': entity.get('indication'),
        'created_at': datetime.utcnow(),
        'source_type': prov.get('source_type', 'generated'),
        'source_system': prov.get('source_system', 'patientsim'),
        'skill_used': prov.get('skill_used'),
        'generation_seed': prov.get('seed'),
    }


def serialize_lab_result(entity: dict[str, Any], provenance: dict | None = None) -> dict[str, Any]:
    """Prepare a lab result entity for database insertion."""
    prov = provenance or entity.get('_provenance', {})
    
    return {
        'id': entity.get('id') or str(uuid4()),
        'test_name': entity.get('test_name') or entity.get('name'),
        'loinc_code': entity.get('loinc_code') or entity.get('code'),
        'value': entity.get('value'),
        'unit': entity.get('unit'),
        'reference_range': entity.get('reference_range'),
        'abnormal_flag': entity.get('abnormal_flag') or entity.get('interpretation'),
        'patient_mrn': entity.get('patient_mrn') or entity.get('patient_id'),
        'encounter_id': entity.get('encounter_id'),
        'collected_time': _parse_datetime(entity.get('collected_time') or entity.get('collection_date')),
        'resulted_time': _parse_datetime(entity.get('resulted_time') or entity.get('result_date')),
        'performing_lab': entity.get('performing_lab'),
        'ordering_provider': entity.get('ordering_provider'),
        'created_at': datetime.utcnow(),
        'source_type': prov.get('source_type', 'generated'),
        'source_system': prov.get('source_system', 'patientsim'),
        'skill_used': prov.get('skill_used'),
        'generation_seed': prov.get('seed'),
    }


def serialize_member(entity: dict[str, Any], provenance: dict | None = None) -> dict[str, Any]:
    """Prepare a member entity for database insertion."""
    prov = provenance or entity.get('_provenance', {})
    member_id = entity.get('member_id') or entity.get('id') or str(uuid4())
    
    return {
        'id': entity.get('id') or member_id,
        'member_id': member_id,
        'subscriber_id': entity.get('subscriber_id') or entity.get('patient_id'),
        'relationship_code': _resolve_relationship_code(entity),
        'ssn': entity.get('ssn'),
        'given_name': entity.get('given_name') or entity.get('first_name'),
        'middle_name': entity.get('middle_name'),
        'family_name': entity.get('family_name') or entity.get('last_name'),
        'birth_date': _parse_date(entity.get('birth_date')),
        'gender': entity.get('gender'),
        'street_address': entity.get('street_address'),
        'city': entity.get('city'),
        'state': entity.get('state'),
        'postal_code': entity.get('postal_code') or entity.get('zip_code'),
        'phone': entity.get('phone'),
        'email': entity.get('email'),
        'group_id': entity.get('group_id') or entity.get('group_number'),
        'plan_code': entity.get('plan_code') or entity.get('plan_id'),
        'coverage_start': _parse_date(entity.get('coverage_start') or entity.get('enrollment_start_date')),
        'coverage_end': _parse_date(entity.get('coverage_end') or entity.get('enrollment_end_date')),
        'pcp_npi': entity.get('pcp_npi'),
        'created_at': datetime.utcnow(),
        'source_type': prov.get('source_type', 'generated'),
        'source_system': prov.get('source_system', 'membersim'),
        'skill_used': prov.get('skill_used'),
        'generation_seed': prov.get('seed'),
    }


def serialize_claim(entity: dict[str, Any], provenance: dict | None = None) -> dict[str, Any]:
    """Prepare a claim entity for database insertion."""
    prov = provenance or entity.get('_provenance', {})
    
    return {
        'claim_id': entity.get('claim_id') or entity.get('id') or str(uuid4()),
        'member_id': entity.get('member_id'),
        'claim_type': entity.get('claim_type', 'professional'),
        'service_date': _parse_date(entity.get('service_date')),
        'admission_date': _parse_date(entity.get('admission_date')),
        'discharge_date': _parse_date(entity.get('discharge_date')),
        'provider_npi': entity.get('provider_npi'),
        'facility_npi': entity.get('facility_npi'),
        'total_charge': entity.get('total_charge'),
        'total_paid': entity.get('total_paid'),
        'patient_responsibility': entity.get('patient_responsibility'),
        'status': entity.get('status', 'paid'),
        'created_at': datetime.utcnow(),
        'source_type': prov.get('source_type', 'generated'),
        'source_system': prov.get('source_system', 'membersim'),
        'skill_used': prov.get('skill_used'),
        'generation_seed': prov.get('seed'),
    }


def serialize_prescription(entity: dict[str, Any], provenance: dict | None = None) -> dict[str, Any]:
    """Prepare a prescription entity for database insertion."""
    prov = provenance or entity.get('_provenance', {})
    
    return {
        'prescription_id': entity.get('prescription_id') or entity.get('id') or str(uuid4()),
        'rx_member_id': entity.get('rx_member_id') or entity.get('member_id'),
        'drug_ndc': entity.get('drug_ndc') or entity.get('ndc'),
        'drug_name': entity.get('drug_name'),
        'quantity': entity.get('quantity'),
        'days_supply': entity.get('days_supply'),
        'refills_authorized': entity.get('refills_authorized'),
        'refills_remaining': entity.get('refills_remaining'),
        'prescriber_npi': entity.get('prescriber_npi'),
        'written_date': _parse_date(entity.get('written_date')),
        'expiration_date': _parse_date(entity.get('expiration_date')),
        'status': entity.get('status', 'active'),
        'created_at': datetime.utcnow(),
        'source_type': prov.get('source_type', 'generated'),
        'source_system': prov.get('source_system', 'rxmembersim'),
        'skill_used': prov.get('skill_used'),
        'generation_seed': prov.get('seed'),
    }


def serialize_subject(entity: dict[str, Any], provenance: dict | None = None) -> dict[str, Any]:
    """Prepare a trial subject entity for database insertion."""
    prov = provenance or entity.get('_provenance', {})
    
    return {
        'subject_id': entity.get('subject_id') or entity.get('id') or str(uuid4()),
        'study_id': entity.get('study_id'),
        'site_id': entity.get('site_id'),
        'ssn': entity.get('ssn'),
        'screening_id': entity.get('screening_id'),
        'randomization_id': entity.get('randomization_id'),
        'arm': entity.get('arm'),
        'cohort': entity.get('cohort'),
        'consent_date': _parse_date(entity.get('consent_date')),
        'randomization_date': _parse_date(entity.get('randomization_date')),
        'status': entity.get('status', 'screening'),
        'created_at': datetime.utcnow(),
        'source_type': prov.get('source_type', 'generated'),
        'source_system': prov.get('source_system', 'trialsim'),
        'skill_used': prov.get('skill_used'),
        'generation_seed': prov.get('seed'),
    }


# Serializer Registry
SERIALIZERS = {
    'patient': serialize_patient, 'patients': serialize_patient,
    'encounter': serialize_encounter, 'encounters': serialize_encounter,
    'diagnosis': serialize_diagnosis, 'diagnoses': serialize_diagnosis,
    'medication': serialize_medication, 'medications': serialize_medication,
    'lab_result': serialize_lab_result, 'lab_results': serialize_lab_result,
    'member': serialize_member, 'members': serialize_member,
    'claim': serialize_claim, 'claims': serialize_claim,
    'prescription': serialize_prescription, 'prescriptions': serialize_prescription,
    'subject': serialize_subject, 'subjects': serialize_subject,
}

# Entity type to table name and ID column mapping
ENTITY_TABLE_MAP = {
    'patient': ('patients', 'id'), 'patients': ('patients', 'id'),
    'encounter': ('encounters', 'encounter_id'), 'encounters': ('encounters', 'encounter_id'),
    'diagnosis': ('diagnoses', 'id'), 'diagnoses': ('diagnoses', 'id'),
    'medication': ('medications', 'id'), 'medications': ('medications', 'id'),
    'lab_result': ('lab_results', 'id'), 'lab_results': ('lab_results', 'id'),
    'member': ('members', 'id'), 'members': ('members', 'id'),
    'claim': ('claims', 'claim_id'), 'claims': ('claims', 'claim_id'),
    'claim_line': ('claim_lines', 'id'), 'claim_lines': ('claim_lines', 'id'),
    'prescription': ('prescriptions', 'prescription_id'),
    'prescriptions': ('prescriptions', 'prescription_id'),
    'subject': ('subjects', 'subject_id'), 'subjects': ('subjects', 'subject_id'),
}


def get_serializer(entity_type: str):
    """Get serializer function for entity type."""
    return SERIALIZERS.get(entity_type)


def get_table_info(entity_type: str) -> tuple[str, str]:
    """Get table name and ID column for entity type."""
    return ENTITY_TABLE_MAP.get(entity_type, (f'{entity_type}s', 'id'))
