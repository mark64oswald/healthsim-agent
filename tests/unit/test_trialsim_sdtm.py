"""Tests for TrialSim SDTM format exports.

Tests cover:
- SDTM domain definitions and variables
- SDTM exporter configuration
- SDTM export results
- Domain conversion (DM, AE, EX, SV)
"""

import pytest
from datetime import date
from pathlib import Path
import tempfile

from healthsim_agent.products.trialsim.formats.sdtm.domains import (
    SDTMDomain,
    SDTMVariable,
    DM_VARIABLES,
    AE_VARIABLES,
    EX_VARIABLES,
    SV_VARIABLES,
    DOMAIN_VARIABLES,
)
from healthsim_agent.products.trialsim.formats.sdtm.exporter import (
    ExportFormat,
    ExportConfig,
    ExportResult,
    SDTMExporter,
)
from healthsim_agent.products.trialsim.core.models import (
    Subject,
    Visit,
    AdverseEvent,
    Exposure,
    AESeverity,
    AECausality,
    AEOutcome,
    ArmType,
    VisitType,
)


class TestSDTMDomain:
    """Tests for SDTMDomain enum."""

    def test_dm_domain(self):
        """Test DM domain code."""
        assert SDTMDomain.DM.value == "DM"

    def test_ae_domain(self):
        """Test AE domain code."""
        assert SDTMDomain.AE.value == "AE"

    def test_ex_domain(self):
        """Test EX domain code."""
        assert SDTMDomain.EX.value == "EX"

    def test_sv_domain(self):
        """Test SV domain code."""
        assert SDTMDomain.SV.value == "SV"

    def test_all_domains_two_char(self):
        """Test all domain codes are 2 characters."""
        for domain in SDTMDomain:
            assert len(domain.value) == 2


class TestSDTMVariable:
    """Tests for SDTMVariable dataclass."""

    def test_create_basic_variable(self):
        """Test creating basic variable."""
        var = SDTMVariable(
            name="STUDYID",
            label="Study Identifier",
            data_type="Char",
            length=20,
            required=True,
        )
        assert var.name == "STUDYID"
        assert var.required is True

    def test_default_values(self):
        """Test default values."""
        var = SDTMVariable(
            name="CUSTOM",
            label="Custom Variable",
            data_type="Num",
        )
        assert var.length is None
        assert var.required is False
        assert var.codelist is None
        assert var.origin == "Derived"

    def test_numeric_variable(self):
        """Test numeric variable type."""
        var = SDTMVariable(
            name="AGE",
            label="Age",
            data_type="Num",
            length=8,
        )
        assert var.data_type == "Num"


class TestDMVariables:
    """Tests for DM domain variables."""

    def test_has_studyid(self):
        """Test DM has STUDYID."""
        names = [v.name for v in DM_VARIABLES]
        assert "STUDYID" in names

    def test_has_usubjid(self):
        """Test DM has USUBJID."""
        names = [v.name for v in DM_VARIABLES]
        assert "USUBJID" in names

    def test_has_age(self):
        """Test DM has AGE."""
        names = [v.name for v in DM_VARIABLES]
        assert "AGE" in names

    def test_required_variables(self):
        """Test required variables are marked."""
        required = [v.name for v in DM_VARIABLES if v.required]
        assert "STUDYID" in required
        assert "USUBJID" in required
        assert "SEX" in required


class TestAEVariables:
    """Tests for AE domain variables."""

    def test_has_aeterm(self):
        """Test AE has AETERM."""
        names = [v.name for v in AE_VARIABLES]
        assert "AETERM" in names

    def test_has_aesev(self):
        """Test AE has AESEV."""
        names = [v.name for v in AE_VARIABLES]
        assert "AESEV" in names

    def test_has_aeser(self):
        """Test AE has AESER."""
        names = [v.name for v in AE_VARIABLES]
        assert "AESER" in names


class TestDomainVariablesMapping:
    """Tests for DOMAIN_VARIABLES mapping."""

    def test_dm_mapping(self):
        """Test DM domain maps to variables."""
        assert SDTMDomain.DM in DOMAIN_VARIABLES
        assert DOMAIN_VARIABLES[SDTMDomain.DM] == DM_VARIABLES

    def test_ae_mapping(self):
        """Test AE domain maps to variables."""
        assert SDTMDomain.AE in DOMAIN_VARIABLES
        assert DOMAIN_VARIABLES[SDTMDomain.AE] == AE_VARIABLES


