# HealthSim Agent Examples

Working examples demonstrating HealthSim capabilities.

---

## Example Categories

### 🟢 Basic Examples

Simple, focused examples for learning the fundamentals.

| Example | Description | Domain |
|---------|-------------|--------|
| [Patient Generation](basic/patient-generation.md) | Create patients with conditions | PatientSim |
| [Claims Generation](basic/claims-generation.md) | Generate professional claims | MemberSim |
| [Pharmacy Claims](basic/pharmacy-claims.md) | Create pharmacy transactions | RxMemberSim |
| [Pharmacy Generation](basic/pharmacy-generation.md) | Generate Rx data scenarios | RxMemberSim |
| [Provider Search](basic/provider-search.md) | Find and use provider data | NetworkSim |

### 🟡 Intermediate Examples

More complex scenarios combining features.

| Example | Description | Domains |
|---------|-------------|---------|
| [Cross-Product Workflow](intermediate/cross-product-workflow.md) | Patient journey across domains | All |
| [Cohort Analytics](intermediate/cohort-analytics.md) | Generate and analyze cohorts | Multiple |
| [Format Transformations](intermediate/format-transformations.md) | Export to various formats | All |
| [Oncology Scenarios](intermediate/oncology-scenarios.md) | Cancer patient generation | PatientSim |
| [Denial Scenarios](intermediate/denial-scenarios.md) | Claims denial testing | MemberSim |

### 🔴 Advanced Examples

Complex use cases and integration patterns.

| Example | Description | Focus |
|---------|-------------|-------|
| [Clinical Trial Protocol](advanced/clinical-trial-protocol.md) | Design trial protocols | TrialSim |
| [Full Data Pipeline](advanced/full-data-pipeline.md) | End-to-end workflows | All |
| [Population Study](advanced/population-study.md) | SDOH and demographics | PopulationSim |
| [Custom Skills](advanced/custom-skills.md) | Create your own skills | Extension |
| [Batch Generation](advanced/batch-generation.md) | Generate data at scale | Performance |
| [Integration Testing](advanced/integration-testing.md) | CI/CD integration | DevOps |
| [Star Schema Analytics](advanced/star-schema-analytics.md) | Dimensional modeling | Analytics |

---

## Running Examples

Each example includes:

1. **Goal** - What you'll accomplish
2. **Prerequisites** - What you need first
3. **Steps** - Copy-paste ready commands
4. **Expected Output** - What you should see
5. **Variations** - Ways to modify the example

### Example Format

```markdown
# Example Title

## Goal
What this example demonstrates.

## Prerequisites
- HealthSim installed and configured
- API key set

## Steps

### Step 1: [Action]
```
healthsim › [command]
```

Expected output:
```
[output]
```

### Step 2: [Action]
...

## What You Created
Summary of generated data.

## Variations
- Try this different way
- Modify for your use case

## Related
- Links to other examples
- Links to guides
```

---

## Quick Example: Patient with Claims

Here's a complete mini-example you can run right now:

```
healthsim › Generate a 55-year-old diabetic patient in Houston

✓ Added 1 patient (PAT-001: Robert Martinez)

healthsim › Add an office visit for diabetes follow-up

✓ Added 1 encounter (ENC-001)

healthsim › Generate a professional claim for this visit

✓ Added 1 claim (CLM-2025-000001, $175.00)

healthsim › Add pharmacy claims for metformin and lisinopril

✓ Added 2 pharmacy claims

healthsim › save as quick-example

✓ Saved session 'quick-example'

healthsim › /status

Current Session
═══════════════════════════════════════
Patients:     1
Encounters:   1
Claims:       1 (Professional)
Pharmacy:     2 (Rx Claims)
═══════════════════════════════════════
```

Total time: ~2 minutes.

---

## Examples by Use Case

### EMR/EHR Testing

- [Patient Generation](basic/patient-generation.md) - Basic patient records
- [Format Transformations](intermediate/format-transformations.md) - FHIR, HL7v2, C-CDA
- [Oncology Scenarios](intermediate/oncology-scenarios.md) - Complex clinical data

### Claims System Testing

- [Claims Generation](basic/claims-generation.md) - Professional claims
- [Denial Scenarios](intermediate/denial-scenarios.md) - Error handling
- [Batch Generation](advanced/batch-generation.md) - Volume testing

### PBM/Pharmacy Testing

- [Pharmacy Claims](basic/pharmacy-claims.md) - Basic Rx claims
- [Pharmacy Generation](basic/pharmacy-generation.md) - Rx scenarios
- [Cross-Product Workflow](intermediate/cross-product-workflow.md) - Medical + Pharmacy

### Analytics & Reporting

- [Cohort Analytics](intermediate/cohort-analytics.md) - Cohort analysis
- [Star Schema Analytics](advanced/star-schema-analytics.md) - Dimensional data
- [Population Study](advanced/population-study.md) - SDOH analytics

### Clinical Trial Systems

- [Clinical Trial Protocol](advanced/clinical-trial-protocol.md) - Trial design
- [Full Data Pipeline](advanced/full-data-pipeline.md) - End-to-end

### Provider Networks

- [Provider Search](basic/provider-search.md) - Find providers

### DevOps & Integration

- [Integration Testing](advanced/integration-testing.md) - CI/CD patterns
- [Custom Skills](advanced/custom-skills.md) - Extend HealthSim

---

## Contributing Examples

Have a useful example? We welcome contributions!

1. Follow the example format above
2. Include all necessary context
3. Test all commands before submitting
4. Submit a PR to the examples/ directory

See [Contributing Guide](../docs/contributing/) for details.
