"""Generators for clinical trial entities.

Enhanced with:
- Consistent XxxGenerator naming
- VitalSignGenerator, LabResultGenerator, MedicalHistoryGenerator
- ConcomitantMedicationGenerator, EligibilityGenerator
- MedDRA coding integration for adverse events
- Reference data integration for labs and vitals
"""

import random
from datetime import date, timedelta
from typing import Any

from faker import Faker

from healthsim_agent.products.trialsim.core.models import (
    AdverseEvent,
    AECausality,
    AEOutcome,
    AESeverity,
    ArmType,
    ConcomitantMedication,
    CriterionType,
    EligibilityCriterion,
    Exposure,
    LabCategory,
    LabResult,
    MedicalHistory,
    Subject,
    SubjectStatus,
    Visit,
    VisitType,
    VitalSign,
)

from healthsim_agent.products.trialsim.core.reference_data import (
    MEDDRA_ADVERSE_EVENTS,
    LAB_TESTS,
    VITAL_SIGNS,
    CONCOMITANT_MEDICATIONS,
    MEDICAL_HISTORY_ITEMS,
    get_meddra_for_ae,
    get_lab_reference,
)


class SubjectGenerator:
    """Generate synthetic trial subjects."""

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.random = random.Random(seed)
        self.faker = Faker()
        if seed is not None:
            Faker.seed(seed)

    def generate(
        self,
        protocol_id: str = "PROTO-001",
        site_id: str = "SITE-001",
        arm: ArmType | None = None,
        **kwargs: Any,
    ) -> Subject:
        """Generate a single trial subject."""
        age = kwargs.get("age", self.random.randint(18, 75))
        sex = kwargs.get("sex", self.random.choice(["M", "F"]))

        races = ["White", "Black or African American", "Asian", "American Indian or Alaska Native", "Native Hawaiian or Pacific Islander", "Other", "Multiple"]
        ethnicities = ["Hispanic or Latino", "Not Hispanic or Latino"]

        return Subject(
            protocol_id=protocol_id,
            site_id=site_id,
            age=age,
            sex=sex,
            race=self.random.choice(races),
            ethnicity=self.random.choice(ethnicities),
            arm=arm,
            status=SubjectStatus.SCREENING,
            screening_date=date.today(),
        )

    def generate_many(
        self,
        count: int,
        protocol_id: str = "PROTO-001",
        sites: list[str] | None = None,
        arms: list[str] | None = None,
        **kwargs: Any,
    ) -> list[Subject]:
        """Generate multiple trial subjects."""
        if sites is None:
            sites = ["SITE-001"]

        subjects = []
        for _ in range(count):
            site_id = self.random.choice(sites)
            arm = None
            if arms:
                arm_str = self.random.choice(arms)
                arm = ArmType(arm_str) if arm_str in [a.value for a in ArmType] else None

            subject = self.generate(protocol_id=protocol_id, site_id=site_id, arm=arm, **kwargs)
            subjects.append(subject)

        return subjects


class VisitGenerator:
    """Generate visit records for trial subjects."""

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.random = random.Random(seed)

    def generate_schedule(
        self,
        subject: Subject,
        protocol_phase: str = "phase3",
        duration_weeks: int = 52,
        start_date: date | None = None,
    ) -> list[Visit]:
        """Generate a complete visit schedule for a subject."""
        if start_date is None:
            start_date = date.today()

        visits = []
        visit_num = 1

        # Screening visit
        visits.append(Visit(
            subject_id=subject.subject_id,
            protocol_id=subject.protocol_id,
            site_id=subject.site_id,
            visit_number=visit_num,
            visit_name="Screening",
            visit_type=VisitType.SCREENING,
            planned_date=start_date,
            actual_date=start_date,
            visit_status="completed",
            assessments=["Informed Consent", "Demographics", "Medical History", "Eligibility"],
        ))
        visit_num += 1

        # Baseline/Randomization
        baseline_date = start_date + timedelta(days=self.random.randint(7, 21))
        visits.append(Visit(
            subject_id=subject.subject_id,
            protocol_id=subject.protocol_id,
            site_id=subject.site_id,
            visit_number=visit_num,
            visit_name="Baseline/Randomization",
            visit_type=VisitType.RANDOMIZATION,
            planned_date=baseline_date,
            actual_date=baseline_date,
            visit_status="completed",
            assessments=["Vitals", "Labs", "Physical Exam", "Randomization"],
        ))
        visit_num += 1

        # Scheduled visits
        visit_interval = 4
        week = visit_interval

        while week <= duration_weeks:
            current_date = baseline_date + timedelta(weeks=week)
            visit_name = f"Week {week}"

            actual_offset = self.random.randint(-3, 3)
            actual = current_date + timedelta(days=actual_offset)

            visits.append(Visit(
                subject_id=subject.subject_id,
                protocol_id=subject.protocol_id,
                site_id=subject.site_id,
                visit_number=visit_num,
                visit_name=visit_name,
                visit_type=VisitType.SCHEDULED,
                planned_date=current_date,
                actual_date=actual,
                visit_status="completed" if week < 24 else "scheduled",
                assessments=["Vitals", "AE Assessment", "Concomitant Meds"],
            ))
            visit_num += 1
            week += visit_interval

        # End of Study visit
        eos_date = baseline_date + timedelta(weeks=duration_weeks)
        visits.append(Visit(
            subject_id=subject.subject_id,
            protocol_id=subject.protocol_id,
            site_id=subject.site_id,
            visit_number=visit_num,
            visit_name="End of Study",
            visit_type=VisitType.END_OF_STUDY,
            planned_date=eos_date,
            visit_status="scheduled",
            assessments=["Vitals", "Labs", "Physical Exam", "End of Study Assessment"],
        ))

        return visits


