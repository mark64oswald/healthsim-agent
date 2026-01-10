"""MIMIC-III database schema definitions.

Defines the structure of MIMIC-III tables for synthetic data generation.
Based on the official MIMIC-III v1.4 schema.

References:
- https://mimic.mit.edu/docs/iii/tables/
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class PatientsSchema:
    """Schema for PATIENTS table."""

    COLUMNS = [
        "row_id",
        "subject_id",
        "gender",
        "dob",
        "dod",
        "dod_hosp",
        "dod_ssn",
        "expire_flag",
    ]

    @staticmethod
    def create_empty() -> pd.DataFrame:
        return pd.DataFrame(columns=PatientsSchema.COLUMNS)


@dataclass
class AdmissionsSchema:
    """Schema for ADMISSIONS table."""

    COLUMNS = [
        "row_id",
        "subject_id",
        "hadm_id",
        "admittime",
        "dischtime",
        "deathtime",
        "admission_type",
        "admission_location",
        "discharge_location",
        "insurance",
        "language",
        "religion",
        "marital_status",
        "ethnicity",
        "edregtime",
        "edouttime",
        "diagnosis",
        "hospital_expire_flag",
        "has_chartevents_data",
    ]

    @staticmethod
    def create_empty() -> pd.DataFrame:
        return pd.DataFrame(columns=AdmissionsSchema.COLUMNS)


@dataclass
class DiagnosesIcdSchema:
    """Schema for DIAGNOSES_ICD table."""

    COLUMNS = [
        "row_id",
        "subject_id",
        "hadm_id",
        "seq_num",
        "icd9_code",
    ]

    @staticmethod
    def create_empty() -> pd.DataFrame:
        return pd.DataFrame(columns=DiagnosesIcdSchema.COLUMNS)


@dataclass
class LabeventsSchema:
    """Schema for LABEVENTS table."""

    COLUMNS = [
        "row_id",
        "subject_id",
        "hadm_id",
        "itemid",
        "charttime",
        "value",
        "valuenum",
        "valueuom",
        "flag",
    ]

    @staticmethod
    def create_empty() -> pd.DataFrame:
        return pd.DataFrame(columns=LabeventsSchema.COLUMNS)


@dataclass
class CharteventsSchema:
    """Schema for CHARTEVENTS table."""

    COLUMNS = [
        "row_id",
        "subject_id",
        "hadm_id",
        "icustay_id",
        "itemid",
        "charttime",
        "storetime",
        "cgid",
        "value",
        "valuenum",
        "valueuom",
        "warning",
        "error",
        "resultstatus",
        "stopped",
    ]

    @staticmethod
    def create_empty() -> pd.DataFrame:
        return pd.DataFrame(columns=CharteventsSchema.COLUMNS)


# MIMIC-III Item ID mappings
CHART_ITEMIDS: dict[str, int] = {
    "heart_rate": 220045,
    "sbp": 220050,
    "dbp": 220051,
    "mbp": 220052,
    "respiratory_rate": 220210,
    "temperature_f": 223761,
    "temperature_c": 223762,
    "spo2": 220277,
    "weight": 224639,
    "height": 226730,
    "bmi": 226512,
    "gcs_total": 198,
    "pain_level": 225908,
}

LAB_ITEMIDS: dict[str, int] = {
    # Hematology
    "hemoglobin": 51222,
    "hematocrit": 51221,
    "wbc": 51301,
    "platelets": 51265,
    # Chemistry
    "sodium": 50983,
    "potassium": 50971,
    "chloride": 50902,
    "bicarbonate": 50882,
    "bun": 51006,
    "creatinine": 50912,
    "glucose": 50931,
    "calcium": 50893,
    "magnesium": 50960,
    # Liver Function
    "alt": 50861,
    "ast": 50878,
    "alkaline_phosphatase": 50863,
    "bilirubin_total": 50885,
    "albumin": 50862,
    # Cardiac
    "troponin_t": 51003,
    "troponin_i": 51002,
    "bnp": 50963,
    # Coagulation
    "pt": 51274,
    "ptt": 51275,
    "inr": 51237,
    # Lipids
    "cholesterol_total": 50907,
    "ldl": 50954,
    "hdl": 50953,
    "triglycerides": 51000,
    # Other
    "lactate": 50813,
    "hba1c": 50852,
    "tsh": 50993,
}

# Lab name aliases
LAB_ALIASES: dict[str, str] = {
    "wbc_count": "wbc",
    "white_blood_cell": "wbc",
    "hgb": "hemoglobin",
    "hct": "hematocrit",
    "plt": "platelets",
    "na": "sodium",
    "k": "potassium",
    "cl": "chloride",
    "co2": "bicarbonate",
    "bicarb": "bicarbonate",
    "blood_urea_nitrogen": "bun",
    "cr": "creatinine",
    "glu": "glucose",
    "ca": "calcium",
    "mg": "magnesium",
    "sgot": "ast",
    "sgpt": "alt",
    "alp": "alkaline_phosphatase",
    "tbili": "bilirubin_total",
    "alb": "albumin",
    "trop_t": "troponin_t",
    "trop_i": "troponin_i",
    "chol": "cholesterol_total",
    "a1c": "hba1c",
}

# Vital sign aliases
VITAL_ALIASES: dict[str, str] = {
    "hr": "heart_rate",
    "pulse": "heart_rate",
    "systolic": "sbp",
    "systolic_bp": "sbp",
    "diastolic": "dbp",
    "diastolic_bp": "dbp",
    "mean_bp": "mbp",
    "rr": "respiratory_rate",
    "resp_rate": "respiratory_rate",
    "temp": "temperature_f",
    "temperature": "temperature_f",
    "o2_sat": "spo2",
    "oxygen_saturation": "spo2",
    "wt": "weight",
    "ht": "height",
    "gcs": "gcs_total",
    "pain": "pain_level",
}


def get_lab_itemid(lab_name: str) -> int | None:
    """Get MIMIC-III ITEMID for a lab test."""
    normalized = lab_name.lower().replace(" ", "_").replace("-", "_")
    if normalized in LAB_ITEMIDS:
        return LAB_ITEMIDS[normalized]
    if normalized in LAB_ALIASES:
        return LAB_ITEMIDS.get(LAB_ALIASES[normalized])
    return None


def get_chart_itemid(vital_name: str) -> int | None:
    """Get MIMIC-III ITEMID for a vital sign."""
    normalized = vital_name.lower().replace(" ", "_").replace("-", "_")
    if normalized in CHART_ITEMIDS:
        return CHART_ITEMIDS[normalized]
    if normalized in VITAL_ALIASES:
        return CHART_ITEMIDS.get(VITAL_ALIASES[normalized])
    return None
