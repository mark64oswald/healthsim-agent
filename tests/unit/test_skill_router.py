"""Unit tests for skill router."""
import pytest
from healthsim_agent.skills.router import SkillRouter, RoutingResult
from healthsim_agent.skills.loader import SkillLoader


class TestRoutingResult:
    """Tests for RoutingResult dataclass."""
    
    def test_routing_result_creation(self):
        """Test RoutingResult can be created with defaults."""
        result = RoutingResult()
        
        assert result.matched_skills == []
        assert result.confidence == 0.0
        assert result.matched_triggers == []
        assert result.suggested_product is None
    
    def test_routing_result_with_values(self):
        """Test RoutingResult with explicit values."""
        result = RoutingResult(
            matched_skills=[],
            confidence=0.5,
            matched_triggers=["diabetes"],
            suggested_product="patientsim"
        )
        
        assert result.confidence == 0.5
        assert result.suggested_product == "patientsim"
        assert "diabetes" in result.matched_triggers


class TestSkillRouter:
    """Tests for SkillRouter."""
    
    @pytest.fixture
    def router(self):
        """Create router instance."""
        return SkillRouter()
    
    def test_router_initializes(self, router):
        """Test router initializes properly."""
        assert router.loader is not None
    
    def test_router_with_custom_loader(self):
        """Test router accepts custom loader."""
        loader = SkillLoader()
        router = SkillRouter(loader)
        
        assert router.loader is loader
    
    def test_route_returns_result(self, router):
        """Test routing returns RoutingResult."""
        result = router.route("Generate a diabetic patient")
        
        assert isinstance(result, RoutingResult)
        assert isinstance(result.matched_skills, list)
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0
    
    def test_route_finds_skills(self, router):
        """Test routing finds relevant skills."""
        result = router.route("Generate a diabetic patient")
        
        # Should find at least one skill
        assert len(result.matched_skills) > 0 or result.suggested_product is not None
    
    def test_route_detects_product(self, router):
        """Test routing detects product from message."""
        result = router.route("I need to generate patient data")
        
        assert result.suggested_product == "patientsim"


class TestProductDetection:
    """Tests for product keyword detection."""
    
    @pytest.fixture
    def router(self):
        return SkillRouter()
    
    def test_detect_product_patientsim(self, router):
        """Test product detection for patient-related queries."""
        product = router._detect_product("generate a patient with diabetes")
        
        assert product == "patientsim"
    
    def test_detect_product_from_clinical_keywords(self, router):
        """Test detection from clinical keywords."""
        product = router._detect_product("create encounter with diagnosis")
        
        assert product == "patientsim"
    
    def test_detect_product_membersim(self, router):
        """Test product detection for claims-related queries."""
        product = router._detect_product("create insurance claims for member")
        
        assert product == "membersim"
    
    def test_detect_product_from_payer_keywords(self, router):
        """Test detection from payer keywords."""
        product = router._detect_product("enrollment with accumulator tracking")
        
        assert product == "membersim"
    
    def test_detect_product_rxmembersim(self, router):
        """Test product detection for pharmacy queries."""
        product = router._detect_product("generate prescription fills")
        
        assert product == "rxmembersim"
    
    def test_detect_product_from_pharmacy_keywords(self, router):
        """Test detection from pharmacy keywords."""
        product = router._detect_product("formulary coverage for medication")
        
        assert product == "rxmembersim"
    
    def test_detect_product_trialsim(self, router):
        """Test product detection for clinical trial queries."""
        product = router._detect_product("create a clinical trial with subjects")
        
        assert product == "trialsim"
    
    def test_detect_product_from_trial_keywords(self, router):
        """Test detection from trial keywords."""
        product = router._detect_product("phase 3 protocol with randomization")
        
        assert product == "trialsim"
    
    def test_detect_product_populationsim(self, router):
        """Test product detection for population queries."""
        product = router._detect_product("analyze census demographics")
        
        assert product == "populationsim"
    
    def test_detect_product_networksim(self, router):
        """Test product detection for network queries."""
        product = router._detect_product("search for provider with npi")
        
        assert product == "networksim"
    
    def test_detect_product_none(self, router):
        """Test no product detected for generic queries."""
        product = router._detect_product("hello world how are you")
        
        assert product is None
    
    def test_detect_product_highest_score_wins(self, router):
        """Test that highest scoring product wins."""
        # This message has keywords from multiple products
        # but more patientsim keywords
        product = router._detect_product(
            "patient with diagnosis and lab vitals encounter"
        )
        
        assert product == "patientsim"


