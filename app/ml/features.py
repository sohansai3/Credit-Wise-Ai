NUMERIC_FEATURES = [
    "age",
    "years_employed",
    "annual_income",
    "monthly_income",
    "existing_loans",
    "loan_amount",
    "debt_to_income_ratio",
    "dependents",
    "credit_history_length",
    "previous_defaults",
    "credit_utilization",
    "income_to_loan_ratio",
    "disposable_income",
    "default_pressure",
]
CATEGORICAL_FEATURES = ["gender", "marital_status", "education", "employment_type"]
RAW_FEATURES = [
    "age",
    "gender",
    "marital_status",
    "education",
    "employment_type",
    "years_employed",
    "annual_income",
    "monthly_income",
    "existing_loans",
    "loan_amount",
    "debt_to_income_ratio",
    "dependents",
    "credit_history_length",
    "previous_defaults",
    "credit_utilization",
]


def engineer_features(record: dict) -> dict:
    data = dict(record)
    loan = max(float(data.get("loan_amount", 0.0)), 1.0)
    monthly = max(float(data.get("monthly_income", 0.0)), 1.0)
    data["income_to_loan_ratio"] = float(data.get("annual_income", 0.0)) / loan
    data["disposable_income"] = monthly * max(0.0, 1.0 - float(data.get("debt_to_income_ratio", 0.0)))
    data["default_pressure"] = float(data.get("previous_defaults", 0)) * 0.7 + float(data.get("credit_utilization", 0.0)) * 0.3
    return data
