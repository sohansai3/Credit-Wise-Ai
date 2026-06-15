# CreditWise AI

## Credit Card Approval & Risk Assessment Platform

CreditWise AI is a full-stack credit card approval predictor for lending teams. It helps bank officers evaluate applicants, predict approval decisions, calculate credit scores, classify risk, recommend credit limits, explain model decisions with SHAP, and generate PDF decision reports.

The project is built with FastAPI, SQLAlchemy, Scikit-Learn, Pandas, NumPy, SHAP, Bootstrap 5, Jinja2, and ReportLab. It supports SQLite for local development and PostgreSQL for production deployments.

## Features

- User registration, login, logout, password hashing, signed sessions, and role-based access
- Roles: Admin and Loan Officer
- Credit card approval prediction: Approved or Rejected
- Approval probability and confidence score
- Applicant credit score from 300 to 850
- Risk categories:
  - 300-500: High Risk
  - 501-650: Medium Risk
  - 651-850: Low Risk
- SHAP explainable AI with top approval and rejection factors
- Human-readable decision explanation
- Recommended credit limit based on income, debt, risk level, and credit score
- Financial stability, repayment capacity, risk, and final applicant scores
- Dashboard with application totals, approval rate, average credit score, risk distribution, monthly trends, and charts
- Application history with search, filter, sort, CSV export, and PDF download
- Admin panel for user management and application deletion
- PDF report generation with applicant details, prediction, score, risk level, probability, credit limit, and explanation
- Complete REST API
- Automated model training and model selection
- Docker, Docker Compose, and GitHub Actions CI/CD
- Pytest suite with minimum 80% coverage enforcement

## Tech Stack

Backend:

- Python 3.12
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite fallback
- PostgreSQL support

Machine Learning:

- Scikit-Learn
- Pandas
- NumPy
- XGBoost
- SHAP
- Joblib

Frontend:

- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Jinja2 templates
- Chart.js

Reports:

- ReportLab PDF generation

Testing and DevOps:

- Pytest
- pytest-cov
- Docker
- Docker Compose
- GitHub Actions

## Project Structure

```text
.
├── app/
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   └── session.py
│   ├── ml/
│   │   ├── features.py
│   │   └── train.py
│   ├── routes/
│   │   ├── admin.py
│   │   ├── api.py
│   │   └── pages.py
│   ├── services/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── prediction.py
│   │   ├── reports.py
│   │   └── scoring.py
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── tests/
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── main.py
├── pyproject.toml
├── requirements.txt
└── .env.example
```

## Requirements

- Python 3.12
- pip
- Optional: Docker Desktop
- Optional: PostgreSQL for production-like deployment

Important: use Python 3.12. Newer unreleased or bleeding-edge Python versions may not have prebuilt wheels for scientific packages such as Pandas, NumPy, Scikit-Learn, XGBoost, or SHAP.

Check your Python version:

```powershell
python --version
```

On Windows, create the environment with Python 3.12:

```powershell
py -3.12 -m venv .venv
```

## Local Setup

Clone the repository:

```bash
git clone https://github.com/your-username/creditwise-ai.git
cd creditwise-ai
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment example:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Run the app:

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

If port 8000 is blocked or already in use:

```bash
uvicorn main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

## First Use

1. Open the application in your browser.
2. Register a user.
3. Choose Admin for the first administrative account, or Loan Officer for normal usage.
4. Create a new credit card assessment.
5. Review the decision, credit score, risk level, recommended credit limit, and explanation.
6. Download the PDF report from the result or application history page.

## Machine Learning Pipeline

The app trains a model automatically on first prediction if no saved artifact exists at:

```text
app/ml/artifacts/model.joblib
```

The training pipeline:

- Generates a realistic synthetic credit-risk dataset
- Performs feature engineering
- Handles missing values
- Encodes categorical variables
- Scales numerical variables
- Trains and compares:
  - Logistic Regression
  - Random Forest
  - XGBoost
- Selects the best successful model by ROC AUC
- Saves the model artifact with Joblib
- Saves model metrics and leaderboard data

Manual training:

```bash
python -m app.ml.train
```

Model outputs include:

- Accuracy
- Precision
- Recall
- F1 score
- ROC AUC

Note: if XGBoost is unavailable or incompatible in a local runtime, the training pipeline records the failed candidate and still selects the best successful model.

## Prediction Inputs

The application evaluates:

