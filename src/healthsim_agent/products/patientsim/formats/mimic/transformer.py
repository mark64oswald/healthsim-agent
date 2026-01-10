"""MIMIC-III format transformer.

Converts PatientSim Patient/Encounter objects to MIMIC-III database tables.
"""

from __future__ import annotations

import contextlib
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pandas as pd

from healthsim_agent.products.patientsim.formats.mimic.schema import (
    AdmissionsSchema,
    CharteventsSchema,
    DiagnosesIcdSchema,
    LabeventsSchema,
    PatientsSchema,
    get_chart_itemid,
    get_lab_itemid,
)

if TYPE_CHECKING:
    from healthsim_agent.products.patientsim.core.models import (
        Diagnosis,
        Encounter,
        LabResult,
        Patient,
        VitalSign,
    )


class IDGenerator:
    """Generates unique IDs for MIMIC-III entities."""

    def __init__(self, start_id: int = 10000) -> None:
        self.row_id = start_id
        self.subject_id = start_id
        self.hadm_id = start_id
        self._subject_map: dict[str, int] = {}
        self._hadm_map: dict[str, int] = {}

    def get_row_id(self) -> int:
        current = self.row_id
        self.row_id += 1
        return current

    def get_subject_id(self, mrn: str) -> int:
        if mrn not in self._subject_map:
            self._subject_map[mrn] = self.subject_id
            self.subject_id += 1
        return self._subject_map[mrn]

    def get_hadm_id(self, encounter_id: str) -> int:
        if encounter_id not in self._hadm_map:
            self._hadm_map[encounter_id] = self.hadm_id
            self.hadm_id += 1
        return self._hadm_map[encounter_id]


