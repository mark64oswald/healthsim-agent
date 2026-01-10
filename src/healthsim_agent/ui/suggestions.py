"""
HealthSim Agent - Contextual Suggestions

Generates next-action suggestions based on conversation context.
"""

from typing import List, Optional, Dict, Any


class SuggestionGenerator:
    """
    Generate contextual next-action suggestions.
    
    Uses a combination of:
    1. Rule-based suggestions based on last tool used
    2. Entity-type specific follow-ups
    3. Conversation context hints
    
    Note: In future, could integrate with Claude for AI-generated suggestions.
    """
    
    def __init__(self, skill_router=None):
        """Initialize suggestion generator.
        
        Args:
            skill_router: Optional SkillRouter for finding related skills
        """
        self.skill_router = skill_router
        self._last_tool: Optional[str] = None
        self._last_entity_type: Optional[str] = None
        self._last_result: Optional[Dict] = None
        self._context: Dict[str, Any] = {}
    
    def update_context(
        self,
        tool_name: str,
        result: Dict[str, Any],
        user_message: Optional[str] = None,
    ) -> None:
        """Update context from last tool execution.
        
        Args:
            tool_name: Name of the tool that was executed
            result: Tool result dictionary
            user_message: Optional user message that triggered the tool
        """
        self._last_tool = tool_name
        self._last_result = result
        
        # Extract entity type if present
        if "entity_counts" in result:
            types = list(result.get("entity_counts", {}).keys())
            self._last_entity_type = types[0] if types else None
        elif "cohort_totals" in result:
            types = list(result.get("cohort_totals", {}).get("by_type", {}).keys())
            self._last_entity_type = types[0] if types else None
        
        # Track cohort context
        if result.get("cohort_id"):
            self._context["cohort_id"] = result["cohort_id"]
        if result.get("cohort_name"):
            self._context["cohort_name"] = result["cohort_name"]
        
        # Track what was generated
        if result.get("entities_added_this_batch"):
            self._context["last_entities"] = result["entities_added_this_batch"]
    
    def get_suggestions(self) -> List[str]:
        """Generate suggestions based on current context.
        
        Returns:
            List of 1-3 suggestion strings
        """
        suggestions = []
        
        # Tool-specific suggestions
        if self._last_tool == "add_entities":
            suggestions = self._suggestions_after_add_entities()
        elif self._last_tool == "save_cohort":
            suggestions = self._suggestions_after_save_cohort()
        elif self._last_tool == "search_providers":
            suggestions = self._suggestions_after_search_providers()
        elif self._last_tool == "query":
            suggestions = self._suggestions_after_query()
        elif self._last_tool == "query_reference":
            suggestions = self._suggestions_after_query_reference()
        elif self._last_tool == "list_cohorts":
            suggestions = self._suggestions_after_list_cohorts()
        elif self._last_tool == "load_cohort":
            suggestions = self._suggestions_after_load_cohort()
        elif self._last_tool == "get_summary":
            suggestions = self._suggestions_after_get_summary()
        elif self._last_tool == "list_tables":
            suggestions = self._suggestions_after_list_tables()
        
        # Default suggestions if none specific
        if not suggestions:
            suggestions = self._default_suggestions()
        
        return suggestions[:3]  # Max 3 suggestions
    
    def _suggestions_after_add_entities(self) -> List[str]:
        """Suggestions after adding entities."""
        suggestions = []
        
        if self._last_entity_type == "patients":
            suggestions = [
                "Add encounters for these patients",
                "Generate claims history",
                "Export to FHIR Bundle",
            ]
        elif self._last_entity_type == "members":
            suggestions = [
                "Add claims for these members",
                "Assign PCPs from local providers",
                "Generate pharmacy claims",
            ]
        elif self._last_entity_type == "claims":
            suggestions = [
                "Add claim line items",
                "Generate explanation of benefits",
                "Show claims summary by diagnosis",
            ]
        elif self._last_entity_type == "encounters":
            suggestions = [
                "Add diagnoses for these encounters",
                "Generate procedure codes",
                "Create lab results",
            ]
        elif self._last_entity_type == "prescriptions":
            suggestions = [
                "Add pharmacy fills",
                "Check formulary coverage",
                "Show medication adherence",
            ]
        elif self._last_entity_type == "subjects":
            suggestions = [
                "Add screening visits",
                "Generate adverse events",
                "Create lab assessments",
            ]
        else:
            suggestions = [
                "View cohort summary",
                "Add more entity types",
                "Export the data",
            ]
        
        return suggestions
    
    def _suggestions_after_save_cohort(self) -> List[str]:
        """Suggestions after saving a cohort."""
        return [
            "Load the cohort to view data",
            "Add more entities to this cohort",
            "Export to a standard format",
        ]
    
    def _suggestions_after_search_providers(self) -> List[str]:
        """Suggestions after searching providers."""
        count = 0
        if self._last_result:
            count = self._last_result.get("result_count", 0)
        
        if count > 0:
            return [
                "Create PCP assignments for members",
                "Search for a different specialty",
                "Show provider distribution by city",
            ]
        else:
            return [
                "Try a broader search area",
                "Search for a different specialty",
                "Check available specialties",
            ]
    
    def _suggestions_after_query(self) -> List[str]:
        """Suggestions after running a SQL query."""
        return [
            "Export these results to CSV",
            "Refine the query",
            "Show table schema",
        ]
    
    def _suggestions_after_query_reference(self) -> List[str]:
        """Suggestions after querying reference data."""
        return [
            "Generate population based on this data",
            "Query a different geographic area",
            "Show health indicators correlation",
        ]
    
    def _suggestions_after_list_cohorts(self) -> List[str]:
        """Suggestions after listing cohorts."""
        return [
            "Load a cohort to view details",
            "Create a new cohort",
            "Delete old cohorts",
        ]
    
    def _suggestions_after_load_cohort(self) -> List[str]:
        """Suggestions after loading a cohort."""
        return [
            "Show cohort summary",
            "Add more entities",
            "Export to FHIR",
        ]
    
    def _suggestions_after_get_summary(self) -> List[str]:
        """Suggestions after getting cohort summary."""
        return [
            "Query specific entity types",
            "Add more data to this cohort",
            "Export for analysis",
        ]
    
    def _suggestions_after_list_tables(self) -> List[str]:
        """Suggestions after listing tables."""
        return [
            "Query a specific table",
            "Show table schema",
            "Search reference data",
        ]
    
    def _default_suggestions(self) -> List[str]:
        """Default suggestions when no specific context."""
        return [
            "Generate a patient population",
            "Search for providers in your area",
            "Show available reference data",
        ]
    
    def clear_context(self) -> None:
        """Clear all context."""
        self._last_tool = None
        self._last_entity_type = None
        self._last_result = None
        self._context = {}


# Singleton instance
_suggestion_generator: Optional[SuggestionGenerator] = None


def get_suggestion_generator() -> SuggestionGenerator:
    """Get or create the suggestion generator singleton."""
    global _suggestion_generator
    if _suggestion_generator is None:
        _suggestion_generator = SuggestionGenerator()
    return _suggestion_generator


def get_suggestions_for_tool(
    tool_name: str,
    result: Dict[str, Any],
) -> List[str]:
    """Convenience function to get suggestions for a tool result.
    
    Args:
        tool_name: Name of the tool that was executed
        result: Tool result dictionary
        
    Returns:
        List of suggestion strings
    """
    generator = get_suggestion_generator()
    generator.update_context(tool_name, result)
    return generator.get_suggestions()
