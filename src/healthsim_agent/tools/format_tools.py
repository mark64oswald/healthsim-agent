"""Format transformation tools for HealthSim Agent.

These tools transform cohort data into various healthcare data interchange formats.
"""

import json
from datetime import date, datetime
from typing import Any

from healthsim_agent.tools.base import ToolResult, ok, err
from healthsim_agent.tools.connection import get_manager

# Import models
from healthsim_agent.person import PersonName, Gender, Address
from healthsim_agent.products.patientsim.core.models import (
    Patient, Encounter, Diagnosis, VitalSign, LabResult,
    EncounterClass, EncounterStatus, DiagnosisType
)
from healthsim_agent.products.membersim.core.models import (
    Member, Plan, Claim, ClaimLine, ClaimStatus
)

# Import transformers
from healthsim_agent.products.patientsim.formats.fhir import FHIRTransformer
from healthsim_agent.products.patientsim.formats.ccda import CCDATransformer
from healthsim_agent.products.patientsim.formats.hl7v2 import HL7v2Generator
from healthsim_agent.products.membersim.formats.x12 import (
    X12Generator, EDI837PGenerator, EDI835Generator, EDI834Generator
)
from healthsim_agent.products.rxmembersim.formats.ncpdp import NCPDPScriptGenerator


# ============================================================================
# Helper Functions - Load Data from Database
# ============================================================================

def _load_cohort_data(cohort_id: str) -> dict[str, list[dict]] | None:
    """Load all entity data for a cohort from the database."""
    manager = get_manager()
    conn = manager.get_read_connection()
    
    # Check cohort exists
    result = conn.execute(
        "SELECT id FROM cohorts WHERE id = ? OR name = ?",
        [cohort_id, cohort_id]
    ).fetchone()
    
    if not result:
        return None
    
    actual_id = result[0]
    
    # Load all entities
    entities = conn.execute(
        "SELECT entity_type, entity_data FROM cohort_entities WHERE cohort_id = ?",
        [actual_id]
    ).fetchall()
    
    data: dict[str, list[dict]] = {}
    for entity_type, entity_data in entities:
        if entity_type not in data:
            data[entity_type] = []
        
        # Parse JSON if string
        if isinstance(entity_data, str):
            entity_data = json.loads(entity_data)
        data[entity_type].append(entity_data)
    
    return data


# ============================================================================
# Helper Functions - Convert Dict to Model
# ============================================================================

def _parse_date(value: Any) -> date | None:
    """Parse a date from various formats."""
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
        except:
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except:
                return None
    return None


