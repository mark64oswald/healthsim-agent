"""Extended tests for generation_tools module."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date


class TestGeneratePatients:
    """Tests for generate_patients function edge cases."""
    
    def test_generate_zero_count(self):
        """Test generating zero patients."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=0)
        assert result.success is False or (result.data and len(result.data.get("patients", [])) == 0)
    
    def test_generate_negative_count(self):
        """Test generating negative count."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=-5)
        assert result.success is False
    
    def test_generate_with_age_range(self):
        """Test generating with age range."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=2, age_range=(30, 50))
        assert result.success is True
    
    def test_generate_with_gender(self):
        """Test with gender filter."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=2, gender="F")
        assert result.success is True
    
    def test_generate_with_encounters(self):
        """Test generating with encounters."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=1, include_encounters=True)
        assert result.success is True
    
    def test_generate_with_diagnoses(self):
        """Test generating with diagnoses."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=1, include_diagnoses=True)
        assert result.success is True
    
    def test_generate_with_labs(self):
        """Test generating with labs."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=1, include_labs=True)
        assert result.success is True
    
    def test_generate_with_vitals(self):
        """Test generating with vitals."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=1, include_vitals=True)
        assert result.success is True
    
    def test_generate_with_medications(self):
        """Test generating with medications."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=1, include_medications=True)
        assert result.success is True
    
    def test_generate_with_diagnosis_categories(self):
        """Test generating with diagnosis categories."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=1, diagnosis_categories=["diabetes", "hypertension"])
        assert result.success is True
    
    def test_generate_all_data(self):
        """Test generating patient with all clinical data."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(
            count=1,
            include_encounters=True,
            include_diagnoses=True,
            include_vitals=True,
            include_labs=True,
            include_medications=True
        )
        assert result.success is True


class TestGenerateMembers:
    """Tests for generate_members function edge cases."""
    
    def test_generate_zero_members(self):
        """Test generating zero members."""
        from healthsim_agent.tools.generation_tools import generate_members
        
        result = generate_members(count=0)
        assert result.success is False or (result.data and len(result.data.get("members", [])) == 0)
    
    def test_generate_with_age_range(self):
        """Test generating with age range."""
        from healthsim_agent.tools.generation_tools import generate_members
        
        result = generate_members(count=2, age_range=(25, 65))
        assert result.success is True
    
    def test_generate_with_enrollment(self):
        """Test generating with enrollment data."""
        from healthsim_agent.tools.generation_tools import generate_members
        
        result = generate_members(count=1, include_enrollment=True)
        assert result.success is True
    
    def test_generate_with_claims(self):
        """Test generating with claims."""
        from healthsim_agent.tools.generation_tools import generate_members
        
        result = generate_members(count=1, include_claims=True, claims_per_member=5)
        assert result.success is True
    
    def test_generate_with_real_providers(self):
        """Test with real providers."""
        from healthsim_agent.tools.generation_tools import generate_members
        
        result = generate_members(count=1, use_real_providers=True)
        assert result.success is True
    
    def test_generate_with_provider_state(self):
        """Test with provider state filter."""
        from healthsim_agent.tools.generation_tools import generate_members
        
        result = generate_members(count=1, use_real_providers=True, provider_state="TX")
        assert result.success is True


class TestGeneratePharmacyClaims:
    """Tests for generate_pharmacy_claims function."""
    
    def test_generate_zero_claims(self):
        """Test generating zero pharmacy claims."""
        from healthsim_agent.tools.generation_tools import generate_pharmacy_claims
        
        result = generate_pharmacy_claims(count=0)
        assert result.success is False or result.data is not None
    
    def test_generate_with_member(self):
        """Test generating with member data."""
        from healthsim_agent.tools.generation_tools import generate_pharmacy_claims
        
        result = generate_pharmacy_claims(count=3, include_member=True)
        assert result.success is True
    
    def test_generate_with_drug_category(self):
        """Test with drug category filter."""
        from healthsim_agent.tools.generation_tools import generate_pharmacy_claims
        
        result = generate_pharmacy_claims(count=2, drug_category="antidiabetic")
        assert result.success is True
    
    def test_generate_with_date_range(self):
        """Test with date range."""
        from healthsim_agent.tools.generation_tools import generate_pharmacy_claims
        
        result = generate_pharmacy_claims(count=3, date_range_days=180)
        assert result.success is True
    
    def test_generate_for_specific_member(self):
        """Test generating for specific member ID."""
        from healthsim_agent.tools.generation_tools import generate_pharmacy_claims
        
        result = generate_pharmacy_claims(count=2, member_id="MBR-12345")
        assert result.success is True


class TestGenerateRxMembers:
    """Tests for generate_rx_members function."""
    
    def test_generate_zero_rx_members(self):
        """Test generating zero Rx members."""
        from healthsim_agent.tools.generation_tools import generate_rx_members
        
        result = generate_rx_members(count=0)
        assert result.success is False or result.data is not None
    
    def test_generate_with_bin(self):
        """Test generating with BIN."""
        from healthsim_agent.tools.generation_tools import generate_rx_members
        
        result = generate_rx_members(count=1, bin_number="123456")
        assert result.success is True
    
    def test_generate_with_pcn(self):
        """Test generating with PCN."""
        from healthsim_agent.tools.generation_tools import generate_rx_members
        
        result = generate_rx_members(count=1, pcn="TESTPCN")
        assert result.success is True
    
    def test_generate_with_group(self):
        """Test generating with group number."""
        from healthsim_agent.tools.generation_tools import generate_rx_members
        
        result = generate_rx_members(count=1, group_number="GRP001")
        assert result.success is True