class TestExportFormat:
    """Tests for ExportFormat enum."""

    def test_csv_format(self):
        """Test CSV format."""
        assert ExportFormat.CSV.value == "csv"

    def test_json_format(self):
        """Test JSON format."""
        assert ExportFormat.JSON.value == "json"

    def test_xpt_format(self):
        """Test XPT format."""
        assert ExportFormat.XPT.value == "xpt"


class TestExportConfig:
    """Tests for ExportConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = ExportConfig()
        assert config.study_id == "STUDY01"
        assert config.sponsor == "SPONSOR"
        assert config.include_empty is False
        assert config.date_format == "ISO8601"

    def test_custom_config(self):
        """Test custom configuration."""
        config = ExportConfig(
            study_id="ONCOL01",
            sponsor="ACME Pharma",
            include_empty=True,
            domains=[SDTMDomain.DM, SDTMDomain.AE],
        )
        assert config.study_id == "ONCOL01"
        assert config.sponsor == "ACME Pharma"
        assert len(config.domains) == 2


class TestExportResult:
    """Tests for ExportResult."""

    def test_success_result(self):
        """Test successful result."""
        result = ExportResult(
            success=True,
            domains_exported=[SDTMDomain.DM],
            record_counts={"DM": 10},
        )
        assert result.success is True
        assert SDTMDomain.DM in result.domains_exported

    def test_failed_result(self):
        """Test failed result."""
        result = ExportResult(
            success=False,
            errors=["Export failed"],
        )
        assert result.success is False
        assert "Export failed" in result.errors

    def test_to_summary(self):
        """Test summary generation."""
        result = ExportResult(
            success=True,
            domains_exported=[SDTMDomain.DM, SDTMDomain.AE],
            record_counts={"DM": 10, "AE": 5},
        )
        summary = result.to_summary()
        assert "Success" in summary
        assert "DM: 10 records" in summary
        assert "AE: 5 records" in summary

    def test_summary_with_warnings(self):
        """Test summary includes warnings."""
        result = ExportResult(
            success=True,
            domains_exported=[SDTMDomain.DM],
            warnings=["Missing optional field"],
        )
        summary = result.to_summary()
        assert "Warnings:" in summary
        assert "Missing optional field" in summary


class TestSDTMExporter:
    """Tests for SDTMExporter."""

    @pytest.fixture
    def sample_subjects(self):
        """Create sample subjects."""
        return [
            Subject(
                subject_id="001",
                protocol_id="PROTO01",
                site_id="SITE01",
                age=45,
                sex="M",
                race="White",
                ethnicity="Not Hispanic or Latino",
                arm=ArmType.TREATMENT,
                screening_date=date(2024, 1, 15),
                randomization_date=date(2024, 1, 20),
            ),
            Subject(
                subject_id="002",
                protocol_id="PROTO01",
                site_id="SITE01",
                age=52,
                sex="F",
                race="Asian",
                ethnicity="Not Hispanic or Latino",
                arm=ArmType.PLACEBO,
                screening_date=date(2024, 1, 16),
            ),
        ]

    @pytest.fixture
    def sample_visits(self):
        """Create sample visits."""
        return [
            Visit(
                subject_id="001",
                protocol_id="PROTO01",
                site_id="SITE01",
                visit_number=1,
                visit_name="Screening",
                visit_type=VisitType.SCREENING,
                actual_date=date(2024, 1, 15),
            ),
            Visit(
                subject_id="001",
                protocol_id="PROTO01",
                site_id="SITE01",
                visit_number=2,
                visit_name="Baseline",
                visit_type=VisitType.BASELINE,
                actual_date=date(2024, 1, 20),
            ),
        ]

    @pytest.fixture
    def sample_adverse_events(self):
        """Create sample adverse events."""
        return [
            AdverseEvent(
                subject_id="001",
                protocol_id="PROTO01",
                ae_term="Headache",
                onset_date=date(2024, 2, 1),
                severity=AESeverity.GRADE_1,
                causality=AECausality.POSSIBLY,
                outcome=AEOutcome.RECOVERED,
            ),
        ]

    @pytest.fixture
    def sample_exposures(self):
        """Create sample exposures."""
        return [
            Exposure(
                subject_id="001",
                protocol_id="PROTO01",
                drug_name="Drug A",
                dose=100.0,
                dose_unit="mg",
                route="oral",
                start_date=date(2024, 1, 20),
            ),
        ]

    def test_exporter_default_config(self):
        """Test exporter with default config."""
        exporter = SDTMExporter()
        assert exporter.config.study_id == "STUDY01"

    def test_exporter_custom_config(self):
        """Test exporter with custom config."""
        config = ExportConfig(study_id="CUSTOM01")
        exporter = SDTMExporter(config)
        assert exporter.config.study_id == "CUSTOM01"

    def test_export_dm_domain(self, sample_subjects):
        """Test exporting DM domain."""
        exporter = SDTMExporter()
        result = exporter.export(subjects=sample_subjects)
        assert result.success is True
        assert SDTMDomain.DM in result.domains_exported
        assert result.record_counts.get("DM") == 2

    def test_export_ae_domain(self, sample_adverse_events, sample_subjects):
        """Test exporting AE domain."""
        exporter = SDTMExporter()
        result = exporter.export(
            adverse_events=sample_adverse_events,
            subjects=sample_subjects,
        )
        assert result.success is True
        assert SDTMDomain.AE in result.domains_exported
        assert result.record_counts.get("AE") == 1

    def test_export_ex_domain(self, sample_exposures, sample_subjects):
        """Test exporting EX domain."""
        exporter = SDTMExporter()
        result = exporter.export(
            exposures=sample_exposures,
            subjects=sample_subjects,
        )
        assert result.success is True
        assert SDTMDomain.EX in result.domains_exported
        assert result.record_counts.get("EX") == 1

    def test_export_sv_domain(self, sample_visits, sample_subjects):
        """Test exporting SV domain."""
        exporter = SDTMExporter()
        result = exporter.export(
            visits=sample_visits,
            subjects=sample_subjects,
        )
        assert result.success is True
        assert SDTMDomain.SV in result.domains_exported
        assert result.record_counts.get("SV") == 2

    def test_export_multiple_domains(self, sample_subjects, sample_visits, sample_adverse_events):
        """Test exporting multiple domains."""
        exporter = SDTMExporter()
        result = exporter.export(
            subjects=sample_subjects,
            visits=sample_visits,
            adverse_events=sample_adverse_events,
        )
        assert result.success is True
        assert len(result.domains_exported) >= 2

    def test_export_to_file(self, sample_subjects):
        """Test exporting to actual files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = SDTMExporter()
            result = exporter.export(
                subjects=sample_subjects,
                output_dir=tmpdir,
                format=ExportFormat.CSV,
            )
            assert result.success is True
            assert len(result.files_created) >= 1
            # Verify file exists
            for filepath in result.files_created:
                assert Path(filepath).exists()

    def test_export_empty_data(self):
        """Test exporting with no data."""
        exporter = SDTMExporter()
        result = exporter.export()
        assert result.success is True
        assert len(result.domains_exported) == 0

    def test_export_filtered_domains(self, sample_subjects, sample_visits):
        """Test exporting only specific domains."""
        config = ExportConfig(domains=[SDTMDomain.DM])
        exporter = SDTMExporter(config)
        result = exporter.export(
            subjects=sample_subjects,
            visits=sample_visits,
        )
        assert result.success is True
        assert SDTMDomain.DM in result.domains_exported
        # SV should not be exported even if visits provided
        assert SDTMDomain.SV not in result.domains_exported