class AdverseEventGenerator:
    """Generate adverse events with MedDRA coding for trial subjects."""

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.random = random.Random(seed)

    def generate_for_subject(
        self,
        subject: Subject,
        visits: list[Visit] | None = None,
        ae_probability: float = 0.3,
    ) -> list[AdverseEvent]:
        """Generate adverse events for a subject with MedDRA coding."""
        aes = []
        visit_count = len(visits) if visits else 10

        for i in range(visit_count):
            if self.random.random() < ae_probability:
                # Select from MedDRA-coded AEs
                ae_ref = self.random.choice(MEDDRA_ADVERSE_EVENTS)

                severity_weights = [0.5, 0.3, 0.15, 0.04, 0.01]
                severity = self.random.choices(list(AESeverity), weights=severity_weights)[0]

                is_serious = severity in [AESeverity.GRADE_3, AESeverity.GRADE_4, AESeverity.GRADE_5]

                onset = (visits[i].actual_date if visits and visits[i].actual_date 
                        else date.today() + timedelta(days=i * 28))
                duration = self.random.randint(1, 14)

                ae = AdverseEvent(
                    subject_id=subject.subject_id,
                    protocol_id=subject.protocol_id,
                    ae_term=ae_ref["pt_name"],
                    system_organ_class=ae_ref["soc_name"],
                    meddra_pt_code=ae_ref["pt_code"],
                    meddra_pt_name=ae_ref["pt_name"],
                    meddra_soc_code=ae_ref["soc_code"],
                    meddra_llt_code=ae_ref["llt_code"],
                    onset_date=onset,
                    resolution_date=onset + timedelta(days=duration),
                    duration_days=duration,
                    severity=severity,
                    is_serious=is_serious,
                    causality=self.random.choice(list(AECausality)),
                    outcome=AEOutcome.RECOVERED if not is_serious else self.random.choice(list(AEOutcome)),
                )
                aes.append(ae)

        return aes


class ExposureGenerator:
    """Generate drug exposure records."""

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.random = random.Random(seed)

    def generate_for_subject(
        self,
        subject: Subject,
        drug_name: str = "Study Drug",
        dose: float = 100.0,
        dose_unit: str = "mg",
        duration_weeks: int = 52,
        start_date: date | None = None,
    ) -> list[Exposure]:
        """Generate exposure records for a subject."""
        if start_date is None:
            start_date = date.today()

        exposures = []
        current_date = start_date

        while current_date < start_date + timedelta(weeks=duration_weeks):
            doses_planned = 7
            compliance = self.random.uniform(0.8, 1.0)
            doses_taken = int(doses_planned * compliance)

            exposure = Exposure(
                subject_id=subject.subject_id,
                protocol_id=subject.protocol_id,
                drug_name=drug_name,
                dose=dose,
                dose_unit=dose_unit,
                start_date=current_date,
                end_date=current_date + timedelta(days=6),
                doses_planned=doses_planned,
                doses_taken=doses_taken,
                compliance_pct=round(compliance * 100, 1),
            )
            exposures.append(exposure)
            current_date += timedelta(weeks=1)

        return exposures


