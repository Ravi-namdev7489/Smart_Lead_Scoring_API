# Smart Lead Scoring API

A backend system that automatically scores incoming business leads as **HOT, WARM, or COLD** using a hybrid AI + rule-based scoring approach.

The system accepts individual leads as well as batches of up to 50 leads, detects duplicate leads, stores scoring/audit information, provides analytics, and handles AI-service failures using a `PENDING_SCORE` state.

---

## 1. Project Overview

Businesses receive leads from multiple sources such as:

* Website
* WhatsApp
* Email
* Instagram
* Referral

The Smart Lead Scoring API automatically analyzes each lead and calculates a final score.

### Scoring Flow

```text
Client
   |
   v
Django REST API
   |
   +-----> MySQL
   |        Lead data
   |        Scoring configuration
   |
   v
FastAPI AI Service
   |
   v
AI / Intent Score
   |
   v
Django Hybrid Scoring
   |
   +-----> SQLite
   |        Score audit
   |
   v
Final Score + Category
```

---

# 2. Technology Stack

## Backend

* Python
* Django
* Django REST Framework
* FastAPI

## Databases

* MySQL — lead and scoring configuration data
* SQLite — score audit data in the current implementation

> **Assignment note:** The original assignment specifies PostgreSQL with JSONB for AI raw output, scoring history, and audit data. This implementation currently uses SQLite for `ScoreAudit` as an implementation deviation.

## API Documentation

* Django REST Framework
* drf-spectacular / Swagger UI
* FastAPI Swagger UI

---

# 3. Project Structure

```text
smart-lead-scoring/
│
├── manage.py
├── .env
├── .gitignore
├── README.md
│
├── project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── db_router.py
│
├── leads/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   ├── tests.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── ai_services.py
│       └── scoring.py
│
├── main.py
│
└── score_audit.sqlite3
```

---

# 4. Features

## Lead Management

Create and manage leads containing:

```text
name
email
phone
message
source
budget
company
```

At least one of `email` or `phone` is required.

---

## AI Lead Scoring

The FastAPI service analyzes the lead and returns:

```json
{
    "score": 70,
    "category": "HOT",
    "reason": "Strong purchase intent, Urgent requirement"
}
```

The Django backend then applies configurable business rules to calculate the final score.

---

# 5. Hybrid Scoring

The final score combines:

```text
AI Score
    +
Business Rules
    =
Final Score
```

Example:

```text
AI score          = 60
High budget       = +15
Referral source   = +10
Repeat lead       = +10
--------------------------------
Final score       = 95
```

The score is capped at:

```text
100
```

### Categories

```text
70 - 100  → HOT
40 - 69   → WARM
0 - 39    → COLD
```

---

# 6. Configurable Scoring Rules

Scoring rules are stored in the `ScoringConfig` model.

Example:

| Factor          | Weight |
| --------------- | -----: |
| high_budget     |     15 |
| referral_source |     10 |
| repeat_lead     |     10 |
| urgent          |     10 |

The weights can be changed through Django Admin without changing application code.

---

# 7. Duplicate Detection

Duplicate leads are detected using existing:

* Email
* Phone

If the same lead is submitted again:

```text
Existing Lead
      |
      v
Update existing record
      |
      v
repeat_lead = true
```

A new Lead database row is not created.

The lead can then be rescored and a new audit entry can be generated.

---

# 8. Batch Processing

The API supports up to **50 leads per batch**.

Endpoint:

```text
POST /api/leads/batch/
```

The Django backend sends the batch to FastAPI using the batch scoring endpoint instead of making a separate AI request for every lead.

FastAPI endpoint:

```text
POST /score/batch
```

---

# 9. Resilience

If the FastAPI service is unavailable, Django does not lose the lead.

The lead is saved with:

```text
status = PENDING_SCORE
```

Example:

```text
Client
  |
  v
Django
  |
  v
FastAPI unavailable
  |
  v
Lead saved
  |
  v
PENDING_SCORE
```

The lead can later be rescored using:

```text
POST /api/leads/{lead_id}/rescore/
```

---

# 10. Analytics

Analytics endpoint:

```text
GET /api/leads/analytics/
```

Example response:

```json
{
    "total_leads": 10,
    "category_breakdown": {
        "HOT": 4,
        "WARM": 3,
        "COLD": 3
    },
    "average_score_per_source": {
        "website": 72.5,
        "whatsapp": 61.2,
        "email": 55.8,
        "instagram": 68.4
    },
    "top_5_hottest_leads": [
        {
            "id": 1,
            "name": "Ravi",
            "email": "ravi@gmail.com",
            "source": "website",
            "score": 92,
            "category": "HOT"
        }
    ]
}
```

---

# 11. API Endpoints

## Django API

### Create Lead

```text
POST /api/leads/
```

Example request:

```json
{
    "name": "Ravi",
    "email": "ravi@gmail.com",
    "phone": "9876543210",
    "message": "I want to purchase your product urgently",
    "source": "website",
    "budget": 150000,
    "company": "ABC Pvt Ltd"
}
```

---

### Batch Leads

```text
POST /api/leads/batch/
```

Example:

```json
{
    "leads": [
        {
            "name": "Ravi",
            "email": "ravi@gmail.com",
            "phone": "9876543210",
            "message": "I want to purchase your product urgently",
            "source": "website",
            "budget": 150000,
            "company": "ABC Pvt Ltd"
        },
        {
            "name": "Amit",
            "email": "amit@gmail.com",
            "phone": "9876543211",
            "message": "Please send product information",
            "source": "whatsapp",
            "budget": 50000,
            "company": "XYZ Ltd"
        }
    ]
}
```

Maximum:

```text
50 leads
```

---

### Analytics

```text
GET /api/leads/analytics/
```

