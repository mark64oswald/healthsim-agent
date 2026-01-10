"""HL7v2 segment builders.

Ported from: healthsim-workspace/packages/patientsim/src/patientsim/formats/hl7v2/segments.py
"""

from datetime import datetime

from healthsim_agent.products.patientsim.core.models import Encounter, Patient

FIELD_SEP = "|"
COMPONENT_SEP = "^"
REPETITION_SEP = "~"
ESCAPE_CHAR = "\\"
SUBCOMPONENT_SEP = "&"
ENCODING_CHARS = f"{COMPONENT_SEP}{REPETITION_SEP}{ESCAPE_CHAR}{SUBCOMPONENT_SEP}"


def escape_hl7(text: str) -> str:
    """Escape special characters for HL7v2."""
    if not text:
        return ""
    return text.replace("|", "\\F\\").replace("^", "\\S\\").replace("~", "\\R\\").replace("&", "\\T\\")


def format_hl7_datetime(dt: datetime) -> str:
    """Format datetime for HL7v2 (YYYYMMDDHHmmss)."""
    return dt.strftime("%Y%m%d%H%M%S")


def format_hl7_date(dt: datetime | None) -> str:
    """Format date for HL7v2 (YYYYMMDD)."""
    if not dt:
        return ""
    if hasattr(dt, "strftime"):
        return dt.strftime("%Y%m%d")
    return ""


def build_msh_segment(
    message_type: str,
    trigger_event: str,
    message_control_id: str,
    timestamp: datetime,
    sending_application: str = "PATIENTSIM",
    sending_facility: str = "HOSPITAL",
    receiving_application: str = "EMR",
    receiving_facility: str = "HOSPITAL",
) -> str:
    """Build MSH (Message Header) segment."""
    fields = [
        "MSH",
        ENCODING_CHARS,
        sending_application,
        sending_facility,
        receiving_application,
        receiving_facility,
        format_hl7_datetime(timestamp),
        "",
        f"{message_type}{COMPONENT_SEP}{trigger_event}",
        message_control_id,
        "P",
        "2.5",
    ]
    return FIELD_SEP.join(fields)


def build_evn_segment(
    event_type: str,
    event_timestamp: datetime,
    event_reason_code: str | None = None,
) -> str:
    """Build EVN (Event Type) segment."""
    fields = [
        "EVN",
        event_type,
        format_hl7_datetime(event_timestamp),
        "",
        event_reason_code or "",
    ]
    return FIELD_SEP.join(fields)


def build_pid_segment(patient: Patient) -> str:
    """Build PID (Patient Identification) segment."""
    # Get name components
    family_name = patient.name.family_name if patient.name else ""
    given_name = patient.name.given_name if patient.name else ""
    patient_name = f"{escape_hl7(family_name)}{COMPONENT_SEP}{escape_hl7(given_name)}"

    birth_date = format_hl7_date(patient.birth_date) if patient.birth_date else ""
    gender = patient.gender.value if hasattr(patient.gender, "value") else str(patient.gender)

    fields = [
        "PID",
        "1",
        "",
        patient.mrn,
        "",
        patient_name,
        "",
        birth_date,
        gender,
        "",  # Patient alias
        "",  # Race
        "",  # Address
        "",  # County code
        "",  # Phone home
        "",  # Phone business
        "",  # Language
        "",  # Marital status
        "",  # Religion
        "",  # Account number
        "",  # SSN
        "",  # Driver's license
        "",  # Mother's ID
        "",  # Ethnic group
        "",  # Birth place
        "",  # Multiple birth
        "",  # Birth order
        "",  # Citizenship
        "",  # Veteran status
        "",  # Nationality
        "",  # Death datetime
        "",  # Death indicator
    ]
    return FIELD_SEP.join(fields)


def build_pv1_segment(encounter: Encounter, patient_class: str | None = None) -> str:
    """Build PV1 (Patient Visit) segment."""
    class_val = encounter.class_code.value if hasattr(encounter.class_code, "value") else str(encounter.class_code)
    class_map = {"inpatient": "I", "outpatient": "O", "emergency": "E", "observation": "O"}
    patient_class = patient_class or class_map.get(class_val, "O")

    admit_datetime = format_hl7_datetime(encounter.admission_time) if encounter.admission_time else ""
    discharge_datetime = format_hl7_datetime(encounter.discharge_time) if encounter.discharge_time else ""

    admission_type_map = {"inpatient": "1", "emergency": "1", "outpatient": "2", "observation": "2"}
    admission_type = admission_type_map.get(class_val, "3")

    discharge_disposition = ""
    if encounter.discharge_disposition:
        disp = encounter.discharge_disposition.upper()
        if "HOME" in disp:
            discharge_disposition = "01"
        elif "SNF" in disp or "NURSING" in disp:
            discharge_disposition = "03"
        elif "REHAB" in disp:
            discharge_disposition = "02"
        elif "DEAD" in disp or "EXPIRED" in disp or "DECEASED" in disp:
            discharge_disposition = "20"
        else:
            discharge_disposition = "01"

    fields = ["PV1", "1", patient_class, "", admission_type]
    fields.extend([""] * 14)  # Fields 5-18
    fields.append(encounter.encounter_id)  # PV1-19
    fields.extend([""] * 16)  # Fields 20-35
    fields.append(discharge_disposition)  # PV1-36
    fields.extend([""] * 7)  # Fields 37-43
    fields.append(admit_datetime)  # PV1-44
    fields.append(discharge_datetime)  # PV1-45

    return FIELD_SEP.join(fields)


def build_dg1_segment(
    diagnosis_code: str,
    diagnosis_text: str,
    set_id: int = 1,
    diagnosis_type: str = "F",
) -> str:
    """Build DG1 (Diagnosis) segment."""
    fields = [
        "DG1",
        str(set_id),
        "",
        f"{diagnosis_code}{COMPONENT_SEP}{escape_hl7(diagnosis_text)}{COMPONENT_SEP}I10",
        "",
        "",
        diagnosis_type,
    ]
    return FIELD_SEP.join(fields)


__all__ = [
    "FIELD_SEP", "COMPONENT_SEP", "ENCODING_CHARS",
    "escape_hl7", "format_hl7_datetime", "format_hl7_date",
    "build_msh_segment", "build_evn_segment", "build_pid_segment",
    "build_pv1_segment", "build_dg1_segment",
]
