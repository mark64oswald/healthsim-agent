"""Format transformation tools for HealthSim Agent.

These tools transform generated healthcare data into standard interchange formats:
- transform_to_fhir: Convert patient data to FHIR R4 bundles
- transform_to_ccda: Convert patient data to C-CDA documents
- transform_to_hl7v2: Convert patient data to HL7v2 messages
- transform_to_x12: Convert claims/eligibility to X12 EDI
- transform_to_ncpdp: Convert prescriptions to NCPDP SCRIPT
- transform_to_mimic: Convert patient data to MIMIC-III format

All transformations work on cohort data loaded from the database.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional
import json

from .base import ToolResult, ok, err
from .connection import get_manager


# =============================================================================
# FHIR R4 Transformation
# =============================================================================

def transform_to_fhir(
    cohort_id: str,
    resource_types: Optional[List[str]] = None,
    bundle_type: str = "collection",
) -> ToolResult:
    """Transform cohort data to FHIR R4 JSON bundle.
    
    Args:
        cohort_id: ID of the cohort to transform
        resource_types: List of FHIR resource types to include
                       (default: all available - Patient, Condition, 
                        MedicationRequest, Observation, Encounter)
        bundle_type: FHIR bundle type (collection, transaction, batch)
        
    Returns:
        ToolResult with FHIR R4 Bundle JSON
    """
    try:
        from healthsim_agent.products.patientsim.formats.fhir import FHIRTransformer
        from healthsim_agent.products.patientsim.core.models import (
            Patient, Encounter, Diagnosis, LabResult, VitalSign
        )
        
        # Load cohort data
        cohort_data = _load_cohort_data(cohort_id)
        if cohort_data.get("error"):
            return err(cohort_data["error"])
        
        transformer = FHIRTransformer()
        
        # Convert dict data to model objects
        patients_raw = cohort_data.get("patients", [])
        if not patients_raw:
            return err("No patients found in cohort")
        
        # Build bundle entries
        entries = []
        
        for p in patients_raw:
            patient = _dict_to_patient(p)
            resource = transformer.transform_patient(patient)
            entries.append({
                "fullUrl": f"urn:uuid:{resource.id}",
                "resource": resource.model_dump(by_alias=True, exclude_none=True),
            })
        
        for e in cohort_data.get("encounters", []):
            encounter = _dict_to_encounter(e)
            resource = transformer.transform_encounter(encounter)
            entries.append({
                "fullUrl": f"urn:uuid:{resource.id}",
                "resource": resource.model_dump(by_alias=True, exclude_none=True),
            })
        
        for d in cohort_data.get("diagnoses", []):
            diagnosis = _dict_to_diagnosis(d)
            resource = transformer.transform_condition(diagnosis)
            entries.append({
                "fullUrl": f"urn:uuid:{resource.id}",
                "resource": resource.model_dump(by_alias=True, exclude_none=True),
            })
        
        bundle = {
            "resourceType": "Bundle",
            "id": cohort_id,
            "type": bundle_type,
            "timestamp": datetime.now().isoformat(),
            "entry": entries,
        }
        
        return ok(
            data=bundle,
            message=f"Generated FHIR R4 {bundle_type} bundle with {len(patients_raw)} patients",
            format="fhir_r4",
        )
        
    except ImportError as e:
        return err(f"FHIR transformer not available: {e}")
    except Exception as e:
        return err(f"FHIR transformation failed: {e}")


# =============================================================================
# C-CDA Transformation
# =============================================================================

def transform_to_ccda(
    cohort_id: str,
    patient_id: Optional[str] = None,
    document_type: str = "CCD",
    organization_name: str = "HealthSim Generated",
    organization_oid: str = "2.16.840.1.113883.3.9999",
) -> ToolResult:
    """Transform patient data to C-CDA XML document.
    
    Args:
        cohort_id: ID of the cohort
        patient_id: Specific patient MRN (generates all if not specified)
        document_type: CCD, DISCHARGE_SUMMARY, REFERRAL_NOTE, TRANSFER_SUMMARY
        organization_name: Name of generating organization
        organization_oid: OID of generating organization
        
    Returns:
        ToolResult with C-CDA XML document(s)
    """
    try:
        from healthsim_agent.products.patientsim.formats.ccda import (
            CCDATransformer,
            CCDAConfig,
            DocumentType,
        )
        from healthsim_agent.products.patientsim.core.models import (
            Patient, Diagnosis, VitalSign, LabResult
        )
        
        # Map document type string to enum
        doc_type_map = {
            "CCD": DocumentType.CCD,
            "DISCHARGE_SUMMARY": DocumentType.DISCHARGE_SUMMARY,
            "REFERRAL_NOTE": DocumentType.REFERRAL_NOTE,
            "TRANSFER_SUMMARY": DocumentType.TRANSFER_SUMMARY,
        }
        doc_type = doc_type_map.get(document_type.upper(), DocumentType.CCD)
        
        # Load cohort data
        cohort_data = _load_cohort_data(cohort_id, patient_id)
        if cohort_data.get("error"):
            return err(cohort_data["error"])
        
        # Configure transformer
        config = CCDAConfig(
            document_type=doc_type,
            organization_name=organization_name,
            organization_oid=organization_oid,
        )
        transformer = CCDATransformer(config)
        
        patients_raw = cohort_data.get("patients", [])
        if not patients_raw:
            return err("No patients found in cohort")
        
        # Generate documents
        documents = []
        for p in patients_raw:
            patient = _dict_to_patient(p)
            diagnoses = [_dict_to_diagnosis(d) for d in _filter_for_patient(cohort_data.get("diagnoses", []), p)]
            vitals = [_dict_to_vitalsign(v) for v in _filter_for_patient(cohort_data.get("vitals", []), p)]
            labs = [_dict_to_lab(l) for l in _filter_for_patient(cohort_data.get("labs", []), p)]
            
            xml = transformer.transform(
                patient=patient,
                diagnoses=diagnoses,
                medications=[],  # TODO: Add medications
                vitals=vitals,
                labs=labs,
            )
            mrn = p.get("mrn", "unknown")
            documents.append({
                "patient_mrn": mrn,
                "document_type": document_type,
                "xml": xml,
            })
        
        return ok(
            data=documents if len(documents) > 1 else documents[0],
            message=f"Generated {len(documents)} C-CDA {document_type} document(s)",
            format="ccda",
        )
        
    except ImportError as e:
        return err(f"C-CDA transformer not available: {e}")
    except Exception as e:
        return err(f"C-CDA transformation failed: {e}")


# =============================================================================
# HL7v2 Transformation
# =============================================================================

def transform_to_hl7v2(
    cohort_id: str,
    message_type: str = "ADT_A01",
    patient_id: Optional[str] = None,
) -> ToolResult:
    """Transform patient data to HL7v2 messages.
    
    Args:
        cohort_id: ID of the cohort
        message_type: HL7v2 message type (ADT_A01, ORU_R01, etc.)
        patient_id: Specific patient MRN (generates all if not specified)
        
    Returns:
        ToolResult with HL7v2 message(s)
    """
    try:
        from healthsim_agent.products.patientsim.formats.hl7v2 import (
            HL7v2Generator,
            MessageType,
        )
        
        # Map message type string to enum
        msg_type_map = {
            "ADT_A01": MessageType.ADT_A01,
            "ADT_A04": MessageType.ADT_A04,
            "ADT_A08": MessageType.ADT_A08,
            "ORU_R01": MessageType.ORU_R01,
        }
        msg_type = msg_type_map.get(message_type.upper(), MessageType.ADT_A01)
        
        # Load cohort data
        cohort_data = _load_cohort_data(cohort_id, patient_id)
        if cohort_data.get("error"):
            return err(cohort_data["error"])
        
        generator = HL7v2Generator()
        
        patients_raw = cohort_data.get("patients", [])
        if not patients_raw:
            return err("No patients found in cohort")
        
        messages = []
        for p in patients_raw:
            patient = _dict_to_patient(p)
            msg = generator.generate(patient, msg_type)
            mrn = p.get("mrn", "unknown")
            messages.append({
                "patient_mrn": mrn,
                "message_type": message_type,
                "message": msg,
            })
        
        return ok(
            data=messages if len(messages) > 1 else messages[0],
            message=f"Generated {len(messages)} HL7v2 {message_type} message(s)",
            format="hl7v2",
        )
        
    except ImportError as e:
        return err(f"HL7v2 generator not available: {e}")
    except Exception as e:
        return err(f"HL7v2 transformation failed: {e}")


# =============================================================================
# X12 EDI Transformation
# =============================================================================

def transform_to_x12(
    cohort_id: str,
    transaction_type: str = "837P",
    sender_id: str = "HEALTHSIM",
    receiver_id: str = "PAYER001",
) -> ToolResult:
    """Transform claims/eligibility data to X12 EDI.
    
    Args:
        cohort_id: ID of the cohort
        transaction_type: X12 transaction set (270, 271, 278, 834, 835, 837P, 837I)
        sender_id: EDI sender ID
        receiver_id: EDI receiver ID
        
    Returns:
        ToolResult with X12 EDI content
    """
    try:
        from healthsim_agent.products.membersim.formats.x12 import (
            X12Config,
            EDI270Generator,
            EDI271Generator,
            EDI278RequestGenerator,
            EDI835Generator,
            EDI837PGenerator,
            EDI837IGenerator,
            EDI834Generator,
        )
        
        config = X12Config(sender_id=sender_id, receiver_id=receiver_id)
        
        # Load cohort data
        cohort_data = _load_cohort_data(cohort_id)
        if cohort_data.get("error"):
            return err(cohort_data["error"])
        
        transaction_type = transaction_type.upper()
        
        if transaction_type == "270":
            generator = EDI270Generator(config)
            members = cohort_data.get("members", [])
            if not members:
                return err("No members found for eligibility inquiry")
            member = _dict_to_member(members[0])
            edi = generator.generate(member)
            msg = "eligibility inquiry"
            
        elif transaction_type == "271":
            generator = EDI271Generator(config)
            members = cohort_data.get("members", [])
            plans = cohort_data.get("plans", [])
            if not members:
                return err("No members found for eligibility response")
            member = _dict_to_member(members[0])
            plan = _dict_to_plan(plans[0]) if plans else None
            edi = generator.generate(member, plan)
            msg = "eligibility response"
            
        elif transaction_type in ("835", "REMITTANCE"):
            generator = EDI835Generator(config)
            payments = cohort_data.get("payments", [])
            if not payments:
                return err("No payment data found for remittance")
            edi = generator.generate(payments)
            msg = "remittance advice"
            
        elif transaction_type in ("837P", "837"):
            generator = EDI837PGenerator(config)
            claims = cohort_data.get("claims", [])
            if not claims:
                return err("No claims found for professional claim")
            edi = generator.generate(claims)
            msg = "professional claim"
            
        elif transaction_type == "837I":
            generator = EDI837IGenerator(config)
            claims = cohort_data.get("claims", [])
            if not claims:
                return err("No claims found for institutional claim")
            edi = generator.generate(claims)
            msg = "institutional claim"
            
        elif transaction_type == "834":
            generator = EDI834Generator(config)
            members = cohort_data.get("members", [])
            if not members:
                return err("No members found for enrollment")
            edi = generator.generate([_dict_to_member(m) for m in members])
            msg = "enrollment"
            
        else:
            return err(f"Unsupported X12 transaction type: {transaction_type}")
        
        return ok(
            data=edi,
            message=f"Generated X12 {transaction_type} {msg}",
            format=f"x12_{transaction_type.lower()}",
        )
        
    except ImportError as e:
        return err(f"X12 generators not available: {e}")
    except Exception as e:
        return err(f"X12 transformation failed: {e}")


# =============================================================================
# NCPDP Transformation
# =============================================================================

def transform_to_ncpdp(
    cohort_id: str,
    message_type: str = "NEW_RX",
    prescription_id: Optional[str] = None,
) -> ToolResult:
    """Transform prescription data to NCPDP SCRIPT messages.
    
    Args:
        cohort_id: ID of the cohort
        message_type: SCRIPT message type (NEW_RX, RX_CHANGE, RX_RENEWAL, CANCEL_RX)
        prescription_id: Specific prescription ID (processes all if not specified)
        
    Returns:
        ToolResult with NCPDP SCRIPT XML message(s)
    """
    try:
        from healthsim_agent.products.rxmembersim.formats.ncpdp import (
            NCPDPScriptGenerator,
            NewRxMessage,
        )
        
        # Load cohort data
        cohort_data = _load_cohort_data(cohort_id, prescription_id)
        if cohort_data.get("error"):
            return err(cohort_data["error"])
        
        generator = NCPDPScriptGenerator()
        
        prescriptions = cohort_data.get("prescriptions", [])
        if not prescriptions:
            return err("No prescriptions found in cohort")
        
        messages = []
        for rx in prescriptions:
            if message_type.upper() == "NEW_RX":
                msg_obj = _build_new_rx_message(rx)
                xml = generator.generate_new_rx(msg_obj)
            else:
                # Other message types would need appropriate data
                continue
                
            messages.append({
                "prescription_id": rx.get("prescription_number") or rx.get("id"),
                "message_type": message_type,
                "xml": xml,
            })
        
        return ok(
            data=messages if len(messages) > 1 else messages[0],
            message=f"Generated {len(messages)} NCPDP SCRIPT {message_type} message(s)",
            format="ncpdp_script",
        )
        
    except ImportError as e:
        return err(f"NCPDP generators not available: {e}")
    except Exception as e:
        return err(f"NCPDP transformation failed: {e}")


# =============================================================================
# MIMIC-III Transformation
# =============================================================================

def transform_to_mimic(
    cohort_id: str,
    output_format: str = "dataframe",
) -> ToolResult:
    """Transform patient data to MIMIC-III format.
    
    Args:
        cohort_id: ID of the cohort
        output_format: Output format (dataframe, csv, parquet)
        
    Returns:
        ToolResult with MIMIC-III formatted data
    """
    try:
        from healthsim_agent.products.patientsim.formats.mimic import MIMICTransformer
        
        # Load cohort data
        cohort_data = _load_cohort_data(cohort_id)
        if cohort_data.get("error"):
            return err(cohort_data["error"])
        
        transformer = MIMICTransformer()
        
        patients_raw = cohort_data.get("patients", [])
        if not patients_raw:
            return err("No patients found in cohort")
        
        # Convert to model objects
        patients = [_dict_to_patient(p) for p in patients_raw]
        encounters = [_dict_to_encounter(e) for e in cohort_data.get("encounters", [])]
        diagnoses = [_dict_to_diagnosis(d) for d in cohort_data.get("diagnoses", [])]
        labs = [_dict_to_lab(l) for l in cohort_data.get("labs", [])]
        vitals = [_dict_to_vitalsign(v) for v in cohort_data.get("vitals", [])]
        
        # Transform to MIMIC tables
        mimic_data = {
            "PATIENTS": transformer.transform_patients(patients),
            "ADMISSIONS": transformer.transform_admissions(encounters),
            "DIAGNOSES_ICD": transformer.transform_diagnoses_icd(diagnoses),
            "LABEVENTS": transformer.transform_labevents(labs),
            "CHARTEVENTS": transformer.transform_chartevents(vitals),
        }
        
        # Convert DataFrames based on output format
        if output_format == "dataframe":
            result = {table: df.to_dict('records') for table, df in mimic_data.items()}
        elif output_format == "csv":
            result = {table: df.to_csv(index=False) for table, df in mimic_data.items()}
        else:
            result = {table: df.to_dict('records') for table, df in mimic_data.items()}
        
        total_rows = sum(len(df) for df in mimic_data.values())
        
        return ok(
            data=result,
            message=f"Generated MIMIC-III tables with {total_rows} total rows",
            format="mimic_iii",
        )
        
    except ImportError as e:
        return err(f"MIMIC transformer not available: {e}")
    except Exception as e:
        return err(f"MIMIC transformation failed: {e}")


# =============================================================================
# List Available Formats
# =============================================================================

def list_output_formats() -> ToolResult:
    """List all available output formats and their capabilities.
    
    Returns:
        ToolResult with format descriptions
    """
    formats = {
        "fhir_r4": {
            "name": "FHIR R4",
            "description": "HL7 FHIR R4 JSON bundles",
            "entity_types": ["patients", "encounters", "diagnoses", "medications", "observations"],
            "output": "JSON",
            "tool": "transform_to_fhir",
        },
        "ccda": {
            "name": "C-CDA",
            "description": "Consolidated Clinical Document Architecture XML",
            "entity_types": ["patients", "diagnoses", "medications", "vitals", "labs"],
            "output": "XML",
            "document_types": ["CCD", "DISCHARGE_SUMMARY", "REFERRAL_NOTE", "TRANSFER_SUMMARY"],
            "tool": "transform_to_ccda",
        },
        "hl7v2": {
            "name": "HL7v2",
            "description": "HL7 Version 2 messages",
            "entity_types": ["patients", "encounters", "labs"],
            "output": "HL7v2 pipe-delimited",
            "message_types": ["ADT_A01", "ADT_A04", "ADT_A08", "ORU_R01"],
            "tool": "transform_to_hl7v2",
        },
        "x12": {
            "name": "X12 EDI",
            "description": "ANSI X12 Electronic Data Interchange",
            "entity_types": ["members", "claims", "payments"],
            "output": "EDI",
            "transaction_types": ["270", "271", "278", "834", "835", "837P", "837I"],
            "tool": "transform_to_x12",
        },
        "ncpdp_script": {
            "name": "NCPDP SCRIPT",
            "description": "NCPDP SCRIPT for e-prescribing",
            "entity_types": ["prescriptions"],
            "output": "XML",
            "message_types": ["NEW_RX", "RX_CHANGE", "RX_RENEWAL", "CANCEL_RX"],
            "tool": "transform_to_ncpdp",
        },
        "mimic_iii": {
            "name": "MIMIC-III",
            "description": "MIMIC-III compatible tables for research",
            "entity_types": ["patients", "encounters", "diagnoses", "labs", "vitals"],
            "output": "DataFrame/CSV",
            "tables": ["PATIENTS", "ADMISSIONS", "DIAGNOSES_ICD", "LABEVENTS", "CHARTEVENTS"],
            "tool": "transform_to_mimic",
        },
    }
    
    return ok(
        data=formats,
        message=f"Found {len(formats)} available output formats",
    )


# =============================================================================
# Helper Functions
# =============================================================================

def _load_cohort_data(cohort_id: str, entity_id: Optional[str] = None) -> Dict[str, Any]:
    """Load cohort data from database.
    
    Returns dict with entity lists or error key.
    """
    try:
        conn = get_manager().get_read_connection()
        
        # Verify cohort exists
        cohort = conn.execute(
            "SELECT * FROM cohorts WHERE id = ?", [cohort_id]
        ).fetchone()
        
        if not cohort:
            return {"error": f"Cohort not found: {cohort_id}"}
        
        # Load entities by type
        result = {}
        entity_types = ["patients", "members", "claims", "prescriptions", 
                       "encounters", "diagnoses", "medications", "vitals", 
                       "labs", "observations", "payments", "plans"]
        
        for entity_type in entity_types:
            sql = """
                SELECT entity_data 
                FROM cohort_entities 
                WHERE cohort_id = ? AND entity_type = ?
            """
            params = [cohort_id, entity_type]
            
            if entity_id and entity_type in ("patients", "prescriptions"):
                sql += " AND entity_id = ?"
                params.append(entity_id)
            
            rows = conn.execute(sql, params).fetchall()
            if rows:
                result[entity_type] = [
                    json.loads(row[0]) if isinstance(row[0], str) else row[0]
                    for row in rows
                ]
        
        return result
        
    except Exception as e:
        return {"error": f"Failed to load cohort data: {e}"}


def _filter_for_patient(entities: List[Any], patient: Any) -> List[Any]:
    """Filter entities belonging to a specific patient."""
    patient_id = patient.get("mrn") if isinstance(patient, dict) else getattr(patient, "mrn", None)
    if not patient_id:
        return entities
    
    filtered = []
    for entity in entities:
        entity_patient = entity.get("mrn") if isinstance(entity, dict) else getattr(entity, "mrn", None)
        if entity_patient == patient_id:
            filtered.append(entity)
    
    return filtered


# =============================================================================
# Dict to Model Converters
# =============================================================================

def _dict_to_patient(data: Dict[str, Any]):
    """Convert dict to Patient model."""
    from healthsim_agent.products.patientsim.core.models import Patient, Name, Gender
    
    name = None
    if data.get("given_name") or data.get("family_name"):
        name = Name(
            given_name=data.get("given_name", ""),
            family_name=data.get("family_name", ""),
        )
    
    gender = Gender.UNKNOWN
    gender_val = data.get("gender", "U")
    if gender_val in ("M", "male"):
        gender = Gender.MALE
    elif gender_val in ("F", "female"):
        gender = Gender.FEMALE
    elif gender_val in ("O", "other"):
        gender = Gender.OTHER
    
    birth_date = None
    if data.get("birth_date"):
        bd = data["birth_date"]
        if isinstance(bd, str):
            birth_date = date.fromisoformat(bd.split("T")[0])
        elif isinstance(bd, date):
            birth_date = bd
    
    return Patient(
        mrn=data.get("mrn", "UNKNOWN"),
        name=name,
        gender=gender,
        birth_date=birth_date,
    )


def _dict_to_encounter(data: Dict[str, Any]):
    """Convert dict to Encounter model."""
    from healthsim_agent.products.patientsim.core.models import (
        Encounter, EncounterClass, EncounterStatus
    )
    
    # Parse dates
    admission_time = None
    if data.get("admission_date"):
        ad = data["admission_date"]
        if isinstance(ad, str):
            try:
                admission_time = datetime.fromisoformat(ad)
            except:
                admission_time = datetime.fromisoformat(ad + "T00:00:00")
        elif isinstance(ad, datetime):
            admission_time = ad
    
    discharge_time = None
    if data.get("discharge_date"):
        dd = data["discharge_date"]
        if isinstance(dd, str):
            try:
                discharge_time = datetime.fromisoformat(dd)
            except:
                discharge_time = datetime.fromisoformat(dd + "T23:59:59")
        elif isinstance(dd, datetime):
            discharge_time = dd
    
    class_code = EncounterClass.AMBULATORY
    class_val = data.get("encounter_type", "outpatient").lower()
    if class_val == "inpatient":
        class_code = EncounterClass.INPATIENT
    elif class_val == "emergency":
        class_code = EncounterClass.EMERGENCY
    
    return Encounter(
        encounter_id=data.get("encounter_id", "ENC-001"),
        patient_mrn=data.get("mrn", "UNKNOWN"),
        class_code=class_code,
        status=EncounterStatus.FINISHED,
        admission_time=admission_time,
        discharge_time=discharge_time,
    )


def _dict_to_diagnosis(data: Dict[str, Any]):
    """Convert dict to Diagnosis model."""
    from healthsim_agent.products.patientsim.core.models import Diagnosis
    
    return Diagnosis(
        patient_mrn=data.get("mrn", "UNKNOWN"),
        code=data.get("code", ""),
        description=data.get("description", ""),
        is_active=data.get("is_active", True),
    )


def _dict_to_vitalsign(data: Dict[str, Any]):
    """Convert dict to VitalSign model."""
    from healthsim_agent.products.patientsim.core.models import VitalSign
    
    obs_time = datetime.now()
    if data.get("observation_time"):
        ot = data["observation_time"]
        if isinstance(ot, str):
            obs_time = datetime.fromisoformat(ot)
        elif isinstance(ot, datetime):
            obs_time = ot
    
    return VitalSign(
        patient_mrn=data.get("mrn", "UNKNOWN"),
        observation_time=obs_time,
        systolic_bp=data.get("systolic_bp"),
        diastolic_bp=data.get("diastolic_bp"),
        heart_rate=data.get("heart_rate"),
        respiratory_rate=data.get("respiratory_rate"),
        temperature=data.get("temperature"),
        spo2=data.get("spo2"),
    )


def _dict_to_lab(data: Dict[str, Any]):
    """Convert dict to LabResult model."""
    from healthsim_agent.products.patientsim.core.models import LabResult
    
    collected_time = datetime.now()
    if data.get("collected_time"):
        ct = data["collected_time"]
        if isinstance(ct, str):
            collected_time = datetime.fromisoformat(ct)
        elif isinstance(ct, datetime):
            collected_time = ct
    
    return LabResult(
        patient_mrn=data.get("mrn", "UNKNOWN"),
        test_name=data.get("test_name", ""),
        value=data.get("value"),
        units=data.get("unit", ""),
        collected_time=collected_time,
    )


def _dict_to_member(data: Dict[str, Any]):
    """Convert dict to Member model."""
    from healthsim_agent.products.membersim.core.models import Member
    
    return Member(
        member_id=data.get("member_id", "UNKNOWN"),
        subscriber_id=data.get("subscriber_id"),
        first_name=data.get("given_name", ""),
        last_name=data.get("family_name", ""),
        date_of_birth=data.get("birth_date"),
        gender=data.get("gender", "U"),
    )


def _dict_to_plan(data: Dict[str, Any]):
    """Convert dict to Plan model."""
    from healthsim_agent.products.membersim.core.models import Plan
    
    return Plan(
        plan_id=data.get("plan_id", "UNKNOWN"),
        plan_name=data.get("plan_name", ""),
        plan_type=data.get("plan_type", "PPO"),
    )


def _build_new_rx_message(rx: Dict[str, Any]):
    """Build NewRxMessage from prescription data."""
    from healthsim_agent.products.rxmembersim.formats.ncpdp import NewRxMessage
    
    return NewRxMessage(
        message_id=rx.get("id", "MSG001"),
        prescriber_last_name=rx.get("prescriber_last_name", "Unknown"),
        prescriber_first_name=rx.get("prescriber_first_name", ""),
        prescriber_npi=rx.get("prescriber_npi", "0000000000"),
        prescriber_dea=rx.get("prescriber_dea", ""),
        prescriber_address=rx.get("prescriber_address", ""),
        prescriber_city=rx.get("prescriber_city", ""),
        prescriber_state=rx.get("prescriber_state", ""),
        prescriber_zip=rx.get("prescriber_zip", ""),
        prescriber_phone=rx.get("prescriber_phone", ""),
        patient_last_name=rx.get("patient_last_name", "Unknown"),
        patient_first_name=rx.get("patient_first_name", ""),
        patient_dob=rx.get("patient_dob", date.today().isoformat()),
        patient_gender=rx.get("patient_gender", "U"),
        patient_address=rx.get("patient_address", ""),
        patient_city=rx.get("patient_city", ""),
        patient_state=rx.get("patient_state", ""),
        patient_zip=rx.get("patient_zip", ""),
        drug_description=rx.get("drug_name", "Unknown Drug"),
        ndc=rx.get("ndc", ""),
        quantity=str(rx.get("quantity", "30")),
        quantity_unit=rx.get("quantity_unit", "EA"),
        days_supply=rx.get("days_supply", 30),
        directions=rx.get("directions", "As directed"),
        refills=rx.get("refills", 0),
        substitutions_allowed=rx.get("substitutions_allowed", True),
        pharmacy_ncpdp=rx.get("pharmacy_ncpdp", ""),
        pharmacy_npi=rx.get("pharmacy_npi", ""),
        pharmacy_name=rx.get("pharmacy_name", ""),
    )
