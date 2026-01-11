"""Tests for TrialSim ADaM exporter.

Tests the ADaM (Analysis Data Model) export functionality for clinical trial data.
"""

import tempfile
from datetime import date, datetime
from pathlib import Path

import pytest

from healthsim_agent.products.trialsim.core.models import (
    AdverseEvent,
    AECausality,
    AEOutcome,
    AESeverity,
    ArmType,
    Exposure,
    Subject,
    SubjectStatus,
)
from healthsim_agent.products.trialsim.formats.adam.datasets import ADAMDataset
from healthsim_agent.products.trialsim.formats.adam.exporter import (
    ADAMExportConfig,
    ADAMExporter,
    ADAMExportResult,
    ExportFormat,
    export_to_adam,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_subject() -> Subject:
    """Create a sample subject for testing."""
    return Subject(
        subject_id="SUBJ001",
        protocol_id="PROTO001",
        site_id="SITE01",
        age=45,
        sex="M",
        race="WHITE",
        ethnicity="NOT HISPANIC OR LATINO",
        screening_date=date(2024, 1, 15),
        randomization_date=date(2024, 1, 20),
        arm=ArmType.TREATMENT,
        status=SubjectStatus.COMPLETED,
    )


@pytest.fixture
def sample_subjects() -> list[Subject]:
    """Create multiple sample subjects."""
    return [
        Subject(
            subject_id="SUBJ001",
            protocol_id="PROTO001",
            site_id="SITE01",
            age=45,
            sex="M",
            race="WHITE",
            ethnicity="NOT HISPANIC OR LATINO",
            screening_date=date(2024, 1, 15),
            randomization_date=date(2024, 1, 20),
            arm=ArmType.TREATMENT,
            status=SubjectStatus.COMPLETED,
        ),
        Subject(
            subject_id="SUBJ002",
            protocol_id="PROTO001",
            site_id="SITE02",
            age=62,
            sex="F",
            race="BLACK OR AFRICAN AMERICAN",
            ethnicity="NOT HISPANIC OR LATINO",
            screening_date=date(2024, 2, 1),
            randomization_date=date(2024, 2, 5),
            arm=ArmType.PLACEBO,
            status=SubjectStatus.WITHDRAWN,
        ),
        Subject(
            subject_id="SUBJ003",
            protocol_id="PROTO001",
            site_id="SITE01",
            age=28,
            sex="F",
            race="ASIAN",
            ethnicity="NOT HISPANIC OR LATINO",
            screening_date=date(2024, 2, 10),
            randomization_date=date(2024, 2, 15),
            arm=ArmType.TREATMENT,
            status=SubjectStatus.ON_TREATMENT,
        ),
    ]


@pytest.fixture
def sample_adverse_events() -> list[AdverseEvent]:
    """Create sample adverse events."""
    return [
        AdverseEvent(
            ae_id="AE001",
            protocol_id="PROTO001",
            subject_id="SUBJ001",
            ae_term="Headache",
            system_organ_class="Nervous system disorders",
            severity=AESeverity.GRADE_1,
            is_serious=False,
            causality=AECausality.POSSIBLY,
            outcome=AEOutcome.RECOVERED,
            onset_date=date(2024, 1, 25),
            resolution_date=date(2024, 1, 27),
        ),
        AdverseEvent(
            ae_id="AE002",
            protocol_id="PROTO001",
            subject_id="SUBJ001",
            ae_term="Nausea",
            system_organ_class="Gastrointestinal disorders",
            severity=AESeverity.GRADE_2,
            is_serious=False,
            causality=AECausality.PROBABLY,
            outcome=AEOutcome.RECOVERED,
            onset_date=date(2024, 2, 1),
            resolution_date=date(2024, 2, 3),
        ),
        AdverseEvent(
            ae_id="AE003",
            protocol_id="PROTO001",
            subject_id="SUBJ002",
            ae_term="Fatigue",
            system_organ_class="General disorders",
            severity=AESeverity.GRADE_1,
            is_serious=False,
            causality=AECausality.UNLIKELY,
            outcome=AEOutcome.RECOVERING,
            onset_date=date(2024, 2, 10),
            resolution_date=None,
        ),
    ]


@pytest.fixture
def sample_exposures() -> list[Exposure]:
    """Create sample exposures."""
    return [
        Exposure(
            exposure_id="EXP001",
            protocol_id="PROTO001",
            subject_id="SUBJ001",
            drug_name="STUDY DRUG A",
            dose=100.0,
            dose_unit="mg",
            route="oral",
            start_date=date(2024, 1, 20),
            end_date=date(2024, 4, 20),
        ),
        Exposure(
            exposure_id="EXP002",
            protocol_id="PROTO001",
            subject_id="SUBJ002",
            drug_name="PLACEBO",
            dose=100.0,
            dose_unit="mg",
            route="oral",
            start_date=date(2024, 2, 5),
            end_date=date(2024, 3, 1),
        ),
        Exposure(
            exposure_id="EXP003",
            protocol_id="PROTO001",
            subject_id="SUBJ003",
            drug_name="STUDY DRUG A",
            dose=50.0,
            dose_unit="mg",
            route="iv",
            start_date=date(2024, 2, 15),
            end_date=None,
        ),
    ]


# ============================================================================
# Test ADAMExportConfig
# ============================================================================

class TestADAMExportConfig:
    """Tests for ADAMExportConfig dataclass."""

    def test_default_config(self):
        """Default configuration values."""
        config = ADAMExportConfig()
        assert config.study_id == "STUDY01"
        assert config.sponsor == "SPONSOR"
        assert config.include_empty is False
        assert config.date_format == "ISO8601"
        assert config.null_value == ""
        assert config.datasets is None

    def test_custom_config(self):
        """Custom configuration values."""
        config = ADAMExportConfig(
            study_id="MY_STUDY",
            sponsor="MY_SPONSOR",
            include_empty=True,
            datasets=[ADAMDataset.ADSL],
        )
        assert config.study_id == "MY_STUDY"
        assert config.sponsor == "MY_SPONSOR"
        assert config.include_empty is True
        assert config.datasets == [ADAMDataset.ADSL]


class TestADAMExportResult:
    """Tests for ADAMExportResult dataclass."""

    def test_default_result(self):
        """Default result values."""
        result = ADAMExportResult(success=True)
        assert result.success is True
        assert result.datasets_exported == []
        assert result.record_counts == {}
        assert result.warnings == []
        assert result.errors == []
        assert result.files_created == []
        assert result.data == {}

    def test_to_summary_success(self):
        """Summary for successful export."""
        result = ADAMExportResult(
            success=True,
            datasets_exported=[ADAMDataset.ADSL, ADAMDataset.ADAE],
            record_counts={"ADSL": 10, "ADAE": 25},
        )
        summary = result.to_summary()
        assert "Success" in summary
        assert "ADSL: 10 records" in summary
        assert "ADAE: 25 records" in summary

    def test_to_summary_with_warnings(self):
        """Summary includes warnings."""
        result = ADAMExportResult(
            success=True,
            warnings=["Warning 1", "Warning 2"],
        )
        summary = result.to_summary()
        assert "Warnings:" in summary
        assert "Warning 1" in summary

    def test_to_summary_with_errors(self):
        """Summary includes errors."""
        result = ADAMExportResult(
            success=False,
            errors=["Error 1", "Error 2"],
        )
        summary = result.to_summary()
        assert "Failed" in summary
        assert "Errors:" in summary
        assert "Error 1" in summary


# ============================================================================
# Test ADAMExporter Initialization
# ============================================================================

class TestADAMExporterInit:
    """Tests for ADAMExporter initialization."""

    def test_default_exporter(self):
        """Create exporter with default config."""
        exporter = ADAMExporter()
        assert exporter.config.study_id == "STUDY01"

    def test_custom_exporter(self):
        """Create exporter with custom config."""
        config = ADAMExportConfig(study_id="CUSTOM_STUDY")
        exporter = ADAMExporter(config)
        assert exporter.config.study_id == "CUSTOM_STUDY"


# ============================================================================
# Test ADSL Conversion
# ============================================================================

class TestADSLConversion:
    """Tests for ADSL (Subject-Level) dataset conversion."""

    def test_convert_adsl_basic(self, sample_subject):
        """Convert single subject to ADSL."""
        exporter = ADAMExporter()
        records = exporter._convert_adsl([sample_subject])
        
        assert len(records) == 1
        rec = records[0]
        assert rec["STUDYID"] == "STUDY01"
        assert rec["SUBJID"] == "SUBJ001"
        assert rec["SITEID"] == "SITE01"
        assert rec["AGE"] == 45
        assert rec["AGEU"] == "YEARS"
        assert rec["SEX"] == "M"
        assert rec["RACE"] == "WHITE"
        assert rec["RANDFL"] == "Y"

    def test_convert_adsl_with_exposures(self, sample_subject, sample_exposures):
        """ADSL includes treatment dates from exposures."""
        exporter = ADAMExporter()
        exposures = [e for e in sample_exposures if e.subject_id == sample_subject.subject_id]
        records = exporter._convert_adsl([sample_subject], exposures)
        
        rec = records[0]
        assert rec["TRTSDT"] == "2024-01-20"
        assert rec["TRTEDT"] == "2024-04-20"

    def test_convert_adsl_age_groups(self):
        """Age grouping logic."""
        exporter = ADAMExporter()
        
        # Test different age groups
        subjects = [
            Subject(subject_id="S1", protocol_id="PROTO001", site_id="S01", age=16, sex="M"),
            Subject(subject_id="S2", protocol_id="PROTO001", site_id="S01", age=35, sex="F"),
            Subject(subject_id="S3", protocol_id="PROTO001", site_id="S01", age=70, sex="M"),
        ]
        records = exporter._convert_adsl(subjects)
        
        assert records[0]["AGEGR1"] == "<18"
        assert records[1]["AGEGR1"] == "18-64"
        assert records[2]["AGEGR1"] == ">=65"

    def test_convert_adsl_subject_status(self, sample_subjects):
        """EOS status derived from subject status."""
        exporter = ADAMExporter()
        records = exporter._convert_adsl(sample_subjects)
        
        # COMPLETED subject
        completed = next(r for r in records if r["SUBJID"] == "SUBJ001")
        assert completed["EOSSTT"] == "COMPLETED"
        
        # WITHDRAWN subject
        withdrawn = next(r for r in records if r["SUBJID"] == "SUBJ002")
        assert withdrawn["EOSSTT"] == "DISCONTINUED"
        
        # ONGOING subject
        ongoing = next(r for r in records if r["SUBJID"] == "SUBJ003")
        assert ongoing["EOSSTT"] == "ONGOING"

    def test_convert_adsl_treatment_flags(self, sample_subjects):
        """Safety and ITT flags."""
        exporter = ADAMExporter()
        records = exporter._convert_adsl(sample_subjects)
        
        for rec in records:
            # All randomized subjects should have safety/ITT flags
            assert rec["SAFFL"] == "Y"
            assert rec["ITTFL"] == "Y"
            assert rec["RANDFL"] == "Y"


# ============================================================================
# Test ADAE Conversion
# ============================================================================

class TestADAEConversion:
    """Tests for ADAE (Adverse Events) dataset conversion."""

    def test_convert_adae_basic(self, sample_adverse_events, sample_subjects):
        """Convert adverse events to ADAE."""
        exporter = ADAMExporter()
        records = exporter._convert_adae(sample_adverse_events, sample_subjects)
        
        assert len(records) == 3
        
        # Check first AE
        ae1 = records[0]
        assert ae1["AETERM"] == "Headache"
        assert ae1["AEBODSYS"] == "Nervous system disorders"
        assert ae1["AESEV"] == "MILD"
        assert ae1["AESER"] == "N"
        assert ae1["AEREL"] == "POSSIBLE"
        assert ae1["AEOUT"] == "RECOVERED/RESOLVED"

    def test_convert_adae_sequence_numbers(self, sample_adverse_events, sample_subjects):
        """AE sequence numbers per subject."""
        exporter = ADAMExporter()
        records = exporter._convert_adae(sample_adverse_events, sample_subjects)
        
        # SUBJ001 has 2 AEs
        subj001_aes = [r for r in records if r["SUBJID"] == "SUBJ001"]
        assert len(subj001_aes) == 2
        assert subj001_aes[0]["AESEQ"] == 1
        assert subj001_aes[1]["AESEQ"] == 2
        
        # SUBJ002 has 1 AE
        subj002_aes = [r for r in records if r["SUBJID"] == "SUBJ002"]
        assert len(subj002_aes) == 1
        assert subj002_aes[0]["AESEQ"] == 1

    def test_convert_adae_first_occurrence_flags(self, sample_adverse_events, sample_subjects):
        """First occurrence flags (AOCCFL, AOCCSFL, AOCCPFL)."""
        exporter = ADAMExporter()
        records = exporter._convert_adae(sample_adverse_events, sample_subjects)
        
        subj001_aes = [r for r in records if r["SUBJID"] == "SUBJ001"]
        
        # First AE for subject
        assert subj001_aes[0]["AOCCFL"] == "Y"
        assert subj001_aes[1]["AOCCFL"] == "N"
        
        # First occurrence in SOC
        assert subj001_aes[0]["AOCCSFL"] == "Y"  # First Nervous system disorders
        assert subj001_aes[1]["AOCCSFL"] == "Y"  # First Gastrointestinal disorders

    def test_convert_adae_study_day(self, sample_adverse_events, sample_subjects):
        """Study day calculation relative to randomization."""
        exporter = ADAMExporter()
        records = exporter._convert_adae(sample_adverse_events, sample_subjects)
        
        # SUBJ001 randomized 2024-01-20, first AE onset 2024-01-25
        ae1 = records[0]
        assert ae1["ASTDY"] == 6  # Day 6 (5 days after + 1)

    def test_convert_adae_duration(self, sample_adverse_events, sample_subjects):
        """AE duration calculation."""
        exporter = ADAMExporter()
        records = exporter._convert_adae(sample_adverse_events, sample_subjects)
        
        # First AE: 2024-01-25 to 2024-01-27 = 2 days
        ae1 = records[0]
        assert ae1["ADURN"] == 2
        assert ae1["ADURU"] == "DAYS"
        
        # Third AE: no resolution date
        ae3 = records[2]
        assert ae3["ADURN"] is None
        assert ae3["ADURU"] == ""


# ============================================================================
# Test ADEX Conversion
# ============================================================================

class TestADEXConversion:
    """Tests for ADEX (Exposure) dataset conversion."""

    def test_convert_adex_basic(self, sample_exposures, sample_subjects):
        """Convert exposures to ADEX."""
        exporter = ADAMExporter()
        records = exporter._convert_adex(sample_exposures, sample_subjects)
        
        assert len(records) == 3
        
        exp1 = records[0]
        assert exp1["EXTRT"] == "STUDY DRUG A"
        assert exp1["EXDOSE"] == 100.0
        assert exp1["EXDOSU"] == "MG"
        assert exp1["EXROUTE"] == "ORAL"

    def test_convert_adex_routes(self, sample_exposures, sample_subjects):
        """Route mapping."""
        exporter = ADAMExporter()
        records = exporter._convert_adex(sample_exposures, sample_subjects)
        
        oral = next(r for r in records if r["SUBJID"] == "SUBJ001")
        assert oral["EXROUTE"] == "ORAL"
        
        iv = next(r for r in records if r["SUBJID"] == "SUBJ003")
        assert iv["EXROUTE"] == "INTRAVENOUS"

    def test_convert_adex_sequence(self, sample_exposures, sample_subjects):
        """Exposure sequence numbers."""
        exporter = ADAMExporter()
        records = exporter._convert_adex(sample_exposures, sample_subjects)
        
        for rec in records:
            assert rec["EXSEQ"] == 1  # Each subject has 1 exposure


# ============================================================================
# Test Full Export
# ============================================================================

class TestADAMExport:
    """Tests for full ADaM export operation."""

    def test_export_all_datasets(self, sample_subjects, sample_adverse_events, sample_exposures):
        """Export all datasets."""
        exporter = ADAMExporter()
        result = exporter.export(
            subjects=sample_subjects,
            adverse_events=sample_adverse_events,
            exposures=sample_exposures,
        )
        
        assert result.success is True
        assert ADAMDataset.ADSL in result.datasets_exported
        assert ADAMDataset.ADAE in result.datasets_exported
        assert ADAMDataset.ADEX in result.datasets_exported
        assert result.record_counts["ADSL"] == 3
        assert result.record_counts["ADAE"] == 3
        assert result.record_counts["ADEX"] == 3

    def test_export_to_csv_files(self, sample_subjects, sample_adverse_events, sample_exposures):
        """Export to CSV files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = ADAMExporter()
            result = exporter.export(
                subjects=sample_subjects,
                adverse_events=sample_adverse_events,
                exposures=sample_exposures,
                output_dir=tmpdir,
                format=ExportFormat.CSV,
            )
            
            assert result.success is True
            assert len(result.files_created) == 3
            
            # Verify files exist
            for filepath in result.files_created:
                assert Path(filepath).exists()
                assert filepath.endswith(".csv")

    def test_export_to_json_files(self, sample_subjects, sample_adverse_events, sample_exposures):
        """Export to JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = ADAMExporter()
            result = exporter.export(
                subjects=sample_subjects,
                adverse_events=sample_adverse_events,
                exposures=sample_exposures,
                output_dir=tmpdir,
                format=ExportFormat.JSON,
            )
            
            assert result.success is True
            
            for filepath in result.files_created:
                assert filepath.endswith(".json")

    def test_export_specific_datasets(self, sample_subjects):
        """Export only specified datasets."""
        config = ADAMExportConfig(datasets=[ADAMDataset.ADSL])
        exporter = ADAMExporter(config)
        result = exporter.export(subjects=sample_subjects)
        
        assert result.success is True
        assert ADAMDataset.ADSL in result.datasets_exported
        assert ADAMDataset.ADAE not in result.datasets_exported
        assert ADAMDataset.ADEX not in result.datasets_exported

    def test_export_empty_data(self):
        """Export with no data."""
        exporter = ADAMExporter()
        result = exporter.export()
        
        assert result.success is True
        assert result.datasets_exported == []
        assert result.record_counts == {}


# ============================================================================
# Test Helper Functions
# ============================================================================

class TestHelperFunctions:
    """Tests for helper/mapping functions."""

    def test_map_sex(self):
        """Sex code mapping."""
        exporter = ADAMExporter()
        assert exporter._map_sex("M") == "M"
        assert exporter._map_sex("F") == "F"
        assert exporter._map_sex("MALE") == "M"
        assert exporter._map_sex("FEMALE") == "F"
        assert exporter._map_sex("Unknown") == "U"

    def test_map_severity(self):
        """Severity mapping."""
        exporter = ADAMExporter()
        assert exporter._map_severity(AESeverity.GRADE_1) == "MILD"
        assert exporter._map_severity(AESeverity.GRADE_2) == "MODERATE"
        assert exporter._map_severity(AESeverity.GRADE_3) == "SEVERE"
        assert exporter._map_severity(AESeverity.GRADE_4) == "LIFE THREATENING"
        assert exporter._map_severity(AESeverity.GRADE_5) == "FATAL"

    def test_map_causality(self):
        """Causality mapping."""
        exporter = ADAMExporter()
        assert exporter._map_causality(AECausality.NOT_RELATED) == "NOT RELATED"
        assert exporter._map_causality(AECausality.UNLIKELY) == "UNLIKELY"
        assert exporter._map_causality(AECausality.POSSIBLY) == "POSSIBLE"
        assert exporter._map_causality(AECausality.PROBABLY) == "PROBABLE"
        assert exporter._map_causality(AECausality.DEFINITELY) == "DEFINITE"

    def test_map_outcome(self):
        """Outcome mapping."""
        exporter = ADAMExporter()
        assert exporter._map_outcome(AEOutcome.RECOVERED) == "RECOVERED/RESOLVED"
        assert exporter._map_outcome(AEOutcome.RECOVERING) == "RECOVERING/RESOLVING"
        assert exporter._map_outcome(AEOutcome.NOT_RECOVERED) == "NOT RECOVERED/NOT RESOLVED"
        assert exporter._map_outcome(AEOutcome.FATAL) == "FATAL"
        assert exporter._map_outcome(AEOutcome.UNKNOWN) == "UNKNOWN"

    def test_format_date(self):
        """Date formatting."""
        exporter = ADAMExporter()
        assert exporter._format_date(date(2024, 1, 15)) == "2024-01-15"
        assert exporter._format_date(datetime(2024, 1, 15, 10, 30)) == "2024-01-15"
        assert exporter._format_date(None) == ""

    def test_format_datetime(self):
        """Datetime formatting."""
        exporter = ADAMExporter()
        assert exporter._format_datetime(datetime(2024, 1, 15, 10, 30, 45)) == "2024-01-15T10:30:45"
        assert exporter._format_datetime(date(2024, 1, 15)) == "2024-01-15"
        assert exporter._format_datetime(None) == ""

    def test_calc_study_day(self):
        """Study day calculation."""
        exporter = ADAMExporter()
        ref = date(2024, 1, 1)
        
        # Same day = Day 1
        assert exporter._calc_study_day(date(2024, 1, 1), ref) == 1
        
        # Day after = Day 2
        assert exporter._calc_study_day(date(2024, 1, 2), ref) == 2
        
        # Day before = Day -1
        assert exporter._calc_study_day(date(2023, 12, 31), ref) == -1
        
        # None returns empty string
        assert exporter._calc_study_day(None, ref) == ""
        assert exporter._calc_study_day(date(2024, 1, 5), None) == ""


# ============================================================================
# Test Convenience Function
# ============================================================================

class TestExportToAdam:
    """Tests for export_to_adam convenience function."""

    def test_export_to_adam_function(self, sample_subjects, sample_adverse_events):
        """Use convenience function."""
        result = export_to_adam(
            subjects=sample_subjects,
            adverse_events=sample_adverse_events,
            study_id="STUDY123",
        )
        
        assert result.success is True
        assert ADAMDataset.ADSL in result.datasets_exported
        assert ADAMDataset.ADAE in result.datasets_exported

    def test_export_to_adam_with_output_dir(self, sample_subjects):
        """Export to directory via convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = export_to_adam(
                subjects=sample_subjects,
                output_dir=tmpdir,
            )
            
            assert result.success is True
            assert len(result.files_created) > 0
