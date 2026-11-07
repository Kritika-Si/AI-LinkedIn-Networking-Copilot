
import re


# Fictional sample professionals for testing.
# These are not real LinkedIn users.

SAMPLE_PROFESSIONALS = [
    {
        "name": "Sarah Johnson",
        "role": "Technical Recruiter",
        "company": "Google",
        "skills": ["python", "machine learning", "data science"],
        "supports_roles": [
            "Data Analyst",
            "Junior Data Scientist",
            "AI Engineer",
            "Business Analyst",
        ],
        "initials": "SJ",
        "color": "purple",
    },
    {
        "name": "Michael Chen",
        "role": "Engineering Manager",
        "company": "Microsoft",
        "skills": ["python", "sql", "artificial intelligence"],
        "supports_roles": [
            "AI Engineer",
            "Junior Data Scientist",
        ],
        "initials": "MC",
        "color": "blue",
    },
    {
        "name": "Priya Sharma",
        "role": "Talent Acquisition",
        "company": "Amazon",
        "skills": ["data science", "sql", "analytics"],
        "supports_roles": [
            "Data Analyst",
            "Junior Data Scientist",
            "Business Analyst",
        ],
        "initials": "PS",
        "color": "pink",
    },
]


def normalize_text(text):
    """Normalize text for consistent comparisons."""
    return (text or "").lower().strip()


def find_matches(source_text, keywords):
    """Find keywords that appear in the given text."""

    normalized_text = normalize_text(source_text)
    matched = []

    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

        if re.search(pattern, normalized_text):
            matched.append(keyword)

    return matched


def calculate_role_match(preferred_roles, professional):
    """Calculate compatibility with the user's preferred roles."""

    if not preferred_roles or not preferred_roles.strip():
        return 0, []

    user_roles = [
        role.strip()
        for role in preferred_roles.split(",")
        if role.strip()
    ]

    if not user_roles:
        return 0, []

    supported_roles = {
        normalize_text(role)
        for role in professional.get("supports_roles", [])
    }

    matched_roles = [
        role
        for role in user_roles
        if normalize_text(role) in supported_roles
    ]

    role_score = round(
        (len(matched_roles) / len(user_roles)) * 100
    )

    return role_score, matched_roles


def calculate_match(
    profile_text,
    career_goals,
    preferred_roles,
    professional
):
    """Calculate a personalized recommendation score."""

    # 1. Skill matching (50%)
    matched_skills = find_matches(
        profile_text,
        professional["skills"]
    )

    total_skills = len(professional["skills"])

    skill_score = (
        (len(matched_skills) / total_skills) * 100
        if total_skills else 0
    )

    # 2. Preferred role matching (30%)
    role_score, matched_roles = calculate_role_match(
        preferred_roles,
        professional
    )

    # 3. Career goal matching (20%)
    goal_matches = find_matches(
        career_goals,
        professional["skills"]
    )

    goal_score = (
        (len(goal_matches) / total_skills) * 100
        if total_skills else 0
    )

    # Use only the factors for which the user supplied information.
    weighted_total = skill_score * 0.50
    total_weight = 0.50

    if preferred_roles and preferred_roles.strip():
        weighted_total += role_score * 0.30
        total_weight += 0.30

    if career_goals and career_goals.strip():
        weighted_total += goal_score * 0.20
        total_weight += 0.20

    final_score = round(weighted_total / total_weight)

    # Generate explanations for the recommendation.
    reasons = []

    if matched_skills:
        reasons.append(
            "Matching skills: " + ", ".join(matched_skills)
        )

    if matched_roles:
        reasons.append(
            "Relevant preferred roles: " + ", ".join(matched_roles)
        )

    if goal_matches:
        reasons.append(
            "Career goal matches: " + ", ".join(goal_matches)
        )

    if not reasons:
        reason = (
            "Limited matching information. "
            "Consider exploring this professional's background."
        )
    else:
        reason = ". ".join(reasons) + "."

    return {
        "match": final_score,
        "matched_skills": matched_skills,
        "reason": reason,
        "match_breakdown": {
            "skill_match": round(skill_score),
            "role_match": round(role_score),
            "goal_match": round(goal_score),
        },
    }


def generate_recommendations(
    profile_text,
    career_goals="",
    preferred_roles=""
):
    """Generate and rank personalized recommendations."""

    recommendations = []

    for professional in SAMPLE_PROFESSIONALS:

        match_details = calculate_match(
            profile_text,
            career_goals,
            preferred_roles,
            professional
        )

        recommendation = {
            **professional,
            **match_details,
        }

        recommendations.append(recommendation)

    # Highest matching professionals appear first.
    recommendations.sort(
        key=lambda person: person["match"],
        reverse=True
    )

    return recommendations
