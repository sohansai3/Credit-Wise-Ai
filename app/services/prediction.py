from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from app.core.config import get_settings
from app.ml.features import engineer_features
from app.ml.train import train_and_save
from app.services.scoring import compute_scores

POSITIVE_LABELS = {
    "annual_income": "Strong annual income",
    "monthly_income": "Healthy monthly income",
    "years_employed": "Stable employment",
    "credit_history_length": "Established credit history",
    "debt_to_income_ratio": "Low debt-to-income ratio",
    "credit_utilization": "Low credit utilization",
    "previous_defaults": "Clean repayment history",
    "disposable_income": "Strong disposable income",
}
NEGATIVE_LABELS = {
    "previous_defaults": "Previous defaults increase risk",
    "debt_to_income_ratio": "High debt burden",
    "credit_utilization": "High credit utilization",
    "existing_loans": "Multiple existing loans",
    "loan_amount": "Large requested loan amount",
    "employment_type": "Employment profile adds risk",
    "credit_history_length": "Limited credit history",
}


def load_artifact() -> dict:
    settings = get_settings()
    if not Path(settings.model_path).exists():
        return train_and_save()
    return joblib.load(settings.model_path)


def _heuristic_contributions(data: dict) -> list[dict]:
    factors = [
        ("annual_income", (data["annual_income"] - 50000) / 80000),
        ("years_employed", (data["years_employed"] - 2) / 8),
        ("credit_history_length", (data["credit_history_length"] - 3) / 10),
        ("debt_to_income_ratio", (0.38 - data["debt_to_income_ratio"]) * 2.2),
        ("credit_utilization", (0.55 - data["credit_utilization"]) * 1.8),
        ("previous_defaults", -0.85 * data["previous_defaults"]),
        ("existing_loans", -0.12 * data["existing_loans"]),
        ("disposable_income", (data["disposable_income"] - 2500) / 6000),
    ]
    return [{"feature": k, "impact": round(float(v), 4)} for k, v in factors]


def _shap_or_importance(artifact: dict, frame: pd.DataFrame, engineered: dict) -> list[dict]:
    pipeline = artifact["pipeline"]
    preprocessor = pipeline.named_steps["preprocessor"]
    model = pipeline.named_steps["model"]
    try:
        import shap

        transformed = preprocessor.transform(frame)
        if hasattr(transformed, "toarray"):
            transformed = transformed.toarray()
        names = list(preprocessor.get_feature_names_out())
        explainer = shap.Explainer(model, transformed)
        values = explainer(transformed).values
        if values.ndim == 3:
            values = values[:, :, 1]
        ranked = sorted(zip(names, values[0]), key=lambda x: abs(float(x[1])), reverse=True)[:10]
        return [{"feature": name.replace("num__", "").replace("cat__", ""), "impact": round(float(impact), 4)} for name, impact in ranked]
    except Exception:
        return sorted(_heuristic_contributions(engineered), key=lambda x: abs(x["impact"]), reverse=True)[:10]


def human_explanation(decision: str, positives: list[dict], negatives: list[dict]) -> str:
    if decision == "Approved":
        reasons = ", ".join(item["label"] for item in positives[:3]) or "the application has an acceptable risk profile"
        return f"Approved because {reasons}."
    reasons = ", ".join(item["label"] for item in negatives[:3]) or "the application exceeds the bank's risk tolerance"
    return f"Rejected because {reasons}."


def predict_application(payload: dict) -> dict:
    artifact = load_artifact()
    engineered = engineer_features(payload)
    frame = pd.DataFrame([engineered])
    probability = float(artifact["pipeline"].predict_proba(frame)[0][1])
    decision = "Approved" if probability >= 0.5 else "Rejected"
    scores = compute_scores(engineered, probability)
    importance = _shap_or_importance(artifact, frame, engineered)
    positives = []
    negatives = []
    for item in importance:
        key = item["feature"].split("_")[-1] if item["feature"].startswith("employment_type") else item["feature"]
        if item["impact"] >= 0:
            positives.append({"feature": item["feature"], "impact": item["impact"], "label": POSITIVE_LABELS.get(key, item["feature"].replace("_", " ").title())})
        else:
            negatives.append({"feature": item["feature"], "impact": item["impact"], "label": NEGATIVE_LABELS.get(key, item["feature"].replace("_", " ").title())})
    heuristic = _heuristic_contributions(engineered)
    positives = positives or [{"feature": x["feature"], "impact": x["impact"], "label": POSITIVE_LABELS.get(x["feature"], x["feature"].replace("_", " ").title())} for x in heuristic if x["impact"] > 0]
    negatives = negatives or [{"feature": x["feature"], "impact": x["impact"], "label": NEGATIVE_LABELS.get(x["feature"], x["feature"].replace("_", " ").title())} for x in heuristic if x["impact"] < 0]
    return {
        "decision": decision,
        "approval_probability": round(probability, 4),
        "confidence_score": round(max(probability, 1 - probability), 4),
        **scores,
        "top_approval_factors": positives[:5],
        "top_rejection_factors": negatives[:5],
        "feature_importance": importance,
        "explanation": human_explanation(decision, positives, negatives),
        "model_name": artifact["model_name"],
        "metrics": artifact["metrics"],
    }
