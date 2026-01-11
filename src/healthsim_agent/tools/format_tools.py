"""Format transformation tools for HealthSim Agent.

These tools transform entity data into various healthcare data interchange formats.
They accept EITHER:
  - A cohort_id string (loads data from database)
  - Direct data dict (uses data as-is)

This flexibility allows both database-backed workflows and direct generation workflows.
"""

import json
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Union

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
from healthsim_agent.products.patientsim.formats.ccda import CCDATransformer, CCDAConfig, DocumentType
from healthsim_agent.products.patientsim.formats.hl7v2 import HL7v2Generator
from healthsim_agent.products.membersim.formats.x12 import (
    X12Generator, EDI837PGenerator, EDI835Generator, EDI834Generator, Payment, LinePayment
)
from healthsim_agent.products.rxmembersim.formats.ncpdp.telecom import (
    NCPDPTelecomGenerator, PharmacyClaim
)


# ============================================================================
# Helper Functions - Load Data
# ============================================================================

def _load_cohort_data(cohort_id: str) -> dict[str, list[dict]] | None:
    """Load all entity data for a cohort from the database."""
    manager = get_manager()
    conn = manager.get_read_connection()
    
    result = conn.execute(
        "SELECT id FROM cohorts WHERE id = ? OR name = ?",
        [cohort_id, cohort_id]
    ).fetchone()
    
    if not result:
        return None
    
    actual_id = result[0]
    entities = conn.execute(
        "SELECT entity_type, entity_data FROM cohort_entities WHERE cohort_id = ?",
        [actual_id]
    ).fetchall()
    
    data: dict[str, list[dict]] = {}
    for entity_type, entity_data in entities:
        if entity_type not in data:
            data[entity_type] = []
        if isinstance(entity_data, str):
            entity_data = json.loads(entity_data)
        data[entity_type].append(entity_data)
    
    return data


def _resolve_data(data_or_cohort: Union[str, dict]) -> dict[str, list[dict]] | None:
    """Resolve input to data dict - handles both cohort_id strings and direct data."""
    if isinstance(data_or_cohort, str):
        return _load_cohort_data(data_or_cohort)
    elif isinstance(data_or_cohort, dict):
        return data_or_cohort
    return None


# ============================================================================
# Helper Functions - Parse Values
# ============================================================================

def _parse_date(value: Any) -> date | None:
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
    if isinstance(value, Gender):
        return value
    if isinstance(value, str):
        v = value.upper()
        if v in ('M', 'MALE'):
            return Gender.MALE
        elif v in ('F', 'FEMALE'):
            return Gender.FEMALE
        elif v in ('O', 'OTHER'):
            return Gender.OTHER
    return Gender.UNKNOWN


def _parse_encounter_class(value: Any) -> EncounterClass:
    if isinstance(value, EncounterClass):
        return value
    if isinstance(value, str):
        v = value.upper()
        if v in ('I', 'IMP', 'INPATIENT'):
            return EncounterClass.INPATIENT
        elif v in ('E', 'EMER', 'EMERGENCY'):
            return EncounterClass.EMERGENCY
        elif v in ('U', 'URGENT', 'URGENT_CARE'):
            return EncounterClass.URGENT_CARE
    return EncounterClass.OUTPATIENT


# ============================================================================
# Helper Functions - Convert Dict to Model
# ============================================================================

