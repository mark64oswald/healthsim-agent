"""Generation tools for HealthSim Agent.

Exposes the product generators (PatientSim, MemberSim, TrialSim, RxMemberSim)
as tools that can be called by the agent.
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel

from healthsim_agent.tools.base import ToolResult, ok, err


def _model_to_dict(obj: Any) -> dict:
    """Convert a Pydantic model or dataclass to a JSON-serializable dict."""
    if obj is None:
        return None
    
    if isinstance(obj, BaseModel):
        return _serialize_value(obj.model_dump())
    elif hasattr(obj, "__dict__"):
        return _serialize_value(obj.__dict__)
    else:
        return _serialize_value(obj)


def _serialize_value(value: Any) -> Any:
    """Recursively serialize values to JSON-compatible types."""
    if value is None:
        return None
    elif isinstance(value, (str, int, float, bool)):
        return value
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, (date, datetime)):
        return value.isoformat()
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, BaseModel):
        return _serialize_value(value.model_dump())
    elif hasattr(value, "__dict__"):
        return _serialize_value(value.__dict__)
    else:
        return str(value)


# =============================================================================
# PatientSim Generation
# =============================================================================

def generate_patients(
    count: int = 1,
    age_range: tuple[int, int] | None = None,
    gender: str | None = None,
    include_encounters: bool = False,
    include_diagnoses: bool = False,
    include_vitals: bool = False,
    include_labs: bool = False,
    include_medications: bool = False,
    diagnosis_categories: list[str] | None = None,
    seed: int | None = None,
) -> ToolResult:
    """Generate synthetic patient data with optional clinical data.
    
    Args:
        count: Number of patients to generate (1-100)
        age_range: Tuple of (min_age, max_age), defaults to (18, 85)
        gender: 'male', 'female', or None for random
        include_encounters: Generate encounters for each patient
        include_diagnoses: Generate diagnoses
        include_vitals: Generate vital signs
        include_labs: Generate lab results
        include_medications: Generate medication orders
        diagnosis_categories: Filter diagnoses by category
        seed: Random seed for reproducibility
    
    Returns:
        ToolResult with generated patient data
    """
    try:
        from healthsim_agent.products.patientsim.core.generator import PatientGenerator
        from healthsim_agent.products.patientsim.core.models import Gender
        
        if count < 1 or count > 100:
            return err("Count must be between 1 and 100")
        
        generator = PatientGenerator(seed=seed)
        
        # Parse gender
        patient_gender = None
        if gender:
            gender_lower = gender.lower()
            if gender_lower in ('m', 'male'):
                patient_gender = Gender.MALE
            elif gender_lower in ('f', 'female'):
                patient_gender = Gender.FEMALE
        
        results = {
            "patients": [],
            "encounters": [],
            "diagnoses": [],
            "vitals": [],
            "labs": [],
            "medications": [],
        }
        
        for _ in range(count):
            patient = generator.generate_patient(
                age_range=age_range,
                gender=patient_gender,
            )
            results["patients"].append(_model_to_dict(patient))
            
            encounter = None
            if include_encounters:
                encounter = generator.generate_encounter(patient)
                results["encounters"].append(_model_to_dict(encounter))
            
            if include_diagnoses:
                num_diag = generator.random_int(1, 3)
                for _ in range(num_diag):
                    category = generator.random_choice(diagnosis_categories) if diagnosis_categories else None
                    try:
                        diag = generator.generate_diagnosis(patient, encounter, category=category)
                        results["diagnoses"].append(_model_to_dict(diag))
                    except ValueError:
                        pass
            
            if include_vitals:
                vitals = generator.generate_vital_signs(patient, encounter)
                results["vitals"].append(_model_to_dict(vitals))
            
            if include_labs:
                num_labs = generator.random_int(2, 5)
                for _ in range(num_labs):
                    lab = generator.generate_lab_result(patient, encounter)
                    results["labs"].append(_model_to_dict(lab))
            
            if include_medications:
                num_meds = generator.random_int(1, 4)
                for _ in range(num_meds):
                    med = generator.generate_medication(patient, encounter)
                    results["medications"].append(_model_to_dict(med))
        
        # Remove empty lists
        results = {k: v for k, v in results.items() if v}
        
        summary_parts = [f"{count} patients"]
        if results.get("encounters"):
            summary_parts.append(f"{len(results['encounters'])} encounters")
        if results.get("diagnoses"):
            summary_parts.append(f"{len(results['diagnoses'])} diagnoses")
        if results.get("vitals"):
            summary_parts.append(f"{len(results['vitals'])} vital sets")
        if results.get("labs"):
            summary_parts.append(f"{len(results['labs'])} lab results")
        if results.get("medications"):
            summary_parts.append(f"{len(results['medications'])} medications")
        
        return ok(
            data=results,
            message=f"Generated {', '.join(summary_parts)}"
        )
        
    except Exception as e:
        return err(f"Patient generation failed: {str(e)}")


# =============================================================================
# MemberSim Generation
# =============================================================================

def generate_members(
    count: int = 1,
    age_range: tuple[int, int] | None = None,
    include_enrollment: bool = True,
    include_claims: bool = False,
    claims_per_member: int = 3,
    seed: int | None = None,
) -> ToolResult:
    """Generate synthetic health plan member data.
    
    Args:
        count: Number of members to generate (1-100)
        age_range: Tuple of (min_age, max_age), defaults to (18, 85)
        include_enrollment: Include enrollment/coverage data
        include_claims: Generate claims for members
        claims_per_member: Number of claims per member if include_claims
        seed: Random seed for reproducibility
    
    Returns:
        ToolResult with generated member data
    """
    try:
        from healthsim_agent.products.membersim.core.generator import MemberGenerator
        
        if count < 1 or count > 100:
            return err("Count must be between 1 and 100")
        
        generator = MemberGenerator(seed=seed)
        
        results = {
            "members": [],
            "enrollments": [],
            "claims": [],
        }
        
        for _ in range(count):
            member = generator.generate_member(age_range=age_range)
            results["members"].append(_model_to_dict(member))
            
            if include_enrollment:
                enrollment = generator.generate_enrollment(member)
                results["enrollments"].append(_model_to_dict(enrollment))
            
            if include_claims:
                for _ in range(claims_per_member):
                    claim = generator.generate_claim(member)
                    results["claims"].append(_model_to_dict(claim))
        
        # Remove empty lists
        results = {k: v for k, v in results.items() if v}
        
        summary_parts = [f"{count} members"]
        if results.get("enrollments"):
            summary_parts.append(f"{len(results['enrollments'])} enrollments")
        if results.get("claims"):
            summary_parts.append(f"{len(results['claims'])} claims")
        
        return ok(
            data=results,
            message=f"Generated {', '.join(summary_parts)}"
        )
        
    except Exception as e:
        return err(f"Member generation failed: {str(e)}")


# =============================================================================
# TrialSim Generation
# =============================================================================

def generate_subjects(
    count: int = 1,
    protocol_id: str = "PROTO-001",
    site_id: str = "SITE-001",
    age_range: tuple[int, int] | None = None,
    include_visits: bool = False,
    include_adverse_events: bool = False,
    include_exposures: bool = False,
    seed: int | None = None,
) -> ToolResult:
    """Generate synthetic clinical trial subject data.
    
    Args:
        count: Number of subjects to generate (1-100)
        protocol_id: Protocol identifier
        site_id: Site identifier
        age_range: Tuple of (min_age, max_age), defaults to (18, 75)
        include_visits: Generate visit schedule
        include_adverse_events: Generate adverse events
        include_exposures: Generate drug exposure records
        seed: Random seed for reproducibility
    
    Returns:
        ToolResult with generated subject data
    """
    try:
        from healthsim_agent.products.trialsim.core.generator import (
            TrialSubjectGenerator,
            VisitGenerator,
            AdverseEventGenerator,
            ExposureGenerator,
        )
        
        if count < 1 or count > 100:
            return err("Count must be between 1 and 100")
        
        subject_gen = TrialSubjectGenerator(seed=seed)
        visit_gen = VisitGenerator(seed=seed) if include_visits else None
        ae_gen = AdverseEventGenerator(seed=seed) if include_adverse_events else None
        exp_gen = ExposureGenerator(seed=seed) if include_exposures else None
        
        results = {
            "subjects": [],
            "visits": [],
            "adverse_events": [],
            "exposures": [],
        }
        
        # Parse age_range for kwargs
        kwargs = {}
        if age_range:
            # Generate random age in range for each subject
            import random
            rng = random.Random(seed)
            ages = [rng.randint(age_range[0], age_range[1]) for _ in range(count)]
        else:
            ages = [None] * count
        
        for i in range(count):
            if ages[i] is not None:
                kwargs["age"] = ages[i]
            
            subject = subject_gen.generate(
                protocol_id=protocol_id,
                site_id=site_id,
                **kwargs
            )
            results["subjects"].append(_model_to_dict(subject))
            
            if visit_gen:
                visits = visit_gen.generate_schedule(subject)
                for visit in visits:
                    results["visits"].append(_model_to_dict(visit))
            
            if ae_gen:
                aes = ae_gen.generate_for_subject(subject)
                for ae in aes:
                    results["adverse_events"].append(_model_to_dict(ae))
            
            if exp_gen:
                exposures = exp_gen.generate_for_subject(subject)
                for exp in exposures:
                    results["exposures"].append(_model_to_dict(exp))
        
        # Remove empty lists
        results = {k: v for k, v in results.items() if v}
        
        summary_parts = [f"{count} subjects"]
        if results.get("visits"):
            summary_parts.append(f"{len(results['visits'])} visits")
        if results.get("adverse_events"):
            summary_parts.append(f"{len(results['adverse_events'])} AEs")
        if results.get("exposures"):
            summary_parts.append(f"{len(results['exposures'])} exposures")
        
        return ok(
            data=results,
            message=f"Generated {', '.join(summary_parts)}"
        )
        
    except Exception as e:
        return err(f"Subject generation failed: {str(e)}")


# =============================================================================
# RxMemberSim Generation
# =============================================================================

def generate_rx_members(
    count: int = 1,
    bin_number: str | None = None,
    pcn: str | None = None,
    group_number: str | None = None,
    seed: int | None = None,
) -> ToolResult:
    """Generate synthetic pharmacy benefit member data.
    
    Args:
        count: Number of Rx members to generate (1-100)
        bin_number: BIN number (identifies PBM), auto-generated if not provided
        pcn: Processor Control Number, auto-generated if not provided
        group_number: Group number, auto-generated if not provided
        seed: Random seed for reproducibility
    
    Returns:
        ToolResult with generated Rx member data
    """
    try:
        from healthsim_agent.products.rxmembersim.core.member import RxMemberFactory
        
        if count < 1 or count > 100:
            return err("Count must be between 1 and 100")
        
        factory = RxMemberFactory()
        
        results = {
            "rx_members": [],
        }
        
        # Build kwargs only for non-None values
        kwargs = {}
        if bin_number:
            kwargs["bin"] = bin_number
        if pcn:
            kwargs["pcn"] = pcn
        if group_number:
            kwargs["group_number"] = group_number
        
        for _ in range(count):
            member = factory.generate(**kwargs)
            results["rx_members"].append(_model_to_dict(member))
        
        return ok(
            data=results,
            message=f"Generated {count} pharmacy members"
        )
        
    except Exception as e:
        return err(f"Rx member generation failed: {str(e)}")


def generate_pharmacy_claims(
    count: int = 3,
    member_id: str | None = None,
    include_member: bool = True,
    drug_category: str | None = None,
    date_range_days: int = 90,
    seed: int | None = None,
) -> ToolResult:
    """Generate synthetic pharmacy claims with pricing and drug details.
    
    Args:
        count: Number of claims to generate (1-50)
        member_id: Generate claims for specific member (creates new member if not provided)
        include_member: Include member data in output
        drug_category: Filter to specific drug category (e.g., 'diabetes', 'cardiac', 'generic')
        date_range_days: Date range to spread claims over (default 90 days)
        seed: Random seed for reproducibility
    
    Returns:
        ToolResult with generated pharmacy claims
    """
    try:
        from healthsim_agent.products.rxmembersim.claims.factory import PharmacyClaimFactory
        from healthsim_agent.products.rxmembersim.core.member import RxMemberFactory
        
        if count < 1 or count > 50:
            return err("Count must be between 1 and 50")
        
        # Create factories
        claim_factory = PharmacyClaimFactory(seed=seed)
        member_factory = RxMemberFactory()
        
        # Get or create member
        member = member_factory.generate()
        
        # Generate claims
        claims = claim_factory.generate_for_member(
            member=member,
            count=count,
            date_range_days=date_range_days,
        )
        
        results = {
            "pharmacy_claims": [_model_to_dict(claim) for claim in claims],
        }
        
        if include_member:
            results["rx_members"] = [_model_to_dict(member)]
        
        # Calculate totals
        total_submitted = sum(float(c.gross_amount_due) for c in claims)
        
        return ok(
            data=results,
            message=f"Generated {len(claims)} pharmacy claims totaling ${total_submitted:.2f}"
        )
        
    except Exception as e:
        return err(f"Pharmacy claim generation failed: {str(e)}")


def check_formulary(
    drug_name: str,
    ndc: str | None = None,
) -> ToolResult:
    """Check if a drug is covered on formulary.
    
    Args:
        drug_name: Name of the drug
        ndc: National Drug Code (optional)
    
    Returns:
        ToolResult with formulary status
    """
    try:
        from healthsim_agent.products.rxmembersim.formulary.formulary import FormularyGenerator
        
        formulary_gen = FormularyGenerator()
        formulary = formulary_gen.generate_standard_commercial()
        
        # Search formulary
        result = formulary.lookup(drug_name=drug_name, ndc=ndc)
        
        if result:
            return ok(
                data=_model_to_dict(result),
                message=f"Drug '{drug_name}' found on formulary"
            )
        else:
            return ok(
                data={"covered": False, "drug_name": drug_name},
                message=f"Drug '{drug_name}' not found on formulary"
            )
        
    except Exception as e:
        return err(f"Formulary check failed: {str(e)}")


# =============================================================================
# Skill Tools (Cross-Product)
# =============================================================================

def list_skills(product: str | None = None) -> ToolResult:
    """List available generation skills/scenarios.
    
    Args:
        product: Filter by product ('patientsim', 'membersim', 'rxmembersim', 'trialsim', 
                 'populationsim', 'networksim')
                 If None, lists skills for all products.
    
    Returns:
        ToolResult with list of available skills
    """
    from pathlib import Path
    
    try:
        # Skills are in the healthsim-agent/skills directory
        # Go up from tools -> healthsim_agent -> src -> healthsim-agent -> skills
        module_path = Path(__file__).parent.parent.parent.parent
        skills_base = module_path / "skills"
        
        if not skills_base.exists():
            return err(f"Skills directory not found at {skills_base}")
        
        all_products = ["patientsim", "membersim", "rxmembersim", "trialsim", "populationsim", "networksim"]
        products = [product] if product else all_products
        
        skills = {}
        for prod in products:
            prod_dir = skills_base / prod
            if prod_dir.exists():
                # Get all markdown files, excluding README
                skill_files = [f for f in prod_dir.glob("*.md") if f.name not in ("README.md", "SKILL.md")]
                
                # Also get skills from subdirectories
                for subdir in prod_dir.iterdir():
                    if subdir.is_dir() and not subdir.name.startswith("_"):
                        skill_files.extend([f for f in subdir.glob("*.md") if f.name != "README.md"])
                
                skills[prod] = [
                    {
                        "name": f.stem,
                        "path": str(f.relative_to(skills_base)),
                    }
                    for f in sorted(skill_files)
                ]
        
        total = sum(len(v) for v in skills.values())
        return ok(
            data=skills,
            message=f"Found {total} skills across {len(skills)} products"
        )
        
    except Exception as e:
        return err(f"Failed to list skills: {str(e)}")


def describe_skill(skill_name: str, product: str) -> ToolResult:
    """Get detailed information about a specific skill.
    
    Args:
        skill_name: Name of the skill (without extension)
        product: Product the skill belongs to
    
    Returns:
        ToolResult with skill details and examples
    """
    from pathlib import Path
    
    try:
        module_path = Path(__file__).parent.parent.parent.parent
        skills_base = module_path / "skills"
        
        # Try direct path first
        skill_path = skills_base / product / f"{skill_name}.md"
        
        # If not found, search subdirectories
        if not skill_path.exists():
            prod_dir = skills_base / product
            if prod_dir.exists():
                for subdir in prod_dir.iterdir():
                    if subdir.is_dir():
                        candidate = subdir / f"{skill_name}.md"
                        if candidate.exists():
                            skill_path = candidate
                            break
        
        if not skill_path.exists():
            return err(f"Skill '{skill_name}' not found in {product}")
        
        content = skill_path.read_text()
        
        # Parse YAML frontmatter if present
        metadata = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                import yaml
                try:
                    metadata = yaml.safe_load(parts[1])
                except:
                    pass
                body = parts[2].strip()
        
        return ok(
            data={
                "name": skill_name,
                "product": product,
                "path": str(skill_path.relative_to(skills_base)),
                "metadata": metadata,
                "content": body[:3000] + ("..." if len(body) > 3000 else ""),
            },
            message=f"Skill: {skill_name}"
        )
        
    except Exception as e:
        return err(f"Failed to describe skill: {str(e)}")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # PatientSim
    "generate_patients",
    # MemberSim
    "generate_members",
    # TrialSim
    "generate_subjects",
    # RxMemberSim
    "generate_rx_members",
    "generate_pharmacy_claims",
    "check_formulary",
    # Skills
    "list_skills",
    "describe_skill",
]
