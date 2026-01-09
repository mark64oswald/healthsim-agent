"""Tests for generation framework - generators and profiles."""

import pytest
from datetime import date, datetime

from healthsim_agent.generation import (
    GeneratorConfig,
    PatientGenerator,
    MemberGenerator,
    ClaimGenerator,
    SubjectGenerator,
    ProfileSpecification,
    GenerationSpec,
    DemographicsSpec,
    DistributionSpec,
    DistributionType,
    PROFILE_TEMPLATES,
)


class TestGeneratorConfig:
    """Tests for GeneratorConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = GeneratorConfig()
        
        assert config.seed is None
        assert config.state == "TX"
        assert config.rng is not None
    
    def test_seeded_config(self):
        """Test seeded configuration for reproducibility."""
        config1 = GeneratorConfig(seed=42)
        config2 = GeneratorConfig(seed=42)
        
        # Same seed should produce same random values
        assert config1.rng.random() == config2.rng.random()


class TestPatientGenerator:
    """Tests for PatientGenerator."""
    
    @pytest.fixture
    def generator(self):
        return PatientGenerator(GeneratorConfig(seed=42))
    
    def test_generate_single_patient(self, generator):
        """Test generating a single patient."""
        patient = generator.generate()
        
        # Check required fields
        assert "id" in patient
        assert "mrn" in patient
        assert "given_name" in patient
        assert "family_name" in patient
        assert "birth_date" in patient
        assert "gender" in patient
        assert patient["gender"] in ["M", "F"]
        
        # Check address
        assert "city" in patient
        assert "state" in patient
        assert "postal_code" in patient
    
    def test_generate_with_specific_age(self, generator):
        """Test generating patient with specific age."""
        patient = generator.generate(age=65)
        
        birth_date = date.fromisoformat(patient["birth_date"])
        today = date.today()
        age = today.year - birth_date.year
        
        assert 64 <= age <= 66  # Allow for birthday timing
    
    def test_generate_with_specific_gender(self, generator):
        """Test generating patient with specific gender."""
        patient = generator.generate(gender="F")
        
        assert patient["gender"] == "F"
    
    def test_generate_with_conditions(self, generator):
        """Test generating patient with conditions."""
        patient = generator.generate(conditions=["E11", "I10"])
        
        assert "conditions" in patient
        assert len(patient["conditions"]) == 2
        assert patient["conditions"][0]["code"] == "E11"
    
    def test_generate_batch(self, generator):
        """Test generating batch of patients."""
        patients = generator.generate_batch(count=10)
        
        assert len(patients) == 10
        
        # All should have unique IDs
        ids = [p["id"] for p in patients]
        assert len(ids) == len(set(ids))
    
    def test_generate_batch_with_distributions(self, generator):
        """Test generating batch with custom distributions."""
        patients = generator.generate_batch(
            count=100,
            gender_distribution={"M": 0.30, "F": 0.70},
        )
        
        males = [p for p in patients if p["gender"] == "M"]
        females = [p for p in patients if p["gender"] == "F"]
        
        # Should be roughly 30/70 split
        assert len(males) < len(females)
    
    def test_reproducibility(self):
        """Test that same seed produces same patients."""
        gen1 = PatientGenerator(GeneratorConfig(seed=42))
        gen2 = PatientGenerator(GeneratorConfig(seed=42))
        
        p1 = gen1.generate()
        p2 = gen2.generate()
        
        assert p1["given_name"] == p2["given_name"]
        assert p1["family_name"] == p2["family_name"]


class TestMemberGenerator:
    """Tests for MemberGenerator."""
    
    @pytest.fixture
    def generator(self):
        return MemberGenerator(GeneratorConfig(seed=42))
    
    def test_generate_single_member(self, generator):
        """Test generating a single member."""
        member = generator.generate()
        
        # Check required fields
        assert "id" in member
        assert "member_id" in member
        assert "subscriber_id" in member
        assert "coverage_type" in member
        assert "plan_code" in member
        assert "coverage_start" in member
    
    def test_generate_from_patient(self, generator):
        """Test generating member from existing patient."""
        patient_gen = PatientGenerator(GeneratorConfig(seed=42))
        patient = patient_gen.generate()
        
        member = generator.generate(from_patient=patient)
        
        # Should share demographics
        assert member["given_name"] == patient["given_name"]
        assert member["family_name"] == patient["family_name"]
        assert member["ssn"] == patient["ssn"]
        assert member["patient_ref"] == patient["mrn"]
    
    def test_generate_with_coverage_type(self, generator):
        """Test generating member with specific coverage."""
        member = generator.generate(coverage_type="Medicare")
        
        assert member["coverage_type"] == "Medicare"
    
    def test_generate_batch(self, generator):
        """Test generating batch of members."""
        members = generator.generate_batch(count=10)
        
        assert len(members) == 10
        
        # All should have unique member IDs
        ids = [m["member_id"] for m in members]
        assert len(ids) == len(set(ids))


class TestClaimGenerator:
    """Tests for ClaimGenerator."""
    
    @pytest.fixture
    def generator(self):
        return ClaimGenerator(GeneratorConfig(seed=42))
    
    @pytest.fixture
    def member(self):
        gen = MemberGenerator(GeneratorConfig(seed=42))
        return gen.generate()
    
    def test_generate_claim(self, generator, member):
        """Test generating a claim."""
        claim = generator.generate(member)
        
        assert "claim_id" in claim
        assert claim["member_id"] == member["member_id"]
        assert "total_charge" in claim
        assert "total_paid" in claim
        assert claim["total_paid"] <= claim["total_allowed"]
    
    def test_claim_with_diagnosis(self, generator, member):
        """Test generating claim with specific diagnosis."""
        claim = generator.generate(
            member,
            diagnosis_codes=["E11", "I10"],
        )
        
        assert claim["principal_diagnosis"] == "E11"
        assert claim["other_diagnoses"] == ["I10"]
    
    def test_claim_lines(self, generator, member):
        """Test that claims have line items."""
        claim = generator.generate(
            member,
            procedure_codes=["99213", "36415"],
        )
        
        assert "lines" in claim
        assert len(claim["lines"]) == 2


class TestSubjectGenerator:
    """Tests for SubjectGenerator."""
    
    @pytest.fixture
    def generator(self):
        return SubjectGenerator(GeneratorConfig(seed=42))
    
    def test_generate_subject(self, generator):
        """Test generating a clinical trial subject."""
        subject = generator.generate(
            study_id="STUDY001",
            site_id="SITE01",
        )
        
        assert "usubjid" in subject
        assert subject["study_id"] == "STUDY001"
        assert subject["site_id"] == "SITE01"
        assert "STUDY001-SITE01-" in subject["usubjid"]
    
    def test_generate_with_treatment_arm(self, generator):
        """Test generating subject with assigned arm."""
        subject = generator.generate(
            study_id="STUDY001",
            site_id="SITE01",
            treatment_arm="Treatment",
        )
        
        assert subject["treatment_arm"] == "Treatment"
    
    def test_generate_from_patient(self, generator):
        """Test generating subject from existing patient."""
        patient_gen = PatientGenerator(GeneratorConfig(seed=42))
        patient = patient_gen.generate()
        
        subject = generator.generate(
            study_id="STUDY001",
            site_id="SITE01",
            from_patient=patient,
        )
        
        assert subject["given_name"] == patient["given_name"]
        assert subject["patient_ref"] == patient["mrn"]


class TestProfileSpecification:
    """Tests for ProfileSpecification."""
    
    def test_create_basic_profile(self):
        """Test creating a basic profile."""
        profile = ProfileSpecification(
            id="test-profile",
            name="Test Profile",
        )
        
        assert profile.id == "test-profile"
        assert profile.name == "Test Profile"
        assert profile.version == "1.0"
    
    def test_id_validation(self):
        """Test that ID is validated."""
        # Should be lowercased
        profile = ProfileSpecification(
            id="Test-Profile",
            name="Test",
        )
        assert profile.id == "test-profile"
        
        # Invalid characters should fail
        with pytest.raises(ValueError):
            ProfileSpecification(id="test profile", name="Test")
    
    def test_profile_with_demographics(self):
        """Test profile with demographics spec."""
        profile = ProfileSpecification(
            id="demo-profile",
            name="Demo Profile",
            demographics=DemographicsSpec(
                age=DistributionSpec(
                    type=DistributionType.NORMAL,
                    mean=72,
                    std_dev=8,
                ),
                gender=DistributionSpec(
                    type=DistributionType.CATEGORICAL,
                    weights={"M": 0.48, "F": 0.52},
                ),
            ),
        )
        
        assert profile.demographics is not None
        assert profile.demographics.age.mean == 72
    
    def test_profile_serialization(self):
        """Test JSON serialization round-trip."""
        profile = ProfileSpecification(
            id="test-profile",
            name="Test Profile",
            generation=GenerationSpec(count=50, products=["patientsim"]),
        )
        
        json_str = profile.to_json()
        restored = ProfileSpecification.from_json(json_str)
        
        assert restored.id == profile.id
        assert restored.generation.count == 50
    
    def test_profile_templates(self):
        """Test that profile templates are valid."""
        for name, template in PROFILE_TEMPLATES.items():
            # Each template should be loadable
            profile = ProfileSpecification(**template)
            assert profile.id is not None
            assert profile.name is not None
