# Denial Scenarios

Generate claims denial scenarios for testing payer systems, appeals workflows, and exception handling.

---

## Goal

Create realistic denied claims with proper denial reason codes, appeal information, and resolution pathways.

## Prerequisites

- HealthSim Agent installed and configured
- Familiarity with basic claims generation

---

## Example 1: Prior Authorization Required

### Step 1: Generate Denied Claim

```
healthsim › Generate a denied professional claim for MRI requiring prior authorization
```

Expected output:
```json
{
  "member": {
    "member_id": "MEM002345",
    "name": { "given_name": "Michael", "family_name": "Chen" },
    "plan_code": "HMO-PLUS"
  },
  "claim": {
    "claim_id": "CLM-2025-000002",
    "claim_type": "PROFESSIONAL",
    "service_date": "2025-01-15",
    "place_of_service": "22",
    "principal_diagnosis": "M54.5",
    "diagnosis_description": "Low back pain",
    "claim_lines": [
      {
        "line_number": 1,
        "procedure_code": "72148",
        "procedure_description": "MRI lumbar spine without contrast",
        "charge_amount": 1500.00
      }
    ],
    "prior_auth_number": null
  },
  "adjudication": {
    "status": "denied",
    "adjudication_date": "2025-01-17",
    "denial_reason": {
      "code": "CO-15",
      "description": "Authorization required",
      "message": "Prior authorization is required for this service."
    },
    "allowed_amount": 0.00,
    "paid_amount": 0.00,
    "patient_responsibility": 0.00,
    "appeal_info": {
      "can_appeal": true,
      "appeal_deadline": "2025-07-17",
      "instructions": "Submit prior authorization or appeal with medical records"
    }
  }
}
```

### Key Points

- CO-15 = Authorization required
- Patient responsibility is $0 (not billed to member)
- Appeal information provided with deadline
- HMO plans commonly require PA for imaging

---

## Example 2: Duplicate Submission

### Generate Duplicate Denial

```
healthsim › Generate a denied claim for duplicate submission (CO-18)
```

Expected output:
```json
{
  "adjudication": {
    "status": "denied",
    "denial_reason": {
      "code": "CO-18",
      "description": "Exact duplicate claim/service",
      "message": "This service was previously submitted and processed.",
      "original_claim_id": "CLM-2025-000001"
    },
    "resolution": "Review original claim status before resubmitting"
  }
}
```

---

## Example 3: Timely Filing Denial

```
healthsim › Generate a denied claim for timely filing violation (CO-29)
```

Expected output:
```json
{
  "claim": {
    "service_date": "2024-01-15",
    "submission_date": "2025-01-20"
  },
  "adjudication": {
    "status": "denied",
    "denial_reason": {
      "code": "CO-29",
      "description": "The time limit for filing has expired",
      "filing_limit": "365 days from date of service",
      "days_elapsed": 370
    },
    "appeal_info": {
      "can_appeal": true,
      "notes": "Appeal must include proof of timely original submission or extenuating circumstances"
    }
  }
}
```

---

## Example 4: Bundling Denial

```
healthsim › Generate a denied claim for bundling (CO-97) where a procedure is included in another
```

Expected output:
```json
{
  "claim": {
    "claim_lines": [
      {
        "line_number": 1,
        "procedure_code": "99214",
        "status": "paid",
        "paid_amount": 98.50
      },
      {
        "line_number": 2,
        "procedure_code": "36415",
        "procedure_description": "Venipuncture",
        "status": "denied",
        "denial_reason": {
          "code": "CO-97",
          "description": "The benefit for this service is included in the payment for another service",
          "bundled_with": "99214"
        }
      }
    ]
  }
}
```

---

## Example 5: Medical Necessity Denial

```
healthsim › Generate a denied claim for lack of medical necessity with appeal pathway
```

Expected output:
```json
{
  "adjudication": {
    "status": "denied",
    "denial_reason": {
      "code": "CO-50",
      "description": "These services are not deemed medically necessary",
      "clinical_review": {
        "reviewed_by": "Medical Director",
        "review_date": "2025-01-18",
        "rationale": "Documentation does not support medical necessity for advanced imaging"
      }
    },
    "appeal_info": {
      "level": "Peer-to-Peer",
      "deadline": "2025-02-17",
      "required_documentation": [
        "Clinical notes supporting medical necessity",
        "Conservative treatment failure documentation",
        "Relevant test results"
      ]
    }
  }
}
```

---

## Common Denial Codes Reference

| Code | Description | Typical Resolution |
|------|-------------|-------------------|
| CO-4 | Procedure code inconsistent with modifier | Correct billing |
| CO-15 | Authorization required | Submit PA |
| CO-16 | Information inconsistent | Correct/clarify |
| CO-18 | Duplicate claim | Check original |
| CO-29 | Timely filing | Appeal with proof |
| CO-45 | Exceeds fee schedule | Normal adjustment |
| CO-50 | Not medically necessary | Peer-to-peer |
| CO-97 | Bundled service | Review CCI edits |

---

## Variations

```
Generate an out-of-network denial with balance billing
Generate a non-covered service denial
Generate a claim denied for missing information
Generate a claim with partial denial (some lines paid)
Generate a claim denied pending coordination of benefits
```

---

## Related

- [Claims Generation](../basic/claims-generation.md) - Basic paid claims
- [Format Transformations](format-transformations.md) - Export as X12 835/277

---

*Denial Scenarios v1.0 | HealthSim Agent*
