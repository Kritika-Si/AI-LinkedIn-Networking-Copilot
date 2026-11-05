
import re


# Fictional sample professionals for testing.
# These are not real LinkedIn users.

SAMPLE_PROFESSIONALS = [
    {
        "name": "Sarah Johnson",
        "role": "Technical Recruiter",
        "company": "Google",
        "skills": ["python", "machine learning", "data science"],
        "supports_roles": ["*"],
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
            "Junior Data Scientist"
        ],
        "initials": "MC",
        "color": "blue",
    },
    {
        "name": "Priya Sharma",
        "role": "Talent Acquisition",
        "company": "Amazon",
        "skills": ["data science", "sql", "analytics"],
        "supports_roles": ["*"],
        "initials": "PS",
        "color": "pink",
    },
]


def normalize_text(text):
    """Convert text to lowercase for consistent matching."""
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
    """
    Calculate how relevant a professional is to the user's
    preferred job roles.

    Recruiters and talent acquisition professionals can support
    multiple job roles. Other professionals are matched against
    the roles they can specifically support.
    """

    if not preferred_roles or not preferred_roles.strip():
        return 0, []

    user_roles = [
        role.strip()
        for role in preferred_roles.split(",")
        if role.strip()
    ]

    if not user_roles:
        return 0, []

    supported_roles = professional.get("supports_roles", [])

    # Recruiters can potentially help with all preferred roles.
    if "*" in supported_roles:
        return 100, user_roles

    matched_roles = []

    supported_normalized = {
        normalize_text(role) for role in supported_roles
    }

    for role in user_roles:
        if normalize_text(role) in supported_normalized:
            matched_roles.append(role)

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
    """Calculate recommendation score using multiple factors."""

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

    # 2. Contact relevance to preferred roles (30%)
    role_score, matched_roles = calculate_role_match(
        preferred_roles,
        professional
    )

    # 3. Career goal relevance (20%)
    goal_matches = find_matches(
        career_goals,
        professional["skills"]
    )

    goal_score = (
        (len(goal_matches) / total_skills) * 100
        if total_skills else 0
    )

    # Calculate weighted score using available information.
    weighted_total = skill_score * 0.50
    total_weight = 0.50

    if preferred_roles and preferred_roles.strip():
        weighted_total += role_score * 0.30
        total_weight += 0.30

    if career_goals and career_goals.strip():
        weighted_total += goal_score * 0.20
        total_weight += 0.20

    final_score = round(weighted_total / total_weight)

    # Generate an explanation for the recommendation.
    reasons = []

    if matched_skills:
        reasons.append(
            "Matching skills: " + ", ".join(matched_skills)
        )

    if matched_roles:
        reasons.append(
            "Can help with preferred roles: "
            + ", ".join(matched_roles)
        )

    if goal_matches:
        reasons.append(
            "Career goal matches: " + ", ".join(goal_matches)
        )

    reason = (
        ". ".join(reasons)
        if reasons
        else "This professional may be relevant to explore."
    )

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
    """Generate and rank personalized professional recommendations."""

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
