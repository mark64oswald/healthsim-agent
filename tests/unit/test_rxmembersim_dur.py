"""Tests for RxMemberSim Drug Utilization Review (DUR) module.

Tests cover:
- DUR alert types and enums
- DUR alert models
- DUR alert formatter
- DUR alert summary generation
"""

import pytest
from datetime import date

from healthsim_agent.products.rxmembersim.dur.rules import (
    DURAlertType,
    ClinicalSignificance,
    DURReasonForService,
    DURProfessionalService,
    DURResultOfService,
    DURAlert,
    DrugDrugInteraction,
    TherapeuticDuplication,
    AgeRestriction,
)
from healthsim_agent.products.rxmembersim.dur.alerts import (
    DURAlertSummary,
    DUROverride,
    DURAlertFormatter,
)


class TestDURAlertType:
    """Tests for DURAlertType enum."""

    def test_drug_drug_interaction(self):
        """Test DD code for drug-drug interaction."""
        assert DURAlertType.DRUG_DRUG.value == "DD"

    def test_therapeutic_duplication(self):
        """Test TD code for therapeutic duplication."""
        assert DURAlertType.THERAPEUTIC_DUPLICATION.value == "TD"

    def test_early_refill(self):
        """Test ER code for early refill."""
        assert DURAlertType.EARLY_REFILL.value == "ER"

    def test_high_dose(self):
        """Test HD code for high dose."""
        assert DURAlertType.HIGH_DOSE.value == "HD"

    def test_all_types_are_two_char(self):
        """Test all alert types are 2-character NCPDP codes."""
        for alert_type in DURAlertType:
            assert len(alert_type.value) == 2


class TestClinicalSignificance:
    """Tests for ClinicalSignificance enum."""

    def test_level_1_major(self):
        """Test level 1 is major/contraindicated."""
        assert ClinicalSignificance.LEVEL_1.value == "1"

    def test_level_2_moderate(self):
        """Test level 2 is moderate."""
        assert ClinicalSignificance.LEVEL_2.value == "2"

    def test_level_3_minor(self):
        """Test level 3 is minor."""
        assert ClinicalSignificance.LEVEL_3.value == "3"


class TestDURReasonForService:
    """Tests for DURReasonForService enum."""

    def test_drug_drug_code(self):
        """Test MA code for drug-drug interaction."""
        assert DURReasonForService.DRUG_DRUG_INTERACTION.value == "MA"

    def test_therapeutic_duplication_code(self):
        """Test TD code for therapeutic duplication."""
        assert DURReasonForService.THERAPEUTIC_DUPLICATION.value == "TD"

    def test_early_refill_code(self):
        """Test ER code for early refill."""
        assert DURReasonForService.EARLY_REFILL.value == "ER"


class TestDURProfessionalService:
    """Tests for DURProfessionalService enum."""

    def test_pharmacist_consulted(self):
        """Test M0 code for pharmacist consulted."""
        assert DURProfessionalService.PHARMACIST_CONSULTED.value == "M0"

    def test_prescriber_consulted(self):
        """Test P0 code for prescriber consulted."""
        assert DURProfessionalService.PRESCRIBER_CONSULTED.value == "P0"


class TestDURResultOfService:
    """Tests for DURResultOfService enum."""

    def test_filled_as_is(self):
        """Test 1A code for filled as is."""
        assert DURResultOfService.FILLED_AS_IS.value == "1A"

    def test_not_filled(self):
        """Test 1E code for not filled."""
        assert DURResultOfService.NOT_FILLED.value == "1E"


