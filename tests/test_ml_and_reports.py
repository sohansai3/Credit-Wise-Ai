from pathlib import Path

from app.ml import train
from app.models import Application, Prediction
from app.services.prediction import predict_application
from app.services.reports import generate_pdf_report


def test_training_pipeline_selects_model(tmp_path, monkeypatch):
    original_data = train.synthetic_credit_data
    monkeypatch.setattr(train, "XGBClassifier", None)
    monkeypatch.setattr(train, "synthetic_credit_data", lambda: original_data(n=180, seed=7))
    artifact = train.train_and_save(str(tmp_path / "model.joblib"), str(tmp_path / "metrics.json"))
    assert artifact["model_name"] in {"Logistic Regression", "Random Forest"}
    assert artifact["metrics"]["roc_auc"] > 0.5
    assert (tmp_path / "model.joblib").exists()
    assert (tmp_path / "metrics.json").exists()


def test_prediction_contains_explanations(sample_payload):
    result = predict_application(sample_payload)
    assert result["decision"] in {"Approved", "Rejected"}
    assert result["top_approval_factors"]
    assert result["top_rejection_factors"]
    assert result["explanation"].startswith(result["decision"])


def test_pdf_report_generation(db, sample_payload, tmp_path):
    application = Application(**sample_payload)
    db.add(application)
    db.commit()
    db.refresh(application)
    prediction = Prediction(application_id=application.id, **predict_application(sample_payload))
    db.add(prediction)
    db.commit()
    db.refresh(application)
    path = generate_pdf_report(application, output_dir=str(tmp_path))
    assert Path(path).exists()
    assert Path(path).stat().st_size > 1000
