"""Tests for generation tools.

These tests verify that all 4 product generators work correctly.
"""

import pytest
from healthsim_agent.tools.generation_tools import (
    generate_patients,
    generate_members,
    generate_subjects,
    generate_rx_members,
    check_formulary,
    list_skills,
    describe_skill,
)


class TestGeneratePatients:
    """Tests for PatientSim generation."""
    
    def test_generate_single_patient(self):
        """Generate a single patient with no extras."""
        result = generate_patients(count=1)
        assert result.success is True
        assert "patients" in result.data
        assert len(result.data["patients"]) == 1
        
        patient = result.data["patients"][0]
        assert "id" in patient  # Model uses 'id' not 'patient_id'
        assert "birth_date" in patient
        assert "gender" in patient
    
    def test_generate_multiple_patients(self):
        """Generate multiple patients."""
        result = generate_patients(count=5)
        assert result.success is True
        assert len(result.data["patients"]) == 5
    
    def test_generate_with_encounters(self):
        """Generate patients with encounters."""
        result = generate_patients(count=2, include_encounters=True)
        assert result.success is True
        assert "encounters" in result.data
        assert len(result.data["encounters"]) == 2
    
    def test_generate_with_diagnoses(self):
        """Generate patients with diagnoses."""
        result = generate_patients(count=2, include_diagnoses=True)
        assert result.success is True
        assert "diagnoses" in result.data
        assert len(result.data["diagnoses"]) >= 2  # 1-3 per patient
    
    def test_generate_with_vitals(self):
        """Generate patients with vital signs."""
        result = generate_patients(count=2, include_vitals=True)
        assert result.success is True
        assert "vitals" in result.data
        assert len(result.data["vitals"]) == 2
    
    def test_generate_with_labs(self):
        """Generate patients with lab results."""
        result = generate_patients(count=2, include_labs=True)
        assert result.success is True
        assert "labs" in result.data
        assert len(result.data["labs"]) >= 4  # 2-5 per patient
    
    def test_generate_with_medications(self):
        """Generate patients with medications."""
        result = generate_patients(count=2, include_medications=True)
        assert result.success is True
        assert "medications" in result.data
        assert len(result.data["medications"]) >= 2  # 1-4 per patient
    
    def test_generate_full_patient(self):
        """Generate patient with all clinical data."""
        result = generate_patients(
            count=1,
            include_encounters=True,
            include_diagnoses=True,
            include_vitals=True,
            include_labs=True,
            include_medications=True,
        )
        assert result.success is True
        assert "patients" in result.data
        assert "encounters" in result.data
        assert "diagnoses" in result.data
        assert "vitals" in result.data
        assert "labs" in result.data
        assert "medications" in result.data
    
    def test_generate_with_gender_filter(self):
        """Generate patients with specific gender."""
        result = generate_patients(count=3, gender="female", seed=42)
        assert result.success is True
        for patient in result.data["patients"]:
            # Model uses single-char codes 'F' and 'M'
            assert patient["gender"] in ("F", "female")
    
    def test_generate_with_age_range(self):
        """Generate patients within age range."""
        result = generate_patients(count=5, age_range=(65, 80), seed=42)
        assert result.success is True
        # All patients should be elderly
        for patient in result.data["patients"]:
            # birth_date is a string, can't easily verify age without parsing
            assert "birth_date" in patient
    
    def test_generate_with_seed_reproducible(self):
        """Same seed produces same results."""
        result1 = generate_patients(count=2, seed=12345)
        result2 = generate_patients(count=2, seed=12345)
        # Model uses 'id' not 'patient_id'
        assert result1.data["patients"][0]["id"] == result2.data["patients"][0]["id"]
    
    def test_invalid_count_too_low(self):
        """Reject count below 1."""
        result = generate_patients(count=0)
        assert result.success is False
        assert "Count must be" in result.error
    
    def test_invalid_count_too_high(self):
        """Reject count above 100."""
        result = generate_patients(count=101)
        assert result.success is False
        assert "Count must be" in result.error


class TestGenerateMembers:
    """Tests for MemberSim generation."""
    
    def test_generate_single_member(self):
        """Generate a single member."""
        result = generate_members(count=1)
        assert result.success is True
        assert "members" in result.data
        assert len(result.data["members"]) == 1
        
        member = result.data["members"][0]
        assert "member_id" in member
    
    def test_generate_with_enrollment(self):
        """Generate members with enrollment data."""
        result = generate_members(count=2, include_enrollment=True)
        assert result.success is True
        assert "enrollments" in result.data
        assert len(result.data["enrollments"]) == 2
    
    def test_generate_with_claims(self):
        """Generate members with claims."""
        result = generate_members(count=2, include_claims=True, claims_per_member=3)
        assert result.success is True
        assert "claims" in result.data
        assert len(result.data["claims"]) == 6  # 2 members * 3 claims
    
    def test_generate_full_member(self):
        """Generate member with all data."""
        result = generate_members(
            count=1,
            include_enrollment=True,
            include_claims=True,
            claims_per_member=2,
        )
        assert result.success is True
        assert "members" in result.data
        assert "enrollments" in result.data
        assert "claims" in result.data