---

### Rescore Lead

```text
POST /api/leads/{lead_id}/rescore/
```

Example:

```text
POST /api/leads/2/rescore/
```

Request body:

```json
{}
```

---

# 12. FastAPI Endpoints

### Single Lead Scoring

```text
POST /score
```

### Batch Scoring

```text
POST /score/batch
```

FastAPI Swagger:

```text
http://127.0.0.1:8001/docs
```

---

# 13. Django Swagger Documentation

Swagger UI:

```text
http://127.0.0.1:8000/doc/
```

Schema:

```text
http://127.0.0.1:8000/schema/
```

Swagger allows API endpoints to be tested directly from the browser.

---

# 14. Database Design

## MySQL

### Lead

Important fields:

```text
id
name
email
phone
message
source
budget
company
category
latest_score
status
repeat_lead
created_at
updated_at
```

### ScoringConfig

```text
id
factor_name
weight
is_active
```

---

## SQLite

### ScoreAudit

```text
id
lead_id
model_name
raw_ai_response
rule_breakdown
final_score
scored_at
```

`raw_ai_response` and `rule_breakdown` use Django `JSONField`.

---

# 15. Environment Variables

Create `.env` in the project root.

Example:

```env
DJANGO_SECRET_KEY=your-secret-key

FASTAPI_URL=http://127.0.0.1:8001

MYSQL_DATABASE=lead_score
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

Do not commit `.env` to GitHub.

---

# 16. Installation

## Clone the project

```bash
git clone <repository-url>
cd smart-lead-scoring
```

---

## Create virtual environment

Windows:

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

---

## Install dependencies

```bash
pip install django
pip install djangorestframework
pip install mysqlclient
pip install fastapi
pip install uvicorn
pip install requests
pip install python-dotenv
pip install drf-spectacular
```

---

# 17. Database Setup

Create the MySQL database:

```sql
CREATE DATABASE lead_score;
```

Configure the credentials in `.env`.

Run Django migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

For the SQLite audit database:

```bash
python manage.py migrate --database=sqlite
```

---

# 18. Create Admin User

```bash
python manage.py createsuperuser
```

Run Django:

```bash
python manage.py runserver
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

Use Django Admin to configure scoring weights.

---

# 19. Run FastAPI

From the directory containing `main.py`:

```bash
uvicorn main:app --reload --port 8001
```

FastAPI:

```text
http://127.0.0.1:8001
```

Swagger:

```text
http://127.0.0.1:8001/docs
```

---

# 20. Testing

Run Django tests:

```bash
python manage.py test leads
```

Run Django system check:

```bash
python manage.py check
```

---

# 21. Example End-to-End Flow

```text
1. Client submits lead
          |
          v
2. Django validates request
          |
          v
3. Check duplicate
          |
          +---- Existing → repeat_lead = true
          |
          v
4. Save Lead in MySQL
          |
          v
5. Send lead to FastAPI
          |
          v
6. AI scoring
          |
          v
7. Apply configurable business rules
          |
          v
8. Calculate final score
          |
          v
9. HOT / WARM / COLD
          |
          v
10. Save audit information
          |
          v
11. Return final response
```

---

# 22. Failure Flow

```text
Django
   |
   v
FastAPI
   |
   X
Unavailable
   |
   v
Lead remains saved
   |
   v
PENDING_SCORE
   |
   v
Rescore API
   |
   v
SCORED
```

---

# 23. Security

The following should not be committed to Git:

```text
.env
database passwords
API keys
secret keys
```

`.gitignore`:

```gitignore
venv/
.env
__pycache__/
*.pyc
score_audit.sqlite3
db.sqlite3
.idea/
.vscode/
```

---

# 24. Assignment Requirement Status

| Requirement                      | Status                                                                          |
| -------------------------------- | ------------------------------------------------------------------------------- |
| REST API                         | Completed                                                                       |
| Single lead scoring              | Completed                                                                       |
| Batch up to 50                   | Completed                                                                       |
| Duplicate detection              | Completed                                                                       |
| Configurable scoring             | Completed                                                                       |
| Analytics                        | Completed                                                                       |
| PENDING_SCORE resilience         | Completed                                                                       |
| Rescore API                      | Completed                                                                       |
| Swagger documentation            | Completed                                                                       |
| Automated tests                  | In progress/completed according to test suite                                   |
| MySQL lead storage               | Completed                                                                       |
| PostgreSQL JSONB audit           | **Not implemented — SQLite currently used**                                     |
| Real external AI/LLM integration | **Requires final integration if the current FastAPI rule-based scorer remains** |
| README                           | Completed                                                                       |

---

# 25. Important Assignment Deviations

The original assignment specifies:

```text
MySQL
   ↓
Lead/master data

PostgreSQL + JSONB
   ↓
AI raw response
Scoring history
Audit data
```

The current implementation uses:

```text
MySQL
   ↓
Lead/master data

SQLite
   ↓
ScoreAudit
```

Therefore, for strict assignment compliance, `ScoreAudit` should ultimately be moved from SQLite to PostgreSQL with JSONB.

The current FastAPI scoring logic is also a local scoring implementation. If strict compliance with the assignment is required, it should be replaced or extended with a real AI/LLM API integration, with its API key stored in environment variables rather than source code.

---

# 26. Future Improvements

Possible improvements include:

* PostgreSQL + JSONB audit storage
* Real LLM integration
* API-key authentication
* Docker Compose
* Celery/background scoring
* Redis queue
* Rate limiting
* Pagination
* More advanced analytics
* Automated API tests
* Production deployment

---

# 27. Author

**Smart Lead Scoring API**

Built using:

```text
Python
Django REST Framework
FastAPI
MySQL
SQLite
REST APIs
```