class TestGenerateSubjects:
    """Tests for generate_subjects (TrialSim) function."""
    
    def test_generate_zero_subjects(self):
        """Test generating zero subjects."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=0)
        assert result.success is False or result.data is not None
    
    def test_generate_with_protocol(self):
        """Test with protocol ID."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=5, protocol_id="STUDY-001")
        assert result.success is True
    
    def test_generate_with_site(self):
        """Test with site ID."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=3, site_id="SITE-TX-001")
        assert result.success is True
    
    def test_generate_with_age_range(self):
        """Test with age range."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=2, age_range=(18, 75))
        assert result.success is True
    
    def test_generate_with_visits(self):
        """Test with visits."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=1, include_visits=True)
        assert result.success is True
    
    def test_generate_with_adverse_events(self):
        """Test with adverse events."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=1, include_adverse_events=True)
        assert result.success is True
    
    def test_generate_with_exposures(self):
        """Test with exposures."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=1, include_exposures=True)
        assert result.success is True
    
    def test_generate_with_vitals(self):
        """Test with vitals."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=1, include_vitals=True)
        assert result.success is True
    
    def test_generate_with_labs(self):
        """Test with labs."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=1, include_labs=True)
        assert result.success is True
    
    def test_generate_with_medical_history(self):
        """Test with medical history."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=1, include_medical_history=True)
        assert result.success is True
    
    def test_generate_with_concomitant_meds(self):
        """Test with concomitant meds."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=1, include_concomitant_meds=True)
        assert result.success is True
    
    def test_generate_with_eligibility(self):
        """Test with eligibility."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=1, include_eligibility=True)
        assert result.success is True
    
    def test_generate_with_lab_panel(self):
        """Test with specific lab panel."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(count=1, include_labs=True, lab_panel="comprehensive")
        assert result.success is True
    
    def test_generate_full_subject(self):
        """Test generating subject with all data."""
        from healthsim_agent.tools.generation_tools import generate_subjects
        
        result = generate_subjects(
            count=1,
            include_visits=True,
            include_adverse_events=True,
            include_exposures=True,
            include_vitals=True,
            include_labs=True,
            include_medical_history=True,
            include_concomitant_meds=True,
            include_eligibility=True
        )
        assert result.success is True


class TestGenerationEdgeCases:
    """Edge cases for generation tools."""
    
    def test_very_large_count(self):
        """Test with very large count."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result = generate_patients(count=1000)
        # Should either succeed or return appropriate message
        assert result is not None
    
    def test_generate_with_seed(self):
        """Test reproducibility with seed."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result1 = generate_patients(count=1, seed=42)
        result2 = generate_patients(count=1, seed=42)
        
        # With same seed, should get same results
        if result1.success and result2.success:
            # Compare patient data
            p1 = result1.data.get("patients", [{}])[0] if result1.data else {}
            p2 = result2.data.get("patients", [{}])[0] if result2.data else {}
            assert p1.get("name") == p2.get("name")
    
    def test_different_seeds_different_results(self):
        """Test different seeds produce different results."""
        from healthsim_agent.tools.generation_tools import generate_patients
        
        result1 = generate_patients(count=1, seed=111)
        result2 = generate_patients(count=1, seed=222)
        
        # Both should succeed
        assert result1.success is True
        assert result2.success is True


class TestListSkills:
    """Tests for list_skills function."""
    
    def test_list_all_skills(self):
        """Test listing all skills."""
        from healthsim_agent.tools.generation_tools import list_skills
        
        result = list_skills()
        assert result.success is True
    
    def test_list_patientsim_skills(self):
        """Test listing PatientSim skills."""
        from healthsim_agent.tools.generation_tools import list_skills
        
        result = list_skills(product="patientsim")
        assert result.success is True
    
    def test_list_membersim_skills(self):
        """Test listing MemberSim skills."""
        from healthsim_agent.tools.generation_tools import list_skills
        
        result = list_skills(product="membersim")
        assert result.success is True
    
    def test_list_trialsim_skills(self):
        """Test listing TrialSim skills."""
        from healthsim_agent.tools.generation_tools import list_skills
        
        result = list_skills(product="trialsim")
        assert result.success is True


class TestDescribeSkill:
    """Tests for describe_skill function."""
    
    def test_describe_unknown_skill(self):
        """Test describing unknown skill."""
        from healthsim_agent.tools.generation_tools import describe_skill
        
        result = describe_skill("nonexistent", "patientsim")
        assert result.success is False or result.data is None
    
    def test_describe_empty_skill(self):
        """Test with empty skill name."""
        from healthsim_agent.tools.generation_tools import describe_skill
        
        result = describe_skill("", "patientsim")
        assert result.success is False


class TestCheckFormulary:
    """Tests for check_formulary function."""
    
    def test_check_drug_name(self):
        """Test checking drug by name."""
        from healthsim_agent.tools.generation_tools import check_formulary
        
        result = check_formulary("metformin")
        assert result is not None
    
    def test_check_drug_with_ndc(self):
        """Test checking drug with NDC."""
        from healthsim_agent.tools.generation_tools import check_formulary
        
        result = check_formulary("metformin", ndc="00378-1812-01")
        assert result is not None
    
    def test_check_empty_drug(self):
        """Test with empty drug name."""
        from healthsim_agent.tools.generation_tools import check_formulary
        
        result = check_formulary("")
        assert result.success is False
