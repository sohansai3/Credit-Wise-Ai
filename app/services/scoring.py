def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def risk_category(credit_score: int) -> str:
    if credit_score <= 500:
        return "High Risk"
    if credit_score <= 650:
        return "Medium Risk"
    return "Low Risk"


def compute_scores(data: dict, approval_probability: float) -> dict:
    income_score = clamp(data["annual_income"] / 150000 * 100, 0, 100)
    employment_score = clamp(data["years_employed"] / 10 * 100, 0, 100)
    history_score = clamp(data["credit_history_length"] / 15 * 100, 0, 100)
    debt_score = clamp((1 - data["debt_to_income_ratio"]) * 100, 0, 100)
    utilization_score = clamp((1 - data["credit_utilization"]) * 100, 0, 100)
    default_score = clamp(100 - data["previous_defaults"] * 35, 0, 100)
    financial_stability = round(0.45 * income_score + 0.35 * employment_score + 0.20 * history_score, 2)
    repayment_capacity = round(0.55 * debt_score + 0.30 * utilization_score + 0.15 * income_score, 2)
    risk_score = round(0.55 * default_score + 0.25 * utilization_score + 0.20 * debt_score, 2)
    final_score = round(0.35 * financial_stability + 0.35 * repayment_capacity + 0.30 * risk_score, 2)
    credit_score = int(round(clamp(300 + final_score * 5.5, 300, 850)))
    risk = risk_category(credit_score)
    risk_multiplier = {"Low Risk": 0.32, "Medium Risk": 0.18, "High Risk": 0.07}[risk]
    debt_penalty = max(0.0, 1.0 - data["debt_to_income_ratio"] * 0.65 - data["existing_loans"] * 0.03)
    recommended_limit = round(max(500.0, data["annual_income"] * risk_multiplier * debt_penalty * approval_probability), 2)
    return {
        "financial_stability_score": financial_stability,
        "repayment_capacity_score": repayment_capacity,
        "risk_score": risk_score,
        "final_applicant_score": final_score,
        "credit_score": credit_score,
        "risk_level": risk,
        "recommended_credit_limit": recommended_limit,
    }
