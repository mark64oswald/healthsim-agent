# Format Transformations Example

Export HealthSim data to various industry standard formats.

---

## Goal

Learn to export generated data to FHIR, X12, NCPDP, CDISC, and other formats. You'll learn:

- Format-specific exports
- Multi-format packages
- Format validation
- Transformation options

---

## Prerequisites

- Generated patient or claims data
- Basic understanding of healthcare data standards
- ~10 minutes

---

## Setup: Generate Source Data

First, let's create some data to transform:

```
healthsim › Create a patient named Sarah Johnson, 45, with hypertension 
            and type 2 diabetes. Add an office visit with labs and 
            prescriptions for lisinopril and metformin.
```

Expected output:
```
✓ Generated patient with clinical data

Patient: PAT-001 (Sarah Johnson)
  Conditions: 2 (HTN, T2DM)
  Encounters: 1 (Office visit)
  Observations: 6 (Labs, vitals)
  Medications: 2 (Lisinopril, Metformin)
```

---

## FHIR Exports

### FHIR R4 Bundle

```
healthsim › Export as FHIR R4 bundle
```

Expected output:
```
✓ Exported FHIR R4 Bundle

Output: ./exports/fhir-bundle-20260112.json
Format: FHIR R4 (4.0.1)
Bundle Type: collection

Resources:
  Patient: 1
  Condition: 2
  Encounter: 1
  Observation: 6
  MedicationRequest: 2
  Practitioner: 1
  Organization: 1
  
Total Resources: 14
Validation: ✓ Valid
```

### FHIR Bundle Preview

```
healthsim › Show me the FHIR Patient resource
```

```json
{
  "resourceType": "Patient",
  "id": "PAT-001",
  "identifier": [{
    "system": "urn:healthsim:patient",
    "value": "PAT-001"
  }],
  "name": [{
    "use": "official",
    "family": "Johnson",
    "given": ["Sarah"]
  }],
  "gender": "female",
  "birthDate": "1980-07-15",
  "address": [{
    "use": "home",
    "line": ["123 Main Street"],
    "city": "Denver",
    "state": "CO",
    "postalCode": "80202"
  }]
}
```

### US Core Profile

```
healthsim › Export as FHIR US Core bundle
```

```
✓ Exported FHIR US Core Bundle

Output: ./exports/fhir-uscore-20260112.json
Profile: US Core 5.0.1

Additional Elements Added:
  • Patient.identifier (MRN, SSN)
  • Patient.race extension
  • Patient.ethnicity extension
  • Encounter.type (US Core codes)
  
Validation: ✓ US Core compliant
```

---

## HL7v2 Exports

### ADT Message

```
healthsim › Export patient as HL7v2 ADT^A01
```

Expected output:
```
✓ Exported HL7v2 ADT^A01

Output: ./exports/adt-a01-20260112.hl7
Message Type: ADT^A01 (Admit/Visit)
Version: 2.5.1

Segments:
  MSH - Message Header
  EVN - Event Type
  PID - Patient Identification
  PV1 - Patient Visit
  DG1 - Diagnosis (x2)
  OBX - Observation (x6)
```

### HL7v2 Preview

```
MSH|^~\&|HEALTHSIM|FAC001|RECEIVER|FAC002|20260112143022||ADT^A01|MSG00001|P|2.5.1
EVN|A01|20260112143022
PID|1||PAT-001^^^HEALTHSIM&1.2.3.4&ISO||Johnson^Sarah||19800715|F|||123 Main Street^^Denver^CO^80202
PV1|1|O|^^^CLINIC||||1234567890^Park^Lisa^MD
DG1|1||I10^Essential hypertension^ICD10|||A
DG1|2||E11.9^Type 2 diabetes mellitus^ICD10|||A
```

### ORU Message (Results)

```
healthsim › Export lab results as HL7v2 ORU^R01
```

```
✓ Exported HL7v2 ORU^R01

Output: ./exports/oru-r01-20260112.hl7
Message Type: ORU^R01 (Observation Result)
Results: 6 observations
```

---

## X12 EDI Exports

### 837P Professional Claim

First, generate a claim:

```
healthsim › Generate a professional claim for Sarah's office visit
```

Then export:

```
healthsim › Export as X12 837P
```

Expected output:
```
✓ Exported X12 837P

Output: ./exports/837p-20260112.edi
Transaction: 837P (Professional Claim)
Version: 005010X222A1

Segments:
  ISA/IEA - Interchange envelope
  GS/GE - Functional group
  ST/SE - Transaction set
  BHT - Beginning of hierarchical transaction
  NM1 - Billing/Pay-to provider
  CLM - Claim information
  DTP - Date/time reference
  HI - Health care information codes
  SV1 - Professional service
  
Claims: 1
Total Billed: $175.00
```

### 837P Preview

```
ISA*00*          *00*          *ZZ*HEALTHSIM     *ZZ*PAYER001      *260112*1430*^*00501*000000001*0*P*:~
GS*HC*HEALTHSIM*PAYER001*20260112*1430*1*X*005010X222A1~
ST*837*0001*005010X222A1~
BHT*0019*00*0001*20260112*1430*CH~
NM1*41*2*DENVER MEDICAL GROUP*****46*1234567890~
...
```

### 835 Remittance Advice

