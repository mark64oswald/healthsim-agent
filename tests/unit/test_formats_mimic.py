"""Tests for PatientSim MIMIC-III format support."""

import pytest
from datetime import date, datetime, timedelta

import pandas as pd

from healthsim_agent.products.patientsim.formats.mimic import (
    AdmissionsSchema,
    CHART_ITEMIDS,
    CharteventsSchema,
    DiagnosesIcdSchema,
    IDGenerator,
    LAB_ITEMIDS,
    LabeventsSchema,
    MIMICTransformer,
    PatientsSchema,
    get_chart_itemid,
    get_lab_itemid,
)


class TestSchemas:
    """Tests for MIMIC-III schema definitions."""

    def test_patients_schema_columns(self):
        """Test PATIENTS schema has required columns."""
        expected = [
            "row_id", "subject_id", "gender", "dob",
            "dod", "dod_hosp", "dod_ssn", "expire_flag",
        ]
        assert PatientsSchema.COLUMNS == expected

    def test_admissions_schema_columns(self):
        """Test ADMISSIONS schema has required columns."""
        assert "row_id" in AdmissionsSchema.COLUMNS
        assert "subject_id" in AdmissionsSchema.COLUMNS
        assert "hadm_id" in AdmissionsSchema.COLUMNS
        assert "admittime" in AdmissionsSchema.COLUMNS
        assert "dischtime" in AdmissionsSchema.COLUMNS
        assert "admission_type" in AdmissionsSchema.COLUMNS

    def test_diagnoses_icd_schema_columns(self):
        """Test DIAGNOSES_ICD schema has required columns."""
        expected = ["row_id", "subject_id", "hadm_id", "seq_num", "icd9_code"]
        assert DiagnosesIcdSchema.COLUMNS == expected

    def test_labevents_schema_columns(self):
        """Test LABEVENTS schema has required columns."""
        assert "row_id" in LabeventsSchema.COLUMNS
        assert "subject_id" in LabeventsSchema.COLUMNS
        assert "itemid" in LabeventsSchema.COLUMNS
        assert "charttime" in LabeventsSchema.COLUMNS
        assert "value" in LabeventsSchema.COLUMNS

    def test_chartevents_schema_columns(self):
        """Test CHARTEVENTS schema has required columns."""
        assert "row_id" in CharteventsSchema.COLUMNS
        assert "subject_id" in CharteventsSchema.COLUMNS
        assert "itemid" in CharteventsSchema.COLUMNS
        assert "charttime" in CharteventsSchema.COLUMNS
        assert "valuenum" in CharteventsSchema.COLUMNS

    def test_create_empty_dataframes(self):
        """Test creating empty DataFrames with correct schemas."""
        patients_df = PatientsSchema.create_empty()
        assert isinstance(patients_df, pd.DataFrame)
        assert list(patients_df.columns) == PatientsSchema.COLUMNS
        assert len(patients_df) == 0

        admissions_df = AdmissionsSchema.create_empty()
        assert isinstance(admissions_df, pd.DataFrame)
        assert len(admissions_df) == 0


class TestItemIDMappings:
    """Tests for MIMIC Item ID mappings."""

    def test_chart_itemids_defined(self):
        """Test that common vital signs have item IDs."""
        assert "heart_rate" in CHART_ITEMIDS
        assert "sbp" in CHART_ITEMIDS
        assert "dbp" in CHART_ITEMIDS
        assert "respiratory_rate" in CHART_ITEMIDS
        assert "temperature_f" in CHART_ITEMIDS
        assert "spo2" in CHART_ITEMIDS

    def test_lab_itemids_defined(self):
        """Test that common labs have item IDs."""
        assert "hemoglobin" in LAB_ITEMIDS
        assert "sodium" in LAB_ITEMIDS
        assert "potassium" in LAB_ITEMIDS
        assert "creatinine" in LAB_ITEMIDS
        assert "glucose" in LAB_ITEMIDS

    def test_get_chart_itemid_direct(self):
        """Test getting chart item ID by direct name."""
        assert get_chart_itemid("heart_rate") == 220045
        assert get_chart_itemid("sbp") == 220050
        assert get_chart_itemid("spo2") == 220277

    def test_get_chart_itemid_alias(self):
        """Test getting chart item ID by alias."""
        assert get_chart_itemid("hr") == 220045
        assert get_chart_itemid("pulse") == 220045
        assert get_chart_itemid("systolic") == 220050
        assert get_chart_itemid("o2_sat") == 220277

    def test_get_chart_itemid_unknown(self):
        """Test getting unknown chart item returns None."""
        assert get_chart_itemid("unknown_vital") is None

    def test_get_lab_itemid_direct(self):
        """Test getting lab item ID by direct name."""
        assert get_lab_itemid("hemoglobin") == 51222
        assert get_lab_itemid("sodium") == 50983
        assert get_lab_itemid("creatinine") == 50912

    def test_get_lab_itemid_alias(self):
        """Test getting lab item ID by alias."""
        assert get_lab_itemid("hgb") == 51222
        assert get_lab_itemid("na") == 50983
        assert get_lab_itemid("cr") == 50912
        assert get_lab_itemid("k") == 50971

    def test_get_lab_itemid_unknown(self):
        """Test getting unknown lab item returns None."""
        assert get_lab_itemid("unknown_lab") is None