def _dict_to_patient(data: dict) -> Patient:
    """Convert dictionary to Patient model."""
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
        name = PersonName(
            given_name=data.get('given_name', data.get('first_name', 'Unknown')),
            family_name=data.get('family_name', data.get('last_name', 'Unknown')),
            middle_name=data.get('middle_name'),
        )
    
    address_data = data.get('address')
    address = None
    if address_data and isinstance(address_data, dict):
        address = Address(
            street=address_data.get('street_address', address_data.get('street', '')),
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
    """Convert dictionary to Encounter model (matching patientsim model)."""
    encounter_id = data.get('encounter_id', data.get('id', ''))
    patient_mrn = data.get('patient_mrn', data.get('patient_id', ''))
    class_code = _parse_encounter_class(
        data.get('class_code', data.get('encounter_class', data.get('class', 'O')))
    )
    
    status_str = data.get('status', 'finished')
    status = EncounterStatus.FINISHED
    for s in EncounterStatus:
        if s.value == status_str:
            status = s
            break
    
    admission_time = _parse_datetime(data.get('admission_time', data.get('start_time')))
    if admission_time is None:
        admission_time = datetime.now()
    
    return Encounter(
        encounter_id=encounter_id,
        patient_mrn=patient_mrn,
        class_code=class_code,
        status=status,
        admission_time=admission_time,
        discharge_time=_parse_datetime(data.get('discharge_time', data.get('end_time'))),
        facility=data.get('facility', data.get('location')),
        department=data.get('department'),
        chief_complaint=data.get('chief_complaint', data.get('reason')),
        attending_physician=data.get('attending_physician', data.get('provider_id')),
    )


def _dict_to_diagnosis(data: dict) -> Diagnosis:
    """Convert dictionary to Diagnosis model."""
    diag_type_str = data.get('type', data.get('diagnosis_type', 'final'))
    diag_type = DiagnosisType.FINAL
    for t in DiagnosisType:
        if t.value == diag_type_str:
            diag_type = t
            break
    
    diagnosed_date = _parse_date(data.get('diagnosed_date', data.get('onset_date')))
    if diagnosed_date is None:
        diagnosed_date = date.today()
    
    return Diagnosis(
        code=data.get('code', data.get('icd_code', '')),
        description=data.get('description', data.get('diagnosis_description', 'Unknown')),
        type=diag_type,
        patient_mrn=data.get('patient_mrn', data.get('patient_id', '')),
        encounter_id=data.get('encounter_id'),
        diagnosed_date=diagnosed_date,
        resolved_date=_parse_date(data.get('resolved_date')),
    )


def _dict_to_vitalsign(data: dict) -> VitalSign:
    """Convert dictionary to VitalSign model."""
    observation_time = _parse_datetime(data.get('observation_time', data.get('recorded_at')))
    if observation_time is None:
        observation_time = datetime.now()
    
    return VitalSign(
        patient_mrn=data.get('patient_mrn', data.get('patient_id', '')),
        encounter_id=data.get('encounter_id'),
        observation_time=observation_time,
        heart_rate=data.get('heart_rate', data.get('pulse')),
        systolic_bp=data.get('systolic_bp', data.get('systolic')),
        diastolic_bp=data.get('diastolic_bp', data.get('diastolic')),
        respiratory_rate=data.get('respiratory_rate', data.get('resp_rate')),
        temperature=Decimal(str(data['temperature'])) if data.get('temperature') else None,
        oxygen_saturation=data.get('oxygen_saturation', data.get('spo2')),
    )


def _dict_to_lab(data: dict) -> LabResult:
    """Convert dictionary to LabResult model."""
    collected_time = _parse_datetime(data.get('collected_time', data.get('collected_at')))
    if collected_time is None:
        collected_time = datetime.now()
    
    return LabResult(
        test_name=data.get('test_name', data.get('test_description', 'Unknown Test')),
        loinc_code=data.get('loinc_code', data.get('test_code')),
        value=str(data.get('value', data.get('result', ''))),
        unit=data.get('unit', data.get('units')),
        reference_range=data.get('reference_range'),
        abnormal_flag=data.get('abnormal_flag', data.get('interpretation')),
        patient_mrn=data.get('patient_mrn', data.get('patient_id', '')),
        encounter_id=data.get('encounter_id'),
        collected_time=collected_time,
    )


def _dict_to_member(data: dict) -> Member:
    """Convert dictionary to Member model."""
    address = data.get('address', {})
    return Member(
        member_id=data.get('member_id', data.get('id', '')),
        subscriber_id=data.get('subscriber_id', data.get('member_id', '')),
        given_name=data.get('given_name', data.get('first_name', '')),
        family_name=data.get('family_name', data.get('last_name', '')),
        birth_date=_parse_date(data.get('birth_date', data.get('dob'))) or date(1970, 1, 1),
        gender=data.get('gender', 'U'),
        street_address=data.get('street_address', address.get('street', '')),
        city=data.get('city', address.get('city', '')),
        state=data.get('state', address.get('state', '')),
        postal_code=data.get('postal_code', address.get('postal_code', '')),
        phone=data.get('phone'),
        email=data.get('email'),
        group_id=data.get('group_id', data.get('group_number', 'GRP001')),
        plan_code=data.get('plan_code', 'PLN001'),
        relationship_code=data.get('relationship_code', '18'),
        coverage_start=_parse_date(data.get('coverage_start')) or date.today(),
        coverage_end=_parse_date(data.get('coverage_end')),
    )


def _dict_to_claim(data: dict) -> Claim:
    """Convert dictionary to Claim model."""
    lines_data = data.get('lines', data.get('claim_lines', []))
    lines = []
    for i, line_data in enumerate(lines_data):
        lines.append(ClaimLine(
            line_number=line_data.get('line_number', i + 1),
            procedure_code=line_data.get('procedure_code', line_data.get('cpt_code', '')),
            procedure_modifier=line_data.get('procedure_modifier'),
            diagnosis_code=line_data.get('diagnosis_code'),
            diagnosis_pointers=line_data.get('diagnosis_pointers', [1]),
            service_date=_parse_date(line_data.get('service_date')) or date.today(),
            quantity=line_data.get('quantity', line_data.get('units', 1)),
            billed_amount=Decimal(str(line_data.get('billed_amount', 0))),
            allowed_amount=Decimal(str(line_data.get('allowed_amount', 0))),
            paid_amount=Decimal(str(line_data.get('paid_amount', 0))),
            place_of_service=line_data.get('place_of_service', '11'),
        ))
    
    status_val = data.get('status', 'paid')
    if isinstance(status_val, ClaimStatus):
        status = status_val
    elif isinstance(status_val, str):
        status = ClaimStatus.PAID
        for s in ClaimStatus:
            if s.value == status_val:
                status = s
                break
    else:
        status = ClaimStatus.PAID
    
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

def transform_to_fhir(data_or_cohort: Union[str, dict], bundle_type: str = "collection", as_eob: bool = False) -> ToolResult:
    """Transform data to FHIR R4 format.
    
    Supports both PatientSim clinical data and MemberSim financial data:
    - PatientSim: Patient, Encounter, Observation, DiagnosticReport resources
    - MemberSim: Coverage, Patient, Claim, ExplanationOfBenefit resources
    
    Args:
        data_or_cohort: Either a cohort ID string OR a data dictionary with entity lists
        bundle_type: Type of FHIR bundle (collection, batch, transaction)
        as_eob: For claims, generate ExplanationOfBenefit instead of Claim
    
    Returns:
        ToolResult with FHIR Bundle as dict
    """
    try:
        data = _resolve_data(data_or_cohort)
        if data is None:
            return err("No data found. Provide either a cohort ID or data dictionary.")
        
        # Check if this is MemberSim data (has members or claims)
        members_data = data.get('members', data.get('member', []))
        claims_data = data.get('claims', data.get('claim', []))
        
        if members_data or claims_data:
            # MemberSim FHIR transformation
            from healthsim_agent.products.membersim.formats.fhir import (
                MemberSimFHIRTransformer, create_fhir_bundle
            )
            
            members = [_dict_to_member(d) for d in members_data]
            claims = [_dict_to_claim(d) for d in claims_data]
            
            transformer = MemberSimFHIRTransformer()
            resources = []
            
            if members:
                member_bundle = transformer.transform_members(members, include_patient=True)
                resources.extend([e['resource'] for e in member_bundle.get('entry', [])])
            
            if claims:
                claims_bundle = transformer.transform_claims(claims, members, as_eob=as_eob)
                resources.extend([e['resource'] for e in claims_bundle.get('entry', [])])
            
            bundle = create_fhir_bundle(resources, bundle_type)
            
            resource_type = "ExplanationOfBenefit" if as_eob else "Claim"
            return ok(
                data=bundle,
                message=f"Generated FHIR R4 bundle with {len(members)} members, {len(claims)} {resource_type}s"
            )
        
        # PatientSim FHIR transformation (original behavior)
        patients = [_dict_to_patient(d) for d in data.get('patients', data.get('patient', []))]
        encounters = [_dict_to_encounter(d) for d in data.get('encounters', data.get('encounter', []))]
        diagnoses = [_dict_to_diagnosis(d) for d in data.get('diagnoses', data.get('diagnosis', []))]
        vitals = [_dict_to_vitalsign(d) for d in data.get('vitals', data.get('vital_sign', []))]
        labs = [_dict_to_lab(d) for d in data.get('labs', data.get('lab_result', []))]
        
        if not patients and not encounters and not diagnoses:
            return err("No patient data found. Requires patients, encounters, or diagnoses.")
        
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
            message=f"Generated FHIR R4 bundle with {len(patients)} patients, {len(encounters)} encounters"
        )
    except Exception as e:
        import traceback
        return err(f"FHIR transformation failed: {str(e)}\n{traceback.format_exc()}")


