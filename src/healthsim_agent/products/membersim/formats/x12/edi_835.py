"""X12 835 Healthcare Claim Payment/Remittance generator.

Ported from: healthsim-workspace/packages/membersim/src/membersim/formats/x12/edi_835.py
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from healthsim_agent.products.membersim.formats.x12.base import X12Config, X12Generator


class LinePayment(BaseModel):
    """Payment details for a claim line."""
    line_number: int
    charged_amount: Decimal
    allowed_amount: Decimal
    paid_amount: Decimal
    deductible_amount: Decimal = Decimal("0")
    coinsurance_amount: Decimal = Decimal("0")
    copay_amount: Decimal = Decimal("0")
    adjustment_amount: Decimal = Decimal("0")


class Payment(BaseModel):
    """Claim payment/remittance."""
    payment_id: str = Field(..., description="Payment ID")
    claim_id: str = Field(..., description="Claim ID")
    check_number: str | None = Field(None, description="Check number")
    payment_date: date = Field(..., description="Payment date")
    total_charged: Decimal = Field(..., description="Total billed")
    total_allowed: Decimal = Field(..., description="Total allowed")
    total_paid: Decimal = Field(..., description="Total paid")
    total_patient_responsibility: Decimal = Field(Decimal("0"), description="Patient owes")
    line_payments: list[LinePayment] = Field(default_factory=list)


class EDI835Generator(X12Generator):
    """Generate X12 835 Remittance Advice."""

    def generate(self, payments: list[Payment]) -> str:
        """Generate 835 remittance for payments."""
        self.reset()

        self._isa_segment("HP")
        self._gs_segment("HP", self.config.sender_id, self.config.receiver_id)
        self._st_segment("835")

        total_amount = sum(p.total_paid for p in payments)
        today = date.today()
        self._add(
            "BPR", "I", str(total_amount), "C", "ACH", "CTX",
            "01", "ROUTING", "DA", "ACCOUNT", "PAYERID", "",
            "01", "PAYEEROUTING", "DA", "PAYEEACCOUNT", today.strftime("%Y%m%d"),
        )

        check_num = payments[0].check_number if payments else "000"
        self._add("TRN", "1", check_num or "000", "PAYERID")
        self._add("REF", "EV", "RECEIVERID")
        self._add("DTM", "405", today.strftime("%Y%m%d"))
        self._add("N1", "PR", "PAYER NAME", "XV", "PAYERID")
        self._add("N1", "PE", "PAYEE NAME", "XX", "PAYEENPI")

        for payment in payments:
            self._generate_payment_loop(payment)

        self._se_segment()
        self._ge_segment()
        self._iea_segment()

        return self.to_string()

    def _generate_payment_loop(self, payment: Payment) -> None:
        """Generate CLP loop for a payment."""
        self._add(
            "CLP", payment.claim_id, "1",
            str(payment.total_charged), str(payment.total_paid),
            str(payment.total_patient_responsibility), "12", payment.payment_id,
        )

        self._add("DTM", "232", payment.payment_date.strftime("%Y%m%d"))

        for line_pay in payment.line_payments:
            self._add(
                "SVC", "HC:99213", str(line_pay.charged_amount),
                str(line_pay.paid_amount), "", str(line_pay.line_number),
            )
            self._add("DTM", "472", payment.payment_date.strftime("%Y%m%d"))

            if line_pay.deductible_amount > Decimal("0"):
                self._add("CAS", "PR", "1", str(line_pay.deductible_amount))
            if line_pay.coinsurance_amount > Decimal("0"):
                self._add("CAS", "PR", "2", str(line_pay.coinsurance_amount))
            if line_pay.copay_amount > Decimal("0"):
                self._add("CAS", "PR", "3", str(line_pay.copay_amount))
            if line_pay.adjustment_amount > Decimal("0"):
                self._add("CAS", "CO", "45", str(line_pay.adjustment_amount))

            self._add("AMT", "B6", str(line_pay.allowed_amount))


def generate_835(payments: list[Payment], config: X12Config | None = None) -> str:
    """Convenience function for 835 generation."""
    return EDI835Generator(config).generate(payments)


__all__ = ["EDI835Generator", "Payment", "LinePayment", "generate_835"]
