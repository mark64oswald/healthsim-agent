"""X12 837 Healthcare Claim generators.

Ported from: healthsim-workspace/packages/membersim/src/membersim/formats/x12/edi_837.py
"""

from datetime import date

from healthsim_agent.products.membersim.core.models import Claim
from healthsim_agent.products.membersim.formats.x12.base import X12Config, X12Generator


class EDI837PGenerator(X12Generator):
    """Generate X12 837P Professional Claims."""

    def generate(self, claims: list[Claim]) -> str:
        """Generate 837P for professional claims."""
        self.reset()

        self._isa_segment("HC")
        self._gs_segment("HC", self.config.sender_id, self.config.receiver_id)
        self._st_segment("837")

        today = date.today()
        self._add(
            "BHT", "0019", "00", f"CLM{today.strftime('%Y%m%d%H%M%S')}",
            today.strftime("%Y%m%d"), today.strftime("%H%M"), "CH",
        )

        self._add("NM1", "41", "2", "SUBMITTER NAME", "", "", "", "", "46", "SUBMITTERID")
        self._add("PER", "IC", "CONTACT NAME", "TE", "5551234567")
        self._add("NM1", "40", "2", "RECEIVER NAME", "", "", "", "", "46", "RECEIVERID")

        for idx, claim in enumerate(claims, 1):
            self._generate_claim_loop(claim, idx)

        self._se_segment()
        self._ge_segment()
        self._iea_segment()

        return self.to_string()

    def _generate_claim_loop(self, claim: Claim, hl_id: int) -> None:
        """Generate 2000A/B/C loops for a claim."""
        self._add("HL", str(hl_id), "", "20", "1")
        self._add("NM1", "85", "2", "BILLING PROVIDER", "", "", "", "", "XX", claim.provider_npi or "0000000000")

        self._add("HL", str(hl_id + 100), str(hl_id), "22", "0")
        self._add("NM1", "IL", "1", "LASTNAME", "FIRSTNAME", "", "", "", "MI", claim.member_id)

        self._add(
            "CLM", claim.claim_id, str(claim.total_billed), "", "",
            "11:B:1", "Y", "A", "Y", "I",
        )

        self._add("DTP", "472", "D8", claim.service_date.strftime("%Y%m%d"))

        # Diagnosis codes from claim lines
        dx_codes = []
        for line in claim.lines:
            if line.diagnosis_code and f"ABK:{line.diagnosis_code}" not in dx_codes:
                if not dx_codes:
                    dx_codes.append(f"ABK:{line.diagnosis_code}")
                else:
                    dx_codes.append(f"ABF:{line.diagnosis_code}")
        if dx_codes:
            self._add("HI", *dx_codes[:12])

        self._add("NM1", "82", "1", "PROVIDER", "RENDERING", "", "", "", "XX", claim.provider_npi or "0000000000")

        for line in claim.lines:
            self._add("LX", str(line.line_number))
            self._add(
                "SV1", f"HC:{line.procedure_code}", str(line.billed_amount),
                "UN", str(line.quantity), "", "", "1",
            )
            self._add("DTP", "472", "D8", claim.service_date.strftime("%Y%m%d"))


class EDI837IGenerator(X12Generator):
    """Generate X12 837I Institutional Claims."""

    def generate(self, claims: list[Claim]) -> str:
        """Generate 837I for institutional claims."""
        self.reset()

        self._isa_segment("HC")
        self._gs_segment("HC", self.config.sender_id, self.config.receiver_id)
        self._st_segment("837")

        today = date.today()
        self._add(
            "BHT", "0019", "00", f"CLM{today.strftime('%Y%m%d%H%M%S')}",
            today.strftime("%Y%m%d"), today.strftime("%H%M"), "CH",
        )

        self._add("NM1", "41", "2", "SUBMITTER NAME", "", "", "", "", "46", "SUBMITTERID")
        self._add("PER", "IC", "CONTACT NAME", "TE", "5551234567")
        self._add("NM1", "40", "2", "RECEIVER NAME", "", "", "", "", "46", "RECEIVERID")

        for idx, claim in enumerate(claims, 1):
            self._generate_institutional_claim(claim, idx)

        self._se_segment()
        self._ge_segment()
        self._iea_segment()

        return self.to_string()

    def _generate_institutional_claim(self, claim: Claim, hl_id: int) -> None:
        """Generate institutional claim loops."""
        self._add("HL", str(hl_id), "", "20", "1")
        self._add("NM1", "85", "2", "FACILITY NAME", "", "", "", "", "XX", claim.provider_npi or "0000000000")

        self._add("HL", str(hl_id + 100), str(hl_id), "22", "0")
        self._add("NM1", "IL", "1", "LASTNAME", "FIRSTNAME", "", "", "", "MI", claim.member_id)

        self._add(
            "CLM", claim.claim_id, str(claim.total_billed), "", "",
            "0111::1", "Y", "A", "Y", "I",
        )

        self._add("DTP", "435", "D8", claim.service_date.strftime("%Y%m%d"))

        # Principal diagnosis
        dx_codes = [line.diagnosis_code for line in claim.lines if line.diagnosis_code]
        if dx_codes:
            self._add("HI", f"BK:{dx_codes[0]}")

        for line in claim.lines:
            self._add("LX", str(line.line_number))
            self._add(
                "SV2", "0120", f"HC:{line.procedure_code}",
                str(line.billed_amount), "UN", str(line.quantity),
            )
            self._add("DTP", "472", "D8", claim.service_date.strftime("%Y%m%d"))


def generate_837p(claims: list[Claim], config: X12Config | None = None) -> str:
    """Convenience function for 837P generation."""
    return EDI837PGenerator(config).generate(claims)


def generate_837i(claims: list[Claim], config: X12Config | None = None) -> str:
    """Convenience function for 837I generation."""
    return EDI837IGenerator(config).generate(claims)


__all__ = ["EDI837PGenerator", "EDI837IGenerator", "generate_837p", "generate_837i"]
