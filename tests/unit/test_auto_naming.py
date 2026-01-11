"""
Tests for auto_naming module - cohort name generation and parsing.
"""
import pytest
from datetime import datetime
from unittest.mock import patch

from healthsim_agent.state.auto_naming import (
    extract_keywords,
    sanitize_name,
    ensure_unique_name,
    generate_cohort_name,
    parse_cohort_name,
    STOP_WORDS,
    HEALTHCARE_KEYWORDS,
)


class TestExtractKeywords:
    """Test keyword extraction from context."""
    
    def test_extract_healthcare_keywords_priority(self):
        """Healthcare keywords should be prioritized."""
        context = "Generate diabetic patients with hypertension and cardiac conditions"
        keywords = extract_keywords(context)
        
        # Should prioritize healthcare terms
        assert len(keywords) <= 3
        assert any(k in HEALTHCARE_KEYWORDS for k in keywords)
    
    def test_extract_from_empty_context(self):
        """Empty context returns empty list."""
        assert extract_keywords(None) == []
        assert extract_keywords("") == []
    
    def test_extract_removes_stop_words(self):
        """Stop words should be filtered out."""
        context = "the patient and the doctor"
        keywords = extract_keywords(context)
        
        assert "the" not in keywords
        assert "and" not in keywords
    
    def test_extract_with_entity_type(self):
        """Entity type should be appended if not already present."""
        keywords = extract_keywords(context=None, entity_type="Patient")
        
        assert "patients" in keywords
    
    def test_extract_entity_type_not_duplicated(self):
        """Entity type not duplicated if already in keywords."""
        context = "diabetic patients"
        keywords = extract_keywords(context, entity_type="Patient")
        
        # Should not have both 'patient' and 'patients'
        count = sum(1 for k in keywords if k.startswith('patient'))
        assert count <= 1
    
    def test_extract_max_keywords_limit(self):
        """Should respect max_keywords parameter."""
        context = "diabetes hypertension cardiac cancer oncology"
        keywords = extract_keywords(context, max_keywords=2)
        
        assert len(keywords) <= 2
    
    def test_extract_min_word_length(self):
        """Words less than 3 chars should be filtered."""
        context = "an rx for diabetes"
        keywords = extract_keywords(context)
        
        assert "an" not in keywords
        # Note: 'rx' is only 2 chars so filtered out before healthcare check
        assert "rx" not in keywords
        assert "diabetes" in keywords


class TestSanitizeName:
    """Test name sanitization."""
    
    def test_sanitize_lowercase(self):
        """Names should be lowercased."""
        assert sanitize_name("DiAbEtEs") == "diabetes"
    
    def test_sanitize_spaces_to_hyphens(self):
        """Spaces should become hyphens."""
        assert sanitize_name("diabetic patients") == "diabetic-patients"
    
    def test_sanitize_underscores_to_hyphens(self):
        """Underscores should become hyphens."""
        assert sanitize_name("diabetic_patients") == "diabetic-patients"
    
    def test_sanitize_removes_special_chars(self):
        """Special characters should be removed."""
        assert sanitize_name("test@name!#$") == "testname"
    
    def test_sanitize_collapses_multiple_hyphens(self):
        """Multiple hyphens should collapse to one."""
        assert sanitize_name("test---name") == "test-name"
    
    def test_sanitize_strips_leading_trailing_hyphens(self):
        """Leading/trailing hyphens should be stripped."""
        assert sanitize_name("-test-name-") == "test-name"
    
    def test_sanitize_max_length(self):
        """Names should be truncated at 50 chars."""
        long_name = "a" * 100
        result = sanitize_name(long_name)
        
        assert len(result) <= 50
    
    def test_sanitize_truncation_removes_trailing_hyphen(self):
        """Truncation should not leave trailing hyphen."""
        name = "test-" + "a" * 50
        result = sanitize_name(name)
        
        assert not result.endswith("-")


class TestEnsureUniqueName:
    """Test unique name generation."""
    
    def test_unique_name_no_existing(self):
        """No changes needed if no existing names."""
        assert ensure_unique_name("test") == "test"
        assert ensure_unique_name("test", None) == "test"
        assert ensure_unique_name("test", set()) == "test"
    
    def test_unique_name_already_unique(self):
        """No changes if name not in existing."""
        existing = {"cohort-1", "cohort-2"}
        assert ensure_unique_name("cohort-3", existing) == "cohort-3"
    
    def test_unique_name_append_counter(self):
        """Counter appended when name exists."""
        existing = {"test-cohort"}
        result = ensure_unique_name("test-cohort", existing)
        
        assert result == "test-cohort-2"
    
    def test_unique_name_increment_counter(self):
        """Counter increments until unique."""
        existing = {"test", "test-2", "test-3", "test-4"}
        result = ensure_unique_name("test", existing)
        
        assert result == "test-5"
    
    def test_unique_name_high_counter_fallback(self):
        """Very high counter falls back to timestamp."""
        # Create set with 1000+ names
        existing = {"test"} | {f"test-{i}" for i in range(2, 1005)}
        
        with patch('healthsim_agent.state.auto_naming.datetime') as mock_dt:
            mock_dt.utcnow.return_value.strftime.return_value = "123456"
            result = ensure_unique_name("test", existing)
        
        assert result == "test-123456"


