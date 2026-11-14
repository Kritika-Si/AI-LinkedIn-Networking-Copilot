
def test_register_user(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/auth/register",
        json={
            "full_name": "New User",
            "email": "newuser@example.com",
            "password": "NewPassword123!",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["full_name"] == "New User"
    assert data["email"] == "newuser@example.com"
    assert "hashed_password" not in data

    me_response = unauthenticated_client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "newuser@example.com"


def test_register_duplicate_email(client):
    response = client.post(
        "/api/auth/register",
        json={
            "full_name": "Another User",
            "email": "testuser@example.com",
            "password": "AnotherPassword123!",
        },
    )

    assert response.status_code == 409


def test_login_success(unauthenticated_client):
    unauthenticated_client.post(
        "/api/auth/register",
        json={
            "full_name": "Login User",
            "email": "loginuser@example.com",
            "password": "LoginPassword123!",
        },
    )

    unauthenticated_client.post("/api/auth/logout")

    response = unauthenticated_client.post(
        "/api/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "LoginPassword123!",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "loginuser@example.com"

    me_response = unauthenticated_client.get("/api/auth/me")
    assert me_response.status_code == 200


def test_login_wrong_password(unauthenticated_client):
    unauthenticated_client.post(
        "/api/auth/register",
        json={
            "full_name": "Login User",
            "email": "loginuser@example.com",
            "password": "LoginPassword123!",
        },
    )

    unauthenticated_client.post("/api/auth/logout")

    response = unauthenticated_client.post(
        "/api/auth/login",
        json={
            "email": "loginuser@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_login_unknown_email(unauthenticated_client):
    response = unauthenticated_client.post(
        "/api/auth/login",
        json={
            "email": "unknown@example.com",
            "password": "SomePassword123!",
        },
    )

    assert response.status_code == 401


def test_logout(client):
    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully."

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 401


def test_unauthenticated_access_is_rejected(unauthenticated_client):
    profiles_response = unauthenticated_client.get("/api/profiles/")
    recommendations_response = unauthenticated_client.get(
        "/api/recommendations/"
    )

    assert profiles_response.status_code == 401
    assert recommendations_response.status_code == 401


def test_users_cannot_access_each_others_profiles(client, second_client):
    create_response = client.post(
        "/api/profiles/",
        json={
            "linkedin_profile": "First user's Python and SQL profile",
        },
    )

    assert create_response.status_code == 200
    profile_id = create_response.json()["id"]

    second_user_profiles = second_client.get("/api/profiles/")

    assert second_user_profiles.status_code == 200
    assert second_user_profiles.json() == []

    second_user_profile = second_client.get(
        f"/api/profiles/{profile_id}"
    )

    assert second_user_profile.status_code == 404

    update_response = second_client.put(
        f"/api/profiles/{profile_id}",
        json={
            "linkedin_profile": "Trying to update another user's profile",
        },
    )

    assert update_response.status_code == 404

    delete_response = second_client.delete(
        f"/api/profiles/{profile_id}"
    )

    assert delete_response.status_code == 404

    original_response = client.get(
        f"/api/profiles/{profile_id}"
    )

    assert original_response.status_code == 200
    assert (
        original_response.json()["linkedin_profile"]
        == "First user's Python and SQL profile"
    )


def test_recommendations_use_only_logged_in_users_profile(
    client,
    second_client,
):
    first_profile = client.post(
        "/api/profiles/",
        json={
            "linkedin_profile": "Python, SQL and Data Science",
            "career_goals": "Become a Data Analyst",
            "preferred_roles": "Data Analyst",
        },
    )

    assert first_profile.status_code == 200

    first_profile_id = first_profile.json()["id"]

    # The second user has no profile yet.
    second_response = second_client.get("/api/recommendations/")

    assert second_response.status_code == 404

    # Create a separate profile for the second user.
    second_profile = second_client.post(
        "/api/profiles/",
        json={
            "linkedin_profile": "Java and Backend Development",
            "career_goals": "Become a Backend Developer",
            "preferred_roles": "Backend Developer",
        },
    )

    assert second_profile.status_code == 200

    second_profile_id = second_profile.json()["id"]

    # Each user receives recommendations based on their own profile.
    first_recommendations = client.get("/api/recommendations/")
    second_recommendations = second_client.get("/api/recommendations/")

    assert first_recommendations.status_code == 200
    assert second_recommendations.status_code == 200

    assert first_recommendations.json()["profile_id"] == first_profile_id
    assert second_recommendations.json()["profile_id"] == second_profile_id

    assert first_profile_id != second_profile_id
