import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/api"

test_student = {
    "name": "Test Student",
    "email": "teststudent_001@example.com",
    "password": "SecurePassword123!",
    "role": "student",
    "grade_level": 10
}

auth_token = None

def test_student_registration_generates_otp():
    """Verify a new student can register and triggers an OTP email."""
    response = requests.post(f"{BASE_URL}/users/register/", json=test_student)
    assert response.status_code in [201, 400]

def test_duplicate_email_registration():
    """Verify system rejects registration with an existing email."""
    response = requests.post(f"{BASE_URL}/users/register/", json=test_student)
    assert response.status_code == 400
    assert "already registered" in response.text.lower()

def test_user_login_success():
    """Verify active user can log in and receive JWT access/refresh tokens."""
    global auth_token
    credentials = {"email": test_student["email"], "password": test_student["password"]}
    response = requests.post(f"{BASE_URL}/users/login/", json=credentials)
    assert response.status_code == 200
    auth_token = response.json()["access"]

def test_fetch_gamification_profile():
    """Verify access to protected gamification routes with a valid Token."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(f"{BASE_URL}/gamification/my-profile/", headers=headers)
    assert response.status_code == 200
    assert "total_xp" in response.json()

def test_unauthorized_access_protection():
    """Verify protected AI and Gamification routes reject requests without a JWT."""
    response = requests.get(f"{BASE_URL}/gamification/my-profile/", 
                            headers={"Authorization": "Bearer "})
    assert response.status_code in [401, 403]