"""Tests for skill schema definitions.

Tests the data structures for skill definitions.
"""

import pytest

from healthsim_agent.skills.schema import (
    ParameterType,
    Skill,
    SkillMetadata,
    SkillParameter,
    SkillType,
    SkillVariation,
)


class TestSkillType:
    """Tests for SkillType enum."""

    def test_skill_type_values(self):
        """Test skill type values."""
        assert SkillType.DOMAIN_KNOWLEDGE.value == "domain-knowledge"
        assert SkillType.COHORT_TEMPLATE.value == "cohort-template"
        assert SkillType.FORMAT_SPEC.value == "format-spec"
        assert SkillType.VALIDATION_RULES.value == "validation-rules"
        assert SkillType.GENERATION_GUIDE.value == "generation-guide"


class TestParameterType:
    """Tests for ParameterType enum."""

    def test_parameter_type_values(self):
        """Test parameter type values."""
        assert ParameterType.RANGE.value == "range"
        assert ParameterType.ENUM.value == "enum"
        assert ParameterType.BOOLEAN.value == "boolean"
        assert ParameterType.INTEGER.value == "integer"
        assert ParameterType.FLOAT.value == "float"
        assert ParameterType.STRING.value == "string"
        assert ParameterType.LIST.value == "list"
        assert ParameterType.OBJECT.value == "object"


class TestSkillMetadata:
    """Tests for SkillMetadata class."""

    def test_default_values(self):
        """Test default metadata values."""
        meta = SkillMetadata()
        assert meta.type == SkillType.COHORT_TEMPLATE
        assert meta.version == "1.0"
        assert meta.author is None
        assert meta.tags == []
        assert meta.requires_version is None

    def test_custom_values(self):
        """Test custom metadata values."""
        meta = SkillMetadata(
            type=SkillType.DOMAIN_KNOWLEDGE,
            version="2.0",
            author="HealthSim Team",
            tags=["clinical", "demographics"],
            requires_version="1.5",
        )
        assert meta.type == SkillType.DOMAIN_KNOWLEDGE
        assert meta.version == "2.0"
        assert meta.author == "HealthSim Team"
        assert meta.tags == ["clinical", "demographics"]
        assert meta.requires_version == "1.5"


class TestSkillParameter:
    """Tests for SkillParameter class."""

    def test_basic_parameter(self):
        """Test creating a basic parameter."""
        param = SkillParameter(name="age", type=ParameterType.INTEGER)
        assert param.name == "age"
        assert param.type == ParameterType.INTEGER
        assert param.default is None
        assert param.required is False

    def test_parameter_with_constraints(self):
        """Test parameter with min/max constraints."""
        param = SkillParameter(
            name="age",
            type=ParameterType.INTEGER,
            min_value=0,
            max_value=120,
            default=45,
        )
        assert param.min_value == 0
        assert param.max_value == 120
        assert param.default == 45

    def test_enum_parameter(self):
        """Test enum parameter with options."""
        param = SkillParameter(
            name="gender",
            type=ParameterType.ENUM,
            options=["male", "female", "other"],
            required=True,
        )
        assert param.options == ["male", "female", "other"]
        assert param.required is True


class TestSkillParameterValidation:
    """Tests for SkillParameter.validate_value() method."""

    def test_validate_none_required(self):
        """Test None value for required parameter."""
        param = SkillParameter(name="age", type=ParameterType.INTEGER, required=True)
        assert param.validate_value(None) is False

    def test_validate_none_optional(self):
        """Test None value for optional parameter."""
        param = SkillParameter(name="age", type=ParameterType.INTEGER, required=False)
        assert param.validate_value(None) is True

    def test_validate_enum_valid(self):
        """Test valid enum value."""
        param = SkillParameter(
            name="gender",
            type=ParameterType.ENUM,
            options=["male", "female"],
        )
        assert param.validate_value("male") is True

    def test_validate_enum_invalid(self):
        """Test invalid enum value."""
        param = SkillParameter(
            name="gender",
            type=ParameterType.ENUM,
            options=["male", "female"],
        )
        assert param.validate_value("other") is False

    def test_validate_enum_no_options(self):
        """Test enum with no options (any value valid)."""
        param = SkillParameter(name="status", type=ParameterType.ENUM)
        assert param.validate_value("anything") is True

    def test_validate_boolean_valid(self):
        """Test valid boolean value."""
        param = SkillParameter(name="active", type=ParameterType.BOOLEAN)
        assert param.validate_value(True) is True
        assert param.validate_value(False) is True

    def test_validate_boolean_invalid(self):
        """Test invalid boolean value."""
        param = SkillParameter(name="active", type=ParameterType.BOOLEAN)
        assert param.validate_value("true") is False
        assert param.validate_value(1) is False

    def test_validate_integer_valid(self):
        """Test valid integer value."""
        param = SkillParameter(
            name="age",
            type=ParameterType.INTEGER,
            min_value=0,
            max_value=120,
        )
        assert param.validate_value(45) is True
        assert param.validate_value(0) is True
        assert param.validate_value(120) is True

    def test_validate_integer_below_min(self):
        """Test integer below minimum."""
        param = SkillParameter(
            name="age",
            type=ParameterType.INTEGER,
            min_value=0,
        )
        assert param.validate_value(-5) is False

    def test_validate_integer_above_max(self):
        """Test integer above maximum."""
        param = SkillParameter(
            name="age",
            type=ParameterType.INTEGER,
            max_value=120,
        )
        assert param.validate_value(150) is False

    def test_validate_integer_not_number(self):
        """Test non-numeric value for integer."""
        param = SkillParameter(name="age", type=ParameterType.INTEGER)
        assert param.validate_value("45") is False

    def test_validate_float_valid(self):
        """Test valid float value."""
        param = SkillParameter(
            name="weight",
            type=ParameterType.FLOAT,
            min_value=0.0,
            max_value=500.0,
        )
        assert param.validate_value(75.5) is True
        assert param.validate_value(75) is True  # int is also valid

    def test_validate_range_valid(self):
        """Test valid range value."""
        param = SkillParameter(name="age_range", type=ParameterType.RANGE)
        assert param.validate_value([18, 65]) is True
        assert param.validate_value((18, 65)) is True

    def test_validate_range_invalid_format(self):
        """Test invalid range format."""
        param = SkillParameter(name="age_range", type=ParameterType.RANGE)
        assert param.validate_value([18]) is False  # Too short
        assert param.validate_value([18, 65, 100]) is False  # Too long
        assert param.validate_value("18-65") is False  # Not list/tuple

    def test_validate_range_inverted(self):
        """Test inverted range (start > end)."""
        param = SkillParameter(name="age_range", type=ParameterType.RANGE)
        assert param.validate_value([65, 18]) is False

    def test_validate_string_always_valid(self):
        """Test that string type accepts any value."""
        param = SkillParameter(name="name", type=ParameterType.STRING)
        assert param.validate_value("anything") is True
        assert param.validate_value(123) is True  # No type check for string


