# Output Formats Reference

HealthSim Agent supports 12 output formats covering clinical, claims, pharmacy, and research data exchange. This reference documents each format, its use cases, and transformation patterns.

## Format Summary

| Format | Domain | Standard | Use Case |
|--------|--------|----------|----------|
| **FHIR R4** | Clinical | HL7 FHIR | Modern interoperability, EHR integration |
| **C-CDA** | Clinical | HL7 CDA | Clinical document exchange |
| **HL7v2** | Clinical | HL7 v2.x | Legacy system integration |
| **X12 837P** | Claims | ANSI X12 | Professional claims submission |
| **X12 837I** | Claims | ANSI X12 | Institutional claims submission |
| **X12 835** | Claims | ANSI X12 | Remittance advice |
| **X12 834** | Enrollment | ANSI X12 | Benefit enrollment |
| **X12 270/271** | Eligibility | ANSI X12 | Eligibility inquiry/response |
| **NCPDP D.0** | Pharmacy | NCPDP | Pharmacy claims telecom |
| **NCPDP SCRIPT** | Pharmacy | NCPDP | e-Prescribing |
| **CDISC SDTM** | Research | CDISC | Clinical trial submissions |
| **CDISC ADaM** | Research | CDISC | Analysis datasets |

---

## Clinical Formats

### FHIR R4

Fast Healthcare Interoperability Resources (Release 4)

**Resource Types Generated:**
- Patient, Practitioner, Organization
- Encounter, Condition, Procedure
- Observation (vitals, labs)
- MedicationRequest, MedicationAdministration
- Claim, ExplanationOfBenefit
- ResearchStudy, ResearchSubject

**Usage:**
```
You: Export the diabetes cohort as FHIR

Claude: Generating FHIR R4 Bundle...

Bundle contains:
- 20 Patient resources
- 45 Condition resources  
- 156 Encounter resources
- 89 MedicationRequest resources
```

**Key Features:**
- Full FHIR R4 compliance
- Resource references maintained
- Identifiers use standard systems (NPI, SSN placeholders)
- CodeableConcepts with proper coding systems

**Example Patient Resource:**
```json
{
  "resourceType": "Patient",
  "id": "patient-a8c4e2f1",
  "identifier": [{
    "system": "urn:oid:2.16.840.1.113883.4.1",
    "value": "900-12-3456"
  }],
  "name": [{
    "family": "Santos",
    "given": ["Maria"]
  }],
  "gender": "female",
  "birthDate": "1979-03-15",
  "address": [{
    "city": "Houston",
    "state": "TX",
    "postalCode": "77001"
  }]
}
```

---

### C-CDA (Consolidated CDA)

Clinical Document Architecture for structured documents.

**Document Types:**
| Type | Description |
|------|-------------|
| CCD | Continuity of Care Document |
| Discharge Summary | Hospital discharge |
| Progress Note | Encounter documentation |
| Referral Note | Provider referral |
| Transfer Summary | Care transitions |

**Usage:**
```
You: Generate a CCD document for patient MRN-2847391

Claude: Creating Continuity of Care Document...

Sections included:
- Problems (4 conditions)
- Medications (6 active)
- Allergies (2 documented)
- Vital Signs (last 3 encounters)
- Results (recent labs)
- Encounters (last 12 months)
```

---

### HL7 v2.x

Legacy messaging format for real-time system integration.

**Message Types:**
| Type | Trigger | Description |
|------|---------|-------------|
| ADT^A01 | Admit | Patient admission |
| ADT^A03 | Discharge | Patient discharge |
| ADT^A04 | Register | Outpatient registration |
| ADT^A08 | Update | Patient information update |
| ORU^R01 | Results | Lab/observation results |
| ORM^O01 | Order | Order message |
| RDE^O11 | Pharmacy | Pharmacy order |

**Usage:**
```
You: Generate ADT messages for the emergency department encounters

Claude: Creating HL7v2 ADT messages...

Generated:
- 12 ADT^A04 (Registration)
- 3 ADT^A01 (Admission)
- 3 ADT^A03 (Discharge)
```

**Example ADT Message:**
```
MSH|^~\&|HEALTHSIM|HOSPITAL|RECEIVER|DEST|20240115143022||ADT^A04|MSG001|P|2.5.1
EVN|A04|20240115143022
PID|1||MRN-2847391^^^HOSPITAL^MR||SANTOS^MARIA||19790315|F|||123 MAIN ST^^HOUSTON^TX^77001
PV1|1|E|ED^^^HOSPITAL||||1234567890^SMITH^JOHN^MD||||||||||||V123456
```

---

## Claims Formats

### X12 837P (Professional Claims)

Professional (non-institutional) healthcare claims.

**Loop Structure:**
- 1000A/B - Submitter/Receiver
- 2000A - Billing Provider
- 2000B - Subscriber
- 2300 - Claim Information
- 2400 - Service Lines

**Usage:**
```
You: Export professional claims for member MBR-9284756 as X12

Claude: Generating 837P transactions...

Claims exported:
- 8 professional claims
- 23 service lines
- $3,450 total charges
```

---

### X12 837I (Institutional Claims)

Hospital and facility claims.

**Loop Structure:**
- 2300 - Claim Information (with UB-04 data)
- 2310 - Attending/Rendering providers
- 2400 - Service Lines (revenue codes)

**Includes:**
- Admission/discharge dates
- Revenue codes
- DRG assignment
- Occurrence codes
- Value codes

---

### X12 835 (Remittance Advice)

Payment and remittance information.

