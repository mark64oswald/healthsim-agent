"""Pharmacy claim factory for generating synthetic pharmacy claims.

Creates realistic pharmacy claims with NDCs, pricing, and member information.
"""

from datetime import date, timedelta
from decimal import Decimal
import random
from typing import Any

from healthsim_agent.products.rxmembersim.claims.claim import PharmacyClaim, TransactionCode
from healthsim_agent.products.rxmembersim.core.member import RxMember


# Common medications with their typical NDCs and pricing
COMMON_DRUGS = [
    {"ndc": "00071015523", "name": "Lipitor 10mg", "awp": 450.00, "days": 30, "qty": 30},
    {"ndc": "00006027431", "name": "Januvia 100mg", "awp": 520.00, "days": 30, "qty": 30},
    {"ndc": "00169413012", "name": "Ozempic 1mg", "awp": 968.00, "days": 28, "qty": 1},
    {"ndc": "00078060315", "name": "Entresto 97/103mg", "awp": 620.00, "days": 30, "qty": 60},
    {"ndc": "00002140180", "name": "Trulicity 1.5mg", "awp": 892.00, "days": 28, "qty": 4},
    {"ndc": "00310089590", "name": "Xarelto 20mg", "awp": 520.00, "days": 30, "qty": 30},
    {"ndc": "00006027431", "name": "Keytruda 200mg", "awp": 9200.00, "days": 21, "qty": 1},
    {"ndc": "00006011700", "name": "Singulair 10mg", "awp": 280.00, "days": 30, "qty": 30},
    {"ndc": "00002323380", "name": "Cymbalta 60mg", "awp": 380.00, "days": 30, "qty": 30},
    {"ndc": "50242006201", "name": "Synthroid 100mcg", "awp": 75.00, "days": 30, "qty": 30},
    {"ndc": "00078042715", "name": "Cosentyx 150mg", "awp": 6200.00, "days": 28, "qty": 2},
    {"ndc": "00173072520", "name": "Advair Diskus", "awp": 420.00, "days": 30, "qty": 1},
    {"ndc": "00093322601", "name": "Metformin 500mg", "awp": 12.00, "days": 30, "qty": 60},
    {"ndc": "00093088201", "name": "Lisinopril 10mg", "awp": 8.00, "days": 30, "qty": 30},
    {"ndc": "00591204501", "name": "Amlodipine 5mg", "awp": 10.00, "days": 30, "qty": 30},
    {"ndc": "00378180501", "name": "Omeprazole 20mg", "awp": 22.00, "days": 30, "qty": 30},
    {"ndc": "00603129821", "name": "Gabapentin 300mg", "awp": 28.00, "days": 30, "qty": 90},
    {"ndc": "00093537501", "name": "Atorvastatin 20mg", "awp": 15.00, "days": 30, "qty": 30},
]


class PharmacyClaimFactory:
    """Factory for generating synthetic pharmacy claims."""
    
    def __init__(self, seed: int | None = None):
        if seed is not None:
            random.seed(seed)
    
    def generate(
        self,
        member: RxMember | None = None,
        drug: dict | None = None,
        service_date: date | None = None,
        pharmacy_npi: str | None = None,
        prescriber_npi: str | None = None,
        fill_number: int = 0,
    ) -> PharmacyClaim:
        """Generate a pharmacy claim.
        
        Args:
            member: RxMember to generate claim for (generates one if not provided)
            drug: Drug info dict with ndc, awp, days, qty (random if not provided)
            service_date: Date of service (defaults to today)
            pharmacy_npi: Pharmacy NPI (auto-generated if not provided)
            prescriber_npi: Prescriber NPI (auto-generated if not provided)
            fill_number: Fill number (0 for new, 1+ for refills)
        
        Returns:
            PharmacyClaim
        """
        from faker import Faker
        fake = Faker()
        
        # Generate member if not provided
        if member is None:
            from healthsim_agent.products.rxmembersim.core.member import RxMemberFactory
            member_factory = RxMemberFactory()
            member = member_factory.generate()
        
        # Select drug
        if drug is None:
            drug = random.choice(COMMON_DRUGS)
        
        # Generate IDs and NPIs
        claim_id = f"CLM-{fake.random_number(digits=12, fix_len=True)}"
        rx_number = f"RX{fake.random_number(digits=7, fix_len=True)}"
        
        if pharmacy_npi is None:
            pharmacy_npi = str(fake.random_number(digits=10, fix_len=True))
        
        if prescriber_npi is None:
            prescriber_npi = str(fake.random_number(digits=10, fix_len=True))
        
        if service_date is None:
            service_date = date.today() - timedelta(days=random.randint(0, 30))
        
        # Calculate pricing (apply discount to AWP)
        awp = Decimal(str(drug["awp"]))
        discount = Decimal(str(random.uniform(0.80, 0.95)))  # 5-20% discount
        ingredient_cost = (awp * discount).quantize(Decimal("0.01"))
        dispensing_fee = Decimal(str(random.choice([1.50, 2.00, 2.50, 3.00])))
        gross_amount = ingredient_cost + dispensing_fee
        
        return PharmacyClaim(
            claim_id=claim_id,
            transaction_code=TransactionCode.BILLING,
            service_date=service_date,
            pharmacy_npi=pharmacy_npi,
            pharmacy_ncpdp=str(fake.random_number(digits=7, fix_len=True)),
            member_id=member.member_id,
            cardholder_id=member.cardholder_id,
            person_code=member.person_code,
            bin=member.bin,
            pcn=member.pcn,
            group_number=member.group_number,
            prescription_number=rx_number,
            fill_number=fill_number,
            ndc=drug["ndc"],
            quantity_dispensed=Decimal(str(drug["qty"])),
            days_supply=drug["days"],
            daw_code="0",  # No product selection indicated
            compound_code="0",  # Not a compound
            prescriber_npi=prescriber_npi,
            ingredient_cost_submitted=ingredient_cost,
            dispensing_fee_submitted=dispensing_fee,
            usual_customary_charge=gross_amount + Decimal("5.00"),
            gross_amount_due=gross_amount,
        )
    
    def generate_for_member(
        self,
        member: RxMember,
        count: int = 3,
        date_range_days: int = 90,
    ) -> list[PharmacyClaim]:
        """Generate multiple claims for a member over a date range.
        
        Args:
            member: RxMember to generate claims for
            count: Number of claims to generate
            date_range_days: Date range in days to spread claims over
        
        Returns:
            List of PharmacyClaims
        """
        claims = []
        drugs_used = random.sample(COMMON_DRUGS, min(count, len(COMMON_DRUGS)))
        
        for i, drug in enumerate(drugs_used):
            days_ago = random.randint(0, date_range_days)
            service_date = date.today() - timedelta(days=days_ago)
            
            claim = self.generate(
                member=member,
                drug=drug,
                service_date=service_date,
                fill_number=random.choice([0, 0, 0, 1, 1, 2]),  # Weight toward new fills
            )
            claims.append(claim)
        
        # Sort by service date
        claims.sort(key=lambda c: c.service_date)
        return claims


__all__ = ["PharmacyClaimFactory", "COMMON_DRUGS"]
