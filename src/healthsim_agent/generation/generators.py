"""
Entity generators for healthcare data.

Generates realistic synthetic healthcare entities:
- Patients (PatientSim)
- Members (MemberSim)  
- Prescriptions (RxMemberSim)
- Subjects (TrialSim)

Each generator produces canonical JSON that can be transformed to various formats.
"""

import hashlib
import random
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from healthsim_agent.generation.distributions import (
    AgeDistribution,
    CategoricalDistribution,
    NormalDistribution,
    create_distribution,
)


# Common name data for realistic generation
FIRST_NAMES_MALE = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark",
    "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian",
    "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan",
]

FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Dorothy", "Carol",
    "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
]

STREET_NAMES = [
    "Main", "Oak", "Maple", "Cedar", "Pine", "Elm", "Washington", "Park",
    "Lake", "Hill", "Forest", "River", "Spring", "Valley", "Meadow",
]

STREET_TYPES = ["St", "Ave", "Blvd", "Dr", "Ln", "Rd", "Way", "Ct", "Pl"]

CITIES_BY_STATE = {
    "TX": ["Houston", "San Antonio", "Dallas", "Austin", "Fort Worth", "El Paso"],
    "CA": ["Los Angeles", "San Diego", "San Jose", "San Francisco", "Fresno", "Sacramento"],
    "FL": ["Jacksonville", "Miami", "Tampa", "Orlando", "St. Petersburg", "Hialeah"],
    "NY": ["New York", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany"],
    "IL": ["Chicago", "Aurora", "Rockford", "Joliet", "Naperville", "Springfield"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Reading", "Erie", "Scranton"],
    "AZ": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale", "Glendale"],
    "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron", "Dayton"],
}

# Common ICD-10 codes for conditions
COMMON_CONDITIONS = {
    "E11": "Type 2 diabetes mellitus",
    "I10": "Essential hypertension",
    "E78": "Disorders of lipoprotein metabolism",
    "J45": "Asthma",
    "M54": "Dorsalgia (back pain)",
    "F32": "Major depressive disorder",
    "G47": "Sleep disorders",
    "K21": "Gastro-esophageal reflux disease",
    "N39": "Other disorders of urinary system",
    "M79": "Other soft tissue disorders",
}


@dataclass
class GeneratorConfig:
    """Configuration for entity generators."""
    seed: int | None = None
    state: str = "TX"
    default_facility_npi: str = "1234567890"
    default_provider_npi: str = "1111111111"
    
    def __post_init__(self):
        self.rng = random.Random(self.seed)


class PatientGenerator:
    """Generates synthetic patient data for PatientSim."""
    
    def __init__(self, config: GeneratorConfig | None = None):
        self.config = config or GeneratorConfig()
        self._rng = self.config.rng
        self._counter = 0
    
    def generate(
        self,
        age: int | None = None,
        gender: str | None = None,
        conditions: list[str] | None = None,
        state: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate a single patient.
        
        Args:
            age: Patient age (or generated if None)
            gender: 'M' or 'F' (or generated if None)
            conditions: List of ICD-10 codes
            state: State abbreviation
            **kwargs: Additional attributes
            
        Returns:
            Patient dictionary in canonical format
        """
        self._counter += 1
        
        # Generate demographics
        if gender is None:
            gender = self._rng.choice(["M", "F"])
        
        if age is None:
            age_dist = AgeDistribution.adult()
            age_dist.seed(self._rng.randint(0, 1000000))
            age = age_dist.sample()
        
        birth_date = self._calculate_birth_date(age)
        
        # Generate name
        if gender == "M":
            first_name = self._rng.choice(FIRST_NAMES_MALE)
        else:
            first_name = self._rng.choice(FIRST_NAMES_FEMALE)
        
        last_name = self._rng.choice(LAST_NAMES)
        
        # Generate identifiers
        patient_id = self._generate_id("PAT", self._counter)
        mrn = f"MRN{self._counter:08d}"
        ssn = self._generate_ssn()
        
        # Generate address
        state = state or self.config.state
        address = self._generate_address(state)
        
        patient = {
            "id": patient_id,
            "mrn": mrn,
            "ssn": ssn,
            "given_name": first_name,
            "family_name": last_name,
            "birth_date": birth_date.isoformat(),
            "gender": gender,
            "race": self._generate_race(),
            "ethnicity": self._generate_ethnicity(),
            "language": "en",
            **address,
            "phone": self._generate_phone(),
            "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "deceased": False,
            "source_system": "patientsim",
            "created_at": datetime.now().isoformat(),
        }
        
        # Add conditions if specified
        if conditions:
            patient["conditions"] = [
                {"code": code, "description": COMMON_CONDITIONS.get(code, "Condition")}
                for code in conditions
            ]
        
        patient.update(kwargs)
        return patient
    
    def generate_batch(
        self,
        count: int,
        age_distribution: dict | None = None,
        gender_distribution: dict | None = None,
        conditions: list[str] | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """Generate multiple patients.
        
        Args:
            count: Number of patients to generate
            age_distribution: Age distribution spec
            gender_distribution: Gender distribution spec
            conditions: Conditions to apply with prevalence
            **kwargs: Additional attributes for all patients
            
        Returns:
            List of patient dictionaries
        """
        patients = []
        
        # Create distributions
        if age_distribution:
            age_dist = create_distribution(age_distribution)
        else:
            age_dist = None
        
        if gender_distribution:
            gender_dist = CategoricalDistribution(weights=gender_distribution)
        else:
            gender_dist = CategoricalDistribution(weights={"M": 0.48, "F": 0.52})
        
        for _ in range(count):
            age = age_dist.sample(self._rng) if age_dist else None
            if age is not None:
                age = int(age)
            
            gender = gender_dist.sample(self._rng)
            
            patient = self.generate(age=age, gender=gender, conditions=conditions, **kwargs)
            patients.append(patient)
        
        return patients
    
    def _generate_id(self, prefix: str, counter: int) -> str:
        """Generate deterministic ID."""
        combined = f"{self.config.seed or 0}:{counter}"
        hash_val = hashlib.md5(combined.encode()).hexdigest()[:8]
        return f"{prefix}-{hash_val.upper()}"
    
    def _generate_ssn(self) -> str:
        """Generate fake SSN."""
        area = self._rng.randint(100, 899)
        group = self._rng.randint(10, 99)
        serial = self._rng.randint(1000, 9999)
        return f"{area}-{group}-{serial}"
    
    def _generate_phone(self) -> str:
        """Generate phone number."""
        area = self._rng.randint(200, 999)
        prefix = self._rng.randint(200, 999)
        line = self._rng.randint(1000, 9999)
        return f"({area}) {prefix}-{line}"
    
    def _calculate_birth_date(self, age: int) -> date:
        """Calculate birth date from age."""
        today = date.today()
        birth_year = today.year - age
        birth_month = self._rng.randint(1, 12)
        max_day = 28  # Safe for all months
        birth_day = self._rng.randint(1, max_day)
        return date(birth_year, birth_month, birth_day)
    
    def _generate_address(self, state: str) -> dict[str, str]:
        """Generate address."""
        street_num = self._rng.randint(100, 9999)
        street_name = self._rng.choice(STREET_NAMES)
        street_type = self._rng.choice(STREET_TYPES)
        
        cities = CITIES_BY_STATE.get(state, ["Springfield"])
        city = self._rng.choice(cities)
        
        zip_code = f"{self._rng.randint(10000, 99999)}"
        
        return {
            "street_address": f"{street_num} {street_name} {street_type}",
            "city": city,
            "state": state,
            "postal_code": zip_code,
            "country": "US",
        }
    
    def _generate_race(self) -> str:
        """Generate race."""
        races = ["White", "Black", "Asian", "Hispanic", "Other"]
        weights = [0.60, 0.13, 0.06, 0.18, 0.03]
        return self._rng.choices(races, weights=weights, k=1)[0]
    
    def _generate_ethnicity(self) -> str:
        """Generate ethnicity."""
        return self._rng.choices(
            ["Not Hispanic", "Hispanic"],
            weights=[0.82, 0.18],
            k=1
        )[0]


class MemberGenerator:
    """Generates synthetic member data for MemberSim."""
    
    def __init__(self, config: GeneratorConfig | None = None):
        self.config = config or GeneratorConfig()
        self._rng = self.config.rng
        self._counter = 0
        self._patient_gen = PatientGenerator(config)
    
    def generate(
        self,
        from_patient: dict | None = None,
        plan_type: str | None = None,
        coverage_type: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate a single member.
        
        Args:
            from_patient: Base on existing patient data
            plan_type: Insurance plan type
            coverage_type: Medicare, Medicaid, Commercial
            **kwargs: Additional attributes
            
        Returns:
            Member dictionary in canonical format
        """
        self._counter += 1
        
        # Get base demographics from patient or generate
        if from_patient:
            base = from_patient
        else:
            base = self._patient_gen.generate(**kwargs)
        
        # Generate member-specific fields
        member_id = f"MBR{self._counter:010d}"
        subscriber_id = f"SUB{self._rng.randint(10000000, 99999999)}"
        group_id = f"GRP{self._rng.randint(1000, 9999)}"
        
        # Determine coverage
        if coverage_type is None:
            coverage_type = self._rng.choices(
                ["Commercial", "Medicare", "Medicaid"],
                weights=[0.55, 0.30, 0.15],
                k=1
            )[0]
        
        if plan_type is None:
            plan_type = self._generate_plan_type(coverage_type)
        
        # Coverage dates
        coverage_start = date.today() - timedelta(days=self._rng.randint(30, 730))
        
        member = {
            "id": self._generate_id("MBR", self._counter),
            "member_id": member_id,
            "subscriber_id": subscriber_id,
            "relationship_code": "18",  # Self
            "ssn": base.get("ssn"),
            "given_name": base.get("given_name"),
            "family_name": base.get("family_name"),
            "birth_date": base.get("birth_date"),
            "gender": base.get("gender"),
            "street_address": base.get("street_address"),
            "city": base.get("city"),
            "state": base.get("state"),
            "postal_code": base.get("postal_code"),
            "phone": base.get("phone"),
            "email": base.get("email"),
            "group_id": group_id,
            "plan_code": plan_type,
            "coverage_type": coverage_type,
            "coverage_start": coverage_start.isoformat(),
            "coverage_end": None,
            "pcp_npi": self.config.default_provider_npi,
            "source_system": "membersim",
            "created_at": datetime.now().isoformat(),
        }
        
        # Link to patient if provided
        if from_patient:
            member["patient_ref"] = from_patient.get("mrn")
        
        return member
    
    def generate_batch(
        self,
        count: int,
        patients: list[dict] | None = None,
        coverage_distribution: dict[str, float] | None = None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """Generate multiple members.
        
        Args:
            count: Number of members to generate
            patients: Optional list of patients to create members from
            coverage_distribution: Distribution of coverage types
            **kwargs: Additional attributes
            
        Returns:
            List of member dictionaries
        """
        members = []
        
        if coverage_distribution:
            coverage_dist = CategoricalDistribution(weights=coverage_distribution)
        else:
            coverage_dist = None
        
        for i in range(count):
            coverage = coverage_dist.sample(self._rng) if coverage_dist else None
            
            patient = patients[i] if patients and i < len(patients) else None
            member = self.generate(from_patient=patient, coverage_type=coverage, **kwargs)
            members.append(member)
        
        return members
    
    def _generate_id(self, prefix: str, counter: int) -> str:
        combined = f"{self.config.seed or 0}:{counter}"
        hash_val = hashlib.md5(combined.encode()).hexdigest()[:8]
        return f"{prefix}-{hash_val.upper()}"
    
    def _generate_plan_type(self, coverage_type: str) -> str:
        """Generate plan type based on coverage."""
        if coverage_type == "Medicare":
            return self._rng.choices(
                ["Medicare Advantage", "Original Medicare", "Medicare Supplement"],
                weights=[0.45, 0.40, 0.15],
                k=1
            )[0]
        elif coverage_type == "Medicaid":
            return self._rng.choices(
                ["Medicaid Managed Care", "Medicaid FFS"],
                weights=[0.70, 0.30],
                k=1
            )[0]
        else:  # Commercial
            return self._rng.choices(
                ["PPO", "HMO", "HDHP", "POS", "EPO"],
                weights=[0.40, 0.30, 0.15, 0.10, 0.05],
                k=1
            )[0]


class ClaimGenerator:
    """Generates synthetic claims for MemberSim."""
    
    def __init__(self, config: GeneratorConfig | None = None):
        self.config = config or GeneratorConfig()
        self._rng = self.config.rng
        self._counter = 0
    
    def generate(
        self,
        member: dict,
        claim_type: str = "PROFESSIONAL",
        service_date: date | None = None,
        diagnosis_codes: list[str] | None = None,
        procedure_codes: list[str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate a single claim.
        
        Args:
            member: Member dictionary
            claim_type: PROFESSIONAL, INSTITUTIONAL, DENTAL, RX
            service_date: Date of service
            diagnosis_codes: ICD-10 codes
            procedure_codes: CPT codes
            **kwargs: Additional attributes
            
        Returns:
            Claim dictionary in canonical format
        """
        self._counter += 1
        
        if service_date is None:
            service_date = date.today() - timedelta(days=self._rng.randint(1, 365))
        
        if diagnosis_codes is None:
            diagnosis_codes = [self._rng.choice(list(COMMON_CONDITIONS.keys()))]
        
        if procedure_codes is None:
            procedure_codes = [self._generate_cpt_code(claim_type)]
        
        # Generate amounts
        total_charge = round(self._rng.uniform(50, 2000), 2)
        allowed = round(total_charge * self._rng.uniform(0.4, 0.8), 2)
        paid = round(allowed * self._rng.uniform(0.7, 0.95), 2)
        
        claim = {
            "claim_id": f"CLM{self._counter:012d}",
            "claim_type": claim_type,
            "member_id": member.get("member_id"),
            "subscriber_id": member.get("subscriber_id"),
            "provider_npi": self.config.default_provider_npi,
            "facility_npi": self.config.default_facility_npi if claim_type == "INSTITUTIONAL" else None,
            "service_date": service_date.isoformat(),
            "place_of_service": "11" if claim_type == "PROFESSIONAL" else "21",
            "principal_diagnosis": diagnosis_codes[0],
            "other_diagnoses": diagnosis_codes[1:] if len(diagnosis_codes) > 1 else None,
            "total_charge": total_charge,
            "total_allowed": allowed,
            "total_paid": paid,
            "member_responsibility": round(allowed - paid, 2),
            "source_system": "membersim",
            "created_at": datetime.now().isoformat(),
        }
        
        # Add claim lines
        claim["lines"] = []
        for i, cpt in enumerate(procedure_codes):
            line_charge = total_charge / len(procedure_codes)
            claim["lines"].append({
                "line_number": i + 1,
                "procedure_code": cpt,
                "service_date": service_date.isoformat(),
                "units": 1,
                "charge_amount": round(line_charge, 2),
                "allowed_amount": round(line_charge * 0.6, 2),
                "paid_amount": round(line_charge * 0.5, 2),
            })
        
        return claim
    
    def _generate_cpt_code(self, claim_type: str) -> str:
        """Generate realistic CPT code."""
        if claim_type == "PROFESSIONAL":
            # Office visit codes
            codes = ["99213", "99214", "99215", "99203", "99204", "99205"]
        elif claim_type == "INSTITUTIONAL":
            # Hospital codes
            codes = ["99221", "99222", "99223", "99231", "99232", "99233"]
        else:
            codes = ["99213"]
        return self._rng.choice(codes)


class SubjectGenerator:
    """Generates synthetic subject data for TrialSim."""
    
    def __init__(self, config: GeneratorConfig | None = None):
        self.config = config or GeneratorConfig()
        self._rng = self.config.rng
        self._counter = 0
        self._patient_gen = PatientGenerator(config)
    
    def generate(
        self,
        study_id: str,
        site_id: str,
        from_patient: dict | None = None,
        treatment_arm: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate a clinical trial subject.
        
        Args:
            study_id: Study identifier
            site_id: Site identifier
            from_patient: Base on existing patient
            treatment_arm: Treatment assignment
            **kwargs: Additional attributes
            
        Returns:
            Subject dictionary in canonical format
        """
        self._counter += 1
        
        if from_patient:
            base = from_patient
        else:
            base = self._patient_gen.generate(**kwargs)
        
        subject_id = f"{self._counter:04d}"
        usubjid = f"{study_id}-{site_id}-{subject_id}"
        
        # Generate trial dates
        consent_date = date.today() - timedelta(days=self._rng.randint(30, 365))
        screening_date = consent_date + timedelta(days=self._rng.randint(1, 7))
        randomization_date = screening_date + timedelta(days=self._rng.randint(7, 21))
        
        subject = {
            "id": str(uuid.uuid4()),
            "subject_id": subject_id,
            "usubjid": usubjid,
            "study_id": study_id,
            "site_id": site_id,
            "patient_ref": base.get("mrn"),
            "ssn": base.get("ssn"),
            "given_name": base.get("given_name"),
            "family_name": base.get("family_name"),
            "birth_date": base.get("birth_date"),
            "gender": base.get("gender"),
            "race": base.get("race"),
            "ethnicity": base.get("ethnicity"),
            "screening_id": f"SCR-{self._counter:06d}",
            "screening_date": screening_date.isoformat(),
            "informed_consent_date": consent_date.isoformat(),
            "randomization_date": randomization_date.isoformat(),
            "treatment_arm": treatment_arm or self._rng.choice(["Treatment", "Placebo"]),
            "status": "RANDOMIZED",
            "source_system": "trialsim",
            "created_at": datetime.now().isoformat(),
        }
        
        return subject