def _parse_datetime(value: Any) -> datetime | None:
    """Parse a datetime from various formats."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except:
            return None
    return None


def _parse_gender(value: Any) -> Gender:
    """Parse gender from various formats."""
    if isinstance(value, Gender):
        return value
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ('m', 'male'):
            return Gender.MALE
        elif value_lower in ('f', 'female'):
            return Gender.FEMALE
        elif value_lower in ('o', 'other'):
            return Gender.OTHER
    return Gender.UNKNOWN


def _dict_to_patient(data: dict) -> Patient:
    """Convert a dictionary to a Patient model."""
    # Handle name - could be dict or already structured
    name_data = data.get('name', {})
    if isinstance(name_data, dict):
        name = PersonName(
            given_name=name_data.get('given_name', name_data.get('given', 'Unknown')),
            family_name=name_data.get('family_name', name_data.get('family', 'Unknown')),
            middle_name=name_data.get('middle_name'),
            prefix=name_data.get('prefix'),
            suffix=name_data.get('suffix'),
        )
    else:
        # Flat structure - name fields at top level
        name = PersonName(
            given_name=data.get('given_name', data.get('first_name', 'Unknown')),
            family_name=data.get('family_name', data.get('last_name', 'Unknown')),
            middle_name=data.get('middle_name'),
        )
    
    # Handle address
    address_data = data.get('address')
    address = None
    if address_data and isinstance(address_data, dict):
        address = Address(
            street=address_data.get('street', address_data.get('line', [''])[0] if isinstance(address_data.get('line'), list) else ''),
            city=address_data.get('city', ''),
            state=address_data.get('state', ''),
            postal_code=address_data.get('postal_code', address_data.get('zip', '')),
            country=address_data.get('country', 'US'),
        )
    
    return Patient(
        id=data.get('id', data.get('patient_id', '')),
        name=name,
        birth_date=_parse_date(data.get('birth_date', data.get('dob'))) or date(1970, 1, 1),
        gender=_parse_gender(data.get('gender', data.get('sex'))),
        address=address,
        mrn=data.get('mrn', data.get('id', '')),
        ssn=data.get('ssn'),
        race=data.get('race'),
        language=data.get('language', 'en'),
    )


def _dict_to_encounter(data: dict) -> Encounter:
    """Convert a dictionary to an Encounter model."""
    # Parse encounter class
    enc_class_str = data.get('encounter_class', data.get('class', 'O'))
    enc_class = EncounterClass.OUTPATIENT
    if enc_class_str in ('I', 'inpatient', 'INPATIENT'):
        enc_class = EncounterClass.INPATIENT
    elif enc_class_str in ('E', 'emergency', 'EMERGENCY'):
        enc_class = EncounterClass.EMERGENCY
    
    # Parse status
    status_str = data.get('status', 'finished')
    status = EncounterStatus.FINISHED
    for s in EncounterStatus:
        if s.value == status_str:
            status = s
            break
    
    return Encounter(
        id=data.get('id', data.get('encounter_id', '')),
        patient_id=data.get('patient_id', ''),
        encounter_class=enc_class,
        status=status,
        admission_time=_parse_datetime(data.get('admission_time', data.get('start_time'))),
        discharge_time=_parse_datetime(data.get('discharge_time', data.get('end_time'))),
        location=data.get('location', data.get('facility')),
        provider_id=data.get('provider_id', data.get('attending_provider')),
        reason=data.get('reason', data.get('chief_complaint')),
    )


def _dict_to_diagnosis(data: dict) -> Diagnosis:
    """Convert a dictionary to a Diagnosis model."""
    diag_type_str = data.get('type', data.get('diagnosis_type', 'final'))
    diag_type = DiagnosisType.FINAL
    for t in DiagnosisType:
        if t.value == diag_type_str:
            diag_type = t
            break
    
    return Diagnosis(
        id=data.get('id', data.get('diagnosis_id', '')),
        patient_id=data.get('patient_id', ''),
        encounter_id=data.get('encounter_id'),
        code=data.get('code', data.get('icd_code', '')),
        code_system=data.get('code_system', 'ICD-10-CM'),
        description=data.get('description', data.get('diagnosis_description', '')),
        type=diag_type,
        onset_date=_parse_date(data.get('onset_date')),
        resolved_date=_parse_date(data.get('resolved_date')),
    )


def _dict_to_vitalsign(data: dict) -> VitalSign:
    """Convert a dictionary to a VitalSign model."""
    from decimal import Decimal
    
    return VitalSign(
        id=data.get('id', data.get('vital_id', '')),
        patient_id=data.get('patient_id', ''),
        encounter_id=data.get('encounter_id'),
        recorded_at=_parse_datetime(data.get('recorded_at', data.get('timestamp'))) or datetime.now(),
        heart_rate=data.get('heart_rate', data.get('pulse')),
        systolic_bp=data.get('systolic_bp', data.get('systolic')),
        diastolic_bp=data.get('diastolic_bp', data.get('diastolic')),
        respiratory_rate=data.get('respiratory_rate', data.get('resp_rate')),
        temperature=Decimal(str(data['temperature'])) if data.get('temperature') else None,
        oxygen_saturation=data.get('oxygen_saturation', data.get('spo2')),
        height=Decimal(str(data['height'])) if data.get('height') else None,
        weight=Decimal(str(data['weight'])) if data.get('weight') else None,
    )


def _dict_to_lab(data: dict) -> LabResult:
    """Convert a dictionary to a LabResult model."""
    return LabResult(
        id=data.get('id', data.get('lab_id', '')),
        patient_id=data.get('patient_id', ''),
        encounter_id=data.get('encounter_id'),
        test_code=data.get('test_code', data.get('loinc_code', '')),
        test_name=data.get('test_name', data.get('test_description', '')),
        value=str(data.get('value', data.get('result', ''))),
        unit=data.get('unit', data.get('units', '')),
        reference_range=data.get('reference_range'),
        interpretation=data.get('interpretation', data.get('flag')),
        collected_at=_parse_datetime(data.get('collected_at', data.get('collection_time'))) or datetime.now(),
        resulted_at=_parse_datetime(data.get('resulted_at', data.get('result_time'))),
    )


def _dict_to_member(data: dict) -> Member:
    """Convert a dictionary to a Member model."""
    return Member(
        member_id=data.get('member_id', data.get('id', '')),
        subscriber_id=data.get('subscriber_id', data.get('member_id', '')),
        given_name=data.get('given_name', data.get('first_name', '')),
        family_name=data.get('family_name', data.get('last_name', '')),
        birth_date=_parse_date(data.get('birth_date', data.get('dob'))) or date(1970, 1, 1),
        gender=data.get('gender', 'U'),
        street_address=data.get('street_address', data.get('address', {}).get('street', '')),
        city=data.get('city', data.get('address', {}).get('city', '')),
        state=data.get('state', data.get('address', {}).get('state', '')),
        postal_code=data.get('postal_code', data.get('address', {}).get('zip', '')),
        phone=data.get('phone'),
        email=data.get('email'),
        group_id=data.get('group_id', 'GRP001'),
        plan_code=data.get('plan_code', 'PLN001'),
        relationship_code=data.get('relationship_code', '18'),  # Self
        coverage_start=_parse_date(data.get('coverage_start', data.get('effective_date'))) or date.today(),
        coverage_end=_parse_date(data.get('coverage_end', data.get('termination_date'))),
    )


def _dict_to_claim(data: dict) -> Claim:
    """Convert a dictionary to a Claim model."""
    from decimal import Decimal
    
    # Parse claim lines
    lines_data = data.get('lines', data.get('claim_lines', []))
    lines = []
    for i, line_data in enumerate(lines_data):
        lines.append(ClaimLine(
            line_number=line_data.get('line_number', i + 1),
            procedure_code=line_data.get('procedure_code', line_data.get('cpt_code', '')),
            procedure_modifier=line_data.get('procedure_modifier'),
            diagnosis_pointers=line_data.get('diagnosis_pointers', [1]),
            service_date=_parse_date(line_data.get('service_date')) or date.today(),
            units=line_data.get('units', 1),
            billed_amount=Decimal(str(line_data.get('billed_amount', line_data.get('charge', 0)))),
            allowed_amount=Decimal(str(line_data.get('allowed_amount', 0))),
            paid_amount=Decimal(str(line_data.get('paid_amount', 0))),
            place_of_service=line_data.get('place_of_service', '11'),
        ))
    
    # Parse status
    status_str = data.get('status', 'paid')
    status = ClaimStatus.PAID
    for s in ClaimStatus:
        if s.value == status_str:
            status = s
            break
    
    return Claim(
        claim_id=data.get('claim_id', data.get('id', '')),
        member_id=data.get('member_id', ''),
        service_date=_parse_date(data.get('service_date')) or date.today(),
        submission_date=_parse_date(data.get('submission_date')) or date.today(),
        provider_npi=data.get('provider_npi', data.get('npi', '')),
        provider_name=data.get('provider_name', ''),
        facility_name=data.get('facility_name'),
        status=status,
        claim_type=data.get('claim_type', 'professional'),
        total_billed=Decimal(str(data.get('total_billed', 0))),
        total_allowed=Decimal(str(data.get('total_allowed', 0))),
        total_paid=Decimal(str(data.get('total_paid', 0))),
        member_responsibility=Decimal(str(data.get('member_responsibility', 0))),
        lines=lines,
    )


# ============================================================================
# Format Transformation Functions
# ============================================================================

def transform_to_fhir(cohort_id: str, bundle_type: str = "collection") -> ToolResult:
    """Transform cohort data to FHIR R4 format.
    
    Args:
        cohort_id: ID or name of the cohort to transform
        bundle_type: Type of FHIR bundle (collection, batch, transaction)
    
    Returns:
        ToolResult with FHIR Bundle as dict
    """
    try:
        data = _load_cohort_data(cohort_id)
        if data is None:
            return err(f"Cohort not found: {cohort_id}")
        
        # Convert to models
        patients = [_dict_to_patient(d) for d in data.get('patient', data.get('patients', []))]
        encounters = [_dict_to_encounter(d) for d in data.get('encounter', data.get('encounters', []))]
        diagnoses = [_dict_to_diagnosis(d) for d in data.get('diagnosis', data.get('diagnoses', []))]
        vitals = [_dict_to_vitalsign(d) for d in data.get('vital_sign', data.get('vitals', []))]
        labs = [_dict_to_lab(d) for d in data.get('lab_result', data.get('labs', []))]
        
        if not patients and not encounters and not diagnoses:
            return err("No patient data found in cohort")
        
        # Transform
        transformer = FHIRTransformer()
        bundle = transformer.create_bundle(
            patients=patients or None,
            encounters=encounters or None,
            diagnoses=diagnoses or None,
            vitals=vitals or None,
            labs=labs or None,
            bundle_type=bundle_type,
        )
        
        return ok(
            data=bundle.model_dump(mode='json', exclude_none=True),
            message=f"Generated FHIR R4 bundle with {len(patients)} patients"
        )
        
    except Exception as e:
        return err(f"FHIR transformation failed: {str(e)}")


def transform_to_ccda(cohort_id: str, document_type: str = "ccd") -> ToolResult:
    """Transform cohort data to C-CDA format.
    
    Args:
        cohort_id: ID or name of the cohort to transform
        document_type: Type of C-CDA document (ccd, discharge_summary, progress_note)
    
    Returns:
        ToolResult with C-CDA XML string
    """
    try:
        data = _load_cohort_data(cohort_id)
        if data is None:
            return err(f"Cohort not found: {cohort_id}")
        
        # Convert to models
        patients = [_dict_to_patient(d) for d in data.get('patient', data.get('patients', []))]
        encounters = [_dict_to_encounter(d) for d in data.get('encounter', data.get('encounters', []))]
        diagnoses = [_dict_to_diagnosis(d) for d in data.get('diagnosis', data.get('diagnoses', []))]
        vitals = [_dict_to_vitalsign(d) for d in data.get('vital_sign', data.get('vitals', []))]
        labs = [_dict_to_lab(d) for d in data.get('lab_result', data.get('labs', []))]
        
        if not patients:
            return err("No patient data found in cohort")
        
        # Transform first patient (C-CDA is single-patient)
        transformer = CCDATransformer()
        ccda_xml = transformer.transform(
            patient=patients[0],
            encounters=encounters or None,
            diagnoses=diagnoses or None,
            vitals=vitals or None,
            labs=labs or None,
        )
        
        return ok(
            data={"xml": ccda_xml, "document_type": document_type},
            message=f"Generated C-CDA {document_type} document"
        )
        
    except Exception as e:
        return err(f"C-CDA transformation failed: {str(e)}")


def transform_to_hl7v2(cohort_id: str, message_type: str = "ADT_A01") -> ToolResult:
    """Transform cohort data to HL7v2 format.
    
    Args:
        cohort_id: ID or name of the cohort to transform
        message_type: Type of HL7v2 message (ADT_A01, ADT_A03, ADT_A08)
    
    Returns:
        ToolResult with list of HL7v2 message strings
    """
    try:
        data = _load_cohort_data(cohort_id)
        if data is None:
            return err(f"Cohort not found: {cohort_id}")
        
        # Convert to models
        patients = [_dict_to_patient(d) for d in data.get('patient', data.get('patients', []))]
        encounters = [_dict_to_encounter(d) for d in data.get('encounter', data.get('encounters', []))]
        diagnoses = [_dict_to_diagnosis(d) for d in data.get('diagnosis', data.get('diagnoses', []))]
        
        if not patients:
            return err("No patient data found in cohort")
        
        # Generate messages
        generator = HL7v2Generator()
        messages = []
        
        for patient in patients:
            # Find encounters for this patient
            patient_encounters = [e for e in encounters if e.patient_id == patient.id]
            patient_diagnoses = [d for d in diagnoses if d.patient_id == patient.id]
            
            # Generate message for each encounter (or one message if no encounters)
            if patient_encounters:
                for encounter in patient_encounters:
                    enc_diagnoses = [d for d in patient_diagnoses if d.encounter_id == encounter.id]
                    
                    if message_type == "ADT_A01":
                        msg = generator.generate_adt_a01(patient, encounter, enc_diagnoses or None)
                    elif message_type == "ADT_A03":
                        msg = generator.generate_adt_a03(patient, encounter, enc_diagnoses or None)
                    elif message_type == "ADT_A08":
                        msg = generator.generate_adt_a08(patient, encounter)
                    else:
                        msg = generator.generate_adt_a01(patient, encounter, enc_diagnoses or None)
                    
                    messages.append(msg)
            else:
                # Create minimal encounter for message
                encounter = Encounter(
                    id=f"ENC-{patient.id}",
                    patient_id=patient.id,
                    encounter_class=EncounterClass.OUTPATIENT,
                    status=EncounterStatus.FINISHED,
                )
                msg = generator.generate_adt_a01(patient, encounter, patient_diagnoses or None)
                messages.append(msg)
        
        return ok(
            data={"messages": messages, "message_type": message_type, "count": len(messages)},
            message=f"Generated {len(messages)} HL7v2 {message_type} messages"
        )
        
    except Exception as e:
        return err(f"HL7v2 transformation failed: {str(e)}")


def transform_to_x12(cohort_id: str, transaction_type: str = "837P") -> ToolResult:
    """Transform cohort data to X12 EDI format.
    
    Args:
        cohort_id: ID or name of the cohort to transform
        transaction_type: Type of X12 transaction (837P, 837I, 835, 834, 270, 271)
    
    Returns:
        ToolResult with X12 EDI content
    """
    try:
        data = _load_cohort_data(cohort_id)
        if data is None:
            return err(f"Cohort not found: {cohort_id}")
        
        # Convert to models
        members = [_dict_to_member(d) for d in data.get('member', data.get('members', []))]
        claims = [_dict_to_claim(d) for d in data.get('claim', data.get('claims', []))]
        
        if not members and not claims:
            return err("No member or claim data found in cohort")
        
        # Generate based on transaction type
        if transaction_type == "837P":
            if not claims:
                return err("837P requires claim data")
            generator = EDI837PGenerator()
            # Group claims by member
            edi_content = []
            for claim in claims:
                member = next((m for m in members if m.member_id == claim.member_id), None)
                if member:
                    edi = generator.generate(claim, member)
                    edi_content.append(edi)
            
            return ok(
                data={"transactions": edi_content, "type": "837P", "count": len(edi_content)},
                message=f"Generated {len(edi_content)} X12 837P transactions"
            )
        
        elif transaction_type == "835":
            if not claims:
                return err("835 requires claim data")
            generator = EDI835Generator()
            edi_content = []
            for claim in claims:
                edi = generator.generate(claim)
                edi_content.append(edi)
            
            return ok(
                data={"transactions": edi_content, "type": "835", "count": len(edi_content)},
                message=f"Generated {len(edi_content)} X12 835 transactions"
            )
        
        elif transaction_type == "834":
            if not members:
                return err("834 requires member data")
            generator = EDI834Generator()
            edi_content = generator.generate(members)
            
            return ok(
                data={"transaction": edi_content, "type": "834", "member_count": len(members)},
                message=f"Generated X12 834 with {len(members)} members"
            )
        
        else:
            return err(f"Unsupported X12 transaction type: {transaction_type}")
        
    except Exception as e:
        return err(f"X12 transformation failed: {str(e)}")


def transform_to_ncpdp(cohort_id: str, message_type: str = "NewRx") -> ToolResult:
    """Transform cohort data to NCPDP SCRIPT format.
    
    Args:
        cohort_id: ID or name of the cohort to transform
        message_type: Type of NCPDP message (NewRx, RxRenewal, RxChange)
    
    Returns:
        ToolResult with NCPDP XML content
    """
    try:
        data = _load_cohort_data(cohort_id)
        if data is None:
            return err(f"Cohort not found: {cohort_id}")
        
        # Look for prescription/rx data
        prescriptions = data.get('prescription', data.get('prescriptions', []))
        rx_claims = data.get('pharmacy_claim', data.get('rx_claims', []))
        
        if not prescriptions and not rx_claims:
            return err("No prescription or pharmacy claim data found in cohort")
        
        # Generate NCPDP messages
        generator = NCPDPScriptGenerator()
        messages = []
        
        for rx in (prescriptions or rx_claims):
            # Build message data structure
            msg_data = {
                'patient': {
                    'id': rx.get('patient_id', rx.get('member_id', '')),
                    'given_name': rx.get('patient_first_name', ''),
                    'family_name': rx.get('patient_last_name', ''),
                    'birth_date': rx.get('patient_dob', ''),
                    'gender': rx.get('patient_gender', 'U'),
                },
                'prescriber': {
                    'npi': rx.get('prescriber_npi', ''),
                    'name': rx.get('prescriber_name', ''),
                },
                'medication': {
                    'ndc': rx.get('ndc', rx.get('drug_ndc', '')),
                    'drug_name': rx.get('drug_name', ''),
                    'quantity': rx.get('quantity', 30),
                    'days_supply': rx.get('days_supply', 30),
                    'sig': rx.get('sig', rx.get('directions', '')),
                    'refills': rx.get('refills', 0),
                },
            }
            
            if message_type == "NewRx":
                xml = generator.generate_new_rx(msg_data)
            else:
                xml = generator.generate_new_rx(msg_data)  # Default to NewRx
            
            messages.append(xml)
        
        return ok(
            data={"messages": messages, "type": message_type, "count": len(messages)},
            message=f"Generated {len(messages)} NCPDP {message_type} messages"
        )
        
    except Exception as e:
        return err(f"NCPDP transformation failed: {str(e)}")


def transform_to_mimic(cohort_id: str) -> ToolResult:
    """Transform cohort data to MIMIC-III compatible format.
    
    Args:
        cohort_id: ID or name of the cohort to transform
    
    Returns:
        ToolResult with MIMIC-style tables as dict of lists
    """
    try:
        data = _load_cohort_data(cohort_id)
        if data is None:
            return err(f"Cohort not found: {cohort_id}")
        
        # Convert to models
        patients = [_dict_to_patient(d) for d in data.get('patient', data.get('patients', []))]
        encounters = [_dict_to_encounter(d) for d in data.get('encounter', data.get('encounters', []))]
        diagnoses = [_dict_to_diagnosis(d) for d in data.get('diagnosis', data.get('diagnoses', []))]
        vitals = [_dict_to_vitalsign(d) for d in data.get('vital_sign', data.get('vitals', []))]
        labs = [_dict_to_lab(d) for d in data.get('lab_result', data.get('labs', []))]
        
        if not patients:
            return err("No patient data found in cohort")
        
        # Build MIMIC-style tables
        mimic_patients = []
        mimic_admissions = []
        mimic_diagnoses = []
        mimic_chartevents = []
        mimic_labevents = []
        
        for idx, patient in enumerate(patients):
            subject_id = idx + 1000
            
            # PATIENTS table
            mimic_patients.append({
                "subject_id": subject_id,
                "gender": "M" if patient.gender == Gender.MALE else "F" if patient.gender == Gender.FEMALE else "U",
                "dob": patient.birth_date.isoformat() if patient.birth_date else None,
                "dod": patient.death_date.isoformat() if patient.death_date else None,
                "expire_flag": 1 if patient.deceased else 0,
            })
            
            # ADMISSIONS table
            patient_encounters = [e for e in encounters if e.patient_id == patient.id]
            for enc_idx, enc in enumerate(patient_encounters):
                hadm_id = (subject_id * 100) + enc_idx
                mimic_admissions.append({
                    "subject_id": subject_id,
                    "hadm_id": hadm_id,
                    "admittime": enc.admission_time.isoformat() if enc.admission_time else None,
                    "dischtime": enc.discharge_time.isoformat() if enc.discharge_time else None,
                    "admission_type": "EMERGENCY" if enc.encounter_class == EncounterClass.EMERGENCY else "ELECTIVE",
                    "admission_location": enc.location or "EMERGENCY ROOM",
                    "discharge_location": "HOME",
                })
                
                # DIAGNOSES_ICD table
                enc_diagnoses = [d for d in diagnoses if d.encounter_id == enc.id]
                for seq, diag in enumerate(enc_diagnoses):
                    mimic_diagnoses.append({
                        "subject_id": subject_id,
                        "hadm_id": hadm_id,
                        "seq_num": seq + 1,
                        "icd9_code": diag.code,  # MIMIC uses ICD-9, we use ICD-10
                    })
            
            # CHARTEVENTS (vitals)
            patient_vitals = [v for v in vitals if v.patient_id == patient.id]
            for vital in patient_vitals:
                if vital.heart_rate:
                    mimic_chartevents.append({
                        "subject_id": subject_id,
                        "charttime": vital.recorded_at.isoformat() if vital.recorded_at else None,
                        "itemid": 220045,  # Heart Rate
                        "value": str(vital.heart_rate),
                        "valuenum": vital.heart_rate,
                        "valueuom": "bpm",
                    })
                if vital.systolic_bp:
                    mimic_chartevents.append({
                        "subject_id": subject_id,
                        "charttime": vital.recorded_at.isoformat() if vital.recorded_at else None,
                        "itemid": 220179,  # Systolic BP
                        "value": str(vital.systolic_bp),
                        "valuenum": vital.systolic_bp,
                        "valueuom": "mmHg",
                    })
            
            # LABEVENTS
            patient_labs = [l for l in labs if l.patient_id == patient.id]
            for lab in patient_labs:
                mimic_labevents.append({
                    "subject_id": subject_id,
                    "charttime": lab.collected_at.isoformat() if lab.collected_at else None,
                    "itemid": lab.test_code,
                    "value": lab.value,
                    "valuenum": float(lab.value) if lab.value and lab.value.replace('.', '').isdigit() else None,
                    "valueuom": lab.unit,
                    "flag": lab.interpretation,
                })
        
        return ok(
            data={
                "PATIENTS": mimic_patients,
                "ADMISSIONS": mimic_admissions,
                "DIAGNOSES_ICD": mimic_diagnoses,
                "CHARTEVENTS": mimic_chartevents,
                "LABEVENTS": mimic_labevents,
            },
            message=f"Generated MIMIC-III tables: {len(mimic_patients)} patients, {len(mimic_admissions)} admissions"
        )
        
    except Exception as e:
        return err(f"MIMIC transformation failed: {str(e)}")


def list_output_formats() -> ToolResult:
    """List all available output formats.
    
    Returns:
        ToolResult with format catalog
    """
    formats = {
        "fhir_r4": {
            "name": "FHIR R4",
            "description": "HL7 FHIR R4 JSON bundles for interoperability",
            "entity_types": ["patient", "encounter", "diagnosis", "vital_sign", "lab_result"],
            "output": "JSON Bundle",
            "tool": "transform_to_fhir",
        },
        "ccda": {
            "name": "C-CDA",
            "description": "Consolidated Clinical Document Architecture XML",
            "entity_types": ["patient", "encounter", "diagnosis", "vital_sign", "lab_result"],
            "output": "XML Document",
            "tool": "transform_to_ccda",
        },
        "hl7v2": {
            "name": "HL7v2",
            "description": "HL7 Version 2.x messages (ADT, ORU)",
            "entity_types": ["patient", "encounter", "diagnosis"],
            "output": "Pipe-delimited messages",
            "tool": "transform_to_hl7v2",
        },
        "x12": {
            "name": "X12 EDI",
            "description": "HIPAA X12 transactions (837, 835, 834)",
            "entity_types": ["member", "claim"],
            "output": "EDI segments",
            "tool": "transform_to_x12",
        },
        "ncpdp_script": {
            "name": "NCPDP SCRIPT",
            "description": "NCPDP SCRIPT Standard for e-prescribing",
            "entity_types": ["prescription", "pharmacy_claim"],
            "output": "XML messages",
            "tool": "transform_to_ncpdp",
        },
        "mimic_iii": {
            "name": "MIMIC-III",
            "description": "MIMIC-III compatible table structure for research",
            "entity_types": ["patient", "encounter", "diagnosis", "vital_sign", "lab_result"],
            "output": "Table dictionaries",
            "tool": "transform_to_mimic",
        },
    }
    
    return ok(data=formats, message=f"Found {len(formats)} output formats")


# Export all tools
__all__ = [
    "transform_to_fhir",
    "transform_to_ccda", 
    "transform_to_hl7v2",
    "transform_to_x12",
    "transform_to_ncpdp",
    "transform_to_mimic",
    "list_output_formats",
]