def transform_to_ccda(data_or_cohort: Union[str, dict], document_type: str = "ccd") -> ToolResult:
    """Transform data to C-CDA format.
    
    Args:
        data_or_cohort: Either a cohort ID string OR a data dictionary
        document_type: Type of C-CDA document (ccd, discharge_summary, progress_note)
    
    Returns:
        ToolResult with C-CDA XML string
    """
    try:
        data = _resolve_data(data_or_cohort)
        if data is None:
            return err("No data found. Provide either a cohort ID or data dictionary.")
        
        patients = [_dict_to_patient(d) for d in data.get('patients', data.get('patient', []))]
        encounters = [_dict_to_encounter(d) for d in data.get('encounters', data.get('encounter', []))]
        diagnoses = [_dict_to_diagnosis(d) for d in data.get('diagnoses', data.get('diagnosis', []))]
        vitals = [_dict_to_vitalsign(d) for d in data.get('vitals', data.get('vital_sign', []))]
        labs = [_dict_to_lab(d) for d in data.get('labs', data.get('lab_result', []))]
        
        if not patients:
            return err("No patient data found. C-CDA requires at least one patient.")
        
        # Map document_type string to enum
        doc_type_map = {
            "ccd": DocumentType.CCD,
            "discharge_summary": DocumentType.DISCHARGE_SUMMARY,
            "referral_note": DocumentType.REFERRAL_NOTE,
            "transfer_summary": DocumentType.TRANSFER_SUMMARY,
        }
        doc_type = doc_type_map.get(document_type.lower(), DocumentType.CCD)
        
        # Create default config
        config = CCDAConfig(
            document_type=doc_type,
            organization_name="HealthSim Generated",
            organization_oid="2.16.840.1.113883.3.9999",
            author_name="HealthSim Agent",
        )
        
        transformer = CCDATransformer(config)
        ccda_xml = transformer.transform(
            patient=patients[0],
            encounters=encounters or None,
            diagnoses=diagnoses or None,
            vitals=vitals or None,
            labs=labs or None,
        )
        
        return ok(
            data={"xml": ccda_xml, "document_type": document_type},
            message=f"Generated C-CDA {document_type} document for patient {patients[0].mrn}"
        )
    except Exception as e:
        import traceback
        return err(f"C-CDA transformation failed: {str(e)}\n{traceback.format_exc()}")


def transform_to_hl7v2(data_or_cohort: Union[str, dict], message_type: str = "ADT_A01") -> ToolResult:
    """Transform data to HL7v2 format.
    
    Args:
        data_or_cohort: Either a cohort ID string OR a data dictionary
        message_type: Type of HL7v2 message (ADT_A01, ADT_A03, ADT_A08)
    
    Returns:
        ToolResult with list of HL7v2 message strings
    """
    try:
        data = _resolve_data(data_or_cohort)
        if data is None:
            return err("No data found. Provide either a cohort ID or data dictionary.")
        
        patients = [_dict_to_patient(d) for d in data.get('patients', data.get('patient', []))]
        encounters = [_dict_to_encounter(d) for d in data.get('encounters', data.get('encounter', []))]
        diagnoses = [_dict_to_diagnosis(d) for d in data.get('diagnoses', data.get('diagnosis', []))]
        
        if not patients:
            return err("No patient data found. HL7v2 requires at least one patient.")
        
        generator = HL7v2Generator()
        messages = []
        
        for patient in patients:
            patient_encounters = [e for e in encounters 
                                  if e.patient_mrn == patient.mrn]
            patient_diagnoses = [d for d in diagnoses 
                                 if d.patient_mrn == patient.mrn]
            
            if patient_encounters:
                for encounter in patient_encounters:
                    enc_diagnoses = [d for d in patient_diagnoses if d.encounter_id == encounter.encounter_id]
                    if message_type == "ADT_A01":
                        msg = generator.generate_adt_a01(patient, encounter, enc_diagnoses or None)
                    elif message_type == "ADT_A03":
                        msg = generator.generate_adt_a03(patient, encounter, enc_diagnoses or None)
                    else:
                        msg = generator.generate_adt_a08(patient, encounter)
                    messages.append(msg)
            else:
                encounter = Encounter(
                    encounter_id=f"ENC-{patient.mrn}",
                    patient_mrn=patient.mrn,
                    class_code=EncounterClass.OUTPATIENT,
                    status=EncounterStatus.FINISHED,
                    admission_time=datetime.now(),
                )
                msg = generator.generate_adt_a01(patient, encounter, patient_diagnoses or None)
                messages.append(msg)
        
        return ok(
            data={"messages": messages, "message_type": message_type, "count": len(messages)},
            message=f"Generated {len(messages)} HL7v2 {message_type} messages"
        )
    except Exception as e:
        import traceback
        return err(f"HL7v2 transformation failed: {str(e)}\n{traceback.format_exc()}")