class VitalSignGenerator:
    """Generate vital sign measurements with reference ranges."""

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.random = random.Random(seed)

    def generate_for_visit(
        self,
        subject: Subject,
        visit: Visit,
        tests: list[str] | None = None,
    ) -> list[VitalSign]:
        """Generate vital signs for a visit."""
        if tests is None:
            tests = ["SYSBP", "DIABP", "PULSE", "RESP", "TEMP", "WEIGHT"]
        
        vitals = []
        collection_date = visit.actual_date or visit.planned_date or date.today()
        
        # Generate correlated BP values
        bp_base_normal = self.random.random() < 0.7  # 70% normal BP
        
        for test_code in tests:
            ref = next((v for v in VITAL_SIGNS if v["test"] == test_code), None)
            if not ref:
                continue
            
            # Generate value based on reference range
            low = ref["low"]
            high = ref["high"]
            
            # Add some realistic variation
            if test_code == "SYSBP":
                if bp_base_normal:
                    result = self.random.gauss((low + high) / 2, 8)
                else:
                    result = self.random.gauss(high + 15, 10)  # Elevated
            elif test_code == "DIABP":
                if bp_base_normal:
                    result = self.random.gauss((low + high) / 2, 5)
                else:
                    result = self.random.gauss(high + 8, 6)  # Elevated
            else:
                mean = (low + high) / 2
                std = (high - low) / 6
                result = self.random.gauss(mean, std)
            
            result = round(result, 1)
            
            vital = VitalSign(
                subject_id=subject.subject_id,
                protocol_id=subject.protocol_id,
                visit_id=visit.visit_id,
                vs_test=test_code,
                vs_test_name=ref["name"],
                vs_result=result,
                vs_unit=ref["unit"],
                vs_position=ref.get("position"),
                collection_date=collection_date,
            )
            vitals.append(vital)
        
        return vitals

    def generate_for_subject(
        self,
        subject: Subject,
        visits: list[Visit],
        tests: list[str] | None = None,
    ) -> list[VitalSign]:
        """Generate vital signs for all visits."""
        all_vitals = []
        for visit in visits:
            vitals = self.generate_for_visit(subject, visit, tests)
            all_vitals.extend(vitals)
        return all_vitals


class LabResultGenerator:
    """Generate laboratory results with reference ranges and LOINC codes."""

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.random = random.Random(seed)

    def generate_for_visit(
        self,
        subject: Subject,
        visit: Visit,
        panel: str = "standard",
    ) -> list[LabResult]:
        """Generate lab results for a visit.
        
        Args:
            subject: Trial subject
            visit: Visit record
            panel: Lab panel type (standard, liver, renal, lipid, hematology, comprehensive)
        """
        # Select tests based on panel
        if panel == "standard":
            tests = ["HGB", "WBC", "PLT", "ALT", "AST", "CREAT", "NA", "K", "GLUC"]
        elif panel == "liver":
            tests = ["ALT", "AST", "ALP", "TBIL", "ALB"]
        elif panel == "renal":
            tests = ["CREAT", "BUN", "EGFR", "NA", "K", "CA"]
        elif panel == "lipid":
            tests = ["CHOL", "LDL", "HDL", "TRIG"]
        elif panel == "hematology":
            tests = ["HGB", "HCT", "WBC", "PLT", "RBC", "NEUT", "LYMPH"]
        elif panel == "comprehensive":
            tests = ["HGB", "WBC", "PLT", "ALT", "AST", "ALP", "TBIL", "CREAT", "BUN", 
                    "NA", "K", "CL", "CO2", "CA", "GLUC", "CHOL"]
        else:
            tests = ["HGB", "WBC", "PLT", "ALT", "CREAT"]
        
        labs = []
        collection_date = visit.actual_date or visit.planned_date or date.today()
        sex = subject.sex
        
        for test_code in tests:
            ref = next((l for l in LAB_TESTS if l["test"] == test_code), None)
            if not ref:
                continue
            
            # Determine reference range (sex-specific if available)
            if f"low_{sex.lower()}" in ref:
                low = ref[f"low_{sex.lower()}"]
                high = ref[f"high_{sex.lower()}"]
            else:
                low = ref.get("low", 0)
                high = ref.get("high", 100)
            
            # Generate value with realistic distribution
            # 85% normal, 10% slightly abnormal, 5% significantly abnormal
            roll = self.random.random()
            if roll < 0.85:
                # Normal range
                mean = (low + high) / 2
                std = (high - low) / 6
                result = self.random.gauss(mean, std)
            elif roll < 0.95:
                # Slightly abnormal
                if self.random.random() < 0.5:
                    result = low * self.random.uniform(0.85, 0.99)
                else:
                    result = high * self.random.uniform(1.01, 1.15)
            else:
                # Significantly abnormal
                if self.random.random() < 0.5:
                    result = low * self.random.uniform(0.6, 0.84)
                else:
                    result = high * self.random.uniform(1.16, 1.5)
            
            result = round(result, 2)
            
            # Determine flag
            flag = None
            if result < low:
                flag = "L"
            elif result > high:
                flag = "H"
            else:
                flag = "N"
            
            lab = LabResult(
                subject_id=subject.subject_id,
                protocol_id=subject.protocol_id,
                visit_id=visit.visit_id,
                lb_test=test_code,
                lb_test_name=ref["name"],
                lb_category=LabCategory(ref["category"]),
                lb_spec=ref.get("specimen", "BLOOD"),
                lb_result=result,
                lb_unit=ref.get("unit"),
                lb_low=low,
                lb_high=high,
                lb_flag=flag,
                collection_date=collection_date,
                loinc_code=ref.get("loinc"),
            )
            labs.append(lab)
        
        return labs

    def generate_for_subject(
        self,
        subject: Subject,
        visits: list[Visit],
        panel: str = "standard",
    ) -> list[LabResult]:
        """Generate lab results for selected visits (screening, baseline, EOS)."""
        all_labs = []
        lab_visits = [v for v in visits if v.visit_type in 
                     [VisitType.SCREENING, VisitType.RANDOMIZATION, VisitType.END_OF_STUDY]]
        
        for visit in lab_visits:
            labs = self.generate_for_visit(subject, visit, panel)
            all_labs.extend(labs)
        
        return all_labs