class TestDURAlert:
    """Tests for DURAlert model."""

    def test_create_basic_alert(self):
        """Test creating basic DUR alert."""
        alert = DURAlert(
            alert_type=DURAlertType.DRUG_DRUG,
            clinical_significance=ClinicalSignificance.LEVEL_1,
            drug1_ndc="12345678901",
            drug1_name="Drug A",
            message="Interacts with Drug B",
            reason_for_service="MA",
        )
        assert alert.alert_type == DURAlertType.DRUG_DRUG
        assert alert.clinical_significance == ClinicalSignificance.LEVEL_1
        assert alert.drug1_name == "Drug A"

    def test_create_alert_with_second_drug(self):
        """Test creating alert with interacting drug."""
        alert = DURAlert(
            alert_type=DURAlertType.DRUG_DRUG,
            clinical_significance=ClinicalSignificance.LEVEL_2,
            drug1_ndc="12345678901",
            drug1_name="Warfarin",
            drug2_ndc="98765432109",
            drug2_name="Aspirin",
            message="Increased bleeding risk",
            reason_for_service="MA",
            recommendation="Monitor INR closely",
        )
        assert alert.drug2_name == "Aspirin"
        assert alert.recommendation == "Monitor INR closely"

    def test_create_early_refill_alert(self):
        """Test creating early refill alert."""
        alert = DURAlert(
            alert_type=DURAlertType.EARLY_REFILL,
            clinical_significance=ClinicalSignificance.LEVEL_3,
            drug1_ndc="12345678901",
            drug1_name="Lisinopril",
            message="Refill requested 10 days early",
            reason_for_service="ER",
            days_early=10,
            previous_fill_date=date(2024, 1, 1),
        )
        assert alert.days_early == 10
        assert alert.previous_fill_date == date(2024, 1, 1)

    def test_alert_optional_fields_default_none(self):
        """Test optional fields default to None."""
        alert = DURAlert(
            alert_type=DURAlertType.HIGH_DOSE,
            clinical_significance=ClinicalSignificance.LEVEL_2,
            drug1_ndc="12345678901",
            drug1_name="Metformin",
            message="Dose exceeds maximum",
            reason_for_service="HD",
        )
        assert alert.drug2_ndc is None
        assert alert.drug2_name is None
        assert alert.recommendation is None


class TestDrugDrugInteraction:
    """Tests for DrugDrugInteraction model."""

    def test_create_interaction(self):
        """Test creating drug-drug interaction rule."""
        interaction = DrugDrugInteraction(
            interaction_id="INT001",
            drug1_gpi="2710001000",
            drug2_gpi="8310001000",
            drug1_name="Warfarin",
            drug2_name="Aspirin",
            interaction_description="Anticoagulant with antiplatelet",
            clinical_effect="Increased bleeding risk",
            clinical_significance=ClinicalSignificance.LEVEL_1,
            recommendation="Monitor INR and signs of bleeding",
        )
        assert interaction.interaction_id == "INT001"
        assert interaction.clinical_significance == ClinicalSignificance.LEVEL_1


class TestTherapeuticDuplication:
    """Tests for TherapeuticDuplication model."""

    def test_create_duplication_rule(self):
        """Test creating therapeutic duplication rule."""
        rule = TherapeuticDuplication(
            duplication_id="DUP001",
            gpi_class="3610",
            class_name="ACE Inhibitors",
        )
        assert rule.max_concurrent == 1  # Default
        assert rule.significance == ClinicalSignificance.LEVEL_2

    def test_custom_max_concurrent(self):
        """Test custom max concurrent drugs."""
        rule = TherapeuticDuplication(
            duplication_id="DUP002",
            gpi_class="4020",
            class_name="Antihypertensives",
            max_concurrent=2,
        )
        assert rule.max_concurrent == 2


class TestAgeRestriction:
    """Tests for AgeRestriction model."""

    def test_create_min_age_restriction(self):
        """Test creating minimum age restriction."""
        restriction = AgeRestriction(
            restriction_id="AGE001",
            drug_gpi="6610",
            drug_name="Ciprofloxacin",
            min_age=18,
            message="Not recommended under 18 years",
        )
        assert restriction.min_age == 18
        assert restriction.max_age is None

    def test_create_max_age_restriction(self):
        """Test creating maximum age restriction."""
        restriction = AgeRestriction(
            restriction_id="AGE002",
            drug_gpi="3620",
            drug_name="Some Drug",
            max_age=65,
            significance=ClinicalSignificance.LEVEL_3,
            message="Use caution in elderly",
        )
        assert restriction.max_age == 65
        assert restriction.significance == ClinicalSignificance.LEVEL_3


