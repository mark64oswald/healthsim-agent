"""Patient data generation utilities.

Ported from: healthsim-workspace/packages/patientsim/src/patientsim/core/generator.py
"""

from datetime import date, datetime, timedelta
from typing import Any

from healthsim_agent.generation import AgeDistribution, BaseGenerator
from healthsim_agent.person import Address, ContactInfo, PersonName

from healthsim_agent.products.patientsim.core.models import (
    Diagnosis,
    DiagnosisType,
    Encounter,
    EncounterClass,
    EncounterStatus,
    Gender,
    LabResult,
    Medication,
    MedicationStatus,
    Patient,
    VitalSign,
)
from healthsim_agent.products.patientsim.core.reference_data import (
    COMMON_DIAGNOSES,
    LAB_TESTS,
    MEDICATIONS,
    VITAL_RANGES,
    ICD10Code,
    get_lab_test,
    get_medication,
)


class PatientGenerator(BaseGenerator):
    """Generate synthetic patient data with medically plausible relationships."""

    def __init__(self, seed: int | None = None, locale: str = "en_US") -> None:
        super().__init__(seed=seed, locale=locale)
        self.seed = seed

    def generate_patient(
        self,
        age_range: tuple[int, int] | None = None,
        gender: Gender | None = None,
        age_distribution: AgeDistribution | None = None,
    ) -> Patient:
        """Generate a single patient with demographics."""
        if age_distribution is not None:
            age = age_distribution.sample()
        else:
            age_min, age_max = age_range if age_range else (18, 85)
            age = self.random_int(age_min, age_max)

        birth_date = date.today() - timedelta(days=age * 365 + self.random_int(0, 364))

        if gender is None:
            gender = self.random_choice(list(Gender))

        if gender == Gender.MALE:
            given_name = self.faker.first_name_male()
        elif gender == Gender.FEMALE:
            given_name = self.faker.first_name_female()
        else:
            given_name = self.faker.first_name()

        family_name = self.faker.last_name()
        middle_name = self.faker.first_name()[0] if self.random_bool(0.5) else None

        name = PersonName(
            given_name=given_name,
            middle_name=middle_name,
            family_name=family_name,
        )

        patient_id = f"patient-{self.random_int(100000, 999999)}"
        mrn = f"MRN{self.random_int(100000, 999999)}"
        ssn = f"{self.random_int(100, 999)}{self.random_int(10, 99)}{self.random_int(1000, 9999)}"

        address = Address(
            street_address=self.faker.street_address(),
            city=self.faker.city(),
            state=self.faker.state_abbr(),
            postal_code=self.faker.postcode(),
            country="US",
        )

        contact = ContactInfo(
            phone=self.faker.phone_number(),
            email=self.faker.email(),
        )

        races = ["White", "Black or African American", "Asian", "Hispanic or Latino", "Other"]
        race = self.random_choice(races)

        return Patient(
            id=patient_id,
            mrn=mrn,
            ssn=ssn,
            name=name,
            birth_date=birth_date,
            gender=gender,
            address=address,
            contact=contact,
            race=race,
        )

    def generate_encounter(
        self,
        patient: Patient,
        encounter_class: EncounterClass | None = None,
        admission_date: datetime | None = None,
        length_of_stay_days: int | None = None,
    ) -> Encounter:
        """Generate a clinical encounter for a patient."""
        if encounter_class is None:
            encounter_class = self.random_choice(list(EncounterClass))

        if admission_date is None:
            days_ago = self.random_int(0, 30)
            admission_time = datetime.now() - timedelta(days=days_ago, hours=self.random_int(0, 23))
        else:
            admission_time = admission_date

        if length_of_stay_days is None:
            if encounter_class == EncounterClass.INPATIENT:
                length_of_stay_days = self.random_int(2, 10)
            elif encounter_class == EncounterClass.EMERGENCY:
                length_of_stay_days = 0
            elif encounter_class == EncounterClass.OBSERVATION:
                length_of_stay_days = self.random_int(1, 2)
            else:
                length_of_stay_days = 0

        if length_of_stay_days > 0:
            discharge_time = admission_time + timedelta(
                days=length_of_stay_days, hours=self.random_int(8, 18)
            )
        else:
            discharge_time = admission_time + timedelta(hours=self.random_int(2, 8))

        if discharge_time < datetime.now():
            status = EncounterStatus.FINISHED
        else:
            status = self.random_choice([EncounterStatus.IN_PROGRESS, EncounterStatus.ARRIVED])

        encounter_id = f"V{self.random_int(100000, 999999)}"

        facilities = ["General Hospital", "Memorial Medical Center", "University Hospital"]
        departments = ["Emergency", "ICU", "Medical Floor", "Surgical Floor", "Observation"]
        facility = self.random_choice(facilities)
        department = self.random_choice(departments) if encounter_class == EncounterClass.INPATIENT else None

        return Encounter(
            encounter_id=encounter_id,
            patient_mrn=patient.mrn,
            class_code=encounter_class,
            status=status,
            admission_time=admission_time,
            discharge_time=discharge_time if status == EncounterStatus.FINISHED else None,
            facility=facility,
            department=department,
            room=f"{self.random_int(100, 999)}" if department else None,
            bed=f"{self.random_choice(['A', 'B', 'C', 'D'])}" if department else None,
        )

    def generate_diagnosis(
        self,
        patient: Patient,
        encounter: Encounter | None = None,
        category: str | None = None,
        diagnosis_code: ICD10Code | None = None,
    ) -> Diagnosis:
        """Generate a diagnosis for a patient."""
        selected_code: ICD10Code
        if diagnosis_code is None:
            if category:
                available = [d for d in COMMON_DIAGNOSES if d.category == category]
                if not available:
                    raise ValueError(f"No diagnoses found for category: {category}")
                selected_code = self.random_choice(available)
            else:
                selected_code = self.random_choice(COMMON_DIAGNOSES)
        else:
            selected_code = diagnosis_code

        days_ago = self.random_int(1, 365)
        diagnosed_date = date.today() - timedelta(days=days_ago)
        diag_type = self.random_choice(list(DiagnosisType))

        return Diagnosis(
            code=selected_code.code,
            description=selected_code.description,
            type=diag_type,
            patient_mrn=patient.mrn,
            encounter_id=encounter.encounter_id if encounter else None,
            diagnosed_date=diagnosed_date,
        )

    def generate_lab_result(
        self,
        patient: Patient,
        encounter: Encounter | None = None,
        test_name: str | None = None,
        make_abnormal: bool = False,
    ) -> LabResult:
        """Generate a lab result for a patient."""
        if test_name:
            test = get_lab_test(test_name)
            if not test:
                raise ValueError(f"Unknown lab test: {test_name}")
        else:
            test = self.random_choice(LAB_TESTS)

        if make_abnormal:
            if self.random_bool(0.5):
                value = round(self.random_float(test.normal_max * 1.1, test.normal_max * 1.5), 1)
                abnormal_flag = "H" if value < test.normal_max * 1.3 else "HH"
            else:
                value = round(self.random_float(test.normal_min * 0.5, test.normal_min * 0.9), 1)
                abnormal_flag = "L" if value > test.normal_min * 0.7 else "LL"
        else:
            value = round(self.random_float(test.normal_min, test.normal_max), 1)
            abnormal_flag = None

        if encounter:
            collected_time = encounter.admission_time + timedelta(hours=self.random_int(1, 4))
            resulted_time = collected_time + timedelta(hours=self.random_int(2, 6))
        else:
            collected_time = datetime.now() - timedelta(days=self.random_int(0, 7))
            resulted_time = collected_time + timedelta(hours=self.random_int(2, 6))

        return LabResult(
            test_name=test.name,
            loinc_code=test.loinc_code,
            value=str(value),
            unit=test.unit,
            reference_range=f"{test.normal_min}-{test.normal_max}",
            abnormal_flag=abnormal_flag,
            patient_mrn=patient.mrn,
            encounter_id=encounter.encounter_id if encounter else None,
            collected_time=collected_time,
            resulted_time=resulted_time,
        )

    def generate_vital_signs(
        self,
        patient: Patient,
        encounter: Encounter | None = None,
        abnormal_parameters: list[str] | None = None,
    ) -> VitalSign:
        """Generate vital signs for a patient."""
        age_group = "adult" if patient.age >= 18 else "pediatric"
        ranges = VITAL_RANGES[age_group]

        if encounter:
            observation_time = encounter.admission_time + timedelta(minutes=self.random_int(15, 60))
        else:
            observation_time = datetime.now() - timedelta(days=self.random_int(0, 7))

        abnormal = abnormal_parameters or []

        if "temperature" in abnormal:
            temperature = round(self.random_float(100.5, 103.0), 1)
        else:
            temperature = round(self.random_float(*ranges["temperature"]), 1)

        if "heart_rate" in abnormal:
            heart_rate = self.random_int(110, 140)
        else:
            hr_range = ranges["heart_rate"]
            heart_rate = self.random_int(int(hr_range[0]), int(hr_range[1]))

        if "respiratory_rate" in abnormal:
            respiratory_rate = self.random_int(24, 32)
        else:
            rr_range = ranges["respiratory_rate"]
            respiratory_rate = self.random_int(int(rr_range[0]), int(rr_range[1]))

        if "blood_pressure" in abnormal:
            systolic_bp = self.random_int(160, 190)
            diastolic_bp = self.random_int(95, 110)
        else:
            sbp_range = ranges["systolic_bp"]
            dbp_range = ranges["diastolic_bp"]
            systolic_bp = self.random_int(int(sbp_range[0]), int(sbp_range[1]))
            diastolic_bp = self.random_int(int(dbp_range[0]), int(dbp_range[1]))

        if "spo2" in abnormal:
            spo2 = self.random_int(85, 92)
        else:
            spo2_range = ranges["spo2"]
            spo2 = self.random_int(int(spo2_range[0]), int(spo2_range[1]))

        height_cm = self.random_int(150, 190)
        weight_kg = self.random_int(50, 120)

        return VitalSign(
            patient_mrn=patient.mrn,
            encounter_id=encounter.encounter_id if encounter else None,
            observation_time=observation_time,
            temperature=temperature,
            heart_rate=heart_rate,
            respiratory_rate=respiratory_rate,
            systolic_bp=systolic_bp,
            diastolic_bp=diastolic_bp,
            spo2=spo2,
            height_cm=height_cm,
            weight_kg=weight_kg,
        )

    def generate_medication(
        self,
        patient: Patient,
        encounter: Encounter | None = None,
        medication_name: str | None = None,
    ) -> Medication:
        """Generate a medication order for a patient."""
        if medication_name:
            med_info = get_medication(medication_name)
            if not med_info:
                raise ValueError(f"Unknown medication: {medication_name}")
        else:
            med_info = self.random_choice(MEDICATIONS)

        dose = self.random_choice(med_info.common_doses)
        route = self.random_choice(med_info.routes)
        frequency = self.random_choice(med_info.frequencies)

        if encounter:
            start_date = encounter.admission_time
        else:
            start_date = datetime.now() - timedelta(days=self.random_int(1, 365))

        status = self.weighted_choice([
            (MedicationStatus.ACTIVE, 0.7),
            (MedicationStatus.COMPLETED, 0.2),
            (MedicationStatus.STOPPED, 0.1),
        ])

        end_date = None
        if status != MedicationStatus.ACTIVE:
            end_date = start_date + timedelta(days=self.random_int(1, 90))

        return Medication(
            name=med_info.name,
            code=med_info.rxnorm_code,
            dose=dose,
            route=route,
            frequency=frequency,
            patient_mrn=patient.mrn,
            encounter_id=encounter.encounter_id if encounter else None,
            start_date=start_date,
            end_date=end_date,
            status=status,
            indication=med_info.indication,
        )


def generate_patient(seed: int | None = None, **kwargs: Any) -> Patient:
    """Convenience function to generate a single patient."""
    gen = PatientGenerator(seed=seed)
    return gen.generate_patient(**kwargs)


# Backward compatibility
PatientFactory = PatientGenerator


__all__ = [
    "PatientGenerator",
    "PatientFactory",
    "generate_patient",
]
