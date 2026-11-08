
import re
from functools import lru_cache

from sentence_transformers import SentenceTransformer, util


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


# AI model configuration
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Similarity threshold: only sufficiently related phrases match.
SIMILARITY_THRESHOLD = 0.45


# Maps alternative skill names to standard skill names.
SKILL_SYNONYMS = {
    "machine learning": [
        "machine learning",
        "machine-learning",
        "ml",
    ],
    "artificial intelligence": [
        "artificial intelligence",
        "artificial-intelligence",
        "ai",
    ],
    "python": [
        "python",
        "python programming",
        "python language",
    ],
    "sql": [
        "sql",
        "structured query language",
    ],
    "data science": [
        "data science",
    ],
    "data analysis": [
        "data analysis",
        "data analytics",
    ],
    "analytics": [
        "analytics",
        "business analytics",
    ],
    "react": [
        "react",
        "react.js",
        "reactjs",
    ],
    "javascript": [
        "javascript",
        "js",
    ],
    "fastapi": [
        "fastapi",
        "fast api",
    ],
    "mysql": [
        "mysql",
        "my sql",
    ],
}


def normalize_text(text):
    """Normalize text for consistent comparisons."""
    return (text or "").lower().strip()


def normalize_skill(skill):
    """Convert a skill alias into its standard skill name."""

    normalized_skill = normalize_text(skill)

    for standard_skill, aliases in SKILL_SYNONYMS.items():
        if normalized_skill in aliases:
            return standard_skill

    return normalized_skill


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load and cache the sentence-transformer model."""

    return SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )


def split_into_phrases(source_text):
    """
    Split profile information into meaningful phrases
    and remove common introductory wording.
    """

    if not source_text:
        return []

    phrases = re.split(
        r"[\n,;|]+|\s+and\s+",
        source_text,
        flags=re.IGNORECASE
    )

    cleaned_phrases = []

    prefixes = [
        r"i have experience in",
        r"i have experience with",
        r"experience in",
        r"experience with",
        r"i know",
        r"i am skilled in",
        r"skilled in",
        r"knowledge of",
        r"working with",
        r"worked on",
        r"interested in",
    ]

    for phrase in phrases:
        phrase = phrase.strip().lower()

        for prefix in prefixes:
            phrase = re.sub(
                r"^" + prefix + r"\s+",
                "",
                phrase
            )

        if phrase:
            cleaned_phrases.append(phrase)

    return cleaned_phrases


def find_exact_skill_match(source_text, skill):
    """Check exact and known synonym matches."""

    normalized_text = normalize_text(source_text)
    standard_skill = normalize_skill(skill)

    aliases = SKILL_SYNONYMS.get(
        standard_skill,
        [standard_skill]
    )

    for alias in aliases:
        pattern = (
            r"(?<!\w)"
            + re.escape(alias)
            + r"(?!\w)"
        )

        if re.search(pattern, normalized_text):
            return True

    return False


def find_semantic_skill_matches(source_text, professional_skills):
    """
    Find skill matches using exact matching and AI embeddings.

    The highest cosine similarity between each professional skill
    and the user's individual profile phrases is used.
    """

    if not source_text or not professional_skills:
        return []

    phrases = split_into_phrases(source_text)

    if not phrases:
        return []

    matched_skills = []

    # Exact matches are checked first.
    unmatched_skills = []

    for skill in professional_skills:
        standard_skill = normalize_skill(skill)

        if find_exact_skill_match(source_text, skill):
            matched_skills.append(standard_skill)
        else:
            unmatched_skills.append(standard_skill)

    # Avoid loading the model if every skill already matched.
    if not unmatched_skills:
        return list(dict.fromkeys(matched_skills))

    model = get_embedding_model()

    # Generate normalized embeddings.
    phrase_embeddings = model.encode(
        phrases,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    skill_embeddings = model.encode(
        unmatched_skills,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    # Calculate cosine similarities.
    similarity_matrix = util.cos_sim(
        skill_embeddings,
        phrase_embeddings
    )

    # Match each skill with its best profile phrase.
    for index, skill in enumerate(unmatched_skills):

        highest_similarity = similarity_matrix[index].max().item()

        if highest_similarity >= SIMILARITY_THRESHOLD:
            matched_skills.append(skill)

    return list(dict.fromkeys(matched_skills))


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
    matched_skills = find_semantic_skill_matches(
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
    goal_matches = find_semantic_skill_matches(
        career_goals,
        professional["skills"]
    )

    goal_score = (
        (len(goal_matches) / total_skills) * 100
        if total_skills else 0
    )

    # Use only factors for which the user supplied information.
    weighted_total = skill_score * 0.50
    total_weight = 0.50

    if preferred_roles and preferred_roles.strip():
        weighted_total += role_score * 0.30
        total_weight += 0.30

    if career_goals and career_goals.strip():
        weighted_total += goal_score * 0.20
        total_weight += 0.20

    final_score = round(weighted_total / total_weight)

    # Generate explanations.
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