class TestDURAlertSummary:
    """Tests for DURAlertSummary model."""

    def test_create_empty_summary(self):
        """Test creating summary with no alerts."""
        summary = DURAlertSummary(
            claim_id="CLM001",
            total_alerts=0,
        )
        assert summary.total_alerts == 0
        assert summary.can_proceed is True
        assert len(summary.alerts) == 0

    def test_create_summary_with_alerts(self):
        """Test creating summary with alerts."""
        alert = DURAlert(
            alert_type=DURAlertType.DRUG_DRUG,
            clinical_significance=ClinicalSignificance.LEVEL_1,
            drug1_ndc="12345678901",
            drug1_name="Drug A",
            message="Test",
            reason_for_service="MA",
        )
        summary = DURAlertSummary(
            claim_id="CLM001",
            total_alerts=1,
            level_1_alerts=1,
            alerts=[alert],
            requires_override=True,
        )
        assert summary.total_alerts == 1
        assert summary.level_1_alerts == 1
        assert summary.requires_override is True

    def test_summary_with_override(self):
        """Test summary with override provided."""
        summary = DURAlertSummary(
            claim_id="CLM001",
            total_alerts=1,
            level_1_alerts=1,
            override_provided=True,
            override_codes=["M0"],
        )
        assert summary.override_provided is True
        assert "M0" in summary.override_codes


class TestDUROverride:
    """Tests for DUROverride model."""

    def test_create_basic_override(self):
        """Test creating basic override."""
        override = DUROverride(
            alert_type=DURAlertType.DRUG_DRUG,
            reason_for_service="MA",
            professional_service="M0",
            result_of_service="1A",
        )
        assert override.alert_type == DURAlertType.DRUG_DRUG
        assert override.result_of_service == "1A"

    def test_override_with_pharmacist(self):
        """Test override with pharmacist information."""
        override = DUROverride(
            alert_type=DURAlertType.EARLY_REFILL,
            reason_for_service="ER",
            professional_service="M0",
            result_of_service="1A",
            pharmacist_name="John Smith, RPh",
            override_date=date(2024, 6, 15),
            notes="Patient going on vacation",
        )
        assert override.pharmacist_name == "John Smith, RPh"
        assert override.notes == "Patient going on vacation"


