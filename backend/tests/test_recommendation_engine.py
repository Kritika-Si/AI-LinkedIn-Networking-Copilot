
from services.recommendation_engine import (
    find_semantic_skill_matches,
    calculate_match,
    generate_recommendations,
)


def test_exact_skill_matching():
    matches = find_semantic_skill_matches(
        "Python, SQL",
        ["python", "sql", "machine learning"],
    )

    assert "python" in matches
    assert "sql" in matches


def test_semantic_skill_matching():
    matches = find_semantic_skill_matches(
        "I have experience in predictive modeling",
        ["machine learning"],
    )

    assert "machine learning" in matches


def test_unrelated_skill_is_rejected():
    matches = find_semantic_skill_matches(
        "I have experience in graphic design",
        ["machine learning"],
    )

    assert "machine learning" not in matches


def test_role_matching():
    professional = {
        "name": "Sarah Johnson",
        "role": "Technical Recruiter",
        "company": "Google",
        "skills": ["python", "machine learning", "data science"],
        "supports_roles": ["Data Analyst", "AI Engineer"],
    }

    result = calculate_match(
        "Python, machine learning",
        "",
        "Data Analyst, AI Engineer",
        professional,
    )

    assert result["match"] > 0
    assert result["match_breakdown"]["role_match"] == 100


def test_empty_profile_returns_zero_match():
    professional = {
        "name": "Test Professional",
        "role": "Recruiter",
        "company": "Test Company",
        "skills": ["python"],
        "supports_roles": ["Data Analyst"],
    }

    result = calculate_match("", "", "", professional)

    assert result["match"] == 0


def test_recommendations_are_ranked():
    recommendations = generate_recommendations(
        profile_text="Python, SQL, machine learning, data science",
        career_goals="Interested in data science and AI",
        preferred_roles="Data Analyst, Junior Data Scientist, AI Engineer",
    )

    assert len(recommendations) == 3

    scores = [item["match"] for item in recommendations]

    assert scores == sorted(scores, reverse=True)


def test_recommendations_have_required_fields():
    recommendations = generate_recommendations(
        profile_text="Python, SQL, machine learning",
        career_goals="Interested in data science",
        preferred_roles="Data Analyst, AI Engineer",
    )

    for item in recommendations:
        assert "name" in item
        assert "role" in item
        assert "company" in item
        assert "match" in item
        assert "matched_skills" in item
        assert "reason" in item
        assert "match_breakdown" in item
