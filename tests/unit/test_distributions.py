"""Tests for generation framework - distributions."""

import random
import pytest

from healthsim_agent.generation import (
    NormalDistribution,
    UniformDistribution,
    CategoricalDistribution,
    AgeBandDistribution,
    ExplicitDistribution,
    AgeDistribution,
    WeightedChoice,
    create_distribution,
)


class TestNormalDistribution:
    """Tests for NormalDistribution."""
    
    def test_sample(self):
        """Test sampling from normal distribution."""
        dist = NormalDistribution(mean=100, std_dev=15)
        rng = random.Random(42)
        
        values = [dist.sample(rng) for _ in range(1000)]
        
        # Mean should be close to 100
        assert 95 < sum(values) / len(values) < 105
    
    def test_sample_int(self):
        """Test sampling integer from normal distribution."""
        dist = NormalDistribution(mean=50, std_dev=10)
        rng = random.Random(42)
        
        value = dist.sample_int(rng)
        assert isinstance(value, int)
    
    def test_sample_bounded(self):
        """Test bounded sampling."""
        dist = NormalDistribution(mean=50, std_dev=20)
        rng = random.Random(42)
        
        for _ in range(100):
            value = dist.sample_bounded(min_val=30, max_val=70, rng=rng)
            assert 30 <= value <= 70


class TestUniformDistribution:
    """Tests for UniformDistribution."""
    
    def test_sample(self):
        """Test sampling from uniform distribution."""
        dist = UniformDistribution(min_val=0, max_val=100)
        rng = random.Random(42)
        
        values = [dist.sample(rng) for _ in range(1000)]
        
        # All values should be in range
        assert all(0 <= v <= 100 for v in values)
        
        # Mean should be close to 50
        assert 45 < sum(values) / len(values) < 55
    
    def test_sample_int(self):
        """Test sampling integer."""
        dist = UniformDistribution(min_val=1, max_val=10)
        rng = random.Random(42)
        
        values = [dist.sample_int(rng) for _ in range(100)]
        
        assert all(isinstance(v, int) for v in values)
        assert all(1 <= v <= 10 for v in values)


class TestCategoricalDistribution:
    """Tests for CategoricalDistribution."""
    
    def test_sample(self):
        """Test sampling from categorical distribution."""
        dist = CategoricalDistribution(weights={"A": 0.5, "B": 0.3, "C": 0.2})
        rng = random.Random(42)
        
        values = [dist.sample(rng) for _ in range(1000)]
        
        # All values should be valid categories
        assert all(v in ["A", "B", "C"] for v in values)
        
        # A should be most common
        counts = {v: values.count(v) for v in ["A", "B", "C"]}
        assert counts["A"] > counts["B"] > counts["C"]
    
    def test_weights_must_sum_to_one(self):
        """Test that weights must sum to 1.0."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            CategoricalDistribution(weights={"A": 0.5, "B": 0.3})
    
    def test_sample_multiple(self):
        """Test sampling multiple values."""
        dist = CategoricalDistribution(weights={"M": 0.5, "F": 0.5})
        rng = random.Random(42)
        
        values = dist.sample_multiple(10, rng)
        
        assert len(values) == 10
        assert all(v in ["M", "F"] for v in values)


class TestAgeBandDistribution:
    """Tests for AgeBandDistribution."""
    
    def test_sample(self):
        """Test sampling from age bands."""
        dist = AgeBandDistribution(bands={
            "0-17": 0.20,
            "18-64": 0.60,
            "65+": 0.20,
        })
        rng = random.Random(42)
        
        values = [dist.sample(rng) for _ in range(1000)]
        
        # All values should be valid ages
        assert all(0 <= v <= 95 for v in values)
        
        # Most values should be working age (18-64)
        working_age = [v for v in values if 18 <= v <= 64]
        assert len(working_age) > 500


class TestExplicitDistribution:
    """Tests for ExplicitDistribution."""
    
    def test_sample(self):
        """Test sampling from explicit values."""
        dist = ExplicitDistribution(values=[
            ("TX", 0.5),
            ("CA", 0.3),
            ("NY", 0.2),
        ])
        rng = random.Random(42)
        
        values = [dist.sample(rng) for _ in range(100)]
        
        assert all(v in ["TX", "CA", "NY"] for v in values)


class TestAgeDistribution:
    """Tests for AgeDistribution helper class."""
    
    def test_adult_distribution(self):
        """Test adult age distribution."""
        dist = AgeDistribution.adult()
        dist.seed(42)
        
        ages = dist.sample_many(100)
        
        assert all(18 <= a <= 90 for a in ages)
    
    def test_pediatric_distribution(self):
        """Test pediatric age distribution."""
        dist = AgeDistribution.pediatric()
        dist.seed(42)
        
        ages = dist.sample_many(100)
        
        assert all(0 <= a <= 17 for a in ages)
    
    def test_senior_distribution(self):
        """Test senior age distribution."""
        dist = AgeDistribution.senior()
        dist.seed(42)
        
        ages = dist.sample_many(100)
        
        assert all(65 <= a <= 95 for a in ages)


class TestWeightedChoice:
    """Tests for WeightedChoice."""
    
    def test_select(self):
        """Test weighted selection."""
        choices = WeightedChoice(options=[
            ("common", 0.7),
            ("uncommon", 0.2),
            ("rare", 0.1),
        ])
        rng = random.Random(42)
        
        values = [choices.select(rng) for _ in range(1000)]
        
        counts = {v: values.count(v) for v in ["common", "uncommon", "rare"]}
        
        # Common should be most frequent
        assert counts["common"] > counts["uncommon"] > counts["rare"]
    
    def test_select_multiple_unique(self):
        """Test selecting multiple unique values."""
        choices = WeightedChoice(options=[
            ("A", 0.25),
            ("B", 0.25),
            ("C", 0.25),
            ("D", 0.25),
        ])
        rng = random.Random(42)
        
        values = choices.select_multiple(3, rng, unique=True)
        
        assert len(values) == 3
        assert len(set(values)) == 3  # All unique


class TestCreateDistribution:
    """Tests for create_distribution factory."""
    
    def test_create_normal(self):
        """Test creating normal distribution."""
        dist = create_distribution({
            "type": "normal",
            "mean": 72,
            "std_dev": 8,
        })
        
        assert isinstance(dist, NormalDistribution)
        assert dist.mean == 72
        assert dist.std_dev == 8
    
    def test_create_categorical(self):
        """Test creating categorical distribution."""
        dist = create_distribution({
            "type": "categorical",
            "weights": {"M": 0.48, "F": 0.52},
        })
        
        assert isinstance(dist, CategoricalDistribution)
    
    def test_create_uniform(self):
        """Test creating uniform distribution."""
        dist = create_distribution({
            "type": "uniform",
            "min": 0,
            "max": 100,
        })
        
        assert isinstance(dist, UniformDistribution)
    
    def test_create_age_bands(self):
        """Test creating age band distribution."""
        dist = create_distribution({
            "type": "age_bands",
            "bands": {"0-17": 0.25, "18-64": 0.55, "65+": 0.20},
        })
        
        assert isinstance(dist, AgeBandDistribution)
    
    def test_unknown_type_raises(self):
        """Test that unknown type raises error."""
        with pytest.raises(ValueError, match="Unknown distribution type"):
            create_distribution({"type": "invalid"})
