"""
Tests for generation/cohort.py module.

Covers:
- CohortConstraints dataclass and serialization
- CohortProgress tracking and properties
- CohortGenerator base class
- Progress callbacks and iteration
"""

import pytest
from unittest.mock import MagicMock


class TestCohortConstraints:
    """Tests for CohortConstraints dataclass."""
    
    def test_default_values(self):
        """Test CohortConstraints has correct defaults."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        c = CohortConstraints()
        
        assert c.count == 100
        assert c.min_age is None
        assert c.max_age is None
        assert c.gender_distribution == {}
        assert c.custom == {}
    
    def test_custom_values(self):
        """Test CohortConstraints with custom values."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        c = CohortConstraints(
            count=50,
            min_age=30,
            max_age=60,
            gender_distribution={"M": 0.5, "F": 0.5},
            custom={"state": "TX"}
        )
        
        assert c.count == 50
        assert c.min_age == 30
        assert c.max_age == 60
        assert c.gender_distribution == {"M": 0.5, "F": 0.5}
        assert c.custom["state"] == "TX"
    
    def test_to_dict(self):
        """Test CohortConstraints serialization."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        c = CohortConstraints(
            count=25,
            min_age=18,
            max_age=65,
            gender_distribution={"M": 0.6, "F": 0.4},
            custom={"condition": "diabetes"}
        )
        
        d = c.to_dict()
        
        assert d["count"] == 25
        assert d["min_age"] == 18
        assert d["max_age"] == 65
        assert d["gender_distribution"]["M"] == 0.6
        assert d["custom"]["condition"] == "diabetes"
    
    def test_to_dict_with_defaults(self):
        """Test to_dict preserves None values."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        c = CohortConstraints()
        d = c.to_dict()
        
        assert d["min_age"] is None
        assert d["max_age"] is None
        assert d["gender_distribution"] == {}


class TestCohortProgress:
    """Tests for CohortProgress tracking."""
    
    def test_default_values(self):
        """Test CohortProgress has correct defaults."""
        from healthsim_agent.generation.cohort import CohortProgress
        
        p = CohortProgress()
        
        assert p.total == 0
        assert p.completed == 0
        assert p.failed == 0
        assert p.current_item == 0
    
    def test_percent_complete_zero_total(self):
        """Test percent_complete handles zero total."""
        from healthsim_agent.generation.cohort import CohortProgress
        
        p = CohortProgress(total=0)
        
        assert p.percent_complete == 0.0
    
    def test_percent_complete_partial(self):
        """Test percent_complete with partial completion."""
        from healthsim_agent.generation.cohort import CohortProgress
        
        p = CohortProgress(total=100, completed=50)
        
        assert p.percent_complete == 50.0
    
    def test_percent_complete_full(self):
        """Test percent_complete at 100%."""
        from healthsim_agent.generation.cohort import CohortProgress
        
        p = CohortProgress(total=100, completed=100)
        
        assert p.percent_complete == 100.0
    
    def test_is_complete_false(self):
        """Test is_complete returns False when not done."""
        from healthsim_agent.generation.cohort import CohortProgress
        
        p = CohortProgress(total=100, completed=50, failed=0)
        
        assert p.is_complete is False
    
    def test_is_complete_true_all_completed(self):
        """Test is_complete when all completed."""
        from healthsim_agent.generation.cohort import CohortProgress
        
        p = CohortProgress(total=100, completed=100, failed=0)
        
        assert p.is_complete is True
    
    def test_is_complete_true_with_failures(self):
        """Test is_complete counts failures."""
        from healthsim_agent.generation.cohort import CohortProgress
        
        p = CohortProgress(total=100, completed=80, failed=20)
        
        assert p.is_complete is True
    
    def test_is_complete_partial_with_failures(self):
        """Test is_complete with incomplete but some failures."""
        from healthsim_agent.generation.cohort import CohortProgress
        
        p = CohortProgress(total=100, completed=50, failed=20)
        
        assert p.is_complete is False


class TestCohortGenerator:
    """Tests for CohortGenerator base class."""
    
    def test_init_default_seed(self):
        """Test generator initializes with default seed."""
        from healthsim_agent.generation.cohort import CohortGenerator
        
        g = CohortGenerator()
        
        assert g.seed_manager is not None
        assert g.progress.total == 0
    
    def test_init_custom_seed(self):
        """Test generator initializes with custom seed."""
        from healthsim_agent.generation.cohort import CohortGenerator
        
        g = CohortGenerator(seed=12345)
        
        assert g.seed_manager is not None
    
    def test_generate_one_not_implemented(self):
        """Test generate_one raises NotImplementedError."""
        from healthsim_agent.generation.cohort import CohortGenerator, CohortConstraints
        
        g = CohortGenerator()
        c = CohortConstraints(count=1)
        
        with pytest.raises(NotImplementedError):
            g.generate_one(0, c)
    
    def test_progress_property(self):
        """Test progress property returns CohortProgress."""
        from healthsim_agent.generation.cohort import CohortGenerator
        
        g = CohortGenerator()
        
        assert g.progress.total == 0
        assert g.progress.completed == 0
    
    def test_reset(self):
        """Test reset resets the seed manager."""
        from healthsim_agent.generation.cohort import CohortGenerator
        
        g = CohortGenerator(seed=42)
        
        # Get a few values using the rng's random method
        v1 = g.seed_manager.rng.random()
        v2 = g.seed_manager.rng.random()
        
        # Reset
        g.reset()
        
        # Should get same values
        v3 = g.seed_manager.rng.random()
        v4 = g.seed_manager.rng.random()
        
        assert v1 == v3
        assert v2 == v4