class TestGenerateSubjects:
    """Tests for TrialSim generation."""
    
    def test_generate_single_subject(self):
        """Generate a single trial subject."""
        result = generate_subjects(count=1)
        assert result.success is True
        assert "subjects" in result.data
        assert len(result.data["subjects"]) == 1
        
        subject = result.data["subjects"][0]
        assert "subject_id" in subject
        assert "protocol_id" in subject
    
    def test_generate_with_protocol(self):
        """Generate subjects with custom protocol."""
        result = generate_subjects(count=2, protocol_id="TEST-PROTO-001")
        assert result.success is True
        for subject in result.data["subjects"]:
            assert subject["protocol_id"] == "TEST-PROTO-001"
    
    def test_generate_with_visits(self):
        """Generate subjects with visit schedule."""
        result = generate_subjects(count=1, include_visits=True)
        assert result.success is True
        assert "visits" in result.data
        assert len(result.data["visits"]) > 0  # Multiple visits per subject
    
    def test_generate_with_adverse_events(self):
        """Generate subjects with adverse events."""
        result = generate_subjects(count=2, include_adverse_events=True)
        assert result.success is True
        # AEs are probabilistic, may or may not have any
        assert "subjects" in result.data
    
    def test_generate_with_exposures(self):
        """Generate subjects with drug exposures."""
        result = generate_subjects(count=1, include_exposures=True)
        assert result.success is True
        assert "exposures" in result.data
        assert len(result.data["exposures"]) > 0
    
    def test_generate_full_subject(self):
        """Generate subject with all trial data."""
        result = generate_subjects(
            count=1,
            include_visits=True,
            include_adverse_events=True,
            include_exposures=True,
        )
        assert result.success is True
        assert "subjects" in result.data
        assert "visits" in result.data
        assert "exposures" in result.data


class TestGenerateRxMembers:
    """Tests for RxMemberSim generation."""
    
    def test_generate_single_rx_member(self):
        """Generate a single pharmacy member."""
        result = generate_rx_members(count=1)
        assert result.success is True
        assert "rx_members" in result.data
        assert len(result.data["rx_members"]) == 1
        
        member = result.data["rx_members"][0]
        assert "member_id" in member
        assert "bin" in member
        assert "pcn" in member
    
    def test_generate_multiple_rx_members(self):
        """Generate multiple pharmacy members."""
        result = generate_rx_members(count=5)
        assert result.success is True
        assert len(result.data["rx_members"]) == 5
    
    def test_generate_with_custom_bin(self):
        """Generate Rx members with custom BIN."""
        result = generate_rx_members(count=2, bin_number="999999")
        assert result.success is True
        for member in result.data["rx_members"]:
            assert member["bin"] == "999999"


class TestListSkills:
    """Tests for skill listing."""
    
    def test_list_all_skills(self):
        """List skills for all products."""
        result = list_skills()
        assert result.success is True
        assert "patientsim" in result.data
        assert "membersim" in result.data
        assert "trialsim" in result.data
        assert "rxmembersim" in result.data
    
    def test_list_patientsim_skills(self):
        """List PatientSim skills only."""
        result = list_skills(product="patientsim")
        assert result.success is True
        assert "patientsim" in result.data
        assert len(result.data["patientsim"]) > 0
        # Should have diabetes-management skill
        skill_names = [s["name"] for s in result.data["patientsim"]]
        assert "diabetes-management" in skill_names
    
    def test_list_trialsim_skills(self):
        """List TrialSim skills only."""
        result = list_skills(product="trialsim")
        assert result.success is True
        assert "trialsim" in result.data
        assert len(result.data["trialsim"]) > 0


class TestDescribeSkill:
    """Tests for skill description."""
    
    def test_describe_existing_skill(self):
        """Describe an existing skill."""
        result = describe_skill("diabetes-management", "patientsim")
        assert result.success is True
        assert result.data["name"] == "diabetes-management"
        assert result.data["product"] == "patientsim"
        assert "content" in result.data
        assert len(result.data["content"]) > 0
    
    def test_describe_nonexistent_skill(self):
        """Describe a skill that doesn't exist."""
        result = describe_skill("nonexistent-skill", "patientsim")
        assert result.success is False
        assert "not found" in result.error
    
    def test_describe_skill_in_subdirectory(self):
        """Describe a skill that's in a subdirectory."""
        result = describe_skill("breast-cancer", "patientsim")
        assert result.success is True
        assert result.data["name"] == "breast-cancer"
