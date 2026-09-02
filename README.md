# Coderr Backend

Django REST Framework backend for the Coderr platform — a marketplace where
business users offer services (with basic/standard/premium pricing tiers)
and customer users can order them and leave reviews.

This repository contains **only the backend**. The matching frontend lives in
a separate repository: https://github.com/Developer-Akademie-Backendkurs/project.Coderr

## Tech Stack

- Python 3.4.16
- Django 6.1
- Django REST Framework
- Token Authentication
- SQLite (development database)

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
4. Run migrations:
```bash
   python manage.py migrate
```
5. (Optional) Create a superuser for the Django admin panel:
```bash
   python manage.py createsuperuser
```
6. Start the development server:
```bash
   python manage.py runserver
```
   The API will be available at `http://127.0.0.1:8000/api/`.

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
`urls.py`, and `permissions.py`.

## Authentication

This API uses DRF Token Authentication. After registering or logging in,
include the returned token in subsequent requests:
Authorization: Token <your-token>

## Notes / Special Behaviour

- An offer must contain exactly 3 details (basic, standard, premium) on
  creation. When updating (`PATCH`) an offer's details, each detail is
  matched by its `offer_type`, not by its numeric ID.
- Orders are created as a snapshot of the chosen `OfferDetail` — later
  changes to an offer do not retroactively affect existing orders.
- A customer can only leave one review per business user.
- Deleting an order is restricted to staff/admin users.