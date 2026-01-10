"""NCPDP Telecommunication Standard generator.

Ported from: healthsim-workspace/packages/rxmembersim/src/rxmembersim/formats/ncpdp/telecom.py
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class PharmacyClaim(BaseModel):
    """Pharmacy claim for NCPDP processing."""
    claim_id: str
    bin: str = Field(..., description="BIN number")
    pcn: str = Field(..., description="Processor Control Number")
    group_number: str
    cardholder_id: str
    person_code: str = "01"
    member_id: str
    
    ndc: str
    quantity_dispensed: Decimal
    days_supply: int
    daw_code: str = "0"
    prescription_number: str
    fill_number: int = 0
    compound_code: str = "1"
    
    prescriber_npi: str
    pharmacy_npi: str
    service_date: Any  # date
    
    ingredient_cost_submitted: Decimal = Decimal("0")
    dispensing_fee_submitted: Decimal = Decimal("0")
    gross_amount_due: Decimal = Decimal("0")
    usual_customary_charge: Decimal = Decimal("0")
    
    prior_auth_number: str | None = None


class RejectCode(BaseModel):
    """NCPDP reject code."""
    code: str
    description: str | None = None


class ClaimResponse(BaseModel):
    """NCPDP claim response."""
    transaction_response_status: str  # A=Accepted, R=Rejected
    response_status: str  # P=Paid, R=Rejected, D=Duplicate
    authorization_number: str | None = None
    reject_codes: list[RejectCode] = Field(default_factory=list)
    message: str | None = None
    
    ingredient_cost_paid: Decimal | None = None
    dispensing_fee_paid: Decimal | None = None
    total_amount_paid: Decimal | None = None
    patient_pay_amount: Decimal | None = None
    copay_amount: Decimal | None = None
    deductible_amount: Decimal | None = None


class NCPDPTelecomGenerator:
    """Generate NCPDP Telecommunication messages."""

    SEGMENT_SEPARATOR = chr(0x1E)  # ASCII 30
    FIELD_SEPARATOR = chr(0x1C)   # ASCII 28

    def generate_b1_request(self, claim: PharmacyClaim) -> str:
        """Generate B1 (billing) request message."""
        segments = [
            self._build_header_segment(claim),
            self._build_patient_segment(claim),
            self._build_insurance_segment(claim),
            self._build_claim_segment(claim),
            self._build_pricing_segment(claim),
        ]
        return self.SEGMENT_SEPARATOR.join(segments)

    def generate_b2_reversal(self, claim: PharmacyClaim, original_auth: str) -> str:
        """Generate B2 (reversal) request message."""
        segments = [
            self._build_header_segment(claim, transaction_code="B2"),
            self._build_patient_segment(claim),
            self._build_insurance_segment(claim),
            self._build_claim_segment(claim, original_auth=original_auth),
        ]
        return self.SEGMENT_SEPARATOR.join(segments)

    def generate_b3_rebill(self, claim: PharmacyClaim, original_auth: str) -> str:
        """Generate B3 (rebill) request message."""
        segments = [
            self._build_header_segment(claim, transaction_code="B3"),
            self._build_patient_segment(claim),
            self._build_insurance_segment(claim),
            self._build_claim_segment(claim, original_auth=original_auth),
            self._build_pricing_segment(claim),
        ]
        return self.SEGMENT_SEPARATOR.join(segments)

    def generate_response(self, response: ClaimResponse) -> str:
        """Generate response message."""
        segments = [
            self._build_response_header(response),
            self._build_response_status(response),
        ]
        if response.response_status == "P":
            segments.append(self._build_response_pricing(response))
        return self.SEGMENT_SEPARATOR.join(segments)

    def _build_header_segment(self, claim: PharmacyClaim, transaction_code: str = "B1") -> str:
        """Build transaction header segment."""
        service_date = claim.service_date
        if hasattr(service_date, 'strftime'):
            date_str = service_date.strftime('%Y%m%d')
        else:
            date_str = str(service_date).replace('-', '')[:8]
        
        fields = [
            "AM01",
            f"D0{transaction_code}",
            f"C1{claim.bin}",
            f"C2{claim.pcn}",
            f"D1{datetime.now().strftime('%Y%m%d')}",
            f"D2{date_str}",
        ]
        return self.FIELD_SEPARATOR.join(fields)

    def _build_patient_segment(self, claim: PharmacyClaim) -> str:
        """Build patient segment (01)."""
        fields = [
            "AM01",
            f"C2{claim.cardholder_id}",
            f"C3{claim.person_code}",
            f"CA{claim.member_id}",
        ]
        return self.FIELD_SEPARATOR.join(fields)

    def _build_insurance_segment(self, claim: PharmacyClaim) -> str:
        """Build insurance segment (04)."""
        fields = [
            "AM04",
            f"C1{claim.bin}",
            f"C2{claim.pcn}",
            f"C3{claim.group_number}",
            f"CC{claim.cardholder_id}",
        ]
        return self.FIELD_SEPARATOR.join(fields)

    def _build_claim_segment(self, claim: PharmacyClaim, original_auth: str | None = None) -> str:
        """Build claim segment (07)."""
        fields = [
            "AM07",
            f"D2{claim.ndc}",
            f"E1{self._format_quantity(claim.quantity_dispensed)}",
            f"D3{claim.days_supply:03d}",
            f"D6{claim.daw_code}",
            f"D7{claim.prescription_number}",
            f"D8{claim.fill_number:02d}",
            f"DE{claim.compound_code}",
            f"EM{claim.prescriber_npi}",
            f"DB{claim.pharmacy_npi}",
        ]
        if original_auth:
            fields.append(f"F3{original_auth}")
        if claim.prior_auth_number:
            fields.append(f"EU{claim.prior_auth_number}")
        return self.FIELD_SEPARATOR.join(fields)

    def _build_pricing_segment(self, claim: PharmacyClaim) -> str:
        """Build pricing segment (11)."""
        fields = [
            "AM11",
            f"D9{self._format_currency(claim.ingredient_cost_submitted)}",
            f"DC{self._format_currency(claim.dispensing_fee_submitted)}",
            f"DQ{self._format_currency(claim.gross_amount_due)}",
            f"DU{self._format_currency(claim.usual_customary_charge)}",
        ]
        return self.FIELD_SEPARATOR.join(fields)

    def _build_response_header(self, response: ClaimResponse) -> str:
        """Build response header segment (20)."""
        fields = [
            "AM20",
            f"AN{response.transaction_response_status}",
            f"F3{response.authorization_number or ''}",
        ]
        return self.FIELD_SEPARATOR.join(fields)

    def _build_response_status(self, response: ClaimResponse) -> str:
        """Build response status segment (21)."""
        fields = ["AM21", f"AN{response.response_status}"]
        for i, reject in enumerate(response.reject_codes[:5], start=1):
            fields.append(f"F{i}{reject.code}")
        if response.message:
            fields.append(f"FQ{response.message[:200]}")
        return self.FIELD_SEPARATOR.join(fields)

    def _build_response_pricing(self, response: ClaimResponse) -> str:
        """Build response pricing segment (23)."""
        fields = ["AM23"]
        if response.ingredient_cost_paid is not None:
            fields.append(f"F5{self._format_currency(response.ingredient_cost_paid)}")
        if response.dispensing_fee_paid is not None:
            fields.append(f"F6{self._format_currency(response.dispensing_fee_paid)}")
        if response.total_amount_paid is not None:
            fields.append(f"F9{self._format_currency(response.total_amount_paid)}")
        if response.copay_amount is not None:
            fields.append(f"FE{self._format_currency(response.copay_amount)}")
        if response.deductible_amount is not None:
            fields.append(f"FH{self._format_currency(response.deductible_amount)}")
        return self.FIELD_SEPARATOR.join(fields)

    def _format_currency(self, amount: Decimal) -> str:
        """Format currency as 8-digit integer (cents)."""
        return f"{int(amount * 100):08d}"

    def _format_quantity(self, qty: Decimal) -> str:
        """Format quantity as string with 3 decimal places."""
        return f"{qty:.3f}"

    def parse_response(self, message: str) -> dict:
        """Parse NCPDP response message into dictionary."""
        result: dict[str, str | list[str]] = {}
        for segment in message.split(self.SEGMENT_SEPARATOR):
            for field in segment.split(self.FIELD_SEPARATOR):
                if len(field) >= 2:
                    field_id, field_value = field[:2], field[2:]
                    if field_id in result:
                        existing = result[field_id]
                        if isinstance(existing, list):
                            existing.append(field_value)
                        else:
                            result[field_id] = [existing, field_value]
                    else:
                        result[field_id] = field_value
        return result


__all__ = [
    "PharmacyClaim", "ClaimResponse", "RejectCode",
    "NCPDPTelecomGenerator",
]