class TestIDGenerator:
    """Tests for MIMIC ID generator."""

    @pytest.fixture
    def id_gen(self):
        return IDGenerator(start_id=10000)

    def test_row_id_increments(self, id_gen):
        """Test that row IDs increment."""
        id1 = id_gen.get_row_id()
        id2 = id_gen.get_row_id()
        id3 = id_gen.get_row_id()

        assert id1 == 10000
        assert id2 == 10001
        assert id3 == 10002

    def test_subject_id_consistent(self, id_gen):
        """Test that same MRN gets same subject ID."""
        id1 = id_gen.get_subject_id("MRN001")
        id2 = id_gen.get_subject_id("MRN002")
        id3 = id_gen.get_subject_id("MRN001")  # Same as first

        assert id1 == id3  # Same MRN = same subject_id
        assert id1 != id2  # Different MRN = different subject_id

    def test_hadm_id_consistent(self, id_gen):
        """Test that same encounter gets same hadm ID."""
        id1 = id_gen.get_hadm_id("ENC001")
        id2 = id_gen.get_hadm_id("ENC002")
        id3 = id_gen.get_hadm_id("ENC001")  # Same as first

        assert id1 == id3
        assert id1 != id2


class TestMIMICTransformer:
    """Tests for MIMICTransformer."""

    @pytest.fixture
    def transformer(self):
        return MIMICTransformer(start_id=10000)

    @pytest.fixture
    def sample_patient(self):
        """Create a mock patient object."""
        class MockPatient:
            mrn = "MRN001"
            gender = "M"
            birth_date = date(1960, 5, 15)
            age = 64
            deceased = False
            death_date = None

        return MockPatient()

    @pytest.fixture
    def sample_deceased_patient(self):
        """Create a mock deceased patient."""
        class MockPatient:
            mrn = "MRN002"
            gender = "F"
            birth_date = date(1940, 3, 20)
            age = 84
            deceased = True
            death_date = date(2024, 1, 10)

        return MockPatient()

    @pytest.fixture
    def sample_encounter(self):
        """Create a mock encounter object."""
        class MockEncounter:
            encounter_id = "ENC001"
            patient_mrn = "MRN001"
            class_code = "I"  # Inpatient
            admission_time = datetime(2024, 1, 15, 10, 30)
            discharge_time = datetime(2024, 1, 18, 14, 0)
            admitting_diagnosis = "Chest pain"
            discharge_disposition = "HOME"

        return MockEncounter()

    @pytest.fixture
    def sample_diagnosis(self):
        """Create a mock diagnosis object."""
        class MockDiagnosis:
            patient_mrn = "MRN001"
            encounter_id = "ENC001"
            code = "I10"

        return MockDiagnosis()

    @pytest.fixture
    def sample_lab(self):
        """Create a mock lab result object."""
        class MockLab:
            patient_mrn = "MRN001"
            encounter_id = "ENC001"
            test_name = "sodium"
            value = 140
            unit = "mEq/L"
            collected_time = datetime(2024, 1, 15, 11, 0)

        return MockLab()

    @pytest.fixture
    def sample_vital(self):
        """Create a mock vital sign object."""
        class MockVital:
            patient_mrn = "MRN001"
            encounter_id = "ENC001"
            observation_time = datetime(2024, 1, 15, 10, 45)
            temperature = 98.6
            heart_rate = 72
            respiratory_rate = 16
            systolic_bp = 120
            diastolic_bp = 80
            spo2 = 98

        return MockVital()

    def test_transform_patients_single(self, transformer, sample_patient):
        """Test transforming single patient."""
        df = transformer.transform_patients([sample_patient])

        assert len(df) == 1
        assert df.iloc[0]["gender"] == "M"
        assert df.iloc[0]["expire_flag"] == 0
        assert df.iloc[0]["dod"] is None

    def test_transform_patients_deceased(self, transformer, sample_deceased_patient):
        """Test transforming deceased patient."""
        df = transformer.transform_patients([sample_deceased_patient])

        assert len(df) == 1
        assert df.iloc[0]["expire_flag"] == 1
        assert df.iloc[0]["dod"] is not None

    def test_transform_patients_empty(self, transformer):
        """Test transforming empty patient list."""
        df = transformer.transform_patients([])

        assert len(df) == 0
        assert list(df.columns) == PatientsSchema.COLUMNS

    def test_transform_admissions(self, transformer, sample_encounter):
        """Test transforming encounters to admissions."""
        # First transform a patient to establish subject_id mapping
        class MockPatient:
            mrn = "MRN001"
            gender = "M"
            birth_date = date(1960, 5, 15)
            age = 64
            deceased = False
            death_date = None

        transformer.transform_patients([MockPatient()])
        df = transformer.transform_admissions([sample_encounter])

        assert len(df) == 1
        assert df.iloc[0]["admission_type"] == "EMERGENCY"
        assert df.iloc[0]["discharge_location"] == "HOME"
        assert df.iloc[0]["diagnosis"] == "Chest pain"

    def test_transform_diagnoses_icd(self, transformer, sample_diagnosis):
        """Test transforming diagnoses."""
        # Establish mappings first
        class MockPatient:
            mrn = "MRN001"
            gender = "M"
            birth_date = date(1960, 5, 15)
            age = 64
            deceased = False
            death_date = None

        class MockEncounter:
            encounter_id = "ENC001"
            patient_mrn = "MRN001"
            class_code = "I"
            admission_time = datetime.now()
            discharge_time = datetime.now()
            admitting_diagnosis = "Test"
            discharge_disposition = "HOME"

        transformer.transform_patients([MockPatient()])
        transformer.transform_admissions([MockEncounter()])
        df = transformer.transform_diagnoses_icd([sample_diagnosis])

        assert len(df) == 1
        assert df.iloc[0]["icd9_code"] == "I10"
        assert df.iloc[0]["seq_num"] == 1

    def test_transform_labevents(self, transformer, sample_lab):
        """Test transforming lab results."""
        class MockPatient:
            mrn = "MRN001"
            gender = "M"
            birth_date = date(1960, 5, 15)
            age = 64
            deceased = False
            death_date = None

        transformer.transform_patients([MockPatient()])
        df = transformer.transform_labevents([sample_lab])

        assert len(df) == 1
        assert df.iloc[0]["itemid"] == LAB_ITEMIDS["sodium"]
        assert df.iloc[0]["valuenum"] == 140
        assert df.iloc[0]["valueuom"] == "mEq/L"

    def test_transform_labevents_unknown_lab(self, transformer):
        """Test that unknown labs are skipped."""
        class MockLab:
            patient_mrn = "MRN001"
            encounter_id = None
            test_name = "unknown_test_xyz"
            value = 100
            unit = "units"
            collected_time = datetime.now()

        class MockPatient:
            mrn = "MRN001"
            gender = "M"
            birth_date = date(1960, 5, 15)
            age = 64
            deceased = False
            death_date = None

        transformer.transform_patients([MockPatient()])
        df = transformer.transform_labevents([MockLab()])

        assert len(df) == 0  # Unknown lab should be skipped

    def test_transform_chartevents(self, transformer, sample_vital):
        """Test transforming vital signs."""
        class MockPatient:
            mrn = "MRN001"
            gender = "M"
            birth_date = date(1960, 5, 15)
            age = 64
            deceased = False
            death_date = None

        transformer.transform_patients([MockPatient()])
        df = transformer.transform_chartevents([sample_vital])

        # Should have 6 rows (one per vital sign)
        assert len(df) == 6

        # Check for expected item IDs
        itemids = df["itemid"].tolist()
        assert CHART_ITEMIDS["heart_rate"] in itemids
        assert CHART_ITEMIDS["sbp"] in itemids
        assert CHART_ITEMIDS["spo2"] in itemids

    def test_id_consistency_across_transforms(self, transformer):
        """Test that IDs are consistent across different transforms."""
        class MockPatient:
            mrn = "MRN001"
            gender = "M"
            birth_date = date(1960, 5, 15)
            age = 64
            deceased = False
            death_date = None

        class MockEncounter:
            encounter_id = "ENC001"
            patient_mrn = "MRN001"
            class_code = "I"
            admission_time = datetime.now()
            discharge_time = datetime.now()
            admitting_diagnosis = "Test"
            discharge_disposition = "HOME"

        class MockLab:
            patient_mrn = "MRN001"
            encounter_id = "ENC001"
            test_name = "sodium"
            value = 140
            unit = "mEq/L"
            collected_time = datetime.now()

        patients_df = transformer.transform_patients([MockPatient()])
        admissions_df = transformer.transform_admissions([MockEncounter()])
        labs_df = transformer.transform_labevents([MockLab()])

        # All should have same subject_id for MRN001
        patient_subject = patients_df.iloc[0]["subject_id"]
        admission_subject = admissions_df.iloc[0]["subject_id"]
        lab_subject = labs_df.iloc[0]["subject_id"]

        assert patient_subject == admission_subject == lab_subject

        # Labs should have same hadm_id as admission
        admission_hadm = admissions_df.iloc[0]["hadm_id"]
        lab_hadm = labs_df.iloc[0]["hadm_id"]

        assert admission_hadm == lab_hadm