def transform_to_x12(data_or_cohort: Union[str, dict], transaction_type: str = "837P") -> ToolResult:
    """Transform data to X12 EDI format.
    
    Args:
        data_or_cohort: Either a cohort ID string OR a data dictionary
        transaction_type: Type of X12 transaction (837P, 837I, 835, 834, 270, 271)
    
    Returns:
        ToolResult with X12 EDI content
    """
    try:
        from healthsim_agent.products.membersim.formats.x12 import (
            EDI270Generator, EDI271Generator
        )
        
        data = _resolve_data(data_or_cohort)
        if data is None:
            return err("No data found. Provide either a cohort ID or data dictionary.")
        
        members = [_dict_to_member(d) for d in data.get('members', data.get('member', []))]
        claims = [_dict_to_claim(d) for d in data.get('claims', data.get('claim', []))]
        plans = data.get('plans', data.get('plan', []))
        
        if not members and not claims:
            return err("No member or claim data found. X12 requires members and/or claims.")
        
        if transaction_type in ("837P", "837I"):
            if not claims:
                return err(f"{transaction_type} requires claim data")
            generator = EDI837PGenerator()
            # Generator expects list of claims
            edi_content = generator.generate(claims)
            return ok(
                data={"transaction": edi_content, "type": transaction_type, "claim_count": len(claims)},
                message=f"Generated X12 {transaction_type} with {len(claims)} claims"
            )
        
        elif transaction_type == "835":
            if not claims:
                return err("835 requires claim data (remittance advice)")
            # Convert Claims to Payment objects
            payments = []
            for claim in claims:
                line_payments = []
                for line in claim.lines:
                    line_payments.append(LinePayment(
                        line_number=line.line_number,
                        charged_amount=line.billed_amount,
                        allowed_amount=line.allowed_amount,
                        paid_amount=line.paid_amount,
                        deductible_amount=Decimal("0"),
                        coinsurance_amount=Decimal("0"),
                        copay_amount=Decimal("0"),
                    ))
                payments.append(Payment(
                    payment_id=f"PAY-{claim.claim_id}",
                    claim_id=claim.claim_id,
                    check_number=f"CHK{claim.claim_id[:6]}",
                    payment_date=claim.service_date,
                    total_charged=claim.total_billed,
                    total_allowed=claim.total_allowed,
                    total_paid=claim.total_paid,
                    total_patient_responsibility=claim.member_responsibility,
                    line_payments=line_payments,
                ))
            generator = EDI835Generator()
            edi_content = generator.generate(payments)
            return ok(
                data={"transaction": edi_content, "type": "835", "claim_count": len(claims)},
                message=f"Generated X12 835 remittance with {len(claims)} claims"
            )
        
        elif transaction_type == "834":
            if not members:
                return err("834 requires member data (enrollment)")
            generator = EDI834Generator()
            edi_content = generator.generate(members)
            return ok(
                data={"transaction": edi_content, "type": "834", "member_count": len(members)},
                message=f"Generated X12 834 enrollment with {len(members)} members"
            )
        
        elif transaction_type == "270":
            if not members:
                return err("270 requires member data (eligibility inquiry)")
            generator = EDI270Generator()
            transactions = []
            for member in members:
                edi_content = generator.generate(member)
                transactions.append(edi_content)
            return ok(
                data={"transactions": transactions, "type": "270", "inquiry_count": len(members)},
                message=f"Generated X12 270 eligibility inquiries for {len(members)} members"
            )
        
        elif transaction_type == "271":
            if not members:
                return err("271 requires member data (eligibility response)")
            # Get plan data if available
            plan = None
            if plans:
                from healthsim_agent.products.membersim.core.models import Plan
                plan_data = plans[0] if isinstance(plans, list) else plans
                plan = Plan(
                    plan_code=plan_data.get('plan_code', plan_data.get('plan_id', 'PLAN001')),
                    plan_name=plan_data.get('plan_name', 'Standard Plan'),
                    plan_type=plan_data.get('plan_type', 'PPO'),
                    deductible_individual=Decimal(str(plan_data.get('deductible_individual', 500))),
                    deductible_family=Decimal(str(plan_data.get('deductible_family', 1500))),
                    oop_max_individual=Decimal(str(plan_data.get('oop_max_individual', 3000))),
                    oop_max_family=Decimal(str(plan_data.get('oop_max_family', 6000))),
                    copay_pcp=Decimal(str(plan_data.get('copay_pcp', 25))),
                    copay_specialist=Decimal(str(plan_data.get('copay_specialist', 50))),
                    copay_er=Decimal(str(plan_data.get('copay_er', 150))),
                    coinsurance=Decimal(str(plan_data.get('coinsurance', 0.2))),
                )
            else:
                # Create default plan
                from healthsim_agent.products.membersim.core.models import Plan
                plan = Plan(
                    plan_code="PLAN001",
                    plan_name="Standard PPO",
                    plan_type="PPO",
                    deductible_individual=Decimal("500"),
                    deductible_family=Decimal("1500"),
                    oop_max_individual=Decimal("3000"),
                    oop_max_family=Decimal("6000"),
                    copay_pcp=Decimal("25"),
                    copay_specialist=Decimal("50"),
                    copay_er=Decimal("150"),
                    coinsurance=Decimal("0.2"),
                )
            
            generator = EDI271Generator()
            transactions = []
            for member in members:
                edi_content = generator.generate(member, plan, is_eligible=member.is_active)
                transactions.append(edi_content)
            return ok(
                data={"transactions": transactions, "type": "271", "response_count": len(members)},
                message=f"Generated X12 271 eligibility responses for {len(members)} members"
            )
        
        else:
            return err(f"Unsupported X12 transaction type: {transaction_type}. Supported: 837P, 837I, 835, 834, 270, 271")
    except Exception as e:
        import traceback
        return err(f"X12 transformation failed: {str(e)}\n{traceback.format_exc()}")