- Applicant name
- Age
- Gender
- Marital status
- Education
- Employment type
- Years of employment
- Annual income
- Monthly income
- Existing loans
- Loan amount
- Debt-to-income ratio
- Number of dependents
- Credit history length
- Previous defaults
- Current credit utilization

## Prediction Outputs

Each assessment returns:

- Decision: Approved or Rejected
- Approval probability
- Confidence score
- Credit score
- Risk level
- Recommended credit limit
- Financial stability score
- Repayment capacity score
- Risk score
- Final applicant score
- Top approval factors
- Top rejection factors
- Feature importance data
- Human-readable explanation
- Model name
- Model metrics

## REST API

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Main endpoints:

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/register` | Register a user |
| POST | `/login` | Login and create a session |
| POST | `/logout` | Clear the session |
| POST | `/predict` | Create an application and prediction |
| GET | `/applications` | List applications with search/filter/sort |
| GET | `/applications/export` | Export applications as CSV |
| GET | `/dashboard` | Get dashboard metrics |
| GET | `/reports` | List generated reports |
| POST | `/reports/{application_id}` | Generate a PDF report |
| DELETE | `/application/{application_id}` | Delete an application, admin only |

Example prediction request:

```json
{
  "applicant_name": "Ava Patel",
  "age": 35,
  "gender": "Female",
  "marital_status": "Married",
  "education": "Master",
  "employment_type": "Salaried",
  "years_employed": 7,
  "annual_income": 98000,
  "monthly_income": 8166.67,
  "existing_loans": 1,
  "loan_amount": 15000,
  "debt_to_income_ratio": 0.24,
  "dependents": 1,
  "credit_history_length": 8,
  "previous_defaults": 0,
  "credit_utilization": 0.28
}
```

## Database Schema

The app creates the database tables automatically at startup.

Tables:

- `users`
- `applications`
- `predictions`
- `reports`
- `audit_logs`

Default local database:

```text
sqlite:///./creditwise.db
```

PostgreSQL example:

```env
DATABASE_URL=postgresql+psycopg://creditwise:creditwise@localhost:5432/creditwise
```

## Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

This starts:

- FastAPI web app on port 8000
- PostgreSQL database on port 5432

Open:

```text
http://127.0.0.1:8000
```

Stop containers:

```bash
docker compose down
```

Remove database volume:

```bash
docker compose down -v
```

## Testing

Run tests:

```bash
pytest
```

Run tests with explicit coverage output:

```bash
pytest --cov=app --cov-report=term-missing
```

The project enforces at least 80% coverage through `pyproject.toml`.

Current verified test result:

```text
12 passed
Total coverage: 89.84%
```

## GitHub Actions

CI is configured in:

```text
.github/workflows/ci.yml
```

The workflow:

- Checks out the repository
- Sets up Python 3.12
- Installs dependencies
- Runs pytest with coverage
- Fails if coverage drops below 80%

## Environment Variables

Create `.env` from `.env.example`.

| Variable | Description | Default |
| --- | --- | --- |
| `APP_NAME` | Application display name | `CreditWise AI` |
| `SECRET_KEY` | Session signing secret | `change-me-in-production` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./creditwise.db` |
| `POSTGRES_DATABASE_URL` | Example PostgreSQL URL | `postgresql+psycopg://...` |
| `ENVIRONMENT` | Runtime environment | `development` |

For production, set a strong `SECRET_KEY` and use PostgreSQL.

## Troubleshooting

### Pandas tries to build from source on Windows

Use Python 3.12. If your virtual environment uses Python 3.14 or another unsupported version, pip may try to compile Pandas and fail with Visual Studio or Meson errors.

Fix:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Port 8000 is blocked or already in use

Run on another port:

```bash
uvicorn main:app --reload --port 8001
```

### Free port 8000 on Windows

```powershell
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### Uvicorn import string error

Use:

```bash
uvicorn main:app --reload
```

Do not use:

```bash
uvicorn main --reload
```

Current Uvicorn versions require the `<module>:<attribute>` format.

## Security Notes

- Passwords are hashed with bcrypt through Passlib.
- Sessions are signed using Starlette session middleware.
- Admin-only actions are protected with role checks.
- Production deployments should set a strong `SECRET_KEY`.
- Production deployments should use HTTPS and PostgreSQL.
- Generated model artifacts, local databases, reports, and `.env` files are ignored by Git.

## License

This project is provided for educational, portfolio, and internal prototype use. Add a license file before publishing if you intend to distribute it publicly.