**Loop Structure:**
- 1000A/B - Payer/Payee
- 2100 - Claim Payment Information
- 2110 - Service Payment Information

**Usage:**
```
You: Generate ERA for the submitted claims

Claude: Creating 835 Remittance Advice...

Remittance includes:
- 8 claims processed
- $2,890 paid
- $560 patient responsibility
- 3 adjustment reasons
```

---

### X12 834 (Enrollment)

Benefit enrollment and maintenance.

**Usage:**
- New enrollment
- Terminations
- Changes (demographics, coverage)
- Reinstatement

---

### X12 270/271 (Eligibility)

Eligibility inquiry and response.

**270 Request:**
- Member identification
- Date of service
- Service type codes

**271 Response:**
- Eligibility status
- Benefit information
- Co-pay/deductible amounts

---

## Pharmacy Formats

### NCPDP D.0 (Telecom)

Real-time pharmacy claims transmission.

**Transaction Types:**
| Type | Description |
|------|-------------|
| B1 | Billing Request |
| B2 | Reversal |
| B3 | Rebill |
| E1 | Eligibility Verification |

**Segments:**
- Patient, Cardholder, Insurance
- Claim, Pricing, DUR/PPS
- Coordination of Benefits

**Usage:**
```
You: Export pharmacy claims as NCPDP

Claude: Generating NCPDP D.0 transactions...

Transactions:
- 12 B1 billing requests
- Total: $384.50
- 3 with DUR alerts
```

**DUR Response Codes:**
| Code | Description |
|------|-------------|
| TD | Therapeutic Duplication |
| DD | Drug-Drug Interaction |
| ER | Early Refill |
| HD | High Dose |

---

### NCPDP SCRIPT

Electronic prescribing standard.

**Message Types:**
| Type | Description |
|------|-------------|
| NewRx | New prescription |
| RefillRequest | Refill authorization |
| RxChangeRequest | Therapeutic interchange |
| CancelRx | Prescription cancellation |
| RxFill | Dispensing notification |

**Usage:**
```
You: Generate NewRx messages for the metformin prescriptions

Claude: Creating NCPDP SCRIPT messages...

Messages:
- 6 NewRx transactions
- Drug: Metformin 500mg
- Sig: Take 1 tablet by mouth twice daily
```

---

## Research Formats

### CDISC SDTM

Study Data Tabulation Model for regulatory submissions.

**Domains Generated:**
| Domain | Description |
|--------|-------------|
| DM | Demographics |
| DS | Disposition |
| AE | Adverse Events |
| CM | Concomitant Medications |
| EX | Exposure |
| LB | Laboratory Tests |
| VS | Vital Signs |
| MH | Medical History |
| IE | Inclusion/Exclusion |
| SV | Subject Visits |

**Usage:**
```
You: Export trial subjects as SDTM datasets

Claude: Generating CDISC SDTM domains...

Datasets:
- DM.xpt (50 subjects)
- AE.xpt (23 events)
- CM.xpt (156 medications)
- LB.xpt (450 results)
- VS.xpt (300 measurements)
```

**Controlled Terminology:**
- MedDRA for adverse events
- WHO Drug for medications
- LOINC for lab tests
- CDISC CT for standard variables

---

### CDISC ADaM

Analysis Data Model for statistical analysis.

**Dataset Types:**
| Type | Description |
|------|-------------|
| ADSL | Subject-Level Analysis |
| ADAE | Adverse Events Analysis |
| ADLB | Laboratory Analysis |
| ADVS | Vital Signs Analysis |
| ADEFF | Efficacy Analysis |
| ADTTE | Time-to-Event Analysis |

**Key Features:**
- BDS (Basic Data Structure) format
- Analysis flags and derivations
- PARAMCD/PARAM standardization
- Traceability to SDTM

---

## Format Comparison

### By Entity Type

| Entity | Best Formats |
|--------|-------------|
| Patient demographics | FHIR Patient, ADT, 834, DM |
| Encounters | FHIR Encounter, ADT, 837I |
| Conditions | FHIR Condition, CCD, MH/CM |
| Medications | FHIR MedicationRequest, SCRIPT, CM |
| Labs | FHIR Observation, ORU, LB |
| Claims | FHIR Claim, 837P/837I, D.0 |
| Pharmacy | NCPDP D.0, SCRIPT, RxMemberSim JSON |
| Trial data | SDTM, ADaM |

### By Use Case

| Use Case | Recommended Format |
|----------|-------------------|
| EHR integration | FHIR R4 |
| Legacy system | HL7v2 |
| Payer submission | X12 837 |
| Pharmacy real-time | NCPDP D.0 |
| e-Prescribing | NCPDP SCRIPT |
| FDA submission | CDISC SDTM/ADaM |
| Analytics | JSON, CSV |

---

## Transformation Commands

```
You: Show available output formats

Claude: Available formats:
- FHIR R4 (clinical, modern)
- C-CDA (clinical documents)
- HL7v2 (legacy messaging)
- X12 837P/837I/835/834 (claims)
- NCPDP D.0/SCRIPT (pharmacy)
- CDISC SDTM/ADaM (research)
- JSON (native)
- CSV (analysis)

You: Export cohort as [format]
You: Transform [entity] to [format]
You: Generate [format] for [scenario]
```

---

## Related Documentation

- [Tools Reference](tools-reference.md) - Transform tool functions
- [Code Systems](code-systems.md) - Healthcare terminologies
- [PatientSim Guide](../guides/patientsim-guide.md) - Clinical data
- [MemberSim Guide](../guides/membersim-guide.md) - Claims data
- [TrialSim Guide](../guides/trialsim-guide.md) - Research data
