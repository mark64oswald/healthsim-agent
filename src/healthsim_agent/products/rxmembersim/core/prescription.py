"""Prescription model.

Ported from: healthsim-workspace/packages/rxmembersim/src/rxmembersim/core/prescription.py
"""

from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class DAWCode(str, Enum):
    """Dispense As Written codes."""
    NO_SELECTION = "0"
    SUBSTITUTION_NOT_ALLOWED = "1"
    PATIENT_REQUESTED_BRAND = "2"
    PHARMACIST_SELECTED = "3"
    GENERIC_NOT_IN_STOCK = "4"
    BRAND_DISPENSED_GENERIC_PRICE = "5"
    OVERRIDE = "6"
    BRAND_MANDATED_BY_LAW = "7"
    GENERIC_NOT_AVAILABLE = "8"
    OTHER = "9"


class Prescription(BaseModel):
    """Prescription information."""
    prescription_number: str

    ndc: str
    drug_name: str
    quantity_prescribed: Decimal
    days_supply: int
    refills_authorized: int
    refills_remaining: int

    prescriber_npi: str
    prescriber_name: str | None = None
    prescriber_dea: str | None = None

    written_date: date
    expiration_date: date

    daw_code: DAWCode = DAWCode.NO_SELECTION

    diagnosis_codes: list[str] = Field(default_factory=list)
    directions: str | None = None


__all__ = ["DAWCode", "Prescription"]
