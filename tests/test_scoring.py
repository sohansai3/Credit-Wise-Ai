from app.services.scoring import compute_scores, risk_category


def test_risk_category_boundaries():
    assert risk_category(500) == "High Risk"
    assert risk_category(650) == "Medium Risk"
    assert risk_category(651) == "Low Risk"


def test_compute_scores_range(sample_payload):
    result = compute_scores({**sample_payload, "income_to_loan_ratio": 4, "disposable_income": 5000, "default_pressure": 0}, 0.8)
    assert 300 <= result["credit_score"] <= 850
    assert result["recommended_credit_limit"] >= 500
    assert 0 <= result["final_applicant_score"] <= 100
