# CCS User Management System

REST API for managing user records, built with Django REST Framework and PostgreSQL, plus a lightweight Angular client that consumes it.

Submitted by **Augusto Valdez** for the CCS Developer Challenge.

---

## Table of contents

- [Overview](#overview)
- [Tech stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Backend setup](#backend-setup)
- [Database migrations](#database-migrations)
- [Seed data](#seed-data)
- [Frontend setup](#frontend-setup)
- [API reference](#api-reference)
- [Roles and permissions](#roles-and-permissions)
- [Error format](#error-format)
- [API documentation](#api-documentation)
- [Running the tests](#running-the-tests)
- [Project structure](#project-structure)
- [Assumptions and design decisions](#assumptions-and-design-decisions)
- [Optional features implemented](#optional-features-implemented)
- [Troubleshooting](#troubleshooting)

---

## Overview

The system exposes a JWT-authenticated REST API for a simple user management domain:

- A login endpoint that issues access and refresh tokens.
- Full CRUD over person records, protected behind authentication.
- Role-based authorization: administrators can write, regular users can only read.
- Pagination, search and sorting on the list endpoint.

Two concepts are modelled separately:

| Model | App | Purpose |
| --- | --- | --- |
| `Person` | `users` | The business record exposed through `/users`. Has no credentials. |
| `Account` | `accounts` | Login credentials. Owns exactly one `Person`. |

The reasoning behind that split is documented under [Assumptions and design decisions](#assumptions-and-design-decisions).

The Angular client covers the three required screens — sign in, people list and user details — and consumes the API exclusively. It renews expired tokens transparently and adapts its controls to the signed-in user's role.

---

## Tech stack

| Layer | Technology |
| --- | --- |
| Language | Python 3.14 |
| Framework | Django 6.0 · Django REST Framework 3.17 |
| Authentication | JWT via `djangorestframework-simplejwt` (with refresh token rotation and blacklisting) |
| Database | PostgreSQL 16 |
| API documentation | OpenAPI 3 via `drf-spectacular` (Swagger UI) |
| Containers | Docker Compose (PostgreSQL) |
| Frontend | Angular 22 (standalone components, signals, reactive forms) |
| Styling | Tailwind CSS 4 |

---

## Prerequisites

- **Python 3.12 or newer** (developed and tested on 3.14.6)
- **Docker Desktop** with Docker Compose v2
- **Node.js 20 or newer** and npm, for the frontend (developed on Node 24.18)
- **Git**

Verify:

```bash
python --version
docker compose version
node --version
npm --version
```

The Angular CLI does not need to be installed globally: the frontend scripts run it from the project's own dependencies.

---

## Backend setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd CCS-PT-Augusto-Valdez
```

### 2. Create the environment file

```bash
cp .env.example .env          # Linux / macOS
copy .env.example .env        # Windows
```

Then open `.env` and set a real `DJANGO_SECRET_KEY` and `POSTGRES_PASSWORD`. Generate a key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

The `.env` file is git-ignored. `.env.example` documents every variable the project reads.

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Django cryptographic signing key |
| `DJANGO_DEBUG` | `True` for development, `False` otherwise |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames the app will serve |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Database credentials, shared by Docker Compose and Django |
| `POSTGRES_HOST` | `localhost` when Django runs on the host, `db` when it runs inside Compose |
| `POSTGRES_PORT` | Published PostgreSQL port |
| `CORS_ALLOWED_ORIGINS` | Origins allowed to call the API (the Angular dev server) |

### 3. Start PostgreSQL

```bash
docker compose up -d
docker compose ps
```

Wait until the container reports `healthy`. This creates the empty database; Django creates the tables in the next step.

### 4. Create the virtual environment and install dependencies

```bash
cd backend
python -m venv .venv

# Linux / macOS
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Confirm the environment is active before installing — the shell prompt should show `(.venv)`.

To run the test suite as well, install `requirements-dev.txt` instead: it includes everything above plus `pytest`.

### 5. Apply migrations

```bash
python manage.py migrate
```

This creates the schema **and** populates the sample data. See [Seed data](#seed-data).

### 6. Run the server

```bash
python manage.py runserver
```

The API is now available at `http://localhost:8000/api/v1/`.

---

## Database migrations

Migrations are versioned files that describe every change to the database schema, and they are committed to the repository.

```bash
python manage.py migrate                  # apply all pending migrations
python manage.py showmigrations           # [X] applied, [ ] pending
python manage.py makemigrations           # generate migrations after changing a model
python manage.py migrate users 0001       # roll back to a specific migration
```

Migrations are idempotent: Django records what it has applied in the `django_migrations` table and never runs the same migration twice.

---

## Seed data

The sample data ships as **data migrations**, so it is created by `migrate` with no extra command:

| Migration | Creates |
| --- | --- |
| `users/0002_seed_people` | 20 sample people, with varied countries and birth dates |
| `accounts/0002_seed_accounts` | 2 login accounts and their `Person` records |

Total: **22 person records** and **2 accounts**.

Because it runs inside a migration, re-running `migrate` will **not** duplicate the data.

### Credentials

| Username | Password | Role | Can write |
| --- | --- | --- | --- |
| `admin` | `Admin123!` | `ADMIN` | Yes |
| `user123` | `Password1!` | `USER` | No |

The `admin` account is also a Django superuser, so the same credentials work at `http://localhost:8000/admin/`.

To reset the data from scratch:

```bash
docker compose down -v      # destroys the database volume
docker compose up -d
python manage.py migrate
```

---

## Frontend setup

The client is an Angular 22 application using standalone components, signals and Tailwind CSS.

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Run the development server

```bash
npm start
```

The application runs at `http://localhost:4200`, which is already whitelisted in `CORS_ALLOWED_ORIGINS`.

**The backend must be running.** The client consumes the REST API exclusively and performs no direct database access. Start PostgreSQL and the Django server first, as described in [Backend setup](#backend-setup).

The API base URL lives in `frontend/src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
};
```

### Production build

```bash
npm run build
```

Output is written to `frontend/dist/frontend`.

### Screens

| Route | Screen | Access |
| --- | --- | --- |
| `/login` | Sign in | Public |
| `/people` | People list, with search and pagination | Any authenticated user |
| `/people/:id` | User details, editable by administrators | Any authenticated user |

Unauthenticated visits to a protected route are redirected to `/login` with the original URL preserved, so signing in returns the user to where they were heading.

### Minimum requirements coverage

The challenge asks for five Angular concepts. Where each one is demonstrated:

| Concept | Location |
| --- | --- |
| Standalone components | Every component; the project has no `NgModule` |
| Services | `AuthService` and `UserService`, injected with `inject()` |
| HttpClient | Both services, with typed request and response models |
| Routing | `app.routes.ts`, with a route guard and lazily loaded screens |
| Reactive forms | Login form and the user details form, with validators |

---

## API reference

All endpoints are versioned under `/api/v1/`. **Trailing slashes are required.**

### Authentication

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/api/v1/login/` | Public | Authenticate and receive tokens |
| `POST` | `/api/v1/token/refresh/` | Public | Exchange a refresh token for a new access token |
| `POST` | `/api/v1/logout/` | Public | Blacklist a refresh token |

### Users

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/users/` | Any authenticated | List people (paginated) |
| `GET` | `/api/v1/users/{id}/` | Any authenticated | Retrieve one person |
| `POST` | `/api/v1/users/` | Admin only | Create a person |
| `PUT` | `/api/v1/users/{id}/` | Admin only | Replace a person |
| `PATCH` | `/api/v1/users/{id}/` | Admin only | Partially update a person |
| `DELETE` | `/api/v1/users/{id}/` | Admin only | Delete a person |

### Query parameters on `GET /api/v1/users/`

| Parameter | Example | Description |
| --- | --- | --- |
| `page` | `?page=2` | Page number, 10 records per page |
| `search` | `?search=Japan` | Case-insensitive match on first name, last name, email and country |
| `ordering` | `?ordering=-country` | Sort by any field; `-` reverses the order |

### Login

**Request**

```http
POST /api/v1/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin123!"
}
```

**Response** `200 OK`

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "person_id": 21,
  "username": "admin",
  "role": "ADMIN"
}
```

Send the access token on every subsequent request:

```http
Authorization: Bearer <access>
```

Access tokens expire after 30 minutes, refresh tokens after 1 day.

### List people

**Response** `200 OK`

```json
{
  "count": 22,
  "next": "http://localhost:8000/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "first_name": "Ana",
      "last_name": "Torres",
      "full_name": "Ana Torres",
      "email": "ana.torres@example.com",
      "phone": "+51 987 654 321",
      "country": "Peru",
      "birth_date": "1990-03-14"
    }
  ]
}
```

`full_name` is read-only and derived from the first and last name.

### Create a person

```http
POST /api/v1/users/
Authorization: Bearer <admin access token>
Content-Type: application/json

{
  "first_name": "Nuevo",
  "last_name": "Registro",
  "email": "nuevo.registro@example.com",
  "phone": "+51 999 111 222",
  "country": "Peru",
  "birth_date": "1999-02-10"
}
```

Returns `201 Created` with the persisted record. All six fields are required.

---

## Roles and permissions

| Operation | Unauthenticated | `USER` | `ADMIN` |
| --- | --- | --- | --- |
| Log in | Allowed | Allowed | Allowed |
| Read people | `401` | Allowed | Allowed |
| Create / update / delete | `401` | `403` | Allowed |

Authorization is enforced **server side** by `accounts/permissions.py`. The `role` returned by the login endpoint is only meant to let the client hide controls it should not offer; it is never trusted as a security boundary.

---

## Error format

Every error returns the same envelope, so the client has a single shape to handle.

```json
{
  "error": {
    "status": 400,
    "code": "invalid",
    "message": "The submitted data is not valid.",
    "fields": {
      "email": ["A person with this email already exists."]
    }
  }
}
```

| Field | Purpose |
| --- | --- |
| `status` | HTTP status code |
| `code` | Machine-readable identifier, for client-side branching |
| `message` | Human-readable summary, safe to display |
| `fields` | Per-field validation errors; empty for non-validation errors |

### Status codes

| Code | When |
| --- | --- |
| `200 OK` | Successful read or update |
| `201 Created` | Person created |
| `204 No Content` | Person deleted |
| `400 Bad Request` | Missing field, invalid email, duplicate email, birth date in the future |
| `401 Unauthorized` | Missing, invalid or expired token; wrong credentials |
| `403 Forbidden` | Authenticated but not an administrator |
| `404 Not Found` | No person with that id |
| `409 Conflict` | Attempt to delete a person that owns a login account |
| `500 Internal Server Error` | Unhandled error; logged with a full traceback |

### Validation rules

| Rule | Response |
| --- | --- |
| All six fields required | `400` listing each missing field |
| Valid email format | `400` `"Enter a valid email address."` |
| Unique email | `400` `"A person with this email already exists."` |
| Birth date not in the future | `400` `"Birth date cannot be in the future."` |
| Person id must exist | `404` |

---

## API documentation

### Swagger UI

With the server running:

- **Interactive documentation:** http://localhost:8000/api/docs/
- **Raw OpenAPI 3 schema:** http://localhost:8000/api/schema/

The Swagger page includes a *Try it out* button that issues real requests against the running API.

### Postman collection

Import `docs/CCS-API.postman_collection.json` into Postman. It contains 21 requests across three folders:

| Folder | Contents |
| --- | --- |
| Auth | Login as admin, login as user123, failed login, refresh, logout |
| Users | List, paginate, search, sort, retrieve, create, update, delete |
| Error cases | 401, 403, 404, 409 and every validation failure |

Run **Auth → Login as admin** first: a post-response script stores the tokens in collection variables, so every other request is authenticated automatically. To exercise the `403` responses, run **Auth → Login as user123** instead and repeat any write request.

---

## Running the tests

The backend suite uses `pytest` and `pytest-django`. Install the development dependencies, which include the runtime ones:

```bash
cd backend
pip install -r requirements-dev.txt
```

PostgreSQL must be running: Django creates a separate `test_ccs_db` database, applies the migrations to it, runs the suite and drops it. The development database is never touched.

```bash
pytest                                    # whole suite
pytest users                              # one app
pytest users/tests/test_services.py       # one file
pytest -v                                 # one line per test
```

### What is covered

41 tests across four areas:

| File | Focus |
| --- | --- |
| `accounts/tests/test_login.py` | Token issuing, identical message for both invalid-credential cases, refresh rotation, blacklisting on logout |
| `users/tests/test_permissions.py` | `401` when anonymous, `403` when a reader attempts a write, success for administrators |
| `users/tests/test_validation.py` | Required fields, email format, duplicate email, future birth date, error envelope shape |
| `users/tests/test_api.py` | Pagination, search, ordering, retrieve, `404`, create, update, delete, and the `409` on a linked person |
| `users/tests/test_services.py` | Business rules called directly, with no HTTP request involved |

`test_services.py` is the one that justifies the service layer: `delete_person()` is asserted to raise `PersonHasAccount` by calling the function itself — no client, no authentication, no server. Business rules are testable because they do not depend on the framework.

Because the sample data ships as a migration, the test database is created already populated, so the fixed `admin` and `user123` accounts are available to every test.

---

## Project structure

```
CCS-PT-Augusto-Valdez/
├── docker-compose.yml            PostgreSQL service
├── .env.example                  Documented environment variables
├── docs/
│   └── CCS-API.postman_collection.json
├── backend/
│   ├── manage.py
│   ├── pytest.ini
│   ├── conftest.py               Shared test fixtures
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── config/
│   │   ├── settings.py           Configuration, read from .env
│   │   ├── urls.py               Root router, mounts /api/v1/ and Swagger
│   │   └── exceptions.py         Unified error envelope
│   ├── users/                    Person domain
│   │   ├── models.py             Person
│   │   ├── serializers.py        Validation and API contract
│   │   ├── services.py           Business rules and audit logging
│   │   ├── views.py              PersonViewSet
│   │   ├── urls.py               Router registration
│   │   ├── exceptions.py         PersonHasAccount → 409
│   │   └── migrations/           Schema + seed
│   └── accounts/                 Identity domain
│       ├── models.py             Account
│       ├── serializers.py        Login contract
│       ├── services.py           Authentication and token issuing
│       ├── views.py              LoginView
│       ├── urls.py               Login, refresh, logout
│       ├── permissions.py        IsAdminOrReadOnly
│       └── migrations/           Schema + seed
└── frontend/
    └── src/
        ├── environments/
        │   └── environment.ts    API base URL
        └── app/
            ├── app.routes.ts     Routes, guard and lazy loading
            ├── app.config.ts     HttpClient, interceptor, router
            ├── app.component.*   Shell: session bar and router outlet
            ├── core/
            │   ├── models/       Person, Session, Page<T>, ApiErrorBody
            │   ├── services/     AuthService, UserService
            │   ├── interceptors/ Bearer token and 401 refresh
            │   ├── guards/       authGuard
            │   ├── storage/      Session persistence
            │   └── errors/       API error to display text
            ├── components/
            │   ├── login/
            │   └── people/
            │       ├── people-list/
            │       └── user-details/
            └── shared/
                └── confirm-dialog/
```

Backend responsibilities are separated as follows:

| Layer | Responsibility |
| --- | --- |
| **Models** | Persistence and database constraints |
| **Serializers** | Input validation and output shape |
| **Services** | Business rules, orchestration and audit logging |
| **Views** | HTTP handling: receive, authorize, delegate, respond |
| **Permissions** | Authorization |
| **URLs** | Routing |

Views contain no business logic. Every write operation delegates to a service function that is callable without an HTTP request, which keeps the domain testable and reusable from management commands or background jobs.

On the frontend, `core/` holds everything application-wide and injectable, `components/` holds the routed screens, and `shared/` holds presentational components that carry no knowledge of the domain.

---

## Assumptions and design decisions

### 1. `Person` and `Account` are separate models

The challenge uses the word *user* for two different things: the two accounts that can log in, and the twenty records that are managed through the API. The field list in the specification (`id`, `first_name`, `last_name`, `email`, `phone`, `country`, `birth_date`) contains no username or password, which confirms those records are not credentials.

Keeping them separate means:

- `DELETE /users/{id}` can never destroy a login account by accident.
- `POST /users` does not have to invent credentials for a record that will never authenticate.
- The two have genuinely different lifecycles: accounts are fixed system configuration, people are business data.

The API route is still `/users`, as required by the specification. Only the internal class name differs.

### 2. `Account` is a custom user model

`AUTH_USER_MODEL` is set to `accounts.Account`, which subclasses `AbstractUser`. Django's default `User` model is therefore not used and its table is never created.

`AbstractUser` was chosen over `AbstractBaseUser` because it provides password hashing, permissions and admin integration out of the box. The unused inherited fields (`email`, `first_name`, `last_name`) cost nothing on a two-row table and save roughly forty lines of hand-written code.

### 3. Every account must own a person, and that person is protected

`Account.person` is a mandatory `OneToOneField` with `on_delete=PROTECT`. Deleting a person that still owns an account is rejected by the database, and the API surfaces that as `409 Conflict` with an explanatory message rather than a generic failure.

As a consequence, `createsuperuser` prompts for a person id — declared through `REQUIRED_FIELDS = ['person']`.

### 4. Roles use a dedicated field, not `is_staff`

Authorization uses an explicit `role` field with `ADMIN` and `USER` values. Django's `is_staff` and `is_superuser` were deliberately not reused, because they mean *"can access the Django admin site"* — a different concern from API permissions. Conflating them makes both harder to reason about later.

### 5. All six person fields are required

The specification lists them as the fields each user *should contain*, and the People List screen displays country and phone as table columns. Making them optional would leave visible gaps in the UI, so none of them accept blank values.

### 6. The API is versioned under `/api/v1/`

The specification lists the routes as `/login` and `/users`. They are served under an `/api/v1/` prefix so that a future breaking change can ship as `/api/v2/` without breaking existing clients. No endpoint was removed or renamed.

### 7. Seed data ships as a data migration

Rather than a fixture or a standalone script, the sample data is created by migrations. This means a single `migrate` command produces a fully working database, there is no extra step to forget, and the data cannot be inserted twice.

### 8. Errors share one envelope

Django REST Framework returns `{"detail": "..."}` for authentication and permission errors but `{"field": ["..."]}` for validation errors. A custom exception handler normalises both into a single shape so the client only implements one error path. The same handler converts unhandled exceptions into a JSON `500` and logs the traceback.

### 9. Failed logins do not reveal whether a username exists

A wrong password and an unknown username both return the same `401` message. Distinguishing them would let an attacker enumerate valid usernames before attempting passwords. The application log does record which case occurred.

### 10. The login response carries `person_id`, `username` and `role`

No `/users/me` endpoint was added. The client stores `person_id` from the login response and reuses `GET /users/{id}` to show the signed-in user's profile, which keeps the API surface smaller. `role` lets the client hide controls the user cannot use.

### 11. JSON uses `snake_case`

Field names match the database and the specification exactly (`first_name`, not `firstName`), which avoids a translation layer on either side.

### 12. The frontend implements exactly the three required screens

Section 3.1 of the specification lists Login, People List and User Details as the required screens, and section 3.3 lists view, edit and delete as the required actions. No "create person" screen was built, even though `POST /api/v1/users/` exists and is documented, because it was not requested. Adding it would mean one extra route reusing the existing form.

### 13. The session is stored in `localStorage`

JWTs are stateless, so the client is the only place the token lives. Keeping it in memory alone would sign the user out on every page reload, so it is persisted in `localStorage` and restored when the application boots.

The trade-off is that `localStorage` is readable by any JavaScript running on the page, which makes it vulnerable to XSS. The more defensive alternative is an `httpOnly` cookie, which JavaScript cannot read, at the cost of CSRF handling and cross-origin cookie configuration. `localStorage` is the common choice for single-page applications and is mitigated here by short-lived access tokens (30 minutes) and refresh token rotation with blacklisting. A system handling genuinely sensitive data should use `httpOnly` cookies instead.

### 14. Authorization is enforced on the server, mirrored on the client

The client hides the delete and save controls for non-administrators and disables the details form. This is presentation only: `IsAdminOrReadOnly` still rejects the request with `403` if it is issued directly. The two layers are deliberately independent, and the client is never treated as a security boundary.

### 15. Expired access tokens are refreshed transparently

An HTTP interceptor attaches the bearer token to every request and, on a `401`, exchanges the refresh token for a new access token and replays the original request. The component that made the call never observes the failure.

Because the backend rotates and blacklists refresh tokens, concurrent refreshes would invalidate each other. `AuthService.refresh()` therefore shares a single in-flight request between all callers.

---

## Optional features implemented

| # | Feature | Status | Notes |
| --- | --- | --- | --- |
| 1 | Pagination | Implemented | 10 per page, with `count`, `next` and `previous`; paged controls on the list screen |
| 2 | Search and filtering | Implemented | `?search=` across four fields plus `?ordering=`; debounced search box on the list screen |
| 3 | Docker | Implemented | Compose service for PostgreSQL, with health check and named volume |
| 4 | Unit tests | Implemented | 41 backend tests with pytest; see [Running the tests](#running-the-tests) |
| 5 | Swagger / OpenAPI | Implemented | `drf-spectacular`, served at `/api/docs/` |
| 6 | Refresh tokens | Implemented | With rotation and blacklisting, a logout endpoint, and transparent renewal in the client |
| 7 | Role-based authorization | Implemented | `ADMIN` writes, `USER` reads, enforced server side |
| 8 | Logging | Implemented | Structured console logging; failed logins, blocked deletes and every write are recorded |
| 9 | Environment configuration | Implemented | All settings read from `.env`, with a documented `.env.example` |

The specification also lists five frontend features as optional and not evaluated. Three were used because they reduce code rather than add it:

| Feature | Used | Reason |
| --- | --- | --- |
| Angular Signals | Yes | The default idiom in Angular 22; component and session state are signals |
| HTTP Interceptors | Yes | Centralises token attachment and `401` refresh instead of repeating them per call |
| Tailwind CSS | Yes | Configured by the Angular CLI; keeps the styling effort proportionate |
| Angular Material | No | A heavy, opinionated dependency that Tailwind already covers here |
| State management library | No | Disproportionate for three screens; two services with signals are enough |

### Known limitations

- The page size (10) is defined in both `settings.py` and the list component. Changing it on the backend requires the same change on the client.
- The confirmation dialog does not trap keyboard focus. Doing so properly would require `@angular/cdk`.

---

## Troubleshooting

### `docker compose up` fails with "port is already allocated"

Another service is using the port. Either stop it, or change `POSTGRES_PORT` in `.env` to a free port — Django reads the same variable, so both sides stay in sync.

### "this error may indicate that the docker daemon is not running"

Docker Desktop is not running. Start the application and wait until it reports that the engine is ready, then retry.

### `can't open file 'manage.py'`

The command must run from the `backend/` directory. Activating the virtual environment does not change the working directory:

```bash
cd backend
python manage.py runserver
```

### `django.db.utils.OperationalError: connection refused`

PostgreSQL is not reachable. Check `docker compose ps` reports `healthy`, and that `POSTGRES_HOST` and `POSTGRES_PORT` in `.env` match the published port.

### Packages install but Django is not found

The virtual environment was not active when `pip install` ran. Confirm with:

```bash
python -c "import sys; print(sys.prefix)"
```

The path must end in `backend/.venv`.
