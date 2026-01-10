"""FHIR R4 transformer.

Ported from: healthsim-workspace/packages/patientsim/src/patientsim/formats/fhir/transformer.py
"""

import uuid
from datetime import datetime

from healthsim_agent.products.patientsim.core.models import (
    Diagnosis,
    Encounter,
    LabResult,
    Patient,
    VitalSign,
)
from healthsim_agent.products.patientsim.formats.fhir.resources import (
    Bundle,
    BundleEntry,
    CodeableConcept,
    CodeSystems,
    ConditionResource,
    EncounterResource,
    HumanName,
    Identifier,
    ObservationResource,
    PatientResource,
    Period,
    Quantity,
    Reference,
    create_codeable_concept,
    get_loinc_code,
    get_vital_loinc,
)


class FHIRTransformer:
    """Transforms PatientSim objects to FHIR R4 resources."""

    def __init__(self) -> None:
        self._resource_id_map: dict[str, str] = {}

    def _get_resource_id(self, resource_type: str, source_id: str) -> str:
        key = f"{resource_type}/{source_id}"
        if key not in self._resource_id_map:
            self._resource_id_map[key] = str(uuid.uuid5(uuid.NAMESPACE_DNS, source_id))
        return self._resource_id_map[key]

    def transform_patient(self, patient: Patient) -> PatientResource:
        """Transform Patient to FHIR Patient resource."""
        resource_id = self._get_resource_id("Patient", patient.mrn)

        name = HumanName(
            use="official",
            family=patient.name.family_name if patient.name else "",
            given=[patient.name.given_name] if patient.name else [],
            text=f"{patient.name.given_name} {patient.name.family_name}" if patient.name else "",
        )

        identifier = Identifier(system=CodeSystems.PATIENT_MRN, value=patient.mrn, use="usual")

        gender_map = {"M": "male", "F": "female", "O": "other", "U": "unknown"}
        gender_val = patient.gender.value if hasattr(patient.gender, "value") else str(patient.gender)
        gender = gender_map.get(gender_val, "unknown")

        birth_date = patient.birth_date.isoformat() if patient.birth_date else None

        return PatientResource(
            id=resource_id,
            identifier=[identifier],
            name=[name],
            gender=gender,
            birthDate=birth_date,
        )

    def transform_encounter(self, encounter: Encounter) -> EncounterResource:
        """Transform Encounter to FHIR Encounter resource."""
        resource_id = self._get_resource_id("Encounter", encounter.encounter_id)
        patient_id = self._get_resource_id("Patient", encounter.patient_mrn)

        identifier = Identifier(system=CodeSystems.ENCOUNTER_ID, value=encounter.encounter_id)

        status_val = encounter.status.value if hasattr(encounter.status, "value") else str(encounter.status)
        status_map = {"planned": "planned", "in-progress": "in-progress", "finished": "finished", "cancelled": "cancelled"}
        status = status_map.get(status_val, "finished")

        class_val = encounter.class_code.value if hasattr(encounter.class_code, "value") else str(encounter.class_code)
        class_map = {
            "inpatient": ("IMP", "inpatient encounter"),
            "outpatient": ("AMB", "ambulatory"),
            "emergency": ("EMER", "emergency"),
            "observation": ("OBSENC", "observation encounter"),
        }
        class_code, class_display = class_map.get(class_val, ("AMB", "ambulatory"))

        encounter_class = create_codeable_concept(CodeSystems.ENCOUNTER_CLASS, class_code, class_display)

        subject = Reference(reference=f"Patient/{patient_id}", display=f"Patient {encounter.patient_mrn}")

        period = None
        if encounter.admission_time:
            period = Period(
                start=encounter.admission_time.isoformat(),
                end=encounter.discharge_time.isoformat() if encounter.discharge_time else None,
            )

        return EncounterResource(
            id=resource_id,
            identifier=[identifier],
            status=status,
            **{"class": encounter_class},
            subject=subject,
            period=period,
        )

    def transform_condition(self, diagnosis: Diagnosis) -> ConditionResource:
        """Transform Diagnosis to FHIR Condition resource."""
        diag_id = f"{diagnosis.patient_mrn}-{diagnosis.code}"
        resource_id = self._get_resource_id("Condition", diag_id)
        patient_id = self._get_resource_id("Patient", diagnosis.patient_mrn)

        clinical_status = create_codeable_concept(CodeSystems.CONDITION_CLINICAL, "active", "Active")
        verification_status = create_codeable_concept(CodeSystems.CONDITION_VERIFICATION, "confirmed", "Confirmed")

        category = [create_codeable_concept(
            "http://terminology.hl7.org/CodeSystem/condition-category",
            "encounter-diagnosis", "Encounter Diagnosis"
        )]

        code = create_codeable_concept(CodeSystems.ICD10, diagnosis.code, diagnosis.description)
        subject = Reference(reference=f"Patient/{patient_id}")

        encounter = None
        if diagnosis.encounter_id:
            encounter_id = self._get_resource_id("Encounter", diagnosis.encounter_id)
            encounter = Reference(reference=f"Encounter/{encounter_id}")

        return ConditionResource(
            id=resource_id,
            clinicalStatus=clinical_status,
            verificationStatus=verification_status,
            category=category,
            code=code,
            subject=subject,
            encounter=encounter,
        )

    def transform_lab_observation(self, lab: LabResult) -> ObservationResource | None:
        """Transform LabResult to FHIR Observation resource."""
        loinc_info = get_loinc_code(lab.test_name)
        if not loinc_info:
            return None

        loinc_code, loinc_display = loinc_info
        obs_id = f"{lab.patient_mrn}-lab-{loinc_code}"
        resource_id = self._get_resource_id("Observation", obs_id)
        patient_id = self._get_resource_id("Patient", lab.patient_mrn)

        category = [create_codeable_concept(CodeSystems.OBSERVATION_CATEGORY, "laboratory", "Laboratory")]
        code = create_codeable_concept(CodeSystems.LOINC, loinc_code, loinc_display)
        subject = Reference(reference=f"Patient/{patient_id}")

        value_quantity = None
        value_string = None
        try:
            numeric_value = float(lab.value)
            value_quantity = Quantity(value=numeric_value, unit=lab.units, system=CodeSystems.UCUM, code=lab.units)
        except (ValueError, TypeError):
            value_string = str(lab.value)

        return ObservationResource(
            id=resource_id,
            status="final",
            category=category,
            code=code,
            subject=subject,
            valueQuantity=value_quantity,
            valueString=value_string,
        )

    def transform_vital_observations(self, vital: VitalSign) -> list[ObservationResource]:
        """Transform VitalSign to FHIR Observation resources."""
        observations = []
        patient_id = self._get_resource_id("Patient", vital.patient_mrn)

        category = [create_codeable_concept(CodeSystems.OBSERVATION_CATEGORY, "vital-signs", "Vital Signs")]
        subject = Reference(reference=f"Patient/{patient_id}")

        effective_dt = vital.observation_time.isoformat() if vital.observation_time else None

        vital_mappings = [
            ("temperature", vital.temperature, "F"),
            ("heart_rate", vital.heart_rate, "bpm"),
            ("respiratory_rate", vital.respiratory_rate, "/min"),
            ("systolic_bp", vital.systolic_bp, "mm[Hg]"),
            ("diastolic_bp", vital.diastolic_bp, "mm[Hg]"),
            ("spo2", vital.spo2, "%"),
            ("height", vital.height_cm, "cm"),
            ("weight", vital.weight_kg, "kg"),
        ]

        for vital_type, value, unit in vital_mappings:
            if value is None:
                continue

            loinc_info = get_vital_loinc(vital_type)
            if not loinc_info:
                continue

            loinc_code, loinc_display = loinc_info
            obs_id = f"{vital.patient_mrn}-vital-{loinc_code}"
            resource_id = self._get_resource_id("Observation", obs_id)

            code = create_codeable_concept(CodeSystems.LOINC, loinc_code, loinc_display)
            value_quantity = Quantity(value=float(value), unit=unit, system=CodeSystems.UCUM, code=unit)

            obs = ObservationResource(
                id=resource_id,
                status="final",
                category=category,
                code=code,
                subject=subject,
                effectiveDateTime=effective_dt,
                valueQuantity=value_quantity,
            )
            observations.append(obs)

        return observations

    def create_bundle(
        self,
        patients: list[Patient] | None = None,
        encounters: list[Encounter] | None = None,
        diagnoses: list[Diagnosis] | None = None,
        labs: list[LabResult] | None = None,
        vitals: list[VitalSign] | None = None,
        bundle_type: str = "collection",
    ) -> Bundle:
        """Create a FHIR Bundle containing all resources."""
        entries = []

        if patients:
            for patient in patients:
                resource = self.transform_patient(patient)
                entry = BundleEntry(
                    fullUrl=f"urn:uuid:{resource.id}",
                    resource=resource.model_dump(by_alias=True, exclude_none=True),
                )
                entries.append(entry)

        if encounters:
            for encounter in encounters:
                resource = self.transform_encounter(encounter)
                entry = BundleEntry(
                    fullUrl=f"urn:uuid:{resource.id}",
                    resource=resource.model_dump(by_alias=True, exclude_none=True),
                )
                entries.append(entry)

        if diagnoses:
            for diagnosis in diagnoses:
                resource = self.transform_condition(diagnosis)
                entry = BundleEntry(
                    fullUrl=f"urn:uuid:{resource.id}",
                    resource=resource.model_dump(by_alias=True, exclude_none=True),
                )
                entries.append(entry)

        if labs:
            for lab in labs:
                resource = self.transform_lab_observation(lab)
                if resource:
                    entry = BundleEntry(
                        fullUrl=f"urn:uuid:{resource.id}",
                        resource=resource.model_dump(by_alias=True, exclude_none=True),
                    )
                    entries.append(entry)

        if vitals:
            for vital in vitals:
                vital_obs = self.transform_vital_observations(vital)
                for resource in vital_obs:
                    entry = BundleEntry(
                        fullUrl=f"urn:uuid:{resource.id}",
                        resource=resource.model_dump(by_alias=True, exclude_none=True),
                    )
                    entries.append(entry)

        bundle = Bundle(
            id=str(uuid.uuid4()),
            type=bundle_type,
            timestamp=datetime.now().isoformat(),
            entry=entries,
        )

        return bundle


__all__ = ["FHIRTransformer"]