class MedicalHistoryGenerator:
    """Generate medical history records with MedDRA coding."""

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.random = random.Random(seed)

    def generate_for_subject(
        self,
        subject: Subject,
        min_conditions: int = 1,
        max_conditions: int = 5,
    ) -> list[MedicalHistory]:
        """Generate medical history for a subject."""
        count = self.random.randint(min_conditions, max_conditions)
        
        # Select random conditions
        conditions = self.random.sample(MEDICAL_HISTORY_ITEMS, min(count, len(MEDICAL_HISTORY_ITEMS)))
        
        histories = []
        for cond in conditions:
            # Generate onset date (1-20 years ago)
            years_ago = self.random.randint(1, 20)
            onset = date.today() - timedelta(days=years_ago * 365)
            
            # 70% ongoing, 30% resolved
            is_ongoing = self.random.random() < 0.7
            end_date = None
            if not is_ongoing:
                days_duration = self.random.randint(30, 365 * 5)
                end_date = onset + timedelta(days=days_duration)
                if end_date > date.today():
                    end_date = date.today() - timedelta(days=self.random.randint(30, 365))
            
            mh = MedicalHistory(
                subject_id=subject.subject_id,
                protocol_id=subject.protocol_id,
                mh_term=cond["term"],
                mh_category=cond["category"],
                meddra_pt_code=cond.get("meddra_pt"),
                meddra_soc=cond.get("soc"),
                start_date=onset,
                end_date=end_date,
                is_ongoing=is_ongoing,
                is_preexisting=True,
            )
            histories.append(mh)
        
        return histories


class ConcomitantMedicationGenerator:
    """Generate concomitant medication records with ATC coding."""

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.random = random.Random(seed)

    def generate_for_subject(
        self,
        subject: Subject,
        min_meds: int = 0,
        max_meds: int = 5,
    ) -> list[ConcomitantMedication]:
        """Generate concomitant medications for a subject."""
        count = self.random.randint(min_meds, max_meds)
        
        # Select random medications
        meds = self.random.sample(CONCOMITANT_MEDICATIONS, min(count, len(CONCOMITANT_MEDICATIONS)))
        
        conmeds = []
        for med in meds:
            # Generate start date (prior to study or during)
            is_prior = self.random.random() < 0.6
            if is_prior:
                days_ago = self.random.randint(90, 365 * 5)
                start_date = date.today() - timedelta(days=days_ago)
            else:
                days_into_study = self.random.randint(1, 180)
                start_date = date.today() + timedelta(days=days_into_study)
            
            # 80% ongoing
            is_ongoing = self.random.random() < 0.8
            end_date = None
            if not is_ongoing:
                days_duration = self.random.randint(7, 90)
                end_date = start_date + timedelta(days=days_duration)
            
            cm = ConcomitantMedication(
                subject_id=subject.subject_id,
                protocol_id=subject.protocol_id,
                cm_drug=med["drug"],
                cm_class=med.get("class"),
                atc_code=med.get("atc"),
                dose=med.get("dose"),
                dose_unit=med.get("unit"),
                frequency=med.get("frequency"),
                route=med.get("route"),
                start_date=start_date,
                end_date=end_date,
                is_ongoing=is_ongoing,
                is_prior=is_prior,
            )
            conmeds.append(cm)
        
        return conmeds