class MIMICTransformer:
    """Transforms PatientSim objects to MIMIC-III tables."""

    def __init__(self, start_id: int = 10000) -> None:
        self.id_gen = IDGenerator(start_id=start_id)

    def transform_patients(self, patients: list[Patient]) -> pd.DataFrame:
        """Transform patients to PATIENTS table."""
        rows = []

        for patient in patients:
            subject_id = self.id_gen.get_subject_id(patient.mrn)

            dod = None
            dod_hosp = None
            dod_ssn = None
            expire_flag = 0

            if patient.deceased:
                if patient.death_date:
                    dod = datetime.combine(patient.death_date, datetime.min.time())
                else:
                    years_lived = patient.age
                    dod = datetime.combine(patient.birth_date, datetime.min.time()) + timedelta(
                        days=years_lived * 365
                    )
                dod_hosp = dod
                dod_ssn = dod
                expire_flag = 1

            row = {
                "row_id": self.id_gen.get_row_id(),
                "subject_id": subject_id,
                "gender": patient.gender,
                "dob": datetime.combine(patient.birth_date, datetime.min.time()),
                "dod": dod,
                "dod_hosp": dod_hosp,
                "dod_ssn": dod_ssn,
                "expire_flag": expire_flag,
            }
            rows.append(row)

        if not rows:
            return PatientsSchema.create_empty()
        return pd.DataFrame(rows, columns=PatientsSchema.COLUMNS)

    def transform_admissions(self, encounters: list[Encounter]) -> pd.DataFrame:
        """Transform encounters to ADMISSIONS table."""
        rows = []

        for encounter in encounters:
            subject_id = self.id_gen.get_subject_id(encounter.patient_mrn)
            hadm_id = self.id_gen.get_hadm_id(encounter.encounter_id)

            death_time = None
            hospital_expire_flag = 0

            admission_type = "EMERGENCY"
            if encounter.class_code == "I":
                admission_type = "EMERGENCY"
            elif encounter.class_code == "O":
                admission_type = "ELECTIVE"

            admission_location = "EMERGENCY ROOM ADMIT"
            if admission_type == "ELECTIVE":
                admission_location = "PHYS REFERRAL/NORMAL DELI"

            discharge_location = "HOME"
            if encounter.discharge_disposition:
                disp = encounter.discharge_disposition.upper()
                if "SNF" in disp or "NURSING" in disp:
                    discharge_location = "SNF"
                elif "REHAB" in disp:
                    discharge_location = "REHAB/DISTINCT PART HOSP"
                elif "DEAD" in disp or "EXPIRED" in disp or "DECEASED" in disp:
                    discharge_location = "DEAD/EXPIRED"
                    hospital_expire_flag = 1
                    if encounter.discharge_time:
                        death_time = encounter.discharge_time

            diagnosis_text = encounter.admitting_diagnosis or "Unspecified"

            row = {
                "row_id": self.id_gen.get_row_id(),
                "subject_id": subject_id,
                "hadm_id": hadm_id,
                "admittime": encounter.admission_time,
                "dischtime": encounter.discharge_time,
                "deathtime": death_time,
                "admission_type": admission_type,
                "admission_location": admission_location,
                "discharge_location": discharge_location,
                "insurance": "Medicare",
                "language": "ENGL",
                "religion": "NOT SPECIFIED",
                "marital_status": "SINGLE",
                "ethnicity": "UNKNOWN/NOT SPECIFIED",
                "edregtime": None,
                "edouttime": None,
                "diagnosis": diagnosis_text,
                "hospital_expire_flag": hospital_expire_flag,
                "has_chartevents_data": 1,
            }

            if admission_type == "EMERGENCY":
                row["edregtime"] = encounter.admission_time - timedelta(hours=2)
                row["edouttime"] = encounter.admission_time

            rows.append(row)

        if not rows:
            return AdmissionsSchema.create_empty()
        return pd.DataFrame(rows, columns=AdmissionsSchema.COLUMNS)

    def transform_diagnoses_icd(self, diagnoses: list[Diagnosis]) -> pd.DataFrame:
        """Transform diagnoses to DIAGNOSES_ICD table."""
        rows = []

        encounter_groups: dict[str, list[Diagnosis]] = {}
        for diagnosis in diagnoses:
            enc_id = diagnosis.encounter_id or "unknown"
            if enc_id not in encounter_groups:
                encounter_groups[enc_id] = []
            encounter_groups[enc_id].append(diagnosis)

        for enc_id, diag_list in encounter_groups.items():
            if enc_id == "unknown":
                continue

            subject_id = self.id_gen.get_subject_id(diag_list[0].patient_mrn)
            hadm_id = self.id_gen.get_hadm_id(enc_id)

            for seq_num, diagnosis in enumerate(diag_list, start=1):
                icd_code = diagnosis.code.strip()
                if icd_code:
                    row = {
                        "row_id": self.id_gen.get_row_id(),
                        "subject_id": subject_id,
                        "hadm_id": hadm_id,
                        "seq_num": seq_num,
                        "icd9_code": icd_code,
                    }
                    rows.append(row)

        if not rows:
            return DiagnosesIcdSchema.create_empty()
        return pd.DataFrame(rows, columns=DiagnosesIcdSchema.COLUMNS)

    def transform_labevents(self, lab_results: list[LabResult]) -> pd.DataFrame:
        """Transform lab results to LABEVENTS table."""
        rows = []

        for lab in lab_results:
            subject_id = self.id_gen.get_subject_id(lab.patient_mrn)

            hadm_id = None
            if lab.encounter_id:
                hadm_id = self.id_gen.get_hadm_id(lab.encounter_id)

            itemid = get_lab_itemid(lab.test_name)
            if not itemid:
                continue

            chart_time = lab.collected_time

            value_num = None
            value_str = str(lab.value)
            with contextlib.suppress(ValueError, TypeError):
                value_num = float(lab.value)

            flag = "normal"

            row = {
                "row_id": self.id_gen.get_row_id(),
                "subject_id": subject_id,
                "hadm_id": hadm_id,
                "itemid": itemid,
                "charttime": chart_time,
                "value": value_str,
                "valuenum": value_num,
                "valueuom": lab.unit,
                "flag": flag,
            }
            rows.append(row)

        if not rows:
            return LabeventsSchema.create_empty()
        return pd.DataFrame(rows, columns=LabeventsSchema.COLUMNS)

    def transform_chartevents(self, vital_signs: list[VitalSign]) -> pd.DataFrame:
        """Transform vital signs to CHARTEVENTS table."""
        rows = []

        for vital in vital_signs:
            subject_id = self.id_gen.get_subject_id(vital.patient_mrn)

            hadm_id = None
            if vital.encounter_id:
                hadm_id = self.id_gen.get_hadm_id(vital.encounter_id)

            chart_time = vital.observation_time
            store_time = chart_time + timedelta(minutes=5)

            vital_mappings = [
                ("temperature", vital.temperature, "temperature_f", "F"),
                ("heart_rate", vital.heart_rate, "heart_rate", "bpm"),
                ("respiratory_rate", vital.respiratory_rate, "respiratory_rate", "/min"),
                ("systolic_bp", vital.systolic_bp, "sbp", "mmHg"),
                ("diastolic_bp", vital.diastolic_bp, "dbp", "mmHg"),
                ("spo2", vital.spo2, "spo2", "%"),
            ]

            for _field_name, value, vital_type, unit in vital_mappings:
                if value is None:
                    continue

                itemid = get_chart_itemid(vital_type)
                if not itemid:
                    continue

                row = {
                    "row_id": self.id_gen.get_row_id(),
                    "subject_id": subject_id,
                    "hadm_id": hadm_id,
                    "icustay_id": None,
                    "itemid": itemid,
                    "charttime": chart_time,
                    "storetime": store_time,
                    "cgid": 1,
                    "value": str(value),
                    "valuenum": float(value),
                    "valueuom": unit,
                    "warning": 0,
                    "error": 0,
                    "resultstatus": "Final",
                    "stopped": "NotStopped",
                }
                rows.append(row)

        if not rows:
            return CharteventsSchema.create_empty()
        return pd.DataFrame(rows, columns=CharteventsSchema.COLUMNS)
