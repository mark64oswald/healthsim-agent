"""Validation tools for HealthSim Agent.

Provides data validation across all entity types.
"""

from typing import Any

from healthsim_agent.tools.base import ToolResult, ok, err


def validate_data(
    entities: list[dict[str, Any]],
    entity_type: str,
    rules: list[str] | None = None,
    strict: bool = False,
) -> ToolResult:
    """Validate entities against schema and business rules.
    
    Args:
        entities: List of entity dictionaries to validate
        entity_type: Type of entity ('patient', 'member', 'subject', 'rx_member', 
                     'encounter', 'claim', 'diagnosis', etc.)
        rules: Optional list of specific rules to check (e.g., ['required_fields', 
               'code_validity', 'date_consistency'])
        strict: If True, fail on warnings; if False, only fail on errors
    
    Returns:
        ToolResult with validation results including issues found
    """
    try:
        if not entities:
            return err("No entities provided for validation")
        
        all_rules = rules or ["required_fields", "data_types", "code_validity", "date_consistency"]
        
        issues = []
        warnings = []
        
        # Get validator for entity type
        validator = _get_validator(entity_type)
        
        for idx, entity in enumerate(entities):
            entity_issues, entity_warnings = validator(entity, all_rules)
            for issue in entity_issues:
                issues.append({"index": idx, "type": "error", **issue})
            for warning in entity_warnings:
                warnings.append({"index": idx, "type": "warning", **warning})
        
        is_valid = len(issues) == 0 and (not strict or len(warnings) == 0)
        
        return ok(
            data={
                "valid": is_valid,
                "entity_count": len(entities),
                "error_count": len(issues),
                "warning_count": len(warnings),
                "issues": issues,
                "warnings": warnings,
            },
            message=f"Validated {len(entities)} {entity_type}(s): {len(issues)} errors, {len(warnings)} warnings"
        )
        
    except Exception as e:
        return err(f"Validation failed: {str(e)}")


def fix_validation_issues(
    entities: list[dict[str, Any]],
    entity_type: str,
    auto_fix: list[str] | None = None,
) -> ToolResult:
    """Attempt to automatically fix common validation issues.
    
    Args:
        entities: List of entity dictionaries to fix
        entity_type: Type of entity
        auto_fix: List of issue types to auto-fix (e.g., ['missing_ids', 
                  'date_format', 'code_normalization']). If None, fix all fixable issues.
    
    Returns:
        ToolResult with fixed entities and summary of changes
    """
    try:
        if not entities:
            return err("No entities provided for fixing")
        
        fixable_issues = auto_fix or ["missing_ids", "date_format", "code_normalization", "null_defaults"]
        
        fixed_entities = []
        changes = []
        
        for idx, entity in enumerate(entities):
            fixed_entity = entity.copy()
            entity_changes = []
            
            # Fix missing IDs
            if "missing_ids" in fixable_issues:
                id_field = _get_id_field(entity_type)
                if id_field and not fixed_entity.get(id_field):
                    import uuid
                    fixed_entity[id_field] = f"{entity_type}-{uuid.uuid4().hex[:8]}"
                    entity_changes.append({"field": id_field, "action": "generated_id"})
            
            # Fix date format issues
            if "date_format" in fixable_issues:
                for field, value in list(fixed_entity.items()):
                    if "date" in field.lower() and value:
                        normalized = _normalize_date(value)
                        if normalized != value:
                            fixed_entity[field] = normalized
                            entity_changes.append({"field": field, "action": "normalized_date"})
            
            # Fix null defaults
            if "null_defaults" in fixable_issues:
                defaults = _get_defaults(entity_type)
                for field, default_value in defaults.items():
                    if field not in fixed_entity or fixed_entity[field] is None:
                        fixed_entity[field] = default_value
                        entity_changes.append({"field": field, "action": "set_default"})
            
            fixed_entities.append(fixed_entity)
            if entity_changes:
                changes.append({"index": idx, "changes": entity_changes})
        
        total_changes = sum(len(c["changes"]) for c in changes)
        
        return ok(
            data={
                "entities": fixed_entities,
                "changes": changes,
                "entities_modified": len(changes),
                "total_changes": total_changes,
            },
            message=f"Fixed {total_changes} issues in {len(changes)} entities"
        )
        
    except Exception as e:
        return err(f"Fix operation failed: {str(e)}")


# =============================================================================
# Helper Functions
# =============================================================================

def _get_validator(entity_type: str):
    """Get validator function for entity type."""
    validators = {
        "patient": _validate_patient,
        "member": _validate_member,
        "subject": _validate_subject,
        "rx_member": _validate_rx_member,
        "encounter": _validate_encounter,
        "claim": _validate_claim,
        "diagnosis": _validate_diagnosis,
    }
    return validators.get(entity_type, _validate_generic)