class EligibilityGenerator:
    """Generate eligibility criterion assessments."""

    # Standard inclusion criteria
    INCLUSION_CRITERIA = [
        {"id": "IN01", "text": "Age >= 18 years"},
        {"id": "IN02", "text": "Confirmed diagnosis of target condition"},
        {"id": "IN03", "text": "ECOG performance status 0-2"},
        {"id": "IN04", "text": "Adequate organ function"},
        {"id": "IN05", "text": "Ability to provide informed consent"},
        {"id": "IN06", "text": "Life expectancy >= 3 months"},
        {"id": "IN07", "text": "Measurable disease per RECIST 1.1"},
    ]

    # Standard exclusion criteria
    EXCLUSION_CRITERIA = [
        {"id": "EX01", "text": "Prior treatment with study drug class"},
        {"id": "EX02", "text": "Active autoimmune disease"},
        {"id": "EX03", "text": "Known brain metastases"},
        {"id": "EX04", "text": "Pregnant or breastfeeding"},
        {"id": "EX05", "text": "Concurrent malignancy"},
        {"id": "EX06", "text": "Uncontrolled intercurrent illness"},
        {"id": "EX07", "text": "HIV positive with detectable viral load"},
        {"id": "EX08", "text": "Active hepatitis B or C"},
    ]

    def __init__(self, seed: int | None = None):
        self.seed = seed
        self.random = random.Random(seed)

    def generate_for_subject(
        self,
        subject: Subject,
        assessment_date: date | None = None,
        all_criteria_met: bool = True,
    ) -> list[EligibilityCriterion]:
        """Generate eligibility assessments for a subject.
        
        Args:
            subject: Trial subject
            assessment_date: Date of assessment (defaults to screening date)
            all_criteria_met: If True, all criteria are met; if False, one criterion fails
        """
        if assessment_date is None:
            assessment_date = subject.screening_date or date.today()
        
        criteria = []
        
        # Process inclusion criteria
        for inc in self.INCLUSION_CRITERIA:
            is_met = True
            comment = None
            
            # If not all_criteria_met, make one criterion fail
            if not all_criteria_met and inc["id"] == "IN02":
                is_met = False
                comment = "Diagnosis not confirmed by central review"
            
            ie = EligibilityCriterion(
                subject_id=subject.subject_id,
                protocol_id=subject.protocol_id,
                criterion_id=inc["id"],
                criterion_type=CriterionType.INCLUSION,
                criterion_text=inc["text"],
                is_met=is_met,
                assessment_date=assessment_date,
                comment=comment,
            )
            criteria.append(ie)
        
        # Process exclusion criteria (not met = good)
        for exc in self.EXCLUSION_CRITERIA:
            is_met = False  # Exclusion criteria should NOT be met for eligibility
            comment = None
            
            # If not all_criteria_met, make one exclusion criterion positive
            if not all_criteria_met and exc["id"] == "EX06":
                is_met = True
                comment = "Uncontrolled diabetes requiring adjustment"
            
            ie = EligibilityCriterion(
                subject_id=subject.subject_id,
                protocol_id=subject.protocol_id,
                criterion_id=exc["id"],
                criterion_type=CriterionType.EXCLUSION,
                criterion_text=exc["text"],
                is_met=is_met,
                assessment_date=assessment_date,
                comment=comment,
            )
            criteria.append(ie)
        
        return criteria


# Legacy alias for backward compatibility
TrialSubjectGenerator = SubjectGenerator


__all__ = [
    # Consistent naming
    "SubjectGenerator",
    "VisitGenerator",
    "AdverseEventGenerator",
    "ExposureGenerator",
    "VitalSignGenerator",
    "LabResultGenerator",
    "MedicalHistoryGenerator",
    "ConcomitantMedicationGenerator",
    "EligibilityGenerator",
    # Legacy alias
    "TrialSubjectGenerator",
]
