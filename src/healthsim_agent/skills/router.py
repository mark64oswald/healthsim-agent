"""Skill router - matches user intent to relevant skills.

Routes user messages to appropriate skills based on:
1. Trigger phrase matching (from skill frontmatter)
2. Product keyword detection
3. Entity type inference
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from .loader import SkillLoader
from .models import ParsedSkill


@dataclass
class RoutingResult:
    """Result of routing a user message to skills.
    
    Attributes:
        matched_skills: Skills that match the user's intent
        confidence: Overall routing confidence (0.0 - 1.0)
        matched_triggers: Trigger phrases found in the message
        suggested_product: Most likely product based on keywords
    """
    matched_skills: list[ParsedSkill] = field(default_factory=list)
    confidence: float = 0.0
    matched_triggers: list[str] = field(default_factory=list)
    suggested_product: str | None = None


class SkillRouter:
    """Route user messages to relevant skills.
    
    Uses a combination of trigger phrase matching and keyword
    detection to find the most relevant skills for a user request.
    """
    
    # Product keywords for routing (lowercase)
    PRODUCT_KEYWORDS = {
        "patientsim": [
            "patient", "clinical", "emr", "ehr", "encounter", "diagnosis",
            "lab", "vitals", "hospital", "admission", "discharge", "orders",
            "procedure", "surgery", "inpatient", "outpatient", "ed", "emergency"
        ],
        "membersim": [
            "member", "claim", "claims", "payer", "insurance", "enrollment",
            "accumulator", "deductible", "copay", "coinsurance", "oop",
            "prior auth", "authorization", "eob", "835", "837", "x12"
        ],
        "rxmembersim": [
            "pharmacy", "prescription", "rx", "medication", "drug", "fill",
            "formulary", "pbm", "ncpdp", "refill", "dispense", "ndc",
            "tier", "copay", "mail order", "specialty pharmacy"
        ],
        "trialsim": [
            "trial", "clinical trial", "study", "cdisc", "sdtm", "adam",
            "subject", "protocol", "randomization", "adverse event", "ae",
            "screening", "enrollment", "visit", "phase 1", "phase 2", "phase 3",
            "pivotal", "investigator", "site"
        ],
        "populationsim": [
            "population", "demographics", "sdoh", "census", "prevalence",
            "county", "tract", "cdc places", "svi", "adi", "socioeconomic",
            "disparity", "geography", "fips"
        ],
        "networksim": [
            "provider", "network", "npi", "facility", "hospital", "physician",
            "specialist", "adequacy", "taxonomy", "credentialing", "roster",
            "in-network", "out-of-network", "hmo", "ppo"
        ],
    }

    def __init__(self, loader: SkillLoader | None = None):
        """Initialize router with skill loader.
        
        Args:
            loader: SkillLoader instance. Creates new one if not provided.
        """
        self.loader = loader or SkillLoader()
    
    def route(self, message: str) -> RoutingResult:
        """Route a user message to relevant skills.
        
        Uses multiple signals:
        1. Exact trigger phrase matches from skill frontmatter
        2. Product keyword detection
        3. Falls back to product skills if no trigger matches
        
        Args:
            message: The user's input message
            
        Returns:
            RoutingResult with matched skills and confidence
        """
        message_lower = message.lower()
        
        # Find matching triggers
        matched_triggers = []
        matched_skill_names = set()
        
        for trigger, skill_names in self.loader.index.trigger_map.items():
            if trigger in message_lower:
                matched_triggers.append(trigger)
                matched_skill_names.update(skill_names)
        
        # Detect suggested product from keywords
        suggested_product = self._detect_product(message_lower)
        
        # If no trigger matches but we detected a product, get product skills
        if not matched_skill_names and suggested_product:
            product_skills = self.loader.index.get_by_product(suggested_product)
            for skill in product_skills:
                matched_skill_names.add(skill.metadata.name)
        
        # Get actual skill objects
        matched_skills = [
            self.loader.index.skills[name] 
            for name in matched_skill_names 
            if name in self.loader.index.skills
        ]
        
        # Sort skills: product SKILL.md first, then by specificity
        matched_skills.sort(key=lambda s: (
            0 if s.is_product_skill else 1,
            -len(s.triggers)  # More triggers = more specific
        ))
        
        # Calculate confidence based on matches
        confidence = self._calculate_confidence(
            len(matched_triggers), 
            len(matched_skills),
            suggested_product is not None
        )
        
        return RoutingResult(
            matched_skills=matched_skills,
            confidence=confidence,
            matched_triggers=matched_triggers,
            suggested_product=suggested_product
        )
    
    def _detect_product(self, message: str) -> str | None:
        """Detect which product the message is about.
        
        Scores each product based on keyword matches and
        returns the highest-scoring product.
        """
        scores = {}
        
        for product, keywords in self.PRODUCT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in message)
            if score > 0:
                scores[product] = score
        
        if not scores:
            return None
        
        # Return highest scoring product
        return max(scores, key=scores.get)
    
    def _calculate_confidence(
        self, 
        trigger_count: int, 
        skill_count: int,
        has_product: bool
    ) -> float:
        """Calculate routing confidence score.
        
        Factors:
        - Number of trigger matches (0.2 each, max 0.6)
        - Having matched skills (+0.2)
        - Product detection (+0.2)
        """
        if trigger_count == 0 and skill_count == 0:
            return 0.0
        
        # Base confidence from trigger matches
        confidence = min(trigger_count * 0.2, 0.6)
        
        # Boost for having matched skills
        if skill_count > 0:
            confidence += 0.2
        
        # Boost for product detection
        if has_product:
            confidence += 0.2
        
        return min(confidence, 1.0)

    def get_skill_for_generation(
        self, 
        entity_type: str,
        context: dict[str, Any] | None = None
    ) -> ParsedSkill | None:
        """Get the best skill for generating a specific entity type.
        
        Maps entity types to products and returns the most relevant skill.
        
        Args:
            entity_type: Type of entity (patient, member, claim, etc.)
            context: Optional context for better matching
            
        Returns:
            Best matching skill or None
        """
        # Map entity types to likely products
        entity_product_map = {
            # PatientSim entities
            "patient": "patientsim",
            "encounter": "patientsim",
            "diagnosis": "patientsim",
            "procedure": "patientsim",
            "lab": "patientsim",
            "vitals": "patientsim",
            "order": "patientsim",
            
            # MemberSim entities
            "member": "membersim",
            "claim": "membersim",
            "enrollment": "membersim",
            "accumulator": "membersim",
            
            # RxMemberSim entities
            "prescription": "rxmembersim",
            "fill": "rxmembersim",
            "rx": "rxmembersim",
            "formulary": "rxmembersim",
            
            # TrialSim entities
            "subject": "trialsim",
            "visit": "trialsim",
            "adverse_event": "trialsim",
            "study": "trialsim",
            "site": "trialsim",
            
            # NetworkSim entities
            "provider": "networksim",
            "facility": "networksim",
            "network": "networksim",
            
            # PopulationSim entities
            "population": "populationsim",
            "cohort": "populationsim",
            "demographics": "populationsim",
        }
        
        product = entity_product_map.get(entity_type.lower())
        if not product:
            return None
        
        # Get product skills
        product_skills = self.loader.index.get_by_product(product)
        
        if not product_skills:
            return None
        
        # Prefer SKILL.md (product overview) as the primary source
        for skill in product_skills:
            if skill.is_product_skill:
                return skill
        
        # Otherwise return first skill
        return product_skills[0]
    
    def get_skills_for_products(
        self, 
        products: list[str]
    ) -> list[ParsedSkill]:
        """Get all skills for a list of products.
        
        Args:
            products: List of product names
            
        Returns:
            List of skills across all specified products
        """
        skills = []
        seen = set()
        
        for product in products:
            for skill in self.loader.index.get_by_product(product):
                if skill.metadata.name not in seen:
                    seen.add(skill.metadata.name)
                    skills.append(skill)
        
        return skills
    
    def find_related_skills(
        self, 
        skill: ParsedSkill,
        max_results: int = 5
    ) -> list[ParsedSkill]:
        """Find skills related to the given skill.
        
        Uses trigger overlap and product relationships.
        
        Args:
            skill: The source skill
            max_results: Maximum number of related skills to return
            
        Returns:
            List of related skills, most relevant first
        """
        related = []
        source_triggers = set(t.lower() for t in skill.triggers)
        
        for name, candidate in self.loader.index.skills.items():
            if name == skill.metadata.name:
                continue
            
            # Score by trigger overlap
            candidate_triggers = set(t.lower() for t in candidate.triggers)
            overlap = len(source_triggers & candidate_triggers)
            
            # Boost if same product
            same_product = candidate.product == skill.product
            
            if overlap > 0 or same_product:
                score = overlap * 2 + (1 if same_product else 0)
                related.append((score, candidate))
        
        # Sort by score descending
        related.sort(key=lambda x: -x[0])
        
        return [skill for _, skill in related[:max_results]]