def _validate_patient(entity: dict, rules: list[str]) -> tuple[list[dict], list[dict]]:
    """Validate patient entity."""
    errors = []
    warnings = []
    
    if "required_fields" in rules:
        required = ["id", "birth_date", "gender"]
        for field in required:
            if not entity.get(field):
                errors.append({"rule": "required_fields", "field": field, "message": f"Missing required field: {field}"})
    
    if "data_types" in rules:
        if entity.get("birth_date") and not _is_valid_date(entity["birth_date"]):
            errors.append({"rule": "data_types", "field": "birth_date", "message": "Invalid date format"})
    
    if "code_validity" in rules:
        if entity.get("gender") and entity["gender"] not in ("M", "F", "male", "female", "other", "unknown"):
            warnings.append({"rule": "code_validity", "field": "gender", "message": f"Non-standard gender code: {entity['gender']}"})
    
    return errors, warnings


def _validate_member(entity: dict, rules: list[str]) -> tuple[list[dict], list[dict]]:
    """Validate member entity."""
    errors = []
    warnings = []
    
    if "required_fields" in rules:
        required = ["member_id"]
        for field in required:
            if not entity.get(field):
                errors.append({"rule": "required_fields", "field": field, "message": f"Missing required field: {field}"})
    
    return errors, warnings


def _validate_subject(entity: dict, rules: list[str]) -> tuple[list[dict], list[dict]]:
    """Validate trial subject entity."""
    errors = []
    warnings = []
    
    if "required_fields" in rules:
        required = ["subject_id", "protocol_id"]
        for field in required:
            if not entity.get(field):
                errors.append({"rule": "required_fields", "field": field, "message": f"Missing required field: {field}"})
    
    return errors, warnings


def _validate_rx_member(entity: dict, rules: list[str]) -> tuple[list[dict], list[dict]]:
    """Validate Rx member entity."""
    errors = []
    warnings = []
    
    if "required_fields" in rules:
        required = ["member_id", "bin"]
        for field in required:
            if not entity.get(field):
                errors.append({"rule": "required_fields", "field": field, "message": f"Missing required field: {field}"})
    
    return errors, warnings


def _validate_encounter(entity: dict, rules: list[str]) -> tuple[list[dict], list[dict]]:
    """Validate encounter entity."""
    errors = []
    warnings = []
    
    if "required_fields" in rules:
        if not entity.get("id") and not entity.get("encounter_id"):
            errors.append({"rule": "required_fields", "field": "id", "message": "Missing encounter ID"})
    
    return errors, warnings


def _validate_claim(entity: dict, rules: list[str]) -> tuple[list[dict], list[dict]]:
    """Validate claim entity."""
    errors = []
    warnings = []
    
    if "required_fields" in rules:
        required = ["claim_id"]
        for field in required:
            if not entity.get(field):
                errors.append({"rule": "required_fields", "field": field, "message": f"Missing required field: {field}"})
    
    return errors, warnings


def _validate_diagnosis(entity: dict, rules: list[str]) -> tuple[list[dict], list[dict]]:
    """Validate diagnosis entity."""
    errors = []
    warnings = []
    
    if "required_fields" in rules:
        if not entity.get("code"):
            errors.append({"rule": "required_fields", "field": "code", "message": "Missing diagnosis code"})
    
    if "code_validity" in rules:
        code = entity.get("code", "")
        if code and not _is_valid_icd10(code):
            warnings.append({"rule": "code_validity", "field": "code", "message": f"Non-standard ICD-10 format: {code}"})
    
    return errors, warnings


def _validate_generic(entity: dict, rules: list[str]) -> tuple[list[dict], list[dict]]:
    """Generic validation for unknown entity types."""
    return [], []


def _get_id_field(entity_type: str) -> str | None:
    """Get the ID field name for an entity type."""
    id_fields = {
        "patient": "id",
        "member": "member_id",
        "subject": "subject_id",
        "rx_member": "member_id",
        "encounter": "id",
        "claim": "claim_id",
        "diagnosis": "id",
    }
    return id_fields.get(entity_type, "id")


def _get_defaults(entity_type: str) -> dict[str, Any]:
    """Get default values for an entity type."""
    defaults = {
        "patient": {"deceased": False, "language": "en"},
        "member": {},
        "subject": {"status": "screening"},
        "rx_member": {},
    }
    return defaults.get(entity_type, {})


def _is_valid_date(value: Any) -> bool:
    """Check if value is a valid date."""
    if isinstance(value, str):
        try:
            from datetime import datetime
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except:
            return False
    return True


def _normalize_date(value: Any) -> str:
    """Normalize date to ISO format."""
    if isinstance(value, str):
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.date().isoformat()
        except:
            return value
    return value


def _is_valid_icd10(code: str) -> bool:
    """Check if code looks like valid ICD-10."""
    import re
    # ICD-10 format: Letter + 2 digits + optional . + up to 4 alphanumeric
    return bool(re.match(r'^[A-Z]\d{2}(\.\d{1,4})?$', code.upper()))


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "validate_data",
    "fix_validation_issues",
]
