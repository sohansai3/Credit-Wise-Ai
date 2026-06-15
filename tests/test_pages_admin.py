def test_html_register_login_dashboard_and_logout(client):
    register = client.post(
        "/register-view",
        data={"full_name": "Admin User", "email": "adminpage@example.com", "password": "password123", "role": "admin"},
        follow_redirects=False,
    )
    assert register.status_code == 303
    dashboard = client.get("/dashboard-view")
    assert dashboard.status_code == 200
    assert "Risk Dashboard" in dashboard.text
    logout = client.get("/logout-view", follow_redirects=False)
    assert logout.status_code == 303
    failed = client.post("/login-view", data={"email": "adminpage@example.com", "password": "bad"})
    assert failed.status_code == 401
    login = client.post("/login-view", data={"email": "adminpage@example.com", "password": "password123"}, follow_redirects=False)
    assert login.status_code == 303


def test_admin_user_toggle(auth_client):
    created = auth_client.post("/register", json={"email": "other@example.com", "full_name": "Other User", "password": "password123", "role": "loan_officer"})
    assert created.status_code == 200
    users = auth_client.get("/admin/users")
    assert users.status_code == 200
    toggle = auth_client.post(f"/admin/users/{created.json()['id']}/toggle", follow_redirects=False)
    assert toggle.status_code == 303


def test_report_endpoint_and_missing_delete(auth_client, sample_payload):
    created = auth_client.post("/predict", json=sample_payload).json()
    report = auth_client.post(f"/reports/{created['id']}")
    assert report.status_code == 200
    reports = auth_client.get("/reports")
    assert reports.status_code == 200
    missing = auth_client.delete("/application/999999")
    assert missing.status_code == 404