def transform_to_ncpdp(data_or_cohort: Union[str, dict], message_type: str = "B1") -> ToolResult:
    """Transform data to NCPDP D.0 format.
    
    Args:
        data_or_cohort: Either a cohort ID string OR a data dictionary
        message_type: Type of NCPDP transaction (B1=billing, B2=reversal, B3=rebill)
    
    Returns:
        ToolResult with NCPDP D.0 transaction content
    """
    try:
        data = _resolve_data(data_or_cohort)
        if data is None:
            return err("No data found. Provide either a cohort ID or data dictionary.")
        
        rx_members = data.get('rx_members', data.get('rx_member', []))
        pharmacy_claims = data.get('pharmacy_claims', data.get('rx_claims', []))
        
        if not rx_members and not pharmacy_claims:
            return err("No RxMember or pharmacy claim data found. Use generate_rx_members first.")
        
        generator = NCPDPTelecomGenerator()
        transactions = []
        
        if pharmacy_claims:
            for claim_data in pharmacy_claims:
                claim = PharmacyClaim(
                    claim_id=claim_data.get('claim_id', ''),
                    bin=claim_data.get('bin', '610014'),
                    pcn=claim_data.get('pcn', 'RXTEST'),
                    group_number=claim_data.get('group_number', 'GRP001'),
                    cardholder_id=claim_data.get('cardholder_id', ''),
                    person_code=claim_data.get('person_code', '01'),
                    member_id=claim_data.get('member_id', ''),
                    ndc=claim_data.get('ndc', claim_data.get('drug_ndc', '')),
                    quantity_dispensed=Decimal(str(claim_data.get('quantity', 30))),
                    days_supply=claim_data.get('days_supply', 30),
                    daw_code=claim_data.get('daw_code', '0'),
                    prescription_number=claim_data.get('rx_number', claim_data.get('prescription_number', '')),
                    fill_number=claim_data.get('fill_number', 0),
                    prescriber_npi=claim_data.get('prescriber_npi', ''),
                    pharmacy_npi=claim_data.get('pharmacy_npi', ''),
                    service_date=claim_data.get('service_date', claim_data.get('fill_date', date.today())),
                    ingredient_cost_submitted=Decimal(str(claim_data.get('ingredient_cost', 0))),
                    dispensing_fee_submitted=Decimal(str(claim_data.get('dispensing_fee', 0))),
                    gross_amount_due=Decimal(str(claim_data.get('total_submitted', 0))),
                )
                
                if message_type == "B1":
                    tx = generator.generate_b1_request(claim)
                elif message_type == "B2":
                    tx = generator.generate_b2_reversal(claim, claim_data.get('original_auth', ''))
                elif message_type == "B3":
                    tx = generator.generate_b3_rebill(claim, claim_data.get('original_auth', ''))
                else:
                    tx = generator.generate_b1_request(claim)
                transactions.append(tx)
        elif rx_members:
            for member in rx_members:
                claim = PharmacyClaim(
                    claim_id=f"ELIG-{member.get('member_id', '')}",
                    bin=member.get('bin', '610014'),
                    pcn=member.get('pcn', 'RXTEST'),
                    group_number=member.get('group_number', 'GRP001'),
                    cardholder_id=member.get('cardholder_id', ''),
                    person_code=member.get('person_code', '01'),
                    member_id=member.get('member_id', ''),
                    ndc='00000000000',
                    quantity_dispensed=Decimal('1'),
                    days_supply=1,
                    prescription_number='ELIG-CHECK',
                    prescriber_npi='0000000000',
                    pharmacy_npi='0000000000',
                    service_date=date.today(),
                )
                tx = generator.generate_b1_request(claim)
                transactions.append({"member_id": member.get('member_id'), "eligibility_request": tx})
        
        return ok(
            data={"transactions": transactions, "type": message_type, "count": len(transactions)},
            message=f"Generated {len(transactions)} NCPDP D.0 {message_type} transactions"
        )
    except Exception as e:
        import traceback
        return err(f"NCPDP transformation failed: {str(e)}\n{traceback.format_exc()}")


