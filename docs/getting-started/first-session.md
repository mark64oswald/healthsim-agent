# Your First HealthSim Session

This 5-minute walkthrough will teach you the basics of generating healthcare data with HealthSim.

---

## Starting HealthSim

Open your terminal and start an interactive session:

```bash
healthsim
```

You'll see the HealthSim welcome screen:

```
╭──────────────────────────────────────────────────────────╮
│                   HealthSim Agent                        │
│         Synthetic Healthcare Data Generation             │
╰──────────────────────────────────────────────────────────╯

Type your request, or use /help for available commands.

healthsim ›
```

The `healthsim ›` prompt means HealthSim is ready for your requests.

---

## Your First Patient

Let's generate a patient. Just describe what you need:

```
healthsim › Generate a 55-year-old female patient with Type 2 diabetes
```

HealthSim will create a clinically plausible patient:

```
✓ Added 1 patient to current session

  ID:        PAT-001
  Name:      Maria Garcia
  Age:       55 (DOB: 1970-08-15)
  Gender:    Female
  
  Diagnoses:
    • E11.9   Type 2 diabetes mellitus without complications
    • I10     Essential hypertension
    • E78.5   Hyperlipidemia, unspecified
  
  Medications:
    • Metformin 1000mg PO BID
    • Lisinopril 10mg PO daily
    • Atorvastatin 20mg PO daily
  
  Recent Labs:
    • HbA1c: 7.2% (elevated)
    • Glucose: 142 mg/dL
    • Creatinine: 0.9 mg/dL
```

That's it! You just generated a synthetic patient with realistic clinical data.

---

## Understanding the Output

HealthSim creates **clinically plausible** data:

- **Diagnoses** use valid ICD-10 codes with appropriate comorbidities (diabetes often comes with hypertension and hyperlipidemia)
- **Medications** match the diagnoses (metformin for diabetes, lisinopril for hypertension)
- **Labs** reflect the conditions (elevated A1C for diabetes)

This isn't random data—it follows clinical patterns.

---

## Checking Your Session

See what's in your current session:

```
healthsim › /status
```

Output:
```
Current Session
═══════════════════════════════════════
Patients:     1
Encounters:   0
Claims:       0
Pharmacy:     0

Recent Activity:
  • PAT-001 (Maria Garcia) - Type 2 diabetes
```

---

## Adding More Data

### Add an Encounter

```
healthsim › Add an office visit encounter for this patient
```

```
✓ Added 1 encounter

  Encounter: ENC-001
  Type:      Office Visit
  Date:      2025-12-15
  Provider:  Dr. James Wilson, MD (Internal Medicine)
  Reason:    Diabetes follow-up
  
  Procedures:
    • 99214 - Office visit, established patient
```

### Add a Claim

```
healthsim › Generate a professional claim for this visit
```

```
✓ Added 1 claim

  Claim:     CLM-2026-000001
  Type:      Professional (837P)
  DOS:       2025-12-15
  
  Services:
    • 99214 - E&M, established patient, moderate
  
  Financials:
    Charges:   $175.00
    Allowed:   $132.50
    Copay:     $25.00
    Paid:      $107.50
  
  Status:    Paid
```

### Add Pharmacy Claims

```
healthsim › Generate pharmacy claims for her medications
```

```
✓ Added 3 pharmacy claims

  Rx Claims Generated:
  ┌────────────────────┬─────────────┬────────┬────────┐
  │ Medication         │ NDC         │ Qty    │ Copay  │
  ├────────────────────┼─────────────┼────────┼────────┤
  │ Metformin 1000mg   │ 00093-7267  │ 60     │ $8.00  │
  │ Lisinopril 10mg    │ 00093-7339  │ 30     │ $5.00  │
  │ Atorvastatin 20mg  │ 00093-5059  │ 30     │ $10.00 │
  └────────────────────┴─────────────┴────────┴────────┘
```

---

## Viewing Your Data

### Query with SQL

Use the `/sql` command to query your data directly:

```
healthsim › /sql SELECT * FROM patients
```

```
┌─────────┬───────────────┬────────────┬────────┐
│ mrn     │ name          │ birth_date │ gender │
├─────────┼───────────────┼────────────┼────────┤
│ PAT-001 │ Maria Garcia  │ 1970-08-15 │ F      │
└─────────┴───────────────┴────────────┴────────┘
```

### Check Session Status Again

```
healthsim › /status
```

```
Current Session
═══════════════════════════════════════
Patients:     1
Encounters:   1
Claims:       1 (Professional)
Pharmacy:     3 (Rx Claims)

Total Entities: 6
```

---

## Saving Your Work

Don't lose your data! Save it as a named cohort:

```
healthsim › save as my-first-cohort
```

```
✓ Saved session as 'my-first-cohort'

  Entities: 6
  Location: ~/.healthsim/healthsim.duckdb
```

You can come back to this data anytime.

---

## Exporting Data

Export your patient as FHIR R4 for testing healthcare APIs:

```
healthsim › Export as FHIR R4
```

```
✓ Generated FHIR R4 Bundle → output/patient-bundle.json

  Bundle Type: collection
  Resources:
    • 1 Patient
    • 1 Encounter
    • 3 Condition
    • 3 MedicationRequest
```

Other export formats:
- `Export as HL7v2` - HL7v2 messages
- `Export as C-CDA` - Clinical Document Architecture
- `Export as X12 837` - Claims EDI format
- `Export as CSV` - Tabular data

---

## Loading Previous Work

Next time you start HealthSim, load your saved cohort:

```
healthsim › load my-first-cohort
```

```
✓ Loaded 'my-first-cohort'

  Patients:   1
  Encounters: 1
  Claims:     1
  Pharmacy:   3
```

You're right back where you left off.

---

## Ending Your Session

When you're done:

```
healthsim › /quit
```

Or press `Ctrl+D`.

---

## Quick Tips

### Be Specific
The more detail you provide, the better the output:

```
# Basic
Generate a patient with diabetes

# Better
Generate a 65-year-old Hispanic male with poorly controlled Type 2 
diabetes (A1C 9.5), diabetic nephropathy, and hypertension in Houston, TX
```

### Use Natural Language
Describe what you need like you're talking to a colleague:

```
"Create a patient who had a heart attack last month and is now on 
appropriate post-MI medications"
```

### Combine Domains
Generate complete patient journeys:

```
"Generate a diabetic patient with their recent endocrinology visit 
claim and pharmacy fills for insulin"
```

### Try Format Transformations
Same data, different formats:

```
Generate this patient as FHIR
Export as HL7 ADT message
Show as X12 837P
```

---

## What's Next?

You've learned the basics! Explore further:

- **[Quick Reference](quick-reference.md)** - All commands at a glance
- **[PatientSim Guide](../guides/patientsim-guide.md)** - Deep dive into clinical data
- **[MemberSim Guide](../guides/membersim-guide.md)** - Claims and enrollment
- **[Examples](../../examples/)** - More detailed examples

---

## Common First-Session Issues

### "I don't see any output"

HealthSim might be processing. Wait a moment. If it persists, check your API key.

### "My patient doesn't have medications"

Try being more specific:
```
Generate a diabetic patient with appropriate medications
```

### "How do I go back?"

You can't undo within a session, but you can:
1. Save checkpoints frequently
2. Load a previous save
3. Start fresh with a new session

### "The data doesn't match what I asked for"

Rephrase your request to be more specific. HealthSim interprets natural language, and sometimes needs clearer instructions.

---

Happy generating! 🏥
