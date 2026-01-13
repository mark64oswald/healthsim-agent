# Code Systems Reference

Healthcare data relies on standardized code systems for interoperability. This reference documents the code systems used across HealthSim products.

## Code System Overview

| System | Domain | Example | Used In |
|--------|--------|---------|---------|
| **ICD-10-CM** | Diagnoses | E11.65 | PatientSim, MemberSim, TrialSim |
| **ICD-10-PCS** | Procedures | 0DQ60ZZ | PatientSim, MemberSim |
| **CPT** | Professional procedures | 99214 | MemberSim |
| **HCPCS** | Services/supplies | J0129 | MemberSim |
| **NDC** | Drugs | 00069-0150-30 | RxMemberSim |
| **GPI** | Drug classification | 27100010100110 | RxMemberSim |
| **NPI** | Provider identifiers | 1234567890 | NetworkSim, MemberSim |
| **LOINC** | Lab tests | 4548-4 | PatientSim, TrialSim |
| **SNOMED CT** | Clinical terms | 73211009 | PatientSim |
| **RxNorm** | Drug concepts | 860975 | PatientSim, RxMemberSim |
| **MedDRA** | Adverse events | 10019211 | TrialSim |
| **CVX** | Vaccines | 208 | PatientSim |

---

## Diagnosis Codes

### ICD-10-CM (Clinical Modification)

International Classification of Diseases, 10th Revision, Clinical Modification.

**Structure:** 3-7 characters
- Characters 1-3: Category
- Characters 4-7: Subcategory/specificity

**Format:** `A00.0` or `A00.00` (with decimal after 3rd character)

**Common Categories:**

| Range | Description |
|-------|-------------|
| A00-B99 | Infectious diseases |
| C00-D49 | Neoplasms |
| D50-D89 | Blood disorders |
| E00-E89 | Endocrine/metabolic |
| F01-F99 | Mental disorders |
| G00-G99 | Nervous system |
| H00-H59 | Eye diseases |
| H60-H95 | Ear diseases |
| I00-I99 | Circulatory system |
| J00-J99 | Respiratory system |
| K00-K95 | Digestive system |
| L00-L99 | Skin diseases |
| M00-M99 | Musculoskeletal |
| N00-N99 | Genitourinary |
| O00-O9A | Pregnancy |
| P00-P96 | Perinatal |
| Q00-Q99 | Congenital |
| R00-R99 | Symptoms/signs |
| S00-T88 | Injury/poisoning |
| V00-Y99 | External causes |
| Z00-Z99 | Factors influencing health |

**Common Codes in HealthSim:**

| Code | Description | Product |
|------|-------------|---------|
| E11.65 | Type 2 diabetes with hyperglycemia | PatientSim, MemberSim |
| I10 | Essential hypertension | PatientSim, MemberSim |
| J44.1 | COPD with acute exacerbation | PatientSim |
| E78.5 | Hyperlipidemia | PatientSim |
| N18.3 | CKD Stage 3 | PatientSim |
| F32.9 | Major depression | PatientSim |
| M54.5 | Low back pain | MemberSim |

### ICD-10-PCS (Procedure Coding System)

Inpatient procedure classification.

**Structure:** 7 characters (alphanumeric)
- Position 1: Section
- Position 2: Body system
- Position 3: Root operation
- Position 4: Body part
- Position 5: Approach
- Position 6: Device
- Position 7: Qualifier

**Example:** `0DQ60ZZ`
- 0 = Medical/Surgical
- D = Gastrointestinal
- Q = Repair
- 6 = Stomach
- 0 = Open
- Z = No device
- Z = No qualifier

---

## Procedure Codes

### CPT (Current Procedural Terminology)

Professional services and procedures.

**Structure:** 5 digits

**Categories:**

| Range | Description |
|-------|-------------|
| 00100-01999 | Anesthesia |
| 10004-69990 | Surgery |
| 70010-79999 | Radiology |
| 80047-89398 | Pathology/Lab |
| 90281-99607 | Medicine |
| 99201-99499 | E&M (Evaluation/Management) |

**Common E&M Codes:**

