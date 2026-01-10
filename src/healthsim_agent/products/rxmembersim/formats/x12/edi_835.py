"""X12 835 Pharmacy Remittance Advice generator.

Generates payment/remittance advice for pharmacy claims using
X12 835 format with pharmacy-specific extensions.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ClaimStatus(str, Enum):
    """Claim status codes for CLP01."""

    PROCESSED_PRIMARY = "1"
    PROCESSED_SECONDARY = "2"
    PROCESSED_TERTIARY = "3"
    DENIED = "4"
    PENDED = "20"
    FORWARDED = "22"


class AdjustmentGroup(str, Enum):
    """Claim adjustment group codes."""

    CONTRACTUAL = "CO"  # Contractual obligation
    PATIENT_RESP = "PR"  # Patient responsibility
    PAYER_INITIATED = "PI"  # Payer-initiated reduction
    OTHER = "OA"  # Other adjustments


class PharmacyLinePayment(BaseModel):
    """Payment details for a pharmacy claim line."""

    prescription_number: str
    ndc: str
    drug_name: str
    quantity_dispensed: Decimal
    days_supply: int

    ingredient_cost_submitted: Decimal
    dispensing_fee_submitted: Decimal
    total_submitted: Decimal

    ingredient_cost_paid: Decimal
    dispensing_fee_paid: Decimal
    total_paid: Decimal

    patient_pay_amount: Decimal = Decimal("0")
    copay_amount: Decimal = Decimal("0")
    coinsurance_amount: Decimal = Decimal("0")
    deductible_amount: Decimal = Decimal("0")

    # Adjustments
    contractual_adjustment: Decimal = Decimal("0")
    other_adjustment: Decimal = Decimal("0")

    # Service dates
    fill_date: date | None = None


class PharmacyRemittance(BaseModel):
    """Pharmacy claim payment/remittance."""

    remit_id: str = Field(..., description="Remittance ID")
    claim_id: str = Field(..., description="Original claim ID")
    pharmacy_npi: str = Field(..., description="Pharmacy NPI")
    pharmacy_ncpdp: str = Field(..., description="Pharmacy NCPDP ID")
    pharmacy_name: str = Field(..., description="Pharmacy name")

    check_number: str | None = Field(None, description="Check/EFT number")
    payment_method: str = Field("ACH", description="Payment method")
    payment_date: date = Field(..., description="Payment date")

    payer_name: str = Field(..., description="Payer name")
    payer_id: str = Field(..., description="Payer ID")

    total_submitted: Decimal = Field(..., description="Total billed")
    total_paid: Decimal = Field(..., description="Total paid")
    total_patient_responsibility: Decimal = Field(Decimal("0"))

    line_payments: list[PharmacyLinePayment] = Field(default_factory=list)

    # Claim status
    claim_status: ClaimStatus = ClaimStatus.PROCESSED_PRIMARY


class EDI835PharmacyGenerator:
    """Generate X12 835 Remittance Advice for pharmacy claims."""

    def __init__(
        self,
        sender_id: str = "PAYER001",
        receiver_id: str = "PHARMACY001",
        element_sep: str = "*",
        segment_sep: str = "~",
    ) -> None:
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.element_sep = element_sep
        self.segment_sep = segment_sep
        self.segments: list[str] = []
        self.st_count = 0
        self.segment_count = 0

    def reset(self) -> None:
        """Reset generator state."""
        self.segments = []
        self.st_count = 0
        self.segment_count = 0

    def _add(self, *elements: Any) -> None:
        """Add a segment."""
        segment = self.element_sep.join(str(e) for e in elements)
        self.segments.append(segment + self.segment_sep)
        self.segment_count += 1

    def generate(self, remittances: list[PharmacyRemittance]) -> str:
        """Generate 835 remittance for pharmacy payments."""
        self.reset()

        # ISA - Interchange Control Header
        now = datetime.now()
        self._add(
            "ISA", "00", " " * 10, "00", " " * 10,
            "ZZ", self.sender_id.ljust(15), "ZZ", self.receiver_id.ljust(15),
            now.strftime("%y%m%d"), now.strftime("%H%M"),
            "^", "00501", "000000001", "0", "P", ":",
        )

        # GS - Functional Group Header
        self._add(
            "GS", "HP", self.sender_id, self.receiver_id,
            now.strftime("%Y%m%d"), now.strftime("%H%M"),
            "1", "X", "005010X221A1",
        )

        # ST - Transaction Set Header
        self.st_count = self.segment_count
        self._add("ST", "835", "0001", "005010X221A1")

        # BPR - Financial Information
        total_amount = sum(r.total_paid for r in remittances)
        self._add(
            "BPR", "I", str(total_amount), "C", "ACH", "CTX",
            "01", "999999999", "DA", "1234567890",
            self.sender_id, "",
            "01", "888888888", "DA", "0987654321",
            now.strftime("%Y%m%d"),
        )

        # TRN - Reassociation Trace Number
        check_num = remittances[0].check_number if remittances else "000000001"
        self._add("TRN", "1", check_num or "000000001", "1" + self.sender_id)

        # REF - Receiver Identification
        self._add("REF", "EV", self.receiver_id)

        # DTM - Production Date
        self._add("DTM", "405", now.strftime("%Y%m%d"))

        # N1 - Payer Identification
        payer_name = remittances[0].payer_name if remittances else "PHARMACY BENEFIT MANAGER"
        self._add("N1", "PR", payer_name, "XV", self.sender_id)

        # N1 - Payee Identification
        if remittances:
            self._add(
                "N1", "PE", remittances[0].pharmacy_name,
                "XX", remittances[0].pharmacy_npi,
            )
        else:
            self._add("N1", "PE", "PHARMACY", "XX", "1234567890")

        # Generate payment loops for each remittance
        for remittance in remittances:
            self._generate_claim_loop(remittance)

        # SE - Transaction Set Trailer
        segment_in_st = self.segment_count - self.st_count + 1
        self._add("SE", str(segment_in_st), "0001")

        # GE - Functional Group Trailer
        self._add("GE", "1", "1")

        # IEA - Interchange Control Trailer
        self._add("IEA", "1", "000000001")

        return "\n".join(self.segments)

    def _generate_claim_loop(self, remittance: PharmacyRemittance) -> None:
        """Generate CLP loop for a pharmacy remittance."""
        # CLP - Claim Payment Information
        self._add(
            "CLP",
            remittance.claim_id,
            remittance.claim_status.value,
            str(remittance.total_submitted),
            str(remittance.total_paid),
            str(remittance.total_patient_responsibility),
            "12",  # Claim filing indicator - Rx
            remittance.remit_id,
        )

        # NM1 - Patient Name (if available)
        self._add("NM1", "QC", "1", "PATIENT", "", "", "", "", "", "")

        # DTM - Statement Date
        self._add("DTM", "232", remittance.payment_date.strftime("%Y%m%d"))

        # Generate service lines
        for line in remittance.line_payments:
            self._generate_service_line(line, remittance.payment_date)

    def _generate_service_line(
        self,
        line: PharmacyLinePayment,
        payment_date: date,
    ) -> None:
        """Generate SVC loop for a pharmacy service line."""
        # SVC - Service Payment Information
        # Using N4 qualifier for NDC
        self._add(
            "SVC",
            f"N4:{line.ndc}",
            str(line.total_submitted),
            str(line.total_paid),
            "",
            str(line.quantity_dispensed),
        )

        # DTM - Service Date
        service_date = line.fill_date or payment_date
        self._add("DTM", "472", service_date.strftime("%Y%m%d"))

        # CAS - Claim Adjustment (Contractual)
        if line.contractual_adjustment > Decimal("0"):
            self._add(
                "CAS",
                AdjustmentGroup.CONTRACTUAL.value,
                "45",  # Charge exceeds fee schedule
                str(line.contractual_adjustment),
            )

        # CAS - Patient Responsibility
        if line.copay_amount > Decimal("0"):
            self._add(
                "CAS",
                AdjustmentGroup.PATIENT_RESP.value,
                "3",  # Copay amount
                str(line.copay_amount),
            )

        if line.coinsurance_amount > Decimal("0"):
            self._add(
                "CAS",
                AdjustmentGroup.PATIENT_RESP.value,
                "2",  # Coinsurance amount
                str(line.coinsurance_amount),
            )

        if line.deductible_amount > Decimal("0"):
            self._add(
                "CAS",
                AdjustmentGroup.PATIENT_RESP.value,
                "1",  # Deductible amount
                str(line.deductible_amount),
            )

        # AMT - Supplemental Amounts
        # Ingredient cost paid
        self._add("AMT", "F5", str(line.ingredient_cost_paid))

        # Dispensing fee paid
        self._add("AMT", "DY", str(line.dispensing_fee_paid))

        # REF - Prescription Number
        self._add("REF", "XZ", line.prescription_number)

        # LQ - Drug Information
        self._add("LQ", "ND", line.drug_name[:30] if line.drug_name else "")


def generate_pharmacy_835(
    remittances: list[PharmacyRemittance],
    sender_id: str = "PAYER001",
    receiver_id: str = "PHARMACY001",
) -> str:
    """Convenience function for pharmacy 835 generation."""
    return EDI835PharmacyGenerator(sender_id, receiver_id).generate(remittances)


__all__ = [
    "EDI835PharmacyGenerator",
    "PharmacyRemittance",
    "PharmacyLinePayment",
    "ClaimStatus",
    "AdjustmentGroup",
    "generate_pharmacy_835",
]