class TestConfidenceCalculation:
    """Tests for confidence score calculation."""
    
    @pytest.fixture
    def router(self):
        return SkillRouter()
    
    def test_calculate_confidence_no_matches(self, router):
        """Test confidence is 0.0 with no matches."""
        conf = router._calculate_confidence(0, 0, False)
        
        assert conf == 0.0
    
    def test_calculate_confidence_with_triggers(self, router):
        """Test confidence increases with trigger matches."""
        conf_1 = router._calculate_confidence(1, 0, False)
        conf_2 = router._calculate_confidence(2, 0, False)
        conf_3 = router._calculate_confidence(3, 0, False)
        
        assert conf_1 < conf_2 < conf_3
    
    def test_calculate_confidence_with_skills(self, router):
        """Test confidence increases with matched skills."""
        conf_no_skills = router._calculate_confidence(1, 0, False)
        conf_with_skills = router._calculate_confidence(1, 1, False)
        
        assert conf_with_skills > conf_no_skills
    
    def test_calculate_confidence_with_product(self, router):
        """Test confidence increases with product detection."""
        conf_no_product = router._calculate_confidence(1, 0, False)
        conf_with_product = router._calculate_confidence(1, 0, True)
        
        assert conf_with_product > conf_no_product
    
    def test_calculate_confidence_max_is_one(self, router):
        """Test confidence never exceeds 1.0."""
        conf = router._calculate_confidence(10, 10, True)
        
        assert conf <= 1.0
    
    def test_calculate_confidence_combined(self, router):
        """Test confidence with all factors."""
        conf = router._calculate_confidence(3, 2, True)
        
        # Should be high but not exceed 1.0
        assert 0.8 <= conf <= 1.0


class TestSkillForGeneration:
    """Tests for get_skill_for_generation."""
    
    @pytest.fixture
    def router(self):
        return SkillRouter()
    
    def test_get_skill_for_patient(self, router):
        """Test getting skill for patient generation."""
        skill = router.get_skill_for_generation("patient")
        
        if skill is not None:
            assert skill.product == "patientsim"
    
    def test_get_skill_for_claim(self, router):
        """Test getting skill for claim generation."""
        skill = router.get_skill_for_generation("claim")
        
        if skill is not None:
            assert skill.product == "membersim"
    
    def test_get_skill_for_prescription(self, router):
        """Test getting skill for prescription generation."""
        skill = router.get_skill_for_generation("prescription")
        
        if skill is not None:
            assert skill.product == "rxmembersim"
    
    def test_get_skill_for_subject(self, router):
        """Test getting skill for trial subject generation."""
        skill = router.get_skill_for_generation("subject")
        
        if skill is not None:
            assert skill.product == "trialsim"
    
    def test_get_skill_for_provider(self, router):
        """Test getting skill for provider generation."""
        skill = router.get_skill_for_generation("provider")
        
        if skill is not None:
            assert skill.product == "networksim"
    
    def test_get_skill_for_unknown_entity(self, router):
        """Test unknown entity type returns None."""
        skill = router.get_skill_for_generation("unknown_entity_xyz")
        
        assert skill is None


class TestGetSkillsForProducts:
    """Tests for get_skills_for_products."""
    
    @pytest.fixture
    def router(self):
        return SkillRouter()
    
    def test_get_skills_for_single_product(self, router):
        """Test getting skills for one product."""
        skills = router.get_skills_for_products(["patientsim"])
        
        assert len(skills) > 0
        for skill in skills:
            assert skill.product == "patientsim"
    
    def test_get_skills_for_multiple_products(self, router):
        """Test getting skills for multiple products."""
        skills = router.get_skills_for_products(["patientsim", "membersim"])
        
        products = set(s.product for s in skills)
        assert "patientsim" in products
        assert "membersim" in products
    
    def test_get_skills_deduplicates(self, router):
        """Test that skills are not duplicated."""
        skills = router.get_skills_for_products(["patientsim", "patientsim"])
        
        names = [s.metadata.name for s in skills]
        assert len(names) == len(set(names))  # No duplicates


class TestFindRelatedSkills:
    """Tests for find_related_skills."""
    
    @pytest.fixture
    def router(self):
        return SkillRouter()
    
    def test_find_related_skills(self, router):
        """Test finding related skills."""
        # Get a skill first
        patientsim_skills = router.loader.index.get_by_product("patientsim")
        if patientsim_skills:
            skill = patientsim_skills[0]
            related = router.find_related_skills(skill)
            
            assert isinstance(related, list)
            # Should not include the source skill
            for r in related:
                assert r.metadata.name != skill.metadata.name
    
    def test_find_related_skills_max_results(self, router):
        """Test max_results is respected."""
        patientsim_skills = router.loader.index.get_by_product("patientsim")
        if patientsim_skills:
            skill = patientsim_skills[0]
            related = router.find_related_skills(skill, max_results=3)
            
            assert len(related) <= 3