def transform_to_mimic(data_or_cohort: Union[str, dict]) -> ToolResult:
    """Transform data to MIMIC-III compatible format.
    
    Args:
        data_or_cohort: Either a cohort ID string OR a data dictionary
    
    Returns:
        ToolResult with MIMIC-style tables as dict of lists
    """
    try:
        data = _resolve_data(data_or_cohort)
        if data is None:
            return err("No data found. Provide either a cohort ID or data dictionary.")
        
        patients = [_dict_to_patient(d) for d in data.get('patients', data.get('patient', []))]
        encounters = [_dict_to_encounter(d) for d in data.get('encounters', data.get('encounter', []))]
        diagnoses = [_dict_to_diagnosis(d) for d in data.get('diagnoses', data.get('diagnosis', []))]
        vitals = [_dict_to_vitalsign(d) for d in data.get('vitals', data.get('vital_sign', []))]
        labs = [_dict_to_lab(d) for d in data.get('labs', data.get('lab_result', []))]
        
        if not patients:
            return err("No patient data found. MIMIC export requires patients.")
        
        mimic_patients = []
        mimic_admissions = []
        mimic_diagnoses = []
        mimic_chartevents = []
        mimic_labevents = []
        
        for idx, patient in enumerate(patients):
            subject_id = idx + 1000
            mimic_patients.append({
                "subject_id": subject_id,
                "gender": "M" if patient.gender == Gender.MALE else "F" if patient.gender == Gender.FEMALE else "U",
                "dob": patient.birth_date.isoformat() if patient.birth_date else None,
                "dod": patient.death_date.isoformat() if patient.death_date else None,
                "expire_flag": 1 if patient.deceased else 0,
            })
            
            patient_encounters = [e for e in encounters if e.patient_mrn == patient.mrn]
            for enc_idx, enc in enumerate(patient_encounters):
                hadm_id = (subject_id * 100) + enc_idx
                mimic_admissions.append({
                    "subject_id": subject_id,
                    "hadm_id": hadm_id,
                    "admittime": enc.admission_time.isoformat() if enc.admission_time else None,
                    "dischtime": enc.discharge_time.isoformat() if enc.discharge_time else None,
                    "admission_type": "EMERGENCY" if enc.class_code == EncounterClass.EMERGENCY else "ELECTIVE",
                    "admission_location": enc.facility or "EMERGENCY ROOM",
                    "discharge_location": "HOME",
                })
                
                enc_diagnoses = [d for d in diagnoses if d.encounter_id == enc.encounter_id]
                for seq, diag in enumerate(enc_diagnoses):
                    mimic_diagnoses.append({
                        "subject_id": subject_id,
                        "hadm_id": hadm_id,
                        "seq_num": seq + 1,
                        "icd_code": diag.code,
                    })
            
            patient_vitals = [v for v in vitals if v.patient_mrn == patient.mrn]
            for vital in patient_vitals:
                if vital.heart_rate:
                    mimic_chartevents.append({
                        "subject_id": subject_id,
                        "charttime": vital.observation_time.isoformat() if vital.observation_time else None,
                        "itemid": 220045,
                        "value": str(vital.heart_rate),
                        "valuenum": vital.heart_rate,
                        "valueuom": "bpm",
                    })
                if vital.systolic_bp:
                    mimic_chartevents.append({
                        "subject_id": subject_id,
                        "charttime": vital.observation_time.isoformat() if vital.observation_time else None,
                        "itemid": 220179,
                        "value": str(vital.systolic_bp),
                        "valuenum": vital.systolic_bp,
                        "valueuom": "mmHg",
                    })
            
            patient_labs = [l for l in labs if l.patient_mrn == patient.mrn]
            for lab in patient_labs:
                try:
                    valuenum = float(lab.value) if lab.value else None
                except:
                    valuenum = None
                mimic_labevents.append({
                    "subject_id": subject_id,
                    "charttime": lab.collected_time.isoformat() if lab.collected_time else None,
                    "itemid": lab.loinc_code or "",
                    "value": lab.value,
                    "valuenum": valuenum,
                    "valueuom": lab.unit,
                    "flag": lab.abnormal_flag,
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
        import traceback
        return err(f"MIMIC transformation failed: {str(e)}\n{traceback.format_exc()}")


# =============================================================================
# TrialSim CDISC Transforms
# =============================================================================

def transform_to_sdtm(
    cohort_id: str | dict | None = None,
    data: dict | None = None,
    study_id: str = "STUDY01",
    domains: list[str] | None = None,
) -> ToolResult:
    """Transform TrialSim data to CDISC SDTM format.
    
    Args:
        cohort_id: Either cohort ID string OR data dictionary directly
        data: Data dictionary (alternative to cohort_id)
        study_id: Study identifier for SDTM
        domains: List of domains to export (DM, AE, EX, SV). Defaults to all.
    
    Returns:
        ToolResult with SDTM domain data
    """
    try:
        from healthsim_agent.products.trialsim.formats.sdtm import (
            SDTMExporter, ExportConfig, SDTMDomain
        )
        from healthsim_agent.products.trialsim.core.models import (
            Subject, Visit, AdverseEvent, Exposure
        )
        
        # Handle both cohort_id as string or dict
        cohort_data = None
        if isinstance(cohort_id, dict):
            cohort_data = cohort_id
        elif isinstance(cohort_id, str):
            cohort_data = _load_cohort_data(cohort_id)
        elif data is not None:
            cohort_data = data
        
        if not cohort_data:
            return err("No data found. Provide either a cohort ID or data dictionary.")
        
        # Extract trial entities
        subjects_data = cohort_data.get("subjects", cohort_data.get("subject", []))
        visits_data = cohort_data.get("visits", cohort_data.get("visit", []))
        ae_data = cohort_data.get("adverse_events", cohort_data.get("ae", []))
        exp_data = cohort_data.get("exposures", cohort_data.get("exposure", []))
        
        if not subjects_data:
            return err("No subject data found. Use generate_subjects first.")
        
        # Convert to models
        subjects = [_dict_to_subject(s) for s in subjects_data]
        visits = [_dict_to_visit(v) for v in visits_data] if visits_data else []
        adverse_events = [_dict_to_ae(a) for a in ae_data] if ae_data else []
        exposures = [_dict_to_exposure(e) for e in exp_data] if exp_data else []
        
        # Configure domains
        domain_list = None
        if domains:
            domain_map = {"DM": SDTMDomain.DM, "AE": SDTMDomain.AE, "EX": SDTMDomain.EX, "SV": SDTMDomain.SV}
            domain_list = [domain_map[d.upper()] for d in domains if d.upper() in domain_map]
        
        config = ExportConfig(study_id=study_id, domains=domain_list)
        exporter = SDTMExporter(config)
        
        result = exporter.export(
            subjects=subjects,
            visits=visits,
            adverse_events=adverse_events,
            exposures=exposures,
        )
        
        if not result.success:
            return err(f"SDTM export failed: {', '.join(result.errors)}")
        
        # Build output data from conversion results
        output_data = {}
        if subjects:
            output_data["DM"] = exporter._convert_dm(subjects)
        if adverse_events:
            output_data["AE"] = exporter._convert_ae(adverse_events, subjects)
        if exposures:
            output_data["EX"] = exporter._convert_ex(exposures, subjects)
        if visits:
            output_data["SV"] = exporter._convert_sv(visits, subjects)
        
        return ok(
            data=output_data,
            message=f"Generated SDTM domains: {', '.join(output_data.keys())} ({sum(len(v) for v in output_data.values())} records)"
        )
        
    except Exception as e:
        import traceback
        return err(f"SDTM transformation failed: {str(e)}\n{traceback.format_exc()}")


def transform_to_adam(
    cohort_id: str | dict | None = None,
    data: dict | None = None,
    study_id: str = "STUDY01",
    datasets: list[str] | None = None,
) -> ToolResult:
    """Transform TrialSim data to CDISC ADaM format.
    
    Args:
        cohort_id: Either cohort ID string OR data dictionary directly
        data: Data dictionary (alternative to cohort_id)
        study_id: Study identifier for ADaM
        datasets: List of datasets to export (ADSL, ADAE, ADEX). Defaults to all.
    
    Returns:
        ToolResult with ADaM dataset data
    """
    try:
        from healthsim_agent.products.trialsim.formats.adam import (
            ADAMExporter, ADAMExportConfig, ADAMDataset
        )
        from healthsim_agent.products.trialsim.core.models import (
            Subject, AdverseEvent, Exposure
        )
        
        # Handle both cohort_id as string or dict
        cohort_data = None
        if isinstance(cohort_id, dict):
            cohort_data = cohort_id
        elif isinstance(cohort_id, str):
            cohort_data = _load_cohort_data(cohort_id)
        elif data is not None:
            cohort_data = data
        
        if not cohort_data:
            return err("No data found. Provide either a cohort ID or data dictionary.")
        
        # Extract trial entities
        subjects_data = cohort_data.get("subjects", cohort_data.get("subject", []))
        ae_data = cohort_data.get("adverse_events", cohort_data.get("ae", []))
        exp_data = cohort_data.get("exposures", cohort_data.get("exposure", []))
        
        if not subjects_data:
            return err("No subject data found. Use generate_subjects first.")
        
        # Convert to models
        subjects = [_dict_to_subject(s) for s in subjects_data]
        adverse_events = [_dict_to_ae(a) for a in ae_data] if ae_data else []
        exposures = [_dict_to_exposure(e) for e in exp_data] if exp_data else []
        
        # Configure datasets
        dataset_list = None
        if datasets:
            ds_map = {"ADSL": ADAMDataset.ADSL, "ADAE": ADAMDataset.ADAE, "ADEX": ADAMDataset.ADEX}
            dataset_list = [ds_map[d.upper()] for d in datasets if d.upper() in ds_map]
        
        config = ADAMExportConfig(study_id=study_id, datasets=dataset_list)
        exporter = ADAMExporter(config)
        
        result = exporter.export(
            subjects=subjects,
            adverse_events=adverse_events,
            exposures=exposures,
        )
        
        if not result.success:
            return err(f"ADaM export failed: {', '.join(result.errors)}")
        
        return ok(
            data=result.data,
            message=f"Generated ADaM datasets: {', '.join(result.data.keys())} ({sum(len(v) for v in result.data.values())} records)"
        )
        
    except Exception as e:
        import traceback
        return err(f"ADaM transformation failed: {str(e)}\n{traceback.format_exc()}")


def _dict_to_subject(data: dict) -> "Subject":
    """Convert dict to Subject model."""
    from healthsim_agent.products.trialsim.core.models import Subject, ArmType, SubjectStatus
    from datetime import date
    
    # Parse dates
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        return date.fromisoformat(str(val)[:10])
    
    # Parse arm
    arm = None
    arm_val = data.get("arm")
    if arm_val:
        try:
            arm = ArmType(arm_val) if isinstance(arm_val, str) else arm_val
        except:
            arm = ArmType.TREATMENT
    
    return Subject(
        subject_id=data.get("subject_id", data.get("id", "")),
        protocol_id=data.get("protocol_id", "PROTOCOL-001"),
        site_id=data.get("site_id", "SITE01"),
        age=data.get("age", 50),
        sex=data.get("sex", "U"),
        race=data.get("race"),
        ethnicity=data.get("ethnicity"),
        screening_date=parse_date(data.get("screening_date")),
        randomization_date=parse_date(data.get("randomization_date")),
        arm=arm,
    )


def _dict_to_visit(data: dict) -> "Visit":
    """Convert dict to Visit model."""
    from healthsim_agent.products.trialsim.core.models import Visit, VisitType
    from datetime import date
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        return date.fromisoformat(str(val)[:10])
    
    visit_type = VisitType.SCHEDULED
    vt_val = data.get("visit_type")
    if vt_val:
        try:
            visit_type = VisitType(vt_val) if isinstance(vt_val, str) else vt_val
        except:
            pass
    
    return Visit(
        visit_id=data.get("visit_id", data.get("id", "")),
        subject_id=data.get("subject_id", ""),
        protocol_id=data.get("protocol_id", "PROTOCOL-001"),
        site_id=data.get("site_id", "SITE01"),
        visit_number=data.get("visit_number", 1),
        visit_name=data.get("visit_name", "Visit 1"),
        visit_type=visit_type,
        planned_date=parse_date(data.get("planned_date")),
        actual_date=parse_date(data.get("actual_date")),
    )


def _dict_to_ae(data: dict) -> "AdverseEvent":
    """Convert dict to AdverseEvent model."""
    from healthsim_agent.products.trialsim.core.models import (
        AdverseEvent, AESeverity, AECausality, AEOutcome
    )
    from datetime import date
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        return date.fromisoformat(str(val)[:10])
    
    # Parse enums with defaults
    severity = AESeverity.GRADE_2
    sev_val = data.get("severity")
    if sev_val:
        try:
            severity = AESeverity(sev_val) if isinstance(sev_val, str) else sev_val
        except:
            pass
    
    causality = AECausality.POSSIBLY
    caus_val = data.get("causality")
    if caus_val:
        try:
            causality = AECausality(caus_val) if isinstance(caus_val, str) else caus_val
        except:
            pass
    
    outcome = AEOutcome.RECOVERED
    out_val = data.get("outcome")
    if out_val:
        try:
            outcome = AEOutcome(out_val) if isinstance(out_val, str) else out_val
        except:
            pass
    
    # onset_date is required
    onset = parse_date(data.get("onset_date"))
    if onset is None:
        onset = date.today()
    
    return AdverseEvent(
        ae_id=data.get("ae_id", data.get("id", "")),
        subject_id=data.get("subject_id", ""),
        protocol_id=data.get("protocol_id", "PROTOCOL-001"),
        ae_term=data.get("ae_term", data.get("term", "Unknown")),
        system_organ_class=data.get("system_organ_class", data.get("soc")),
        severity=severity,
        is_serious=data.get("is_serious", False),
        causality=causality,
        outcome=outcome,
        onset_date=onset,
        resolution_date=parse_date(data.get("resolution_date")),
    )


def _dict_to_exposure(data: dict) -> "Exposure":
    """Convert dict to Exposure model."""
    from healthsim_agent.products.trialsim.core.models import Exposure
    from datetime import date
    
    def parse_date(val):
        if val is None:
            return None
        if isinstance(val, date):
            return val
        return date.fromisoformat(str(val)[:10])
    
    # start_date is required
    start = parse_date(data.get("start_date"))
    if start is None:
        start = date.today()
    
    return Exposure(
        exposure_id=data.get("exposure_id", data.get("id", "")),
        subject_id=data.get("subject_id", ""),
        protocol_id=data.get("protocol_id", "PROTOCOL-001"),
        drug_name=data.get("drug_name", "Study Drug"),
        dose=data.get("dose", 100),
        dose_unit=data.get("dose_unit", "mg"),
        route=data.get("route", "oral"),
        start_date=start,
        end_date=parse_date(data.get("end_date")),
    )


def list_output_formats() -> ToolResult:
    """List all available output formats with their requirements.
    
    Returns:
        ToolResult with format catalog
    """
    formats = {
        "fhir_r4": {
            "name": "FHIR R4",
            "description": "HL7 FHIR R4 JSON bundles for interoperability",
            "products": ["PatientSim", "MemberSim"],
            "entity_types": ["patients", "encounters", "diagnoses", "vitals", "labs", "members", "claims"],
            "output": "JSON Bundle",
            "tool": "transform_to_fhir",
            "options": {"as_eob": "For claims, generate ExplanationOfBenefit instead of Claim"},
        },
        "ccda": {
            "name": "C-CDA",
            "description": "Consolidated Clinical Document Architecture XML",
            "products": ["PatientSim"],
            "entity_types": ["patients", "encounters", "diagnoses", "vitals", "labs"],
            "output": "XML Document",
            "tool": "transform_to_ccda",
        },
        "hl7v2": {
            "name": "HL7v2",
            "description": "HL7 Version 2.x messages (ADT_A01, ADT_A03, ADT_A08)",
            "products": ["PatientSim"],
            "entity_types": ["patients", "encounters", "diagnoses"],
            "output": "Pipe-delimited messages",
            "tool": "transform_to_hl7v2",
        },
        "x12_837": {
            "name": "X12 837P/I",
            "description": "HIPAA X12 837 Professional/Institutional claims",
            "products": ["MemberSim"],
            "entity_types": ["members", "claims"],
            "output": "EDI segments",
            "tool": "transform_to_x12",
        },
        "x12_835": {
            "name": "X12 835",
            "description": "HIPAA X12 835 remittance advice",
            "products": ["MemberSim"],
            "entity_types": ["claims"],
            "output": "EDI segments",
            "tool": "transform_to_x12",
        },
        "x12_834": {
            "name": "X12 834",
            "description": "HIPAA X12 834 enrollment/benefit",
            "products": ["MemberSim"],
            "entity_types": ["members"],
            "output": "EDI segments",
            "tool": "transform_to_x12",
        },
        "x12_270": {
            "name": "X12 270",
            "description": "HIPAA X12 270 eligibility inquiry",
            "products": ["MemberSim"],
            "entity_types": ["members"],
            "output": "EDI segments",
            "tool": "transform_to_x12",
        },
        "x12_271": {
            "name": "X12 271",
            "description": "HIPAA X12 271 eligibility response",
            "products": ["MemberSim"],
            "entity_types": ["members", "plans"],
            "output": "EDI segments",
            "tool": "transform_to_x12",
        },
        "ncpdp_d0": {
            "name": "NCPDP D.0",
            "description": "NCPDP Telecommunication Standard for pharmacy claims",
            "products": ["RxMemberSim"],
            "entity_types": ["rx_members", "pharmacy_claims"],
            "output": "NCPDP D.0 transactions",
            "tool": "transform_to_ncpdp",
        },
        "mimic_iii": {
            "name": "MIMIC-III",
            "description": "MIMIC-III compatible table structure for research",
            "products": ["PatientSim"],
            "entity_types": ["patients", "encounters", "diagnoses", "vitals", "labs"],
            "output": "Table dictionaries",
            "tool": "transform_to_mimic",
        },
        "cdisc_sdtm": {
            "name": "CDISC SDTM",
            "description": "CDISC Study Data Tabulation Model for regulatory submissions",
            "products": ["TrialSim"],
            "entity_types": ["subjects", "visits", "adverse_events", "exposures"],
            "output": "Domain tables (DM, AE, EX, SV)",
            "tool": "transform_to_sdtm",
        },
        "cdisc_adam": {
            "name": "CDISC ADaM",
            "description": "CDISC Analysis Data Model for statistical analysis",
            "products": ["TrialSim"],
            "entity_types": ["subjects", "adverse_events", "exposures"],
            "output": "Analysis datasets (ADSL, ADAE, ADEX)",
            "tool": "transform_to_adam",
        },
    }
    return ok(data=formats, message=f"Found {len(formats)} output formats across 4 products")


# Export all tools
__all__ = [
    "transform_to_fhir",
    "transform_to_ccda", 
    "transform_to_hl7v2",
    "transform_to_x12",
    "transform_to_ncpdp",
    "transform_to_mimic",
    "transform_to_sdtm",
    "transform_to_adam",
    "list_output_formats",
]
