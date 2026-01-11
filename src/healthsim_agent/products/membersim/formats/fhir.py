"""FHIR R4 resource generation for MemberSim.

Supports the following FHIR Financial resources:
- Coverage: Insurance plan information
- Patient: Member demographics
- Claim: Provider-submitted claim
- ExplanationOfBenefit (EOB): Combined claim + adjudication
"""

from datetime import date
from decimal import Decimal
from typing import Any
import uuid

from healthsim_agent.products.membersim.core.models import Member, Plan, Claim, ClaimLine


def member_to_fhir_coverage(member: Member, plan: Plan | None = None) -> dict[str, Any]:
    """Generate FHIR R4 Coverage resource from member."""
    subscriber_id = getattr(member, "subscriber_id", member.member_id)

    resource: dict[str, Any] = {
        "resourceType": "Coverage",
        "id": member.member_id,
        "status": "active" if member.is_active else "cancelled",
        "type": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "EHCPOL",
                "display": "extended healthcare",
            }]
        },
        "subscriber": {"reference": f"Patient/{subscriber_id}"},
        "beneficiary": {"reference": f"Patient/{member.member_id}"},
        "relationship": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
                "code": _relationship_to_fhir(member.relationship_code),
            }]
        },
        "period": {"start": member.coverage_start.isoformat()},
        "payor": [{"display": "Health Plan"}],
        "class": [
            {
                "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/coverage-class", "code": "plan"}]},
                "value": member.plan_code,
            },
            {
                "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/coverage-class", "code": "group"}]},
                "value": member.group_id,
            },
        ],
    }

    if member.coverage_end:
        resource["period"]["end"] = member.coverage_end.isoformat()

    if plan:
        resource["class"].append({
            "type": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/coverage-class", "code": "subplan"}]},
            "value": plan.plan_type,
            "name": plan.plan_name,
        })

    return resource


def member_to_fhir_patient(member: Member) -> dict[str, Any]:
    """Generate FHIR R4 Patient resource from member demographics."""
    first_name = member.name.given_name
    last_name = member.name.family_name
    dob = member.birth_date
    gender = member.gender.value if hasattr(member.gender, "value") else str(member.gender)
    addr = member.address

    resource: dict[str, Any] = {
        "resourceType": "Patient",
        "id": member.member_id,
        "identifier": [{"system": "http://healthplan.example.org/member-id", "value": member.member_id}],
        "name": [{"use": "official", "family": last_name, "given": [first_name]}],
        "gender": "male" if gender in ("M", "male", "MALE") else "female",
        "birthDate": dob.isoformat(),
    }

    if addr:
        resource["address"] = [{
            "use": "home",
            "line": [addr.street_address],
            "city": addr.city,
            "state": addr.state,
            "postalCode": addr.postal_code,
            "country": "US",
        }]

    return resource


def claim_to_fhir_claim(claim: Claim, member: Member | None = None) -> dict[str, Any]:
    """Generate FHIR R4 Claim resource."""
    patient_ref = f"Patient/{member.member_id}" if member else f"Patient/{claim.member_id}"
    
    # Collect diagnoses from claim lines
    diagnoses = []
    dx_codes_seen = set()
    for line in claim.lines:
        if line.diagnosis_code and line.diagnosis_code not in dx_codes_seen:
            dx_codes_seen.add(line.diagnosis_code)
            diagnoses.append({
                "sequence": len(diagnoses) + 1,
                "diagnosisCodeableConcept": {
                    "coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": line.diagnosis_code}]
                },
            })
    
    items = []
    for line in claim.lines:
        unit_price = float(line.billed_amount / line.quantity) if line.quantity else float(line.billed_amount)
        item: dict[str, Any] = {
            "sequence": line.line_number,
            "productOrService": {
                "coding": [{"system": "http://www.ama-assn.org/go/cpt", "code": line.procedure_code}]
            },
            "servicedDate": claim.service_date.isoformat(),
            "quantity": {"value": line.quantity},
            "unitPrice": {"value": unit_price, "currency": "USD"},
            "net": {"value": float(line.billed_amount), "currency": "USD"},
        }
        items.append(item)

    resource: dict[str, Any] = {
        "resourceType": "Claim",
        "id": claim.claim_id,
        "status": _claim_status_to_fhir(claim.status),
        "type": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                "code": "professional" if claim.claim_type == "P" else "institutional",
            }]
        },
        "use": "claim",
        "patient": {"reference": patient_ref},
        "created": claim.service_date.isoformat(),
        "provider": {
            "identifier": {"system": "http://hl7.org/fhir/sid/us-npi", "value": claim.provider_npi or "0000000000"}
        },
        "priority": {"coding": [{"code": "normal"}]},
        "insurance": [{"sequence": 1, "focal": True, "coverage": {"display": "Primary Coverage"}}],
        "item": items,
        "total": {"value": float(claim.total_billed), "currency": "USD"},
    }

    if diagnoses:
        resource["diagnosis"] = diagnoses

    return resource


