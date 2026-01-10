"""X12 834 Benefit Enrollment generator.

Ported from: healthsim-workspace/packages/membersim/src/membersim/formats/x12/edi_834.py
"""

from datetime import date

from healthsim_agent.products.membersim.core.models import Coverage, Member
from healthsim_agent.products.membersim.formats.x12.base import X12Config, X12Generator


class EDI834Generator(X12Generator):
    """Generate X12 834 Benefit Enrollment transactions."""

    def generate(
        self,
        members: list[Member],
        coverages: list[Coverage] | None = None,
        maintenance_type: str = "021",
        group_id: str | None = None,
    ) -> str:
        """Generate 834 enrollment transaction.

        Args:
            members: List of members to include
            coverages: Optional list of coverage records
            maintenance_type: 021=Addition, 001=Change, 024=Termination
            group_id: Override group ID
        """
        self.reset()

        self._isa_segment("BE")
        self._gs_segment("BE", self.config.sender_id, self.config.receiver_id)
        self._st_segment("834")

        today_str = date.today().strftime("%Y%m%d")
        self._add("BGN", "00", f"REF{today_str}", today_str)

        self._add("N1", "P5", "SPONSOR NAME", "FI", "123456789")
        self._add("N1", "IN", "PAYER NAME", "FI", "987654321")

        # Build coverage lookup
        coverage_map = {}
        if coverages:
            for cov in coverages:
                coverage_map[cov.member_id] = cov

        for member in members:
            cov = coverage_map.get(member.member_id)
            self._generate_member_loop(member, cov, maintenance_type, group_id)

        self._se_segment()
        self._ge_segment()
        self._iea_segment()

        return self.to_string()

    def _generate_member_loop(
        self,
        member: Member,
        coverage: Coverage | None,
        maintenance_type: str,
        group_id: str | None,
    ) -> None:
        """Generate INS loop for a single member."""
        gid = group_id or member.group_number or "GRP001"
        is_subscriber = "Y" if member.subscriber_id == member.member_id else "N"

        self._add("INS", is_subscriber, "18", maintenance_type, "", "A")

        self._add("REF", "0F", member.member_id)
        if member.subscriber_id and member.subscriber_id != member.member_id:
            self._add("REF", "23", member.subscriber_id)
        self._add("REF", "1L", gid)

        # Coverage dates
        if coverage:
            self._add("DTP", "356", "D8", coverage.start_date.strftime("%Y%m%d"))
            if coverage.end_date:
                self._add("DTP", "357", "D8", coverage.end_date.strftime("%Y%m%d"))

        self._add(
            "NM1", "IL", "1", member.family_name, member.given_name,
            "", "", "", "MI", member.member_id,
        )

        gender_code = member.gender.upper()[0] if member.gender else "U"
        if gender_code not in ("M", "F"):
            gender_code = "U"
        self._add("DMG", "D8", member.birth_date.strftime("%Y%m%d"), gender_code)

        if member.street_address:
            self._add("N3", member.street_address)
            self._add("N4", member.city or "", member.state or "", member.postal_code or "")

        self._add(
            "HD", "021" if maintenance_type == "021" else "001",
            "", "HLT", member.plan_code or "PLAN001",
        )

        if coverage:
            self._add("DTP", "348", "D8", coverage.start_date.strftime("%Y%m%d"))


def generate_834(
    members: list[Member],
    coverages: list[Coverage] | None = None,
    maintenance_type: str = "021",
    config: X12Config | None = None,
) -> str:
    """Convenience function to generate 834."""
    return EDI834Generator(config).generate(members, coverages, maintenance_type)


__all__ = ["EDI834Generator", "generate_834"]