```
healthsim › Process the claim and export the 835 remittance
```

```
✓ Adjudicated claim and exported 835

Output: ./exports/835-20260112.edi
Transaction: 835 (Payment/Remittance)

Payment Summary:
  Billed: $175.00
  Allowed: $135.00
  Patient Responsibility: $25.00
  Plan Paid: $110.00
```

---

## NCPDP Exports

### NCPDP D.0 Claim

```
healthsim › Generate pharmacy claim for metformin and export as NCPDP
```

Expected output:
```
✓ Exported NCPDP D.0

Output: ./exports/ncpdp-d0-20260112.dat
Standard: NCPDP D.0 Telecommunication
Version: D.0

Transaction:
  BIN: 003858
  PCN: A4
  Group: RXGRP001
  Service Type: B1 (Billing)
  
Claim Details:
  NDC: 00093-7214-01 (Metformin 1000mg)
  Qty: 90
  Days Supply: 30
  
Response: Paid
```

### NCPDP SCRIPT ePrescription

```
healthsim › Export prescription as NCPDP SCRIPT NewRx
```

```
✓ Exported NCPDP SCRIPT

Output: ./exports/script-newrx-20260112.xml
Standard: NCPDP SCRIPT 2017071
Message Type: NewRx

Elements:
  <Header> - Routing info
  <Body>
    <NewRx>
      <Patient> - Demographics
      <Prescriber> - Provider info
      <MedicationPrescribed> - Drug details
```

---

## CDISC Exports (TrialSim)

Generate trial data first:

```
healthsim › Create a trial subject who completed a 12-week diabetes 
            trial with adverse events and efficacy data
```

### SDTM Datasets

```
healthsim › Export as CDISC SDTM
```

Expected output:
```
✓ Exported CDISC SDTM

Output Directory: ./exports/sdtm/

Datasets:
  dm.xpt - Demographics (1 row)
  ae.xpt - Adverse Events (3 rows)
  cm.xpt - Concomitant Meds (5 rows)
  ex.xpt - Exposure (12 rows)
  lb.xpt - Laboratory (48 rows)
  vs.xpt - Vital Signs (36 rows)
  
Format: SAS Transport (XPT)
SDTM Version: 3.3
Validation: ✓ Pinnacle 21 compatible
```

### ADaM Datasets

```
healthsim › Export as CDISC ADaM
```

```
✓ Exported CDISC ADaM

Output Directory: ./exports/adam/

Datasets:
  adsl.xpt - Subject Level (1 row)
  adae.xpt - Adverse Events Analysis (3 rows)
  adlb.xpt - Laboratory Analysis (48 rows)
  advs.xpt - Vital Signs Analysis (36 rows)
  
Format: SAS Transport (XPT)
ADaM Version: 1.1
```

---

## Multi-Format Package

### Export Everything

```
healthsim › Export Sarah Johnson's data in all available formats
```

Expected output:
```
✓ Created multi-format export package

Package: ./exports/sarah-johnson-20260112.zip

Contents:
  fhir/
    bundle.json (FHIR R4)
    uscore-bundle.json (US Core)
    
  hl7v2/
    adt-a01.hl7 (ADT message)
    oru-r01.hl7 (Results)
    
  x12/
    837p.edi (Professional claim)
    837i.edi (Facility claim)
    835.edi (Remittance)
    
  ncpdp/
    d0-claim.dat (Pharmacy claim)
    script-newrx.xml (ePrescription)
    
  csv/
    patients.csv
    encounters.csv
    claims.csv
    medications.csv
    
  json/
    canonical.json (HealthSim native format)

Total Files: 14
Package Size: 245 KB
```

---

## Format Options

### Specify Format Version

```
healthsim › Export as FHIR STU3 (not R4)
```

### Include Validation Report

```
healthsim › Export with validation report
```

```
✓ Exported with validation

Validation Report: ./exports/validation-report.json

FHIR Validation:
  Errors: 0
  Warnings: 2
    • Missing preferred language
    • Missing emergency contact
  Info: 5
    
US Core Conformance: 94%
```

### Custom Mappings

```
healthsim › Export X12 837P with custom payer-specific requirements
```

---

## What You Created

| Format | Standard | Use Case |
|--------|----------|----------|
| FHIR R4 | HL7 FHIR | EHR integration |
| US Core | HL7 FHIR | US healthcare |
| HL7v2 | HL7 2.5.1 | Legacy systems |
| X12 837 | ANSI X12 | Claims submission |
| X12 835 | ANSI X12 | Payment posting |
| NCPDP D.0 | NCPDP | Pharmacy claims |
| SCRIPT | NCPDP | ePrescribing |
| SDTM | CDISC | Clinical trials |
| ADaM | CDISC | Trial analysis |

---

## Troubleshooting

**Format validation failing?**
- Check required fields: "What fields are missing?"
- Request compliant data: "Generate with US Core required fields"

**Wrong format version?**
- Specify version: "Export as FHIR R4" or "Export as HL7v2 2.5.1"

**Missing segments in X12?**
- Ensure all claim data exists
- Check: "Show claim details before export"

---

## Related

- [Output Formats Reference](../../docs/reference/output-formats.md)
- [Code Systems Reference](../../docs/reference/code-systems.md)
- [Integration Guide](../../docs/reference/integration-guide.md)