def claim_to_fhir_eob(claim: Claim, member: Member | None = None) -> dict[str, Any]:
    """Generate FHIR R4 ExplanationOfBenefit resource."""
    patient_ref = f"Patient/{member.member_id}" if member else f"Patient/{claim.member_id}"
    
    # Collect diagnoses from claim lines
    diagnoses = []
    dx_codes_seen = set()
    for line in claim.lines:
        if line.diagnosis_code and line.diagnosis_code not in dx_codes_seen:
            dx_codes_seen.add(line.diagnosis_code)
            diagnoses.append({
                "sequence": len(diagnoses) + 1,
                "diagnosisCodeableConcept": {
                    "coding": [{"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": line.diagnosis_code}]
                },
            })
    
    items = []
    for line in claim.lines:
        allowed = float(line.allowed_amount) if line.allowed_amount else float(line.billed_amount)
        paid = float(line.paid_amount) if line.paid_amount else 0.0
        
        adjudication = [
            {"category": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/adjudication", "code": "submitted"}]},
             "amount": {"value": float(line.billed_amount), "currency": "USD"}},
            {"category": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/adjudication", "code": "eligible"}]},
             "amount": {"value": allowed, "currency": "USD"}},
            {"category": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/adjudication", "code": "benefit"}]},
             "amount": {"value": paid, "currency": "USD"}},
        ]

        item: dict[str, Any] = {
            "sequence": line.line_number,
            "productOrService": {
                "coding": [{"system": "http://www.ama-assn.org/go/cpt", "code": line.procedure_code}]
            },
            "servicedDate": claim.service_date.isoformat(),
            "quantity": {"value": line.quantity},
            "net": {"value": float(line.billed_amount), "currency": "USD"},
            "adjudication": adjudication,
        }
        items.append(item)

    total_allowed = float(claim.total_allowed) if claim.total_allowed else float(claim.total_billed)
    total_paid = float(claim.total_paid) if claim.total_paid else 0.0
    member_resp = float(claim.member_responsibility) if claim.member_responsibility else 0.0

    resource: dict[str, Any] = {
        "resourceType": "ExplanationOfBenefit",
        "id": f"EOB-{claim.claim_id}",
        "status": _claim_status_to_fhir(claim.status),
        "type": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                "code": "professional" if claim.claim_type == "P" else "institutional",
            }]
        },
        "use": "claim",
        "patient": {"reference": patient_ref},
        "created": claim.service_date.isoformat(),
        "insurer": {"display": "Health Plan"},
        "provider": {
            "identifier": {"system": "http://hl7.org/fhir/sid/us-npi", "value": claim.provider_npi or "0000000000"}
        },
        "outcome": "complete" if claim.status.value in ("PAID", "paid") else "queued",
        "insurance": [{"focal": True, "coverage": {"display": "Primary Coverage"}}],
        "item": items,
        "total": [
            {"category": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/adjudication", "code": "submitted"}]},
             "amount": {"value": float(claim.total_billed), "currency": "USD"}},
            {"category": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/adjudication", "code": "eligible"}]},
             "amount": {"value": total_allowed, "currency": "USD"}},
            {"category": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/adjudication", "code": "benefit"}]},
             "amount": {"value": total_paid, "currency": "USD"}},
            {"category": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/adjudication", "code": "copay"}]},
             "amount": {"value": member_resp, "currency": "USD"}},
        ],
    }

    if diagnoses:
        resource["diagnosis"] = diagnoses

    return resource


def _relationship_to_fhir(code: str) -> str:
    """Convert X12 relationship code to FHIR."""
    mapping = {"18": "self", "01": "spouse", "19": "child", "20": "employee", "21": "unknown", "G8": "other"}
    return mapping.get(code, "other")


def _claim_status_to_fhir(status) -> str:
    """Convert claim status to FHIR status."""
    status_val = status.value if hasattr(status, "value") else str(status)
    mapping = {
        "PENDING": "active", "SUBMITTED": "active", "ADJUDICATED": "active", 
        "PAID": "active", "DENIED": "cancelled",
        "pending": "active", "submitted": "active", "adjudicated": "active",
        "paid": "active", "denied": "cancelled",
    }
    return mapping.get(status_val, "active")


def create_fhir_bundle(resources: list[dict[str, Any]], bundle_type: str = "collection") -> dict[str, Any]:
    """Create FHIR Bundle containing multiple resources."""
    return {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "type": bundle_type,
        "total": len(resources),
        "entry": [{"resource": r} for r in resources],
    }


class MemberSimFHIRTransformer:
    """Transform MemberSim entities to FHIR R4 resources."""

    def transform_members(self, members: list[Member], plans: list[Plan] | None = None, include_patient: bool = True) -> dict[str, Any]:
        """Transform members to FHIR Coverage bundle."""
        resources = []
        plan_map = {p.plan_code: p for p in (plans or [])}
        for member in members:
            if include_patient:
                resources.append(member_to_fhir_patient(member))
            plan = plan_map.get(member.plan_code)
            resources.append(member_to_fhir_coverage(member, plan))
        return create_fhir_bundle(resources)

    def transform_claims(self, claims: list[Claim], members: list[Member] | None = None, as_eob: bool = False) -> dict[str, Any]:
        """Transform claims to FHIR Claim or EOB bundle."""
        resources = []
        member_map = {m.member_id: m for m in (members or [])}
        for claim in claims:
            member = member_map.get(claim.member_id)
            if as_eob:
                resources.append(claim_to_fhir_eob(claim, member))
            else:
                resources.append(claim_to_fhir_claim(claim, member))
        return create_fhir_bundle(resources)
