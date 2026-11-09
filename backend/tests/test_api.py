
def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "Backend is running successfully"


def test_recommendations_without_profile(client):
    response = client.get("/api/recommendations/")

    assert response.status_code == 404
    assert "save your profile" in response.json()["detail"].lower()


def test_create_profile(client):
    profile_data = {
        "full_name": "Test User",
        "headline": "B.Tech CSE Student",
        "linkedin_profile": "Python, SQL and Machine Learning",
        "skills": "Python, SQL, Machine Learning",
        "education": "B.Tech CSE",
        "experience": "Academic projects",
        "career_goals": "Become a Data Analyst",
        "preferred_roles": "Data Analyst, AI Engineer",
    }

    response = client.post(
        "/api/profiles/",
        json=profile_data,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] > 0
    assert data["full_name"] == "Test User"
    assert data["linkedin_profile"] == profile_data["linkedin_profile"]


def test_get_all_profiles(client):
    client.post(
        "/api/profiles/",
        json={"linkedin_profile": "Python and SQL"},
    )

    response = client.get("/api/profiles/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["linkedin_profile"] == "Python and SQL"


def test_get_profile_by_id(client):
    create_response = client.post(
        "/api/profiles/",
        json={
            "full_name": "Test User",
            "linkedin_profile": "Python developer",
        },
    )

    profile_id = create_response.json()["id"]

    response = client.get(f"/api/profiles/{profile_id}")

    assert response.status_code == 200
    assert response.json()["full_name"] == "Test User"


def test_get_nonexistent_profile(client):
    response = client.get("/api/profiles/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"


def test_update_profile(client):
    create_response = client.post(
        "/api/profiles/",
        json={
            "full_name": "Old Name",
            "linkedin_profile": "Python developer",
        },
    )

    profile_id = create_response.json()["id"]

    updated_data = {
        "full_name": "Updated Name",
        "headline": "Aspiring Data Analyst",
        "linkedin_profile": "Python, SQL and Data Science",
        "skills": "Python, SQL",
        "education": "B.Tech CSE",
        "experience": "Projects",
        "career_goals": "Become a Data Analyst",
        "preferred_roles": "Data Analyst",
    }

    response = client.put(
        f"/api/profiles/{profile_id}",
        json=updated_data,
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
    assert response.json()["linkedin_profile"] == updated_data["linkedin_profile"]


def test_update_nonexistent_profile(client):
    response = client.put(
        "/api/profiles/9999",
        json={"linkedin_profile": "Python developer"},
    )

    assert response.status_code == 404


def test_delete_profile(client):
    create_response = client.post(
        "/api/profiles/",
        json={"linkedin_profile": "Python developer"},
    )

    profile_id = create_response.json()["id"]

    response = client.delete(f"/api/profiles/{profile_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Profile deleted successfully"

    get_response = client.get(f"/api/profiles/{profile_id}")

    assert get_response.status_code == 404


def test_delete_nonexistent_profile(client):
    response = client.delete("/api/profiles/9999")

    assert response.status_code == 404


def test_generate_recommendations(client):
    client.post(
        "/api/profiles/",
        json={
            "linkedin_profile": (
                "Python, SQL, Machine Learning, Data Science"
            ),
            "career_goals": "Interested in AI and Data Science",
            "preferred_roles": (
                "Data Analyst, Junior Data Scientist, AI Engineer"
            ),
        },
    )

    response = client.get("/api/recommendations/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Recommendations generated successfully"
    assert data["profile_id"] > 0
    assert data["total_recommendations"] == 3
    assert len(data["recommendations"]) == 3

    scores = [
        item["match"]
        for item in data["recommendations"]
    ]

    assert scores == sorted(scores, reverse=True)