class TestDURAlertFormatter:
    """Tests for DURAlertFormatter class."""

    @pytest.fixture
    def formatter(self):
        """Create formatter instance."""
        return DURAlertFormatter()

    @pytest.fixture
    def sample_alert(self):
        """Create sample alert for testing."""
        return DURAlert(
            alert_type=DURAlertType.DRUG_DRUG,
            clinical_significance=ClinicalSignificance.LEVEL_1,
            drug1_ndc="12345678901",
            drug1_name="Warfarin",
            drug2_ndc="98765432109",
            drug2_name="Aspirin",
            message="Increased bleeding risk when combined",
            recommendation="Monitor INR closely",
            reason_for_service="MA",
        )

    def test_severity_map_level_1(self, formatter):
        """Test severity map for level 1."""
        assert formatter.SEVERITY_MAP[ClinicalSignificance.LEVEL_1] == "MAJOR"

    def test_severity_map_level_2(self, formatter):
        """Test severity map for level 2."""
        assert formatter.SEVERITY_MAP[ClinicalSignificance.LEVEL_2] == "MODERATE"

    def test_severity_map_level_3(self, formatter):
        """Test severity map for level 3."""
        assert formatter.SEVERITY_MAP[ClinicalSignificance.LEVEL_3] == "MINOR"

    def test_type_map_drug_drug(self, formatter):
        """Test type map for drug-drug."""
        assert formatter.TYPE_MAP[DURAlertType.DRUG_DRUG] == "Drug-Drug Interaction"

    def test_type_map_early_refill(self, formatter):
        """Test type map for early refill."""
        assert formatter.TYPE_MAP[DURAlertType.EARLY_REFILL] == "Early Refill"

    def test_format_for_display_basic(self, formatter, sample_alert):
        """Test formatting alert for display."""
        result = formatter.format_for_display(sample_alert)
        assert "[MAJOR]" in result
        assert "Drug-Drug Interaction" in result
        assert "Warfarin" in result
        assert "Aspirin" in result
        assert "Increased bleeding risk" in result

    def test_format_for_display_with_recommendation(self, formatter, sample_alert):
        """Test display includes recommendation."""
        result = formatter.format_for_display(sample_alert)
        assert "Recommendation: Monitor INR closely" in result

    def test_format_for_display_early_refill(self, formatter):
        """Test formatting early refill alert."""
        alert = DURAlert(
            alert_type=DURAlertType.EARLY_REFILL,
            clinical_significance=ClinicalSignificance.LEVEL_3,
            drug1_ndc="12345678901",
            drug1_name="Lisinopril",
            message="Refill requested early",
            reason_for_service="ER",
            days_early=7,
        )
        result = formatter.format_for_display(alert)
        assert "[MINOR]" in result
        assert "Days Early: 7" in result

    def test_format_for_ncpdp(self, formatter, sample_alert):
        """Test formatting alert for NCPDP transmission."""
        result = formatter.format_for_ncpdp(sample_alert)
        assert result["reason_for_service"] == "MA"
        assert result["clinical_significance"] == "1"
        assert result["database_indicator"] == "1"
        assert result["conflict_code"] == "DD"

    def test_format_for_ncpdp_with_date(self, formatter):
        """Test NCPDP format includes previous fill date."""
        alert = DURAlert(
            alert_type=DURAlertType.EARLY_REFILL,
            clinical_significance=ClinicalSignificance.LEVEL_3,
            drug1_ndc="12345678901",
            drug1_name="Test Drug",
            message="Early refill",
            reason_for_service="ER",
            previous_fill_date=date(2024, 1, 15),
        )
        result = formatter.format_for_ncpdp(alert)
        assert result["previous_fill_date"] == "20240115"

    def test_create_summary_no_alerts(self, formatter):
        """Test creating summary with no alerts."""
        summary = formatter.create_summary("CLM001", [])
        assert summary.claim_id == "CLM001"
        assert summary.total_alerts == 0
        assert summary.can_proceed is True

    def test_create_summary_with_level_1(self, formatter, sample_alert):
        """Test creating summary with level 1 alert."""
        summary = formatter.create_summary("CLM001", [sample_alert])
        assert summary.total_alerts == 1
        assert summary.level_1_alerts == 1
        assert summary.level_2_alerts == 0
        assert summary.level_3_alerts == 0

    def test_create_summary_with_override(self, formatter, sample_alert):
        """Test creating summary with override."""
        summary = formatter.create_summary(
            "CLM001",
            [sample_alert],
            override_provided=True,
            override_codes=["M0"]
        )
        assert summary.override_provided is True
        assert summary.override_codes == ["M0"]

    def test_create_summary_mixed_levels(self, formatter):
        """Test summary counts different levels correctly."""
        alerts = [
            DURAlert(
                alert_type=DURAlertType.DRUG_DRUG,
                clinical_significance=ClinicalSignificance.LEVEL_1,
                drug1_ndc="111", drug1_name="A", message="1", reason_for_service="MA"
            ),
            DURAlert(
                alert_type=DURAlertType.THERAPEUTIC_DUPLICATION,
                clinical_significance=ClinicalSignificance.LEVEL_2,
                drug1_ndc="222", drug1_name="B", message="2", reason_for_service="TD"
            ),
            DURAlert(
                alert_type=DURAlertType.EARLY_REFILL,
                clinical_significance=ClinicalSignificance.LEVEL_3,
                drug1_ndc="333", drug1_name="C", message="3", reason_for_service="ER"
            ),
        ]
        summary = formatter.create_summary("CLM002", alerts)
        assert summary.total_alerts == 3
        assert summary.level_1_alerts == 1
        assert summary.level_2_alerts == 1
        assert summary.level_3_alerts == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
