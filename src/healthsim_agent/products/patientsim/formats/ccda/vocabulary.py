"""C-CDA vocabulary utilities.

Provides code system definitions, ICD-10 to SNOMED mappings, and
vocabulary lookup utilities for C-CDA generation.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


@dataclass
class CodedValue:
    """Represents a coded value with optional translation."""

    code: str
    display_name: str
    code_system: str
    code_system_name: str
    translation: CodedValue | None = None

    def to_xml(self, xsi_type: str = "CD", include_translation: bool = True) -> str:
        """Generate XML representation of the coded value."""
        translation_xml = ""
        if include_translation and self.translation:
            translation_xml = (
                f'\n  <translation code="{self.translation.code}" '
                f'codeSystem="{self.translation.code_system}" '
                f'codeSystemName="{self.translation.code_system_name}" '
                f'displayName="{self.translation.display_name}"/>'
            )

        return (
            f'<value xsi:type="{xsi_type}" '
            f'code="{self.code}" '
            f'codeSystem="{self.code_system}" '
            f'codeSystemName="{self.code_system_name}" '
            f'displayName="{self.display_name}">'
            f"{translation_xml}"
            f"</value>"
        )

    def to_code_xml(self) -> str:
        """Generate XML for a code element (not value)."""
        return (
            f'<code code="{self.code}" '
            f'codeSystem="{self.code_system}" '
            f'codeSystemName="{self.code_system_name}" '
            f'displayName="{self.display_name}"/>'
        )


CODE_SYSTEMS: dict[str, tuple[str, str]] = {
    "SNOMED": ("2.16.840.1.113883.6.96", "SNOMED CT"),
    "RXNORM": ("2.16.840.1.113883.6.88", "RxNorm"),
    "LOINC": ("2.16.840.1.113883.6.1", "LOINC"),
    "ICD10CM": ("2.16.840.1.113883.6.90", "ICD-10-CM"),
    "ICD10": ("2.16.840.1.113883.6.90", "ICD-10-CM"),
    "CPT": ("2.16.840.1.113883.6.12", "CPT"),
    "CVX": ("2.16.840.1.113883.12.292", "CVX"),
    "NDC": ("2.16.840.1.113883.6.69", "NDC"),
    "UCUM": ("2.16.840.1.113883.6.8", "UCUM"),
    "HCPCS": ("2.16.840.1.113883.6.285", "HCPCS"),
    "ICD10PCS": ("2.16.840.1.113883.6.4", "ICD-10-PCS"),
    "HL7_ACT_CODE": ("2.16.840.1.113883.5.4", "ActCode"),
    "HL7_ROUTE": ("2.16.840.1.113883.5.112", "RouteOfAdministration"),
    "HL7_GENDER": ("2.16.840.1.113883.5.1", "AdministrativeGender"),
    "HL7_NULL_FLAVOR": ("2.16.840.1.113883.5.1008", "NullFlavor"),
    "HL7_CONFIDENTIALITY": ("2.16.840.1.113883.5.25", "Confidentiality"),
    "HL7_OBSERVATION_INTERP": ("2.16.840.1.113883.5.83", "ObservationInterpretation"),
}


@dataclass
class SNOMEDMapping:
    """Mapping from ICD-10 to SNOMED CT code."""
    icd10_code: str
    icd10_display: str
    snomed_code: str
    snomed_display: str
    domain: str = ""


class CodeSystemRegistry:
    """Registry for code system lookups and ICD-10 to SNOMED mappings."""

    DEFAULT_MAPPINGS_PATH: ClassVar[str] = "references/ccda/ccda-snomed-problem-mappings.csv"

    def __init__(self) -> None:
        self._snomed_mappings: dict[str, SNOMEDMapping] = {}
        self._loaded = False

    def load_mappings(self, csv_path: str | Path | None = None) -> None:
        """Load ICD-10 to SNOMED mappings from CSV file."""
        if csv_path:
            path = Path(csv_path)
        else:
            possible_paths = [
                Path(__file__).parent / "data" / "ccda-snomed-problem-mappings.csv",
            ]
            path = None
            for p in possible_paths:
                if p.exists():
                    path = p
                    break
            if path is None:
                self._loaded = True
                return

        if not path.exists():
            raise FileNotFoundError(f"Mappings file not found: {path}")

        self._load_csv(path)
        self._loaded = True

    def _load_csv(self, path: Path) -> None:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                icd10_code = row.get("icd10_code", "").strip()
                if icd10_code:
                    mapping = SNOMEDMapping(
                        icd10_code=icd10_code,
                        icd10_display=row.get("icd10_display", "").strip(),
                        snomed_code=row.get("snomed_code", "").strip(),
                        snomed_display=row.get("snomed_display", "").strip(),
                        domain=row.get("domain", "").strip(),
                    )
                    self._snomed_mappings[icd10_code] = mapping

    def get_snomed_for_icd10(self, icd10_code: str) -> CodedValue | None:
        """Look up SNOMED code for an ICD-10 code."""
        if not self._loaded:
            try:
                self.load_mappings()
            except FileNotFoundError:
                return None

        mapping = self._snomed_mappings.get(icd10_code)
        if not mapping:
            return None

        snomed_oid, snomed_name = CODE_SYSTEMS["SNOMED"]
        icd10_oid, icd10_name = CODE_SYSTEMS["ICD10CM"]

        return CodedValue(
            code=mapping.snomed_code,
            display_name=mapping.snomed_display,
            code_system=snomed_oid,
            code_system_name=snomed_name,
            translation=CodedValue(
                code=mapping.icd10_code,
                display_name=mapping.icd10_display,
                code_system=icd10_oid,
                code_system_name=icd10_name,
            ),
        )

    def get_icd10_only(self, icd10_code: str, display: str) -> CodedValue:
        """Create CodedValue for ICD-10 code without SNOMED mapping."""
        icd10_oid, icd10_name = CODE_SYSTEMS["ICD10CM"]
        return CodedValue(
            code=icd10_code,
            display_name=display,
            code_system=icd10_oid,
            code_system_name=icd10_name,
        )

    def has_mapping(self, icd10_code: str) -> bool:
        if not self._loaded:
            try:
                self.load_mappings()
            except FileNotFoundError:
                return False
        return icd10_code in self._snomed_mappings

    @property
    def mapping_count(self) -> int:
        return len(self._snomed_mappings)


def get_code_system(name: str) -> tuple[str, str]:
    """Get code system OID and display name by name."""
    name_upper = name.upper().replace("-", "").replace("_", "")
    if name_upper in CODE_SYSTEMS:
        return CODE_SYSTEMS[name_upper]
    variations = {"SNOMEDCT": "SNOMED", "ICD10CM": "ICD10CM", "ICD10": "ICD10CM", "ICD": "ICD10CM"}
    if name_upper in variations:
        return CODE_SYSTEMS[variations[name_upper]]
    raise KeyError(f"Unknown code system: {name}")


def create_loinc_code(code: str, display: str) -> CodedValue:
    oid, name = CODE_SYSTEMS["LOINC"]
    return CodedValue(code=code, display_name=display, code_system=oid, code_system_name=name)


def create_snomed_code(code: str, display: str) -> CodedValue:
    oid, name = CODE_SYSTEMS["SNOMED"]
    return CodedValue(code=code, display_name=display, code_system=oid, code_system_name=name)


def create_rxnorm_code(code: str, display: str) -> CodedValue:
    oid, name = CODE_SYSTEMS["RXNORM"]
    return CodedValue(code=code, display_name=display, code_system=oid, code_system_name=name)


VITAL_SIGNS_LOINC: dict[str, tuple[str, str, str]] = {
    "systolic_bp": ("8480-6", "Systolic blood pressure", "mm[Hg]"),
    "diastolic_bp": ("8462-4", "Diastolic blood pressure", "mm[Hg]"),
    "heart_rate": ("8867-4", "Heart rate", "/min"),
    "respiratory_rate": ("9279-1", "Respiratory rate", "/min"),
    "temperature_f": ("8310-5", "Body temperature", "[degF]"),
    "temperature_c": ("8310-5", "Body temperature", "Cel"),
    "spo2": ("2708-6", "Oxygen saturation", "%"),
    "height_in": ("8302-2", "Body height", "[in_i]"),
    "height_cm": ("8302-2", "Body height", "cm"),
    "weight_lb": ("29463-7", "Body weight", "[lb_av]"),
    "weight_kg": ("29463-7", "Body weight", "kg"),
    "bmi": ("39156-5", "Body mass index", "kg/m2"),
}


def get_vital_loinc(vital_type: str) -> tuple[str, str, str] | None:
    return VITAL_SIGNS_LOINC.get(vital_type.lower())
