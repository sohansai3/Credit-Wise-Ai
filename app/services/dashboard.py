from collections import Counter, defaultdict

from sqlalchemy.orm import Session

from app.models import Application, Prediction


def dashboard_summary(db: Session) -> dict:
    total = db.query(Application).count()
    approved = db.query(Prediction).filter(Prediction.decision == "Approved").count()
    rejected = db.query(Prediction).filter(Prediction.decision == "Rejected").count()
    predictions = db.query(Prediction).all()
    avg_credit = round(sum(p.credit_score for p in predictions) / len(predictions), 2) if predictions else 0
    risk_counts = Counter(p.risk_level for p in predictions)
    score_buckets = {"300-500": 0, "501-650": 0, "651-850": 0}
    for p in predictions:
        if p.credit_score <= 500:
            score_buckets["300-500"] += 1
        elif p.credit_score <= 650:
            score_buckets["501-650"] += 1
        else:
            score_buckets["651-850"] += 1
    monthly = defaultdict(lambda: {"approved": 0, "rejected": 0})
    for app in db.query(Application).join(Prediction).all():
        key = app.created_at.strftime("%Y-%m")
        if app.prediction.decision == "Approved":
            monthly[key]["approved"] += 1
        else:
            monthly[key]["rejected"] += 1
    return {
        "total_applications": total,
        "approved_applications": approved,
        "rejected_applications": rejected,
        "average_credit_score": avg_credit,
        "approval_rate": round((approved / total) * 100, 2) if total else 0,
        "risk_distribution": dict(risk_counts),
        "credit_score_distribution": score_buckets,
        "monthly_trends": dict(sorted(monthly.items())),
    }
