# Coderr Backend

Django REST Framework backend for the Coderr platform — a marketplace where
business users offer services (with basic/standard/premium pricing tiers)
and customer users can order them and leave reviews.

This repository contains **only the backend**. The matching frontend lives in
a separate repository: https://github.com/Developer-Akademie-Backendkurs/project.Coderr

## Table of Contents

- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running the Server](#running-the-server)
- [Connecting the Frontend](#connecting-the-frontend)
- [Guest Login Test Accounts](#guest-login-test-accounts)
- [Project Structure](#project-structure)
- [Authentication](#authentication)
- [Tests](#tests)
  - [Running the tests](#running-the-tests)
  - [Coverage](#coverage)
  - [Test suite overview](#test-suite-overview)
- [Notes / Special Behaviour](#notes--special-behaviour)

## Tech Stack

- Python 3.14
- Django 6.1
- Django REST Framework
- Token Authentication
- SQLite (development database)
- `python-dotenv` for environment configuration
- `coverage` for test coverage reporting

## Setup

1. Clone this repository and navigate into it.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create your local `.env` file from the template and fill in a secret key:
   ```bash
   cp .env.template .env
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Paste the generated value into `DJANGO_SECRET_KEY` in `.env`.
   See [Environment Variables](#environment-variables) for all keys.
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. (Optional) Create a superuser for the Django admin panel:
   ```bash
   python manage.py createsuperuser
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://127.0.0.1:8000/api/`.

## Environment Variables

Configuration is read from a `.env` file in the project root (loaded via
`python-dotenv`). This file is **git-ignored** — never commit it. Use
`.env.template` as the starting point.

| Variable               | Required | Default | Description                                                                 |
|------------------------|----------|---------|-----------------------------------------------------------------------------|
| `DJANGO_SECRET_KEY`    | yes      | —       | Django cryptographic signing key. The app will not start without it.       |
| `DJANGO_DEBUG`         | no       | `False` | Set to `True` only for local development.                                  |
| `DJANGO_ALLOWED_HOSTS` | no       | empty   | Comma-separated hostnames. Required (non-empty) when `DJANGO_DEBUG=False`. |

## Running the Server

```bash
python manage.py runserver
```

The API base URL is `http://127.0.0.1:8000/api/`.

## Connecting the Frontend

Clone the frontend from
https://github.com/Developer-Akademie-Backendkurs/project.Coderr
and open `index.html` (or `login.html`) with VS Code's Live Server extension.

The frontend's `shared/scripts/config.js` already points to
`http://127.0.0.1:8000/api/`, matching this backend's default configuration —
no changes were needed on the frontend side.

## Guest Login Test Accounts

The frontend's "guest login" buttons use the following hardcoded credentials.
Create these two users via `/api/registration/` (or the Django admin panel)
so the guest login works:

| Role     | Username | Password  |
|----------|----------|-----------|
| Business | kevin    | asdasd24  |
| Customer | andrey   | asdasd    |

## Project Structure

The project follows a resource-oriented app structure:

- `core/` — Django project settings and root URL configuration
- `auth_app/` — registration and login
- `profile_app/` — user profile CRUD (business & customer)
- `offers_app/` — offers and their pricing tiers (offer details)
- `orders_app/` — orders created from an offer detail
- `reviews_app/` — customer reviews of business users
- `base_info_app/` — public platform-wide statistics

Each app contains an `api/` subfolder with `serializers.py`, `views.py`,
`urls.py`, and `permissions.py`, plus a `tests.py` with that app's test suite.

## Authentication

This API uses DRF Token Authentication. After registering or logging in,
include the returned token in subsequent requests:

```
Authorization: Token <your-token>
```

## Tests

The backend ships with **56 tests** (Django `APITestCase`), one `tests.py`
per app. They cover the happy paths plus permission, ownership, validation
and authentication edge cases for every endpoint.

### Running the tests

Run the full suite:

```bash
python manage.py test
```

Useful variations:

```bash
python manage.py test offers_app                       # one app
python manage.py test offers_app.tests.OfferListCreateTests   # one test class
python manage.py test -v 2                              # verbose output
python manage.py test --keepdb                          # reuse the test DB (faster reruns)
```

### Coverage

`coverage` is included in `requirements.txt`. Generate a report with:

```bash
coverage run --source='.' manage.py test
coverage report          # summary in the terminal
coverage html            # detailed HTML report in htmlcov/index.html
```

Current status: **all 56 tests pass at ~98% line coverage.**

### Test suite overview

| App             | Tests | What is covered                                                                 |
|-----------------|-------|--------------------------------------------------------------------------------|
| `auth_app`      | 7     | Registration (success, password mismatch, duplicate username/email), login (success, wrong password, unknown user) |
| `profile_app`   | 9     | Profile detail GET/PATCH, auth requirement, ownership on PATCH, nested user field update, business/customer list endpoints |
| `offers_app`    | 15    | Public listing, create as business/customer, "exactly 3 details" rule, filtering & search, offer detail PATCH/DELETE ownership, `offer_type` matching on update, offerdetail retrieve |
| `orders_app`    | 12    | Create as customer/business, invalid detail id, list scoping to involved users, status PATCH permissions, delete restricted to admin, order-count endpoints |
| `reviews_app`   | 10    | Create as customer/business, one-review-per-business rule, list auth requirement, filtering, update/delete ownership |
| `base_info_app` | 3     | Reachable without auth, response structure, correct aggregate counts |

## Notes / Special Behaviour

- An offer must contain exactly 3 details (basic, standard, premium) on
  creation. When updating (`PATCH`) an offer's details, each detail is
  matched by its `offer_type`, not by its numeric ID.
- Orders are created as a snapshot of the chosen `OfferDetail` — later
  changes to an offer do not retroactively affect existing orders.
- A customer can only leave one review per business user.
- Deleting an order is restricted to staff/admin users.
- Only `GET /api/offers/` is paginated (`{count, next, previous, results}`,
  page size 6). All other list endpoints return plain arrays, matching what
  the frontend expects.
- `GET /api/base-info/` is fully public — it skips authentication entirely so
  a stale token from the frontend cannot turn it into a 401.