| Code | Description | Typical Use |
|------|-------------|-------------|
| 99202 | New patient, straightforward | Simple new visit |
| 99203 | New patient, low complexity | Standard new visit |
| 99204 | New patient, moderate | Complex new visit |
| 99212 | Established, straightforward | Brief follow-up |
| 99213 | Established, low complexity | Standard follow-up |
| 99214 | Established, moderate | Extended follow-up |
| 99215 | Established, high complexity | Complex follow-up |
| 99281 | ED visit, self-limited | Minor ED |
| 99283 | ED visit, low complexity | Standard ED |
| 99284 | ED visit, moderate | Urgent ED |
| 99285 | ED visit, high complexity | Emergency |

**Common Lab Codes:**

| Code | Description |
|------|-------------|
| 80053 | Comprehensive metabolic panel |
| 80061 | Lipid panel |
| 82947 | Glucose |
| 83036 | Hemoglobin A1C |
| 85025 | CBC with differential |
| 84443 | TSH |

### HCPCS Level II

Healthcare Common Procedure Coding System.

**Structure:** Letter + 4 digits (e.g., J0129)

**Categories:**

| Prefix | Description |
|--------|-------------|
| A | Transportation, supplies |
| B | Enteral/parenteral |
| C | Hospital outpatient |
| E | Durable medical equipment |
| G | Temporary procedures |
| J | Drugs (not oral) |
| K | DME temporary |
| L | Orthotics/prosthetics |
| M | Medical services |
| P | Pathology/lab |
| Q | Temporary codes |
| R | Diagnostic radiology |
| S | Private payer |
| T | State Medicaid |
| V | Vision/hearing |

---

## Drug Codes

### NDC (National Drug Code)

Drug identification.

**Structure:** 10-11 digits in 3 segments
- Labeler (4-5 digits)
- Product (3-4 digits)
- Package (1-2 digits)

**Formats:**
- 4-4-2: `0069-0150-30`
- 5-3-2: `00069-150-30`
- 5-4-1: `00069-0150-3`

**Normalization:** HealthSim uses 11-digit format with leading zeros

**Example:** Metformin 500mg
- NDC: `00093-7267-01`
- Labeler: 00093 (Teva)
- Product: 7267 (Metformin 500mg)
- Package: 01 (100 count bottle)

### GPI (Generic Product Identifier)

Drug classification hierarchy.

**Structure:** 14 digits

| Positions | Level | Description |
|-----------|-------|-------------|
| 1-2 | Drug Group | Major therapeutic class |
| 3-4 | Drug Class | Therapeutic subclass |
| 5-6 | Drug Sub-Class | Pharmacological class |
| 7-8 | Drug Name | Generic name |
| 9-10 | Drug Name Extension | Variations |
| 11-12 | Dosage Form | Form |
| 13-14 | Strength | Potency |

**Example:** `27100010100110`
- 27 = Antidiabetic agents
- 10 = Biguanides
- 00 = (no sub-class)
- 10 = Metformin
- 10 = HCl
- 01 = Tablet
- 10 = 500mg

### RxNorm

Drug concept unique identifiers.

**Structure:** Numeric (variable length)

**Concept Types:**
- IN (Ingredient)
- BN (Brand Name)
- SCDC (Semantic Clinical Drug Component)
- SCD (Semantic Clinical Drug)
- SBD (Semantic Branded Drug)

---

## Provider Identifiers

### NPI (National Provider Identifier)

Unique provider identification.

**Structure:** 10 digits

**Entity Types:**
- Type 1: Individual providers
- Type 2: Organizations

**Validation:** Luhn algorithm check digit

**HealthSim Usage:**
- Real NPIs from NPPES for realistic scenarios
- Synthetic NPIs (990xxxxxxx range) for testing

### Taxonomy Codes

Provider specialty classification.

**Structure:** 10 characters (alphanumeric)

**Common Codes:**

| Code | Description |
|------|-------------|
| 207Q00000X | Family Medicine |
| 207R00000X | Internal Medicine |
| 207RC0000X | Cardiovascular Disease |
| 208000000X | Pediatrics |
| 208600000X | Surgery |
| 261QM1200X | Hospital (Acute Care) |
| 261QR1300X | Rural Health Clinic |

---

## Laboratory Codes

### LOINC (Logical Observation Identifiers)

Standardized lab test identification.