class TestSkillVariation:
    """Tests for SkillVariation class."""

    def test_basic_variation(self):
        """Test creating a basic variation."""
        var = SkillVariation(name="elderly", description="For patients 65+")
        assert var.name == "elderly"
        assert var.description == "For patients 65+"
        assert var.parameter_overrides == {}

    def test_variation_with_overrides(self):
        """Test variation with parameter overrides."""
        var = SkillVariation(
            name="pediatric",
            description="For patients under 18",
            parameter_overrides={"age_range": [0, 17], "include_growth": True},
        )
        assert var.parameter_overrides["age_range"] == [0, 17]
        assert var.parameter_overrides["include_growth"] is True


class TestSkill:
    """Tests for Skill class."""

    @pytest.fixture
    def sample_skill(self) -> Skill:
        """Create a sample skill for testing."""
        return Skill(
            name="demographics",
            description="Generate patient demographics",
            purpose="Create realistic patient demographic data",
            parameters=[
                SkillParameter(name="age", type=ParameterType.INTEGER, default=45),
                SkillParameter(
                    name="gender",
                    type=ParameterType.ENUM,
                    options=["male", "female"],
                    default="male",
                ),
            ],
            variations=[
                SkillVariation(
                    name="elderly",
                    parameter_overrides={"age": 75},
                ),
                SkillVariation(
                    name="pediatric",
                    parameter_overrides={"age": 10},
                ),
            ],
        )

    def test_basic_skill(self):
        """Test creating a basic skill."""
        skill = Skill(name="test_skill")
        assert skill.name == "test_skill"
        assert skill.description == ""
        assert skill.parameters == []
        assert skill.variations == []

    def test_get_parameter_found(self, sample_skill: Skill):
        """Test getting existing parameter."""
        param = sample_skill.get_parameter("age")
        assert param is not None
        assert param.name == "age"
        assert param.default == 45

    def test_get_parameter_not_found(self, sample_skill: Skill):
        """Test getting non-existent parameter."""
        param = sample_skill.get_parameter("nonexistent")
        assert param is None

    def test_get_parameter_value_default(self, sample_skill: Skill):
        """Test getting parameter value without overrides."""
        value = sample_skill.get_parameter_value("age")
        assert value == 45

    def test_get_parameter_value_with_override(self, sample_skill: Skill):
        """Test getting parameter value with override."""
        value = sample_skill.get_parameter_value("age", overrides={"age": 30})
        assert value == 30

    def test_get_parameter_value_missing(self, sample_skill: Skill):
        """Test getting value for missing parameter."""
        value = sample_skill.get_parameter_value("nonexistent")
        assert value is None

    def test_apply_variation_success(self, sample_skill: Skill):
        """Test applying a valid variation."""
        modified = sample_skill.apply_variation("elderly")
        assert "elderly" in modified.name
        
        # Check that age parameter was overridden
        age_param = modified.get_parameter("age")
        assert age_param is not None
        assert age_param.default == 75
        
        # Check that gender parameter was unchanged
        gender_param = modified.get_parameter("gender")
        assert gender_param is not None
        assert gender_param.default == "male"

    def test_apply_variation_not_found(self, sample_skill: Skill):
        """Test applying non-existent variation."""
        with pytest.raises(ValueError) as exc_info:
            sample_skill.apply_variation("nonexistent")
        assert "Variation 'nonexistent' not found" in str(exc_info.value)

    def test_apply_variation_preserves_original(self, sample_skill: Skill):
        """Test that applying variation doesn't modify original skill."""
        original_age = sample_skill.get_parameter("age").default
        _ = sample_skill.apply_variation("elderly")
        
        # Original should be unchanged
        assert sample_skill.get_parameter("age").default == original_age

    def test_skill_with_all_fields(self):
        """Test skill with all optional fields populated."""
        skill = Skill(
            name="complete_skill",
            description="A complete skill",
            metadata=SkillMetadata(type=SkillType.DOMAIN_KNOWLEDGE),
            purpose="Testing",
            knowledge={"key": "value"},
            examples=["Example 1", "Example 2"],
            references=["ref1", "ref2"],
            dependencies=["other_skill"],
            raw_text="Raw markdown content",
            content={"nested": {"data": True}},
            for_claude="Instructions for Claude",
            when_to_use="Use when testing",
        )
        
        assert skill.metadata.type == SkillType.DOMAIN_KNOWLEDGE
        assert skill.knowledge == {"key": "value"}
        assert len(skill.examples) == 2
        assert skill.for_claude == "Instructions for Claude"
