"""C-CDA validation utilities.

Provides validation for C-CDA documents and section content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationError:
    """Represents a validation error."""

    path: str
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationResult:
    """Result of C-CDA validation."""

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    def add_error(self, path: str, message: str) -> None:
        self.errors.append(ValidationError(path, message, "error"))
        self.is_valid = False

    def add_warning(self, path: str, message: str) -> None:
        self.warnings.append(ValidationError(path, message, "warning"))


class CCDAValidator:
    """Validates C-CDA document structure and content."""

    # Required template OIDs for C-CDA R2.1
    REQUIRED_TEMPLATES = {
        "us_realm": "2.16.840.1.113883.10.20.22.1.1",
        "ccd": "2.16.840.1.113883.10.20.22.1.2",
    }

    # OID pattern
    OID_PATTERN = re.compile(r"^[0-2](\.[1-9]\d*)+$")

    # Date patterns
    DATE_PATTERN = re.compile(r"^\d{8}(\d{6})?$")

    def validate_document(self, xml_content: str) -> ValidationResult:
        """Validate a complete C-CDA document."""
        result = ValidationResult(is_valid=True)

        # Check XML declaration
        if not xml_content.startswith('<?xml'):
            result.add_error("document", "Missing XML declaration")

        # Check for ClinicalDocument root
        if "<ClinicalDocument" not in xml_content:
            result.add_error("document", "Missing ClinicalDocument root element")

        # Check for required namespaces
        if 'xmlns="urn:hl7-org:v3"' not in xml_content:
            result.add_error("document", "Missing HL7 v3 namespace")

        # Check for required sections
        if "<realmCode" not in xml_content:
            result.add_warning("document", "Missing realmCode element")

        if "<typeId" not in xml_content:
            result.add_error("document", "Missing typeId element")

        if "<templateId" not in xml_content:
            result.add_error("document", "Missing templateId element")

        # Check for structuredBody
        if "<structuredBody>" not in xml_content:
            result.add_warning("document", "Missing structuredBody - document has no clinical content")

        return result

    def validate_oid(self, oid: str) -> bool:
        """Validate an OID format."""
        if not oid:
            return False
        return bool(self.OID_PATTERN.match(oid))

    def validate_date(self, date_str: str) -> bool:
        """Validate a CDA date format (YYYYMMDD or YYYYMMDDHHMMSS)."""
        if not date_str:
            return False
        return bool(self.DATE_PATTERN.match(date_str))

    def validate_patient(self, patient: Any) -> ValidationResult:
        """Validate patient data for C-CDA generation."""
        result = ValidationResult(is_valid=True)

        if not hasattr(patient, "given_name") or not patient.given_name:
            result.add_error("patient.given_name", "Patient given name is required")

        if not hasattr(patient, "family_name") or not patient.family_name:
            result.add_error("patient.family_name", "Patient family name is required")

        if not hasattr(patient, "birth_date") or not patient.birth_date:
            result.add_warning("patient.birth_date", "Patient birth date is recommended")

        if not hasattr(patient, "gender") or not patient.gender:
            result.add_warning("patient.gender", "Patient gender is recommended")

        # Check for MRN or patient_id
        mrn = getattr(patient, "mrn", None) or getattr(patient, "patient_id", None)
        if not mrn:
            result.add_error("patient.mrn", "Patient identifier (MRN) is required")

        return result

    def validate_diagnosis(self, diagnosis: Any) -> ValidationResult:
        """Validate diagnosis data for Problems section."""
        result = ValidationResult(is_valid=True)

        if not hasattr(diagnosis, "code") or not diagnosis.code:
            result.add_error("diagnosis.code", "Diagnosis code is required")

        if not hasattr(diagnosis, "description") or not diagnosis.description:
            result.add_warning("diagnosis.description", "Diagnosis description is recommended")

        return result

    def validate_medication(self, medication: Any) -> ValidationResult:
        """Validate medication data for Medications section."""
        result = ValidationResult(is_valid=True)

        if not hasattr(medication, "drug_name") or not medication.drug_name:
            result.add_error("medication.drug_name", "Medication drug name is required")

        if not getattr(medication, "rxnorm_code", None):
            result.add_warning("medication.rxnorm_code", "RxNorm code is recommended for interoperability")

        return result

    def validate_lab_result(self, lab: Any) -> ValidationResult:
        """Validate lab result data for Results section."""
        result = ValidationResult(is_valid=True)

        if not hasattr(lab, "test_name") or not lab.test_name:
            result.add_error("lab.test_name", "Lab test name is required")

        if not hasattr(lab, "value"):
            result.add_error("lab.value", "Lab result value is required")

        if not getattr(lab, "loinc_code", None):
            result.add_warning("lab.loinc_code", "LOINC code is recommended for interoperability")

        return result
