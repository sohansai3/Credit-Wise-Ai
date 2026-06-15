def test_register_login_predict_dashboard(auth_client, sample_payload):
    response = auth_client.post("/predict", json=sample_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"]["decision"] in {"Approved", "Rejected"}
    assert 300 <= data["prediction"]["credit_score"] <= 850
    dash = auth_client.get("/dashboard")
    assert dash.status_code == 200
    assert dash.json()["total_applications"] == 1


def test_applications_filter_and_export(auth_client, sample_payload):
    auth_client.post("/predict", json=sample_payload)
    listing = auth_client.get("/applications?search=Ava")
    assert listing.status_code == 200
    assert len(listing.json()) == 1
    export = auth_client.get("/applications/export")
    assert export.status_code == 200
    assert "creditwise_applications.csv" in export.headers["content-disposition"]


def test_admin_delete(auth_client, sample_payload):
    created = auth_client.post("/predict", json=sample_payload).json()
    response = auth_client.delete(f"/application/{created['id']}")
    assert response.status_code == 200
    assert auth_client.get("/applications").json() == []
