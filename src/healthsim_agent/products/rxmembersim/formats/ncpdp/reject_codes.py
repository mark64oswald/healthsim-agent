"""NCPDP standard reject codes.

Ported from: healthsim-workspace/packages/rxmembersim/src/rxmembersim/formats/ncpdp/reject_codes.py
"""

from enum import Enum


class RejectCategory(str, Enum):
    """Reject code categories."""
    ELIGIBILITY = "Eligibility"
    COVERAGE = "Coverage"
    DUR = "DUR"
    QUANTITY = "Quantity"
    PRIOR_AUTHORIZATION = "Prior Authorization"
    SUBMISSION = "Submission"
    SYSTEM = "System"
    OTHER = "Other"


NCPDP_REJECT_CODES: dict[str, str] = {
    "01": "Missing/Invalid BIN Number",
    "02": "Missing/Invalid Version Number",
    "03": "Missing/Invalid Transaction Code",
    "04": "Missing/Invalid Processor Control Number",
    "05": "Missing/Invalid Date of Birth",
    "06": "Missing/Invalid Cardholder ID",
    "07": "Missing/Invalid Group ID",
    "65": "Patient Not Covered",
    "66": "Patient Age Exceeds Maximum Age",
    "67": "Patient Age Precedes Minimum Age",
    "68": "Member ID Not Found",
    "69": "Invalid Date of Birth",
    "70": "Product/Service Not Covered",
    "71": "Prescriber Not Covered",
    "75": "Prior Authorization Required",
    "76": "Plan Limitations Exceeded",
    "79": "Refill Too Soon",
    "80": "Drug-Drug Interaction",
    "81": "Duplicate Therapy",
    "82": "Overuse",
    "83": "Drug Conflict with Pregnancy",
    "84": "Drug-Disease Precaution",
    "85": "Drug Conflict with Age",
    "86": "Drug-Gender Precaution",
    "87": "Dosage Exceeds Maximum",
    "88": "DUR Reject Error",
    "89": "Quantity Below Minimum",
    "90": "Quantity Exceeds Maximum",
    "91": "Days Supply Below Minimum",
    "92": "Days Supply Exceeds Maximum",
    "93": "Prior Authorization Number Submitted",
    "94": "Prior Authorization Expired",
    "95": "Prior Authorization Cancelled",
    "96": "Claim Not Processed",
    "97": "Host Processor Unavailable",
    "98": "Transmission Error",
    "99": "Host Processing Error",
    "MR": "Product Not On Formulary",
    "ER": "Fill Too Early",
    "NC": "Non-Covered Product",
    "PA": "Prior Authorization Required",
    "QL": "Quantity Limits Exceeded",
    "SE": "Step Therapy Required",
    "SP": "Specialty Pharmacy Required",
}


def get_reject_description(code: str) -> str:
    """Get description for reject code."""
    return NCPDP_REJECT_CODES.get(code, f"Unknown Reject Code ({code})")


def get_reject_category(code: str) -> RejectCategory:
    """Get category for reject code."""
    if code.isdigit():
        code_num = int(code)
        if 1 <= code_num <= 24:
            return RejectCategory.SUBMISSION
        if 65 <= code_num <= 69:
            return RejectCategory.ELIGIBILITY
        if 70 <= code_num <= 79:
            return RejectCategory.COVERAGE
        if 80 <= code_num <= 88:
            return RejectCategory.DUR
        if 89 <= code_num <= 92:
            return RejectCategory.QUANTITY
        if 93 <= code_num <= 95:
            return RejectCategory.PRIOR_AUTHORIZATION
        if 96 <= code_num <= 99:
            return RejectCategory.SYSTEM

    code_upper = code.upper()
    if code_upper in ("PA", "SE", "SP"):
        return RejectCategory.PRIOR_AUTHORIZATION
    if code_upper in ("QL", "QE", "PD", "PM"):
        return RejectCategory.QUANTITY
    if code_upper in ("MR", "FM", "NC", "NF", "TP"):
        return RejectCategory.COVERAGE

    return RejectCategory.OTHER


def is_hard_reject(code: str) -> bool:
    """Determine if reject is a hard reject (cannot be overridden)."""
    return code in {"65", "68", "94", "95", "96", "97", "98", "99"}


def is_dur_reject(code: str) -> bool:
    """Check if code is a DUR-related reject."""
    return get_reject_category(code) == RejectCategory.DUR


__all__ = [
    "RejectCategory", "NCPDP_REJECT_CODES",
    "get_reject_description", "get_reject_category",
    "is_hard_reject", "is_dur_reject",
]
