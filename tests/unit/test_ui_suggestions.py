"""
Tests for HealthSim Agent UI Suggestions Module.
"""

import pytest

from healthsim_agent.ui.suggestions import (
    SuggestionGenerator,
    get_suggestion_generator,
    get_suggestions_for_tool,
)


class TestSuggestionGenerator:
    """Tests for SuggestionGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create fresh generator for each test."""
        return SuggestionGenerator()
    
    def test_initial_state(self, generator):
        """Generator should start with no context."""
        assert generator._last_tool is None
        assert generator._last_entity_type is None
    
    def test_default_suggestions(self, generator):
        """Without context, should return default suggestions."""
        suggestions = generator.get_suggestions()
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3
    
    def test_update_context_sets_tool(self, generator):
        """update_context should set last tool."""
        generator.update_context("test_tool", {})
        assert generator._last_tool == "test_tool"
    
    def test_update_context_extracts_entity_type(self, generator):
        """Should extract entity type from result."""
        generator.update_context("add_entities", {
            "entity_counts": {"patients": 100}
        })
        assert generator._last_entity_type == "patients"
    
    def test_max_three_suggestions(self, generator):
        """Should never return more than 3 suggestions."""
        # Test various tools
        for tool in ["add_entities", "query", "search_providers"]:
            generator.update_context(tool, {})
            suggestions = generator.get_suggestions()
            assert len(suggestions) <= 3
    
    def test_clear_context(self, generator):
        """clear_context should reset all state."""
        generator.update_context("test_tool", {"entity_counts": {"patients": 50}})
        generator.clear_context()
        assert generator._last_tool is None
        assert generator._last_entity_type is None
        assert generator._context == {}


class TestSuggestionsAfterAddEntities:
    """Tests for suggestions after add_entities tool."""
    
    @pytest.fixture
    def generator(self):
        return SuggestionGenerator()
    
    def test_after_adding_patients(self, generator):
        """Should suggest patient-related actions."""
        generator.update_context("add_entities", {
            "entity_counts": {"patients": 100}
        })
        suggestions = generator.get_suggestions()
        
        # Should suggest things relevant to patients
        assert any("encounter" in s.lower() or "claim" in s.lower() or "fhir" in s.lower() 
                   for s in suggestions)
    
    def test_after_adding_members(self, generator):
        """Should suggest member-related actions."""
        generator.update_context("add_entities", {
            "entity_counts": {"members": 100}
        })
        suggestions = generator.get_suggestions()
        
        # Should suggest things relevant to members
        assert any("claim" in s.lower() or "pcp" in s.lower() or "pharmacy" in s.lower()
                   for s in suggestions)
    
    def test_after_adding_claims(self, generator):
        """Should suggest claims-related actions."""
        generator.update_context("add_entities", {
            "entity_counts": {"claims": 500}
        })
        suggestions = generator.get_suggestions()
        
        assert len(suggestions) > 0


class TestSuggestionsAfterSearchProviders:
    """Tests for suggestions after search_providers tool."""
    
    @pytest.fixture
    def generator(self):
        return SuggestionGenerator()
    
    def test_with_results(self, generator):
        """Should suggest provider-related actions when results found."""
        generator.update_context("search_providers", {
            "result_count": 50
        })
        suggestions = generator.get_suggestions()
        
        assert len(suggestions) > 0
    
    def test_without_results(self, generator):
        """Should suggest search refinement when no results."""
        generator.update_context("search_providers", {
            "result_count": 0
        })
        suggestions = generator.get_suggestions()
        
        # Should suggest broadening search
        assert any("search" in s.lower() or "specialty" in s.lower() 
                   for s in suggestions)


class TestSuggestionsAfterQuery:
    """Tests for suggestions after query tool."""
    
    @pytest.fixture
    def generator(self):
        return SuggestionGenerator()
    
    def test_after_query(self, generator):
        """Should suggest query follow-up actions."""
        generator.update_context("query", {
            "row_count": 100
        })
        suggestions = generator.get_suggestions()
        
        # Should suggest things like export or refine
        assert any("export" in s.lower() or "refine" in s.lower() or "schema" in s.lower()
                   for s in suggestions)


class TestSuggestionsAfterListCohorts:
    """Tests for suggestions after list_cohorts tool."""
    
    @pytest.fixture
    def generator(self):
        return SuggestionGenerator()
    
    def test_after_listing(self, generator):
        """Should suggest cohort management actions."""
        generator.update_context("list_cohorts", {
            "cohort_count": 5
        })
        suggestions = generator.get_suggestions()
        
        # Should suggest loading or creating cohorts
        assert any("load" in s.lower() or "create" in s.lower() 
                   for s in suggestions)


class TestGetSuggestionGenerator:
    """Tests for singleton getter."""
    
    def test_returns_generator(self):
        """Should return a SuggestionGenerator instance."""
        gen = get_suggestion_generator()
        assert isinstance(gen, SuggestionGenerator)
    
    def test_returns_same_instance(self):
        """Should return the same instance (singleton)."""
        gen1 = get_suggestion_generator()
        gen2 = get_suggestion_generator()
        assert gen1 is gen2


class TestGetSuggestionsForTool:
    """Tests for convenience function."""
    
    def test_returns_list(self):
        """Should return a list of suggestions."""
        suggestions = get_suggestions_for_tool("test_tool", {})
        assert isinstance(suggestions, list)
    
    def test_updates_context(self):
        """Should update the singleton's context."""
        get_suggestions_for_tool("add_entities", {
            "entity_counts": {"patients": 50}
        })
        
        gen = get_suggestion_generator()
        assert gen._last_tool == "add_entities"
