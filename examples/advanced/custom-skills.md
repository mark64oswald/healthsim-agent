# Custom Skills

Learn how to extend HealthSim with new scenarios, formats, and domain knowledge.

---

## Goal

Create your own skills to customize HealthSim for specific use cases, adding new clinical scenarios, industry formats, or specialized code systems.

## Prerequisites

- Familiarity with HealthSim skill structure
- Understanding of healthcare data standards

---

## Architecture Overview

```
skills/
├── patientsim/           # Clinical data skills
│   ├── SKILL.md          # Product overview
│   ├── demographics.md   # Patient demographics
│   └── conditions.md     # Clinical conditions
├── membersim/            # Claims data skills
├── rxmembersim/          # Pharmacy data skills
├── trialsim/             # Clinical trial skills
├── populationsim/        # Population analytics skills
└── networksim/           # Provider network skills
```

### How Skills Work

1. **User request** → Agent reads relevant skill files
2. **Skill files** → Define what to generate and how
3. **References** → Provide codes, schemas, validation rules
4. **Output** → Generated data follows skill specifications

---

## Example 1: Add a Maternal Health Scenario

### Step 1: Create the Skill File

Create `skills/patientsim/maternal-health.md`:

```markdown
# Maternal Health Scenario

## Trigger Phrases

- pregnancy
- prenatal
- OB visit
- postpartum
- maternal

## Parameters

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| trimester | string | first | first, second, third, postpartum |
| risk_level | string | low | low, moderate, high |
| complications | list | none | gestational_diabetes, preeclampsia |

## Clinical Context

### Normal Pregnancy Timeline
- First trimester: Weeks 1-12
- Second trimester: Weeks 13-26
- Third trimester: Weeks 27-40

### Common Diagnoses

| Condition | ICD-10 | Trimester |
|-----------|--------|-----------|
| Normal pregnancy | Z34.00 | Any |
| Gestational diabetes | O24.4x | 2nd-3rd |
| Preeclampsia | O14.x | 2nd-3rd |

## Example Output

```json
{
  "patient": {
    "mrn": "PAT-001",
    "name": { "given_name": "Sarah", "family_name": "Johnson" },
    "gender": "F"
  },
  "pregnancy": {
    "gestational_age_weeks": 28,
    "trimester": "third",
    "edd": "2025-04-20",
    "gravida": 2,
    "para": 1
  }
}
```

## Related Skills

- [Demographics](demographics.md)
- [Conditions](conditions.md)
```

### Step 2: Update Product SKILL.md

Add to `skills/patientsim/SKILL.md`:

```markdown
## Scenario Skills

| Scenario | Trigger Phrases | File |
|----------|-----------------|------|
| **Maternal Health** | pregnancy, prenatal, OB | [maternal-health.md](maternal-health.md) |
```

### Step 3: Test the Skill

```
healthsim › Generate a third-trimester patient with gestational diabetes

✓ Skill matched: maternal-health
✓ Generated patient with pregnancy data
```

---

## Example 2: Add a New Output Format

### Create Format Skill

Create `skills/formats/ccd-r2.md`:

```markdown
# CCD R2 Format

## Overview

Consolidated Clinical Document Architecture (C-CDA) Release 2.1

## Trigger Phrases

- as CCD
- as C-CDA
- continuity of care document

## Transformation Rules

### Patient → recordTarget

```xml
<recordTarget>
  <patientRole>
    <id extension="{mrn}"/>
    <patient>
      <name>
        <given>{name.given_name}</given>
        <family>{name.family_name}</family>
      </name>
    </patient>
  </patientRole>
</recordTarget>
```
```

---

## Skill Template

Every skill should include:

```markdown
# [Skill Name]

## Trigger Phrases

- phrase 1
- phrase 2

## Parameters

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| param1 | string | default | option1, option2 |

## Generation Rules

[Domain-specific logic]

## Example Output

```json
{ ... }
```

## Validation Rules

| Rule | Description | Severity |
|------|-------------|----------|
| RULE-001 | Description | error/warning |

## Related Skills

- [Related Skill](link.md)
```

---

## Best Practices

### 1. Be Specific with Trigger Phrases

- Choose phrases commonly used in requests
- Avoid overlap with other scenarios
- Include abbreviations AND full terms

### 2. Include Realistic Examples

- At least one complete example output
- Key points explaining important fields
- Variations showing different parameters

### 3. Use Real Code Systems

- ICD-10, CPT, LOINC, NDC codes
- Include code descriptions
- Verify codes are current

### 4. Cross-Reference Properly

- Link to parent SKILL.md files
- Reference related scenarios
- Connect to relevant format skills

---

## Extension Checklist

- [ ] Create skill file with proper structure
- [ ] Add trigger phrases (at least 3)
- [ ] Define parameters with defaults
- [ ] Include at least 2 examples
- [ ] Add validation rules
- [ ] Update product SKILL.md
- [ ] Test with sample prompts

---

## Related

- [HealthSim Architecture](../../docs/architecture/overview.md)
- [PatientSim Guide](../../docs/guides/patientsim-guide.md)
- [Contributing Guide](../../docs/contributing/README.md)

---

*Custom Skills v1.0 | HealthSim Agent*
