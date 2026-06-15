from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.core.config import get_settings
from app.ml.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES, RAW_FEATURES, engineer_features

try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None


def synthetic_credit_data(n: int = 2500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "age": rng.integers(18, 76, n),
            "gender": rng.choice(["Female", "Male", "Non-binary"], n, p=[0.47, 0.49, 0.04]),
            "marital_status": rng.choice(["Single", "Married", "Divorced", "Widowed"], n, p=[0.38, 0.47, 0.12, 0.03]),
            "education": rng.choice(["High School", "Bachelor", "Master", "Doctorate"], n, p=[0.28, 0.45, 0.22, 0.05]),
            "employment_type": rng.choice(["Salaried", "Self-employed", "Contract", "Unemployed", "Retired"], n, p=[0.54, 0.18, 0.13, 0.08, 0.07]),
            "years_employed": np.clip(rng.gamma(3.0, 2.2, n), 0, 45),
            "annual_income": np.clip(rng.lognormal(11.0, 0.55, n), 12000, 300000),
            "existing_loans": rng.poisson(1.4, n),
            "loan_amount": np.clip(rng.lognormal(9.4, 0.75, n), 500, 120000),
            "debt_to_income_ratio": np.clip(rng.beta(2.0, 4.5, n), 0.01, 1.2),
            "dependents": rng.integers(0, 6, n),
            "credit_history_length": np.clip(rng.gamma(2.5, 3.0, n), 0, 45),
            "previous_defaults": rng.poisson(0.25, n),
            "credit_utilization": np.clip(rng.beta(2.2, 3.6, n), 0.01, 1.2),
        }
    )
    df["monthly_income"] = df["annual_income"] / 12
    signal = (
        1.15 * (df["annual_income"] > 52000).astype(float)
        + 1.00 * (df["debt_to_income_ratio"] < 0.38).astype(float)
        + 0.75 * (df["credit_history_length"] > 4).astype(float)
        + 0.65 * (df["years_employed"] > 2).astype(float)
        - 1.45 * (df["previous_defaults"] > 0).astype(float)
        - 1.10 * (df["credit_utilization"] > 0.65).astype(float)
        - 0.55 * (df["employment_type"] == "Unemployed").astype(float)
        - 0.30 * (df["existing_loans"] > 3).astype(float)
        + rng.normal(0, 0.55, n)
    )
    probability = 1 / (1 + np.exp(-signal))
    df["approved"] = (probability > 0.56).astype(int)
    return df


def build_preprocessor() -> ColumnTransformer:
    numeric_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    categorical_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))])
    return ColumnTransformer([("num", numeric_pipe, NUMERIC_FEATURES), ("cat", categorical_pipe, CATEGORICAL_FEATURES)])


def prepare_frame(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([engineer_features(row) for row in df[RAW_FEATURES].to_dict(orient="records")])


def train_and_save(model_path: str | None = None, metrics_path: str | None = None) -> dict:
    settings = get_settings()
    model_path = model_path or settings.model_path
    metrics_path = metrics_path or settings.model_metrics_path
    df = synthetic_credit_data()
    x = prepare_frame(df)
    y = df["approved"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.22, random_state=42, stratify=y)
    estimators = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=180, max_depth=10, random_state=42, class_weight="balanced"),
    }
    if XGBClassifier is not None:
        estimators["XGBoost"] = XGBClassifier(n_estimators=160, max_depth=4, learning_rate=0.08, subsample=0.9, colsample_bytree=0.9, eval_metric="logloss", random_state=42)
    leaderboard = []
    best = None
    for name, estimator in estimators.items():
        pipeline = Pipeline([("preprocessor", build_preprocessor()), ("model", estimator)])
        try:
            pipeline.fit(x_train, y_train)
            pred = pipeline.predict(x_test)
            prob = pipeline.predict_proba(x_test)[:, 1]
        except Exception as exc:
            leaderboard.append({"model": name, "status": "failed", "error": str(exc)})
            continue
        metrics = {
            "accuracy": round(float(accuracy_score(y_test, pred)), 4),
            "precision": round(float(precision_score(y_test, pred)), 4),
            "recall": round(float(recall_score(y_test, pred)), 4),
            "f1": round(float(f1_score(y_test, pred)), 4),
            "roc_auc": round(float(roc_auc_score(y_test, prob)), 4),
        }
        leaderboard.append({"model": name, **metrics})
        if best is None or metrics["roc_auc"] > best["metrics"]["roc_auc"]:
            best = {"name": name, "pipeline": pipeline, "metrics": metrics}
    if best is None:
        raise RuntimeError("No candidate model could be trained successfully")
    artifact = {"model_name": best["name"], "pipeline": best["pipeline"], "metrics": best["metrics"], "leaderboard": leaderboard}
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)
    Path(metrics_path).parent.mkdir(parents=True, exist_ok=True)
    Path(metrics_path).write_text(json.dumps({"selected_model": best["name"], "leaderboard": leaderboard}, indent=2), encoding="utf-8")
    return artifact


if __name__ == "__main__":
    trained = train_and_save()
    print(json.dumps({"selected_model": trained["model_name"], "metrics": trained["metrics"]}, indent=2))
