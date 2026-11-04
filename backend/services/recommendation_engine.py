
import re


# Fictional sample professionals for testing.
# These are not real LinkedIn users.

SAMPLE_PROFESSIONALS = [
    {
        "name": "Sarah Johnson",
        "role": "Technical Recruiter",
        "company": "Google",
        "skills": ["python", "machine learning", "data science"],
        "initials": "SJ",
        "color": "purple",
    },
    {
        "name": "Michael Chen",
        "role": "Engineering Manager",
        "company": "Microsoft",
        "skills": ["python", "sql", "artificial intelligence"],
        "initials": "MC",
        "color": "blue",
    },
    {
        "name": "Priya Sharma",
        "role": "Talent Acquisition",
        "company": "Amazon",
        "skills": ["data science", "sql", "analytics"],
        "initials": "PS",
        "color": "pink",
    },
]


def calculate_match(user_text, professional):
    """Calculate how closely a professional matches the user's profile."""

    normalized_text = user_text.lower()

    matched_skills = []

    for skill in professional["skills"]:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, normalized_text):
            matched_skills.append(skill)

    total_skills = len(professional["skills"])

    if total_skills == 0:
        score = 0
    else:
        score = round((len(matched_skills) / total_skills) * 100)

    if matched_skills:
        reason = "Matching interests: " + ", ".join(matched_skills)
    else:
        reason = "This professional may be relevant to explore."

    return {
        "match": score,
        "matched_skills": matched_skills,
        "reason": reason,
    }


def generate_recommendations(profile_text, career_goals):
    """Generate ranked recommendations using profile information."""

    user_text = f"{profile_text} {career_goals}"

    recommendations = []

    for professional in SAMPLE_PROFESSIONALS:
        match_details = calculate_match(user_text, professional)

        recommendation = {
            **professional,
            **match_details,
        }

        recommendations.append(recommendation)

    recommendations.sort(
        key=lambda person: person["match"],
        reverse=True
    )

    return recommendations
