"""Test Suite for DarkFactory Topic Generator Engine (YouTube 15-30 min Compliance)."""

import pytest
from src.topic_generator import TopicGeneratorEngine, CANONICAL_TOPICS


@pytest.fixture
def engine():
    return TopicGeneratorEngine()


def test_canonical_topics_exist_and_conform_to_15_30_min(engine):
    """Verifies that all canonical topics are designed for 15-30 minute episodes."""
    topics = engine.get_all_topics()
    assert len(topics) >= 10

    for t in topics:
        assert 15 <= t.duration_min <= 30, f"Topic {t.title} duration {t.duration_min} not in 15-30 min range"
        assert t.green_dollar_score == 100, f"Topic {t.title} must be 100% Green Dollar"
        assert t.edsa_compliant is True, f"Topic {t.title} must be EDSA compliant"
        assert len(t.title) > 5
        assert len(t.query) > 3
        assert len(t.viral_hook) > 20
        assert "slow_clock" in t.nolan_threads
        assert "fast_clock" in t.nolan_threads
        assert "aftermath" in t.nolan_threads


def test_categories_aggregation(engine):
    """Verifies that distinct categories are properly reported with counts."""
    categories = engine.get_categories()
    assert len(categories) >= 4
    cat_ids = [c["id"] for c in categories]
    assert "crises_desclassificadas" in cat_ids
    assert "misterios_militares_navais" in cat_ids
    assert "guerra_fria_espionagem" in cat_ids
    assert "ciencia_catastrofes" in cat_ids


def test_filter_by_category(engine):
    """Verifies filtering topics by category."""
    filtered = engine.get_topics_by_category("crises_desclassificadas")
    assert len(filtered) > 0
    for t in filtered:
        assert t.category == "crises_desclassificadas"


def test_random_topic_selection(engine):
    """Verifies single random selection."""
    topic = engine.get_random_topic()
    assert topic is not None
    assert topic.title is not None
    assert 15 <= topic.duration_min <= 30


def test_batch_generation(engine):
    """Verifies batch topic generation."""
    batch = engine.get_batch(count=4)
    assert len(batch) == 4
    # All items must be unique in batch
    titles = [t.title for t in batch]
    assert len(set(titles)) == 4


def test_validate_clean_topic(engine):
    """Verifies compliance validation for a clean educational topic."""
    res = engine.validate_topic_compliance("1983 Soviet nuclear false alarm incident")
    assert res["is_green_dollar"] is True
    assert res["green_dollar_score"] == 100
    assert len(res["flagged_terms"]) == 0


def test_validate_flagged_topic_and_sanitization(engine):
    """Verifies that sensitive terms are flagged and sanitized under EDSA."""
    res = engine.validate_topic_compliance("The Secret Massacre of Cold War Operatives")
    assert res["is_green_dollar"] is False
    assert "massacre" in res["flagged_terms"]
    assert "Incident" in res["sanitized_topic"]
    assert res["green_dollar_score"] < 100


def test_procedural_suggestion_from_seed(engine):
    """Verifies procedural blueprint generation from a custom seed concept."""
    blueprint = engine.generate_procedural_suggestion("Bermuda Triangle 1945 Patrol")
    assert blueprint.duration_min == 20
    assert "Bermuda" in blueprint.title or "Incident" in blueprint.title
    assert blueprint.green_dollar_score == 100
    assert "slow_clock" in blueprint.nolan_threads
