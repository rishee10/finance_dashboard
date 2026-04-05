# FinanceOS — Finance Dashboard Backend

A production-ready, role-based financial records management system built with **Django** and **Django REST Framework**. Features JWT authentication, role-based access control, soft deletes, aggregated analytics, and a complete dark-themed frontend.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Role System](#role-system)
- [API Endpoints](#api-endpoints)
- [Local Setup](#local-setup)
- [Frontend Pages](#frontend-pages)
- [Deployment on Render](#deployment-on-render)
- [Design Decisions](#design-decisions)
- [Assumptions & Tradeoffs](#assumptions--tradeoffs)

---

## Project Overview

FinanceOS is a multi-user financial dashboard system where users have different levels of access based on their role. The system supports creating and managing financial records (income/expenses), viewing dashboard analytics, and managing users — all protected by JWT-based authentication and role-based permission classes.

**Key features:**

- JWT authentication (login, register, token refresh)
- Three-tier role system: Viewer, Analyst, Admin
- Full CRUD on financial records with soft delete
- Dashboard analytics: totals, category breakdown, monthly/weekly trends
- Filter records by type, category, date range, and keyword search
- Pagination on all list endpoints
- Custom permission classes enforced at the view level
- Complete dark-themed frontend served directly from Django

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Framework | Django 4.2 |
| API | Django REST Framework 3.14 |
| Authentication | djangorestframework-simplejwt 5.3 |
| Filtering | django-filter 23.5 |
| CORS | django-cors-headers 4.3 |
| Database | SQLite (development) |
| Config | django-environ |
| Frontend | Vanilla HTML/CSS/JS (served by Django) |
| Charts | Chart.js 4.4 (CDN) |
| Fonts | Syne + DM Sans + DM Mono (Google Fonts CDN) |

---

## Project Structure

```
finance_dashboard/               ← project root
│
├── manage.py
├── requirements.txt
├── .env                         ← secret keys (not in GitHub)
├── .gitignore
├── build.sh                     ← Render build script
├── render.yaml                  ← Render deployment config
│
├── finance_dashboard/           ← Django project config
│   ├── __init__.py
│   ├── settings.py              ← all settings, JWT, CORS, DRF config
│   ├── urls.py                  ← all routes (API + frontend pages)
│   └── wsgi.py
│
├── api/                         ← main Django app
│   ├── models.py                ← User (with role) + FinancialRecord
│   ├── serializers.py           ← input validation & output shaping
│   ├── permissions.py           ← IsAdminRole, IsAnalystOrAbove, IsViewerOrAbove
│   ├── filters.py               ← FinancialRecordFilter (date, type, category, amount)
│   ├── admin.py                 ← Django admin registration
│   ├── tests.py                 ← auth + record + dashboard tests
│   ├── urls.py                  ← API URL patterns
│   └── views/
│       ├── __init__.py
│       ├── auth_views.py        ← RegisterView, LoginView, MeView
│       ├── user_views.py        ← UserListView, UserDetailView (admin only)
│       ├── record_views.py      ← RecordListCreateView, RecordDetailView
│       └── dashboard_views.py  ← DashboardSummaryView, MonthlyTrendView, WeeklyTrendView
│
├── templates/                   ← HTML pages served by Django
│   ├── login.html
│   └── pages/
│       ├── dashboard.html
│       ├── records.html
│       ├── analytics.html
│       ├── users.html
│       └── profile.html
│
└── static/                      ← shared CSS and JS
    ├── css/
    │   └── base.css             ← design tokens, components, layout
    └── js/
        └── api.js               ← API client, auth helpers, sidebar builder
```

---

## Role System

The system has three roles with increasing levels of access:

| Permission | Viewer | Analyst | Admin |
|-----------|:------:|:-------:|:-----:|
| View financial records | ✅ | ✅ | ✅ |
| Search and filter records | ✅ | ✅ | ✅ |
| Dashboard summary (totals, balance) | ✅ | ✅ | ✅ |
| Analytics charts and trends | ❌ | ✅ | ✅ |
| Monthly and weekly trend data | ❌ | ✅ | ✅ |
| Create financial records | ❌ | ❌ | ✅ |
| Edit financial records | ❌ | ❌ | ✅ |
| Delete records (soft delete) | ❌ | ❌ | ✅ |
| List and manage users | ❌ | ❌ | ✅ |
| Change user roles and status | ❌ | ❌ | ✅ |

Roles are enforced using custom DRF permission classes in `api/permissions.py`:

- `IsAdminRole` — only users with `role = 'admin'`
- `IsAnalystOrAbove` — users with `role = 'analyst'` or `role = 'admin'`
- `IsViewerOrAbove` — any authenticated active user

---

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/v1/`

### Authentication

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register/` | Public | Create a new account |
| POST | `/auth/login/` | Public | Get JWT access + refresh tokens |
| GET | `/auth/me/` | Any auth | Get current user info |
| POST | `/auth/token/refresh/` | Public | Refresh an expired access token |

**Register request body:**
```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "StrongPass123!",
  "password2": "StrongPass123!",
  "role": "viewer"
}
```

**Login request body:**
```json
{
  "username": "john",
  "password": "StrongPass123!"
}
```

**Login response:**
```json
{
  "user": { "id": 1, "username": "john", "role": "viewer" },
  "tokens": {
    "access": "eyJ...",
    "refresh": "eyJ..."
  }
}
```

All protected endpoints require: `Authorization: Bearer <access_token>`

---

### Users (Admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/` | List all users |
| GET | `/users/{id}/` | Get a specific user |
| PATCH | `/users/{id}/` | Update role or active status |

---

### Financial Records

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/records/` | Viewer+ | List all records (paginated, filterable) |
| POST | `/records/` | Admin | Create a new record |
| GET | `/records/{id}/` | Viewer+ | Get a specific record |
| PATCH | `/records/{id}/` | Admin | Update a record |
| DELETE | `/records/{id}/` | Admin | Soft-delete a record |

**Record fields:**
```json
{
  "amount": "1500.00",
  "entry_type": "income",
  "category": "salary",
  "date": "2025-01-15",
  "description": "January salary"
}
```

**Entry types:** `income`, `expense`

**Categories:** `salary`, `investment`, `food`, `transport`, `utilities`, `healthcare`, `education`, `other`

**Filtering and search:**
```
GET /records/?entry_type=income
GET /records/?category=salary
GET /records/?date_from=2025-01-01&date_to=2025-12-31
GET /records/?amount_min=500&amount_max=5000
GET /records/?search=rent
GET /records/?ordering=-amount
GET /records/?page=2&page_size=10
```

---

### Dashboard (Analyst + Admin)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/summary/` | Totals, net balance, category breakdown, recent 5 |
| GET | `/dashboard/monthly/?months=6` | Monthly income vs expense trend |
| GET | `/dashboard/weekly/?weeks=8` | Weekly income vs expense trend |

**Summary response:**
```json
{
  "total_income": "45000.00",
  "total_expense": "28500.00",
  "net_balance": "16500.00",
  "category_totals": [...],
  "recent_activity": [...]
}
```

---

## Local Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/yourusername/finance-dashboard.git
cd finance-dashboard

python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` file

Create a file named `.env` in the project root (same folder as `manage.py`):

```env
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

To generate a strong secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Run migrations

```bash
python manage.py makemigrations api
python manage.py migrate
```

### 5. Create test users

```bash
python manage.py shell
```

```python
from api.models import User

# Admin — full access
User.objects.create_superuser(
    username='admin',
    password='admin123',
    email='admin@test.com',
    role='admin'
)

# Analyst — view + analytics
u = User(username='analyst', email='analyst@test.com', role='analyst')
u.set_password('analyst123')
u.save()

# Viewer — read only
u = User(username='viewer', email='viewer@test.com', role='viewer')
u.set_password('viewer123')
u.save()

exit()
```

### 6. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 7. Run the server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

### 8. Run tests

```bash
python manage.py test api --verbosity=2
```

---

## Frontend Pages

The frontend is a multi-page application served directly by Django. No separate server or build step needed.

| URL | Page | Who can see it |
|-----|------|---------------|
| `http://127.0.0.1:8000/` | Login / Register | Everyone |
| `http://127.0.0.1:8000/dashboard/` | Dashboard with stats and charts | All logged-in users |
| `http://127.0.0.1:8000/records/` | Records table with filters | All logged-in users |
| `http://127.0.0.1:8000/analytics/` | Charts and trend analysis | Analyst + Admin |
| `http://127.0.0.1:8000/users/` | User management | Admin only |
| `http://127.0.0.1:8000/profile/` | My account and permissions | All logged-in users |
| `http://127.0.0.1:8000/admin/` | Django admin panel | Superuser |

**Frontend files:**

| File | Purpose |
|------|---------|
| `templates/login.html` | Sign in and register page |
| `templates/pages/dashboard.html` | Stats cards, monthly bar chart, category donut |
| `templates/pages/records.html` | Paginated table, filters, add/edit/delete modals |
| `templates/pages/analytics.html` | Weekly trends, category breakdowns, net balance |
| `templates/pages/users.html` | User cards with role editing |
| `templates/pages/profile.html` | Account info and role permission matrix |
| `static/css/base.css` | Shared design tokens and all component styles |
| `static/js/api.js` | API client, auth helpers, sidebar builder, toasts |

---

## Deployment on Render

### Files needed for Render

The following files are already included in the project:

**`requirements.txt`** — all Python dependencies including `gunicorn` and `whitenoise`

**`build.sh`** — runs on every deploy:
```bash
#!/bin/bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

**`render.yaml`** — tells Render how to run the app:
```yaml
services:
  - type: web
    name: financeos
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn finance_dashboard.wsgi:application"
```

### Step-by-step Render deployment

**Step 1 — Push to GitHub**

Make sure your `.gitignore` excludes secrets (see below). Then:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/finance-dashboard.git
git push -u origin main
```

**Step 2 — Create a Render account**

Go to [render.com](https://render.com) and sign up with GitHub.

**Step 3 — Create a new Web Service**

- Click **New → Web Service**
- Connect your GitHub repository
- Render auto-detects the `render.yaml`

**Step 4 — Set environment variables in Render dashboard**

Go to your service → **Environment** → add these:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | your long random secret key |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourappname.onrender.com` |
| `PYTHON_VERSION` | `3.11.0` |

**Step 5 — Deploy**

Click **Deploy**. Render runs `build.sh` then starts gunicorn. Your app will be live at `https://yourappname.onrender.com`.

**Step 6 — Create admin user on Render**

In the Render dashboard → your service → **Shell**:
```bash
python manage.py createsuperuser
```

---

## Design Decisions

**Custom User model with role field**
Using a `role` field directly on the User model rather than Django's Groups system keeps role logic simple and explicit. The `is_admin` and `is_analyst` properties on the model mean role checks read naturally throughout the codebase.

**JWT over session authentication**
JWT is stateless and scales horizontally without a shared session store. It also avoids Django's CSRF requirement, which would complicate the frontend API calls. The `SessionAuthentication` backend is intentionally excluded from `DEFAULT_AUTHENTICATION_CLASSES`.

**Soft delete on records**
Financial data should never be permanently destroyed. Setting `is_deleted = True` hides records from all API responses while preserving them in the database for audit purposes. A hard delete is not exposed anywhere in the API.

**Separate views folder**
Splitting views into `auth_views.py`, `user_views.py`, `record_views.py`, and `dashboard_views.py` keeps each file focused and under 100 lines, making the codebase easy to navigate.

**Django serves the frontend**
Serving HTML templates directly from Django eliminates the need for a separate frontend server, CORS complexity in production, and any build pipeline. The frontend is plain HTML/CSS/JS — no framework, no npm, no compilation step.

**SQLite for development, easy to swap**
SQLite requires zero configuration and works immediately. Switching to PostgreSQL for production requires only changing the `DATABASES` setting — the rest of the code is unchanged.

---

## Assumptions & Tradeoffs

- Role assignment is open during registration for demonstration purposes. In a real production system, only admins would be able to assign the `admin` or `analyst` roles.
- SQLite is used for local development. Render's free tier does not persist SQLite data between deploys — use PostgreSQL (via `dj-database-url`) for persistent production data.
- Pagination is set to 20 records per page by default, configurable via `page_size` query parameter.
- The `is_deleted` flag is never exposed as a writable field from the API — it can only be set by the DELETE endpoint.
- Token refresh is the client's responsibility. Access tokens expire after 8 hours; refresh tokens after 7 days.