class TestSDTMExporterConversions:
    """Tests for SDTM exporter conversion methods."""

    @pytest.fixture
    def exporter(self):
        """Create exporter instance."""
        return SDTMExporter(ExportConfig(study_id="TEST01"))

    @pytest.fixture
    def subject(self):
        """Create sample subject."""
        return Subject(
            subject_id="001",
            protocol_id="PROTO01",
            site_id="SITE01",
            age=45,
            sex="M",
            race="White",
            ethnicity="Not Hispanic or Latino",
            arm=ArmType.TREATMENT,
            screening_date=date(2024, 1, 15),
        )

    def test_convert_dm_studyid(self, exporter, subject):
        """Test DM conversion includes study ID."""
        records = exporter._convert_dm([subject])
        assert len(records) == 1
        assert records[0]["STUDYID"] == "TEST01"

    def test_convert_dm_usubjid_format(self, exporter, subject):
        """Test USUBJID format is correct."""
        records = exporter._convert_dm([subject])
        # Format: STUDYID-SITEID-SUBJID
        assert records[0]["USUBJID"] == "TEST01-SITE01-001"

    def test_convert_dm_demographics(self, exporter, subject):
        """Test DM conversion includes demographics."""
        records = exporter._convert_dm([subject])
        assert records[0]["AGE"] == 45
        assert records[0]["RACE"] == "White"
        assert records[0]["ETHNIC"] == "Not Hispanic or Latino"

    def test_convert_dm_arm(self, exporter, subject):
        """Test DM conversion includes arm."""
        records = exporter._convert_dm([subject])
        assert "ARMCD" in records[0]
        assert "ARM" in records[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