class TestGenerateCohortName:
    """Test cohort name generation."""
    
    def test_generate_with_keywords(self):
        """Generate name from explicit keywords."""
        with patch('healthsim_agent.state.auto_naming.datetime') as mock_dt:
            mock_dt.utcnow.return_value.strftime.return_value = "20260111"
            name = generate_cohort_name(keywords=["diabetes", "texas"])
        
        assert name == "diabetes-texas-20260111"
    
    def test_generate_from_context(self):
        """Generate name from context string."""
        with patch('healthsim_agent.state.auto_naming.datetime') as mock_dt:
            mock_dt.utcnow.return_value.strftime.return_value = "20260111"
            name = generate_cohort_name(context="diabetic patients in Texas")
        
        assert "diabetic" in name or "patients" in name or "texas" in name
        assert "20260111" in name
    
    def test_generate_with_entity_type(self):
        """Generate name from entity type."""
        with patch('healthsim_agent.state.auto_naming.datetime') as mock_dt:
            mock_dt.utcnow.return_value.strftime.return_value = "20260111"
            name = generate_cohort_name(entity_type="Patient")
        
        assert "patient" in name
        assert "20260111" in name
    
    def test_generate_with_prefix(self):
        """Prefix should be prepended."""
        with patch('healthsim_agent.state.auto_naming.datetime') as mock_dt:
            mock_dt.utcnow.return_value.strftime.return_value = "20260111"
            name = generate_cohort_name(prefix="demo", keywords=["diabetes"])
        
        assert name.startswith("demo-")
    
    def test_generate_without_date(self):
        """Date can be excluded."""
        name = generate_cohort_name(keywords=["test"], include_date=False)
        
        # Should not have 8-digit date suffix
        parts = name.split("-")
        assert not (len(parts[-1]) == 8 and parts[-1].isdigit())
    
    def test_generate_default_fallback(self):
        """Default 'cohort' used when no context provided."""
        with patch('healthsim_agent.state.auto_naming.datetime') as mock_dt:
            mock_dt.utcnow.return_value.strftime.return_value = "20260111"
            name = generate_cohort_name()
        
        assert name.startswith("cohort-")
    
    def test_generate_ensures_uniqueness(self):
        """Name uniqueness enforced with existing names."""
        existing = {"diabetes-20260111"}
        
        with patch('healthsim_agent.state.auto_naming.datetime') as mock_dt:
            mock_dt.utcnow.return_value.strftime.return_value = "20260111"
            name = generate_cohort_name(
                keywords=["diabetes"],
                existing_names=existing
            )
        
        assert name == "diabetes-20260111-2"
    
    def test_generate_max_keywords_from_list(self):
        """Only first 3 keywords used from list."""
        name = generate_cohort_name(
            keywords=["one", "two", "three", "four", "five"],
            include_date=False
        )
        
        # Should only have 3 keyword parts
        parts = name.split("-")
        assert len(parts) == 3


class TestParseCohortName:
    """Test cohort name parsing."""
    
    def test_parse_full_name(self):
        """Parse name with keywords, date, and counter."""
        result = parse_cohort_name("diabetes-texas-20260111-3")
        
        assert result["keywords"] == ["diabetes", "texas"]
        assert result["date"] == "20260111"
        assert result["counter"] == 3
    
    def test_parse_name_no_counter(self):
        """Parse name without counter."""
        result = parse_cohort_name("diabetes-20260111")
        
        assert result["keywords"] == ["diabetes"]
        assert result["date"] == "20260111"
        assert result["counter"] is None
    
    def test_parse_name_no_date(self):
        """Parse name without date."""
        result = parse_cohort_name("diabetes-patients")
        
        assert result["keywords"] == ["diabetes", "patients"]
        assert result["date"] is None
        assert result["counter"] is None
    
    def test_parse_simple_name(self):
        """Parse single keyword name."""
        result = parse_cohort_name("cohort")
        
        assert result["keywords"] == ["cohort"]
        assert result["date"] is None
        assert result["counter"] is None
    
    def test_parse_counter_only_when_small(self):
        """Counter only parsed if 1-3 digits."""
        # 4-digit suffix should not be counter
        result = parse_cohort_name("test-1234")
        
        assert result["counter"] is None
    
    def test_parse_date_must_start_with_20(self):
        """Date only parsed if starts with 20 (valid year)."""
        result = parse_cohort_name("test-19990101")
        
        # 19990101 shouldn't be parsed as date
        assert result["date"] is None
        assert "19990101" in result["keywords"]
    
    def test_parse_invalid_date_format(self):
        """Invalid date format kept as keyword."""
        result = parse_cohort_name("test-20261301")  # Invalid month
        
        # Should not parse as date since month 13 is invalid
        assert result["date"] is None


class TestConstantsSanity:
    """Sanity checks for module constants."""
    
    def test_stop_words_all_lowercase(self):
        """All stop words should be lowercase."""
        for word in STOP_WORDS:
            assert word == word.lower(), f"Stop word not lowercase: {word}"
    
    def test_healthcare_keywords_all_lowercase(self):
        """All healthcare keywords should be lowercase."""
        for word in HEALTHCARE_KEYWORDS:
            assert word == word.lower(), f"Healthcare keyword not lowercase: {word}"
    
    def test_stop_words_no_overlap_healthcare(self):
        """Stop words and healthcare keywords should not overlap."""
        overlap = STOP_WORDS & HEALTHCARE_KEYWORDS
        assert len(overlap) == 0, f"Overlapping words: {overlap}"