**Structure:** Numeric + check digit

**Parts:**
1. Component (analyte)
2. Property (quantity, presence)
3. Time (point, 24h)
4. System (serum, urine)
5. Scale (quantitative, ordinal)
6. Method (optional)

**Common Codes:**

| Code | Description |
|------|-------------|
| 4548-4 | Hemoglobin A1C |
| 2345-7 | Glucose [Mass/Vol] |
| 2093-3 | Cholesterol Total |
| 2571-8 | Triglycerides |
| 1742-6 | ALT |
| 1920-8 | AST |
| 2160-0 | Creatinine |
| 3094-0 | BUN |
| 2823-3 | Potassium |
| 2951-2 | Sodium |

---

## Clinical Terminology

### SNOMED CT

Comprehensive clinical terminology.

**Structure:** 6-18 digit numeric identifier

**Hierarchies:**
- Clinical findings
- Procedures
- Body structures
- Organisms
- Substances
- Pharmaceutical/biological products

**Common Codes:**

| Code | Description |
|------|-------------|
| 73211009 | Diabetes mellitus |
| 38341003 | Hypertensive disorder |
| 195967001 | Asthma |
| 13645005 | COPD |
| 22298006 | Myocardial infarction |
| 84114007 | Heart failure |

### MedDRA (Medical Dictionary for Regulatory Activities)

Adverse event classification for clinical trials.

**Hierarchy:**
1. SOC (System Organ Class)
2. HLGT (High Level Group Term)
3. HLT (High Level Term)
4. PT (Preferred Term) ← Primary coding level
5. LLT (Lowest Level Term)

**Structure:** 8 digits

**Example:**
- SOC: Gastrointestinal disorders
- HLGT: Gastrointestinal signs and symptoms
- HLT: Nausea and vomiting symptoms
- PT: Nausea (10028813)
- LLT: Nausea, Feeling sick

---

## Administrative Codes

### Place of Service

2-digit codes indicating service location.

| Code | Description |
|------|-------------|
| 11 | Office |
| 12 | Home |
| 21 | Inpatient Hospital |
| 22 | Outpatient Hospital |
| 23 | Emergency Room |
| 24 | Ambulatory Surgical Center |
| 31 | Skilled Nursing Facility |
| 32 | Nursing Facility |
| 81 | Independent Lab |

### Revenue Codes

4-digit codes for institutional billing.

| Range | Description |
|-------|-------------|
| 0100-0169 | Room & Board |
| 0250-0259 | Pharmacy |
| 0300-0319 | Lab |
| 0320-0329 | Radiology DX |
| 0350-0359 | CT Scan |
| 0450-0459 | Emergency Room |
| 0636 | Drugs/Biologicals |
| 0730-0739 | EKG |
| 0750-0759 | GI Services |

### DAW Codes (Dispense As Written)

| Code | Description |
|------|-------------|
| 0 | No product selection indicated |
| 1 | Substitution not allowed by prescriber |
| 2 | Substitution allowed, patient requested brand |
| 3 | Substitution allowed, pharmacist selected |
| 4 | Substitution allowed, generic not in stock |
| 5 | Substitution allowed, brand dispensed as generic |

---

## Code System URIs

Standard URIs for FHIR and interoperability:

| System | URI |
|--------|-----|
| ICD-10-CM | `http://hl7.org/fhir/sid/icd-10-cm` |
| CPT | `http://www.ama-assn.org/go/cpt` |
| LOINC | `http://loinc.org` |
| SNOMED CT | `http://snomed.info/sct` |
| RxNorm | `http://www.nlm.nih.gov/research/umls/rxnorm` |
| NDC | `http://hl7.org/fhir/sid/ndc` |
| NPI | `http://hl7.org/fhir/sid/us-npi` |
| MedDRA | `http://www.meddra.org` |

---

## Related Documentation

- [Output Formats](output-formats.md) - Format specifications
- [PatientSim Guide](../guides/patientsim-guide.md) - Clinical codes
- [MemberSim Guide](../guides/membersim-guide.md) - Claims codes
- [RxMemberSim Guide](../guides/rxmembersim-guide.md) - Pharmacy codes
- [TrialSim Guide](../guides/trialsim-guide.md) - Research codes