class TestCohortGeneratorGenerate:
    """Tests for CohortGenerator.generate method using subclass."""
    
    def get_test_generator(self):
        """Create a test generator subclass."""
        from healthsim_agent.generation.cohort import CohortGenerator, CohortConstraints
        
        class TestGenerator(CohortGenerator[dict]):
            def __init__(self, seed=None, fail_on=None):
                super().__init__(seed)
                self.fail_on = fail_on or set()
            
            def generate_one(self, index: int, constraints: CohortConstraints) -> dict:
                if index in self.fail_on:
                    raise ValueError(f"Simulated failure at {index}")
                return {"index": index, "count": constraints.count}
        
        return TestGenerator
    
    def test_generate_all_success(self):
        """Test generate with all successful generations."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        TestGenerator = self.get_test_generator()
        g = TestGenerator()
        c = CohortConstraints(count=5)
        
        results = g.generate(c)
        
        assert len(results) == 5
        assert g.progress.completed == 5
        assert g.progress.failed == 0
        assert g.progress.is_complete is True
    
    def test_generate_with_failures(self):
        """Test generate handles failures gracefully."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        TestGenerator = self.get_test_generator()
        g = TestGenerator(fail_on={1, 3})
        c = CohortConstraints(count=5)
        
        results = g.generate(c)
        
        assert len(results) == 3  # 5 - 2 failures
        assert g.progress.completed == 3
        assert g.progress.failed == 2
        assert g.progress.is_complete is True
    
    def test_generate_with_callback(self):
        """Test generate calls progress callback."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        TestGenerator = self.get_test_generator()
        g = TestGenerator()
        c = CohortConstraints(count=3)
        
        callback_calls = []
        def track_progress(progress):
            callback_calls.append({
                "completed": progress.completed,
                "current": progress.current_item
            })
        
        g.generate(c, progress_callback=track_progress)
        
        assert len(callback_calls) == 3
        assert callback_calls[0]["current"] == 0
        assert callback_calls[2]["completed"] == 3
    
    def test_generate_resets_progress(self):
        """Test generate resets progress for each run."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        TestGenerator = self.get_test_generator()
        g = TestGenerator()
        c = CohortConstraints(count=3)
        
        # First run
        g.generate(c)
        assert g.progress.completed == 3
        
        # Second run should reset
        g.generate(CohortConstraints(count=5))
        assert g.progress.total == 5
        assert g.progress.completed == 5


class TestCohortGeneratorIter:
    """Tests for CohortGenerator.generate_iter method."""
    
    def get_test_generator(self):
        """Create a test generator subclass."""
        from healthsim_agent.generation.cohort import CohortGenerator, CohortConstraints
        
        class TestGenerator(CohortGenerator[dict]):
            def generate_one(self, index: int, constraints: CohortConstraints) -> dict:
                return {"index": index}
        
        return TestGenerator
    
    def test_generate_iter_yields_items(self):
        """Test generate_iter yields all items."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        TestGenerator = self.get_test_generator()
        g = TestGenerator()
        c = CohortConstraints(count=5)
        
        results = list(g.generate_iter(c))
        
        assert len(results) == 5
        assert results[0]["index"] == 0
        assert results[4]["index"] == 4
    
    def test_generate_iter_is_lazy(self):
        """Test generate_iter is a lazy iterator."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        TestGenerator = self.get_test_generator()
        g = TestGenerator()
        c = CohortConstraints(count=100)
        
        iterator = g.generate_iter(c)
        
        # Should be an iterator, not a list
        assert hasattr(iterator, '__next__')
        
        # Get just first item
        first = next(iterator)
        assert first["index"] == 0
    
    def test_generate_iter_empty(self):
        """Test generate_iter with count=0."""
        from healthsim_agent.generation.cohort import CohortConstraints
        
        TestGenerator = self.get_test_generator()
        g = TestGenerator()
        c = CohortConstraints(count=0)
        
        results = list(g.generate_iter(c))
        
        assert results == []


class TestModuleExports:
    """Tests for module __all__ exports."""
    
    def test_exports(self):
        """Test module exports correct symbols."""
        from healthsim_agent.generation import cohort
        
        assert "CohortConstraints" in cohort.__all__
        assert "CohortProgress" in cohort.__all__
        assert "CohortGenerator" in cohort.__all__
