"""Member data generator.

Ported from: healthsim-workspace/packages/membersim/src/membersim/core/generator.py
"""

from datetime import date, timedelta
from decimal import Decimal

from healthsim_agent.generation import BaseGenerator

from healthsim_agent.products.membersim.core.models import (
    Claim,
    ClaimLine,
    ClaimStatus,
    Coverage,
    CoverageType,
    Enrollment,
    Member,
)


class MemberGenerator(BaseGenerator):
    """Generator for health plan member data."""

    def __init__(self, seed: int | None = None, locale: str = "en_US") -> None:
        super().__init__(seed=seed, locale=locale)
        self._member_counter = 0
        self._claim_counter = 0

    def generate_member(
        self,
        age_range: tuple[int, int] | None = None,
        subscriber_id: str | None = None,
    ) -> Member:
        """Generate a random member."""
        if age_range is None:
            age_range = (18, 85)

        self._member_counter += 1

        min_age, max_age = age_range
        today = date.today()
        max_birth = today - timedelta(days=min_age * 365)
        min_birth = today - timedelta(days=max_age * 365)
        birth_date = self.random_date_between(min_birth, max_birth)

        gender = self.random_choice(["M", "F"])
        if gender == "M":
            given_name = self.faker.first_name_male()
        else:
            given_name = self.faker.first_name_female()

        member_id = f"M{self.random_int(100000, 999999)}"
        if subscriber_id is None:
            subscriber_id = f"S{self.random_int(100000, 999999)}"

        return Member(
            member_id=member_id,
            subscriber_id=subscriber_id,
            given_name=given_name,
            family_name=self.faker.last_name(),
            birth_date=birth_date,
            gender=gender,
            street_address=self.faker.street_address(),
            city=self.faker.city(),
            state=self.faker.state_abbr(),
            postal_code=self.faker.postcode(),
            phone=self.faker.phone_number(),
            email=self.faker.email(),
            group_number=f"GRP{self.random_int(1000, 9999)}",
            plan_code=self.random_choice(["HMO", "PPO", "EPO", "POS"]),
        )

    def generate_coverage(
        self,
        member: Member,
        coverage_type: CoverageType | None = None,
        start_date: date | None = None,
    ) -> Coverage:
        """Generate coverage for a member."""
        if coverage_type is None:
            coverage_type = self.random_choice(list(CoverageType))

        if start_date is None:
            days_ago = self.random_int(30, 365 * 2)
            start_date = date.today() - timedelta(days=days_ago)

        end_date = None
        if self.random_bool(0.2):
            end_date = start_date + timedelta(days=self.random_int(90, 365))

        plans = {
            CoverageType.MEDICAL: {
                "names": ["Gold Plan", "Silver Plan", "Bronze Plan", "Platinum Plan"],
                "deductibles": [500, 1000, 2000, 3000, 5000],
                "copays": [20, 30, 40, 50],
            },
            CoverageType.DENTAL: {
                "names": ["Dental Basic", "Dental Plus", "Dental Premium"],
                "deductibles": [50, 100, 150],
                "copays": [0, 10, 20],
            },
            CoverageType.VISION: {
                "names": ["Vision Standard", "Vision Plus"],
                "deductibles": [0, 25, 50],
                "copays": [10, 15, 20],
            },
            CoverageType.PHARMACY: {
                "names": ["Rx Basic", "Rx Plus", "Rx Premium"],
                "deductibles": [100, 200, 500],
                "copays": [10, 20, 30],
            },
        }

        plan_info = plans[coverage_type]

        return Coverage(
            coverage_id=f"COV{self.random_int(100000, 999999)}",
            member_id=member.member_id,
            coverage_type=coverage_type,
            start_date=start_date,
            end_date=end_date,
            plan_name=self.random_choice(plan_info["names"]),
            network=self.random_choice(["HMO", "PPO", "EPO"]),
            deductible=Decimal(self.random_choice(plan_info["deductibles"])),
            copay=Decimal(self.random_choice(plan_info["copays"])),
        )

    def generate_enrollment(
        self,
        member: Member,
        enrollment_date: date | None = None,
    ) -> Enrollment:
        """Generate enrollment record for a member."""
        if enrollment_date is None:
            days_ago = self.random_int(30, 365 * 3)
            enrollment_date = date.today() - timedelta(days=days_ago)

        disenrollment_date = None
        reason_code = "NEW"
        if self.random_bool(0.15):
            disenrollment_date = enrollment_date + timedelta(days=self.random_int(90, 365))
            reason_code = self.random_choice(["TERM", "VOL", "MOVE", "DEATH"])

        return Enrollment(
            enrollment_id=f"ENR{self.random_int(100000, 999999)}",
            member_id=member.member_id,
            enrollment_date=enrollment_date,
            disenrollment_date=disenrollment_date,
            reason_code=reason_code,
        )

    def generate_claim(
        self,
        member: Member,
        service_date: date | None = None,
        num_lines: int | None = None,
        use_real_providers: bool = False,
        provider_state: str | None = None,
        provider_specialty: str | None = None,
    ) -> Claim:
        """Generate a claim for a member.
        
        Args:
            member: The member for this claim
            service_date: Date of service (defaults to random recent date)
            num_lines: Number of claim lines (defaults to 1-5)
            use_real_providers: If True, use NPPES data for provider info
            provider_state: State for provider lookup (defaults to member's state)
            provider_specialty: Specialty filter for provider lookup
        """
        self._claim_counter += 1

        if service_date is None:
            days_ago = self.random_int(1, 180)
            service_date = date.today() - timedelta(days=days_ago)

        submission_date = service_date + timedelta(days=self.random_int(1, 30))

        if num_lines is None:
            num_lines = self.random_int(1, 5)

        lines = []
        total_billed = Decimal(0)
        for i in range(num_lines):
            line = self._generate_claim_line(i + 1)
            lines.append(line)
            total_billed += line.billed_amount

        payment_ratio = self.random_float(0.6, 0.95)
        total_allowed = total_billed * Decimal(str(round(payment_ratio, 2)))
        total_paid = total_allowed * Decimal("0.8")
        member_responsibility = total_allowed - total_paid

        if self.random_bool(0.05):
            status = ClaimStatus.DENIED
            total_paid = Decimal(0)
        elif self.random_bool(0.1):
            status = ClaimStatus.PENDING
        else:
            status = ClaimStatus.PAID

        # Get provider info - try NPPES first if requested
        provider_npi, provider_name, facility_name = self._get_provider_info(
            use_real_providers=use_real_providers,
            state=provider_state or member.state,
            specialty=provider_specialty,
        )

        return Claim(
            claim_id=f"CLM{self.random_int(1000000, 9999999)}",
            member_id=member.member_id,
            service_date=service_date,
            submission_date=submission_date,
            provider_npi=provider_npi,
            provider_name=provider_name,
            facility_name=facility_name,
            status=status,
            claim_type=self.random_choice(["Professional", "Institutional"]),
            total_billed=total_billed,
            total_allowed=total_allowed,
            total_paid=total_paid,
            member_responsibility=member_responsibility,
            lines=lines,
        )

    def _get_provider_info(
        self,
        use_real_providers: bool = False,
        state: str | None = None,
        specialty: str | None = None,
    ) -> tuple[str, str, str]:
        """Get provider information, optionally from NPPES.
        
        Returns:
            Tuple of (npi, provider_name, facility_name)
        """
        if use_real_providers and state:
            try:
                from healthsim_agent.tools.reference_tools import search_providers
                
                result = search_providers(
                    state=state,
                    specialty=specialty or "Family Medicine",
                    entity_type="individual",
                    limit=50,
                )
                
                if result.success and result.data.get("providers"):
                    providers = result.data["providers"]
                    provider = self.random_choice(providers)
                    
                    npi = provider.get("npi", str(self.random_int(1000000000, 9999999999)))
                    
                    # Build name from NPPES data - use 'name' field or fallback
                    name = provider.get("name", "")
                    credential = provider.get("credential", "MD")
                    if name:
                        name = f"{name}, {credential}" if credential else name
                    else:
                        # Fallback to first/last fields if available
                        first = provider.get("provider_first_name", "")
                        last = provider.get("provider_last_name_legal_name", "Dr. Provider")
                        name = f"{first} {last}, {credential}".strip()
                    
                    # Get organization if available
                    org = provider.get("provider_organization_name_legal_business_name", "")
                    facility = org if org else "Medical Practice"
                    
                    return npi, name, facility
            except Exception:
                # Fall through to synthetic generation
                pass
        
        # Generate synthetic provider data
        return (
            str(self.random_int(1000000000, 9999999999)),
            f"Dr. {self.faker.last_name()}",
            self.random_choice(["General Hospital", "Medical Center", "Community Clinic", "Specialty Care"]),
        )

    def _generate_claim_line(self, line_number: int) -> ClaimLine:
        """Generate a single claim line."""
        procedure_codes = [
            ("99213", 100, 200),
            ("99214", 150, 300),
            ("80053", 50, 150),
            ("36415", 10, 30),
            ("71046", 200, 500),
        ]

        code, min_amt, max_amt = self.random_choice(procedure_codes)
        billed = Decimal(str(self.random_int(min_amt, max_amt)))

        return ClaimLine(
            line_number=line_number,
            procedure_code=code,
            diagnosis_code=f"Z{self.random_int(0, 99):02d}.{self.random_int(0, 9)}",
            quantity=1,
            billed_amount=billed,
            allowed_amount=billed * Decimal("0.8"),
            paid_amount=billed * Decimal("0.64"),
        )

    def generate_member_with_history(
        self,
        num_claims: int = 5,
        age_range: tuple[int, int] | None = None,
    ) -> tuple[Member, list[Coverage], list[Enrollment], list[Claim]]:
        """Generate a member with full history."""
        member = self.generate_member(age_range=age_range)

        coverages = [
            self.generate_coverage(member, CoverageType.MEDICAL),
            self.generate_coverage(member, CoverageType.PHARMACY),
        ]

        enrollments = [self.generate_enrollment(member)]
        claims = [self.generate_claim(member) for _ in range(num_claims)]

        return member, coverages, enrollments, claims


__all__ = ["MemberGenerator"]
