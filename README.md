# CampusCare — Campus Dispensary Management System

> A full-featured Django 4.2 LTS web application for managing a university health dispensary — from symptom triage and appointment booking to prescription management, pharmacy dispensing and inventory tracking.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Roles & Permissions](#roles--permissions)
- [Data Flow](#data-flow)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [App-by-App Breakdown](#app-by-app-breakdown)
- [Key Models & Relationships](#key-models--relationships)
- [API / URL Naming Conventions](#api--url-naming-conventions)
- [Development Guidelines](#development-guidelines)
- [Common Pitfalls](#common-pitfalls)
- [Build Steps](#build-steps)
- [Contributing](#contributing)

---

## Overview

CampusCare is a campus dispensary system built for universities to digitize the end-to-end patient journey. Students can triage their symptoms, book appointment slots and receive QR-coded tokens, doctors can manage prescriptions, pharmacists can dispense medicines, and administrators get inventory control.

**Internal Code:** `OK`  
**Status:** Active Development

---

## Features

| Module | Highlights |
|---|---|
| **Accounts** | Role-based registration (student / doctor / pharmacist / admin), auto role redirect on login |
| **Calendar** | Admin-managed dispensary schedule, today-open/closed badge injected site-wide |
| **Appointments** | Time-windowed slot booking, UUID + QR token generation, live queue counter, auto token expiry middleware |
| **Consultation** | Doctor availability toggle, prescription form with dynamic medicine rows (JS), printable prescription slip |
| **Pharmacy** | Dispense queue, per-student monthly medicine quota enforcement, signed receipt generation |
| **Inventory** | Medicine & stock CRUD, real-time stock decrement on dispense, low-stock alert widget |
| **Analytics** | JSON-rule–based symptom triage, queue ETA calculator, medicine history timeline |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2 LTS, Python 3.11+ |
| Database (dev) | SQLite (`db.sqlite3`) |
| Database (prod) | PostgreSQL-ready |
| Frontend | Django Templates, Bootstrap 5, Vanilla JS |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| QR Codes | `qrcode[pil]` — stored as Base64 in `TextField` |
| Image handling | Pillow |
| Static files (prod) | WhiteNoise |
| Config / Secrets | python-decouple via `.env` |

---

## Project Structure

```
campuscare/                         ← Django project root
├── manage.py
├── .env.example                    ← committed; .env is gitignored
├── requirements.txt
│
├── campuscare/                     ← project config package
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                           ← shared utilities
│   ├── decorators.py               ← role_required decorator
│   ├── context_processors.py       ← dispensary status (global)
│   ├── constants.py                ← all magic strings/numbers
│   └── templatetags/
│       └── role_tags.py            ← {% if_role 'doctor' %} tag
│
├── accounts/                       ← user profiles & auth
├── appointments/                   ← slots, tokens, QR, queue
├── consultation/                   ← doctor profiles & prescriptions
├── pharmacy/                       ← dispense queue & receipts
├── inventory/                      ← medicine & stock management
├── calendar_app/                   ← dispensary open/close schedule
├── analytics/                      ← triage, ETA, history
│
├── templates/                      ← all HTML templates
└── static/
    ├── css/campuscare.css
    ├── js/
    │   ├── prescription_rows.js    ← dynamic medicine rows
    │   └── queue_poll.js           ← live queue counter polling
    └── img/
```

---

## Roles & Permissions

| Feature | Student | Doctor | Pharmacist | Admin |
|---|:---:|:---:|:---:|:---:|
| Register / Login | ✅ | ✅ | ✅ | ✅ |
| Book slot + QR token | ✅ | | | |
| View own queue / ETA | ✅ | | | |
| View medicine history | ✅ | | | |
| Run symptom triage | ✅ | | | |
| Toggle availability | | ✅ | | |
| View patient queue | | ✅ | | ✅ |
| Fill prescription + dosage | | ✅ | | |
| View dispense queue | | | ✅ | ✅ |
| Dispense medicines / receipt | | | ✅ | |
| Manage stock | | | ✅ | ✅ |
| View low-stock alerts | | | ✅ | ✅ |
| Manage dispensary calendar | | | | ✅ |
| Manage users / roles | | | | ✅ |

---

## Data Flow

```
[Student]
   │
   ├─ 1. Symptom triage (analytics) ──► suggested doctor type
   │
   ├─ 2. Check doctor availability (consultation)
   │
   ├─ 3. Browse slots (appointments) ──► Slot.remaining_capacity
   │
   ├─ 4. Book slot ──► Token(uuid, qr_base64, expires_at) generated
   │
   └─ 5. Arrive at dispensary, QR scanned ──► Token.status = 'called'
              │
              ▼
         [Doctor]
              │
              ├─ Views ordered queue (Token list by position)
              └─ Fills Prescription + PrescriptionMedicine (dosage)
                         │
                         ▼
                   [Pharmacist]
                         │
                         ├─ Views pending DispenseRecord queue
                         ├─ Checks student quota (max per month)
                         ├─ Marks medicines dispensed ──► Stock.quantity decrements
                         └─ Generates signed receipt (PDF-printable HTML)
                                    │
                                    ▼
                          [Inventory]
                                    │
                                    ├─ Stock levels updated in real time
                                    ├─ Low-stock alerts surfaced to admin
                                    └─ StockPredictor retrains on new data
```

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-org/campuscare.git
cd campuscare
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your values (see Environment Variables section)
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
# A UserProfile with role='admin' is auto-created via post_save signal
```

## Environment Variables

All secrets live in `.env` (gitignored). Only `.env.example` is committed.

```env
# .env.example

SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (swap for postgres URL in production)
DATABASE_URL=sqlite:///db.sqlite3

# Business logic constants
MONTHLY_MEDICINE_QUOTA=5       # max distinct medicines per student per month
SLOT_GRACE_MINUTES=15          # token valid N minutes after slot start time
AVG_CONSULT_MINUTES=7          # used by the ETA calculator in analytics
```

**Accessing in code:**

```python
from decouple import config

SECRET_KEY          = config('SECRET_KEY')
MONTHLY_QUOTA       = config('MONTHLY_MEDICINE_QUOTA', default=5, cast=int)
SLOT_GRACE_MINUTES  = config('SLOT_GRACE_MINUTES',     default=15, cast=int)
AVG_CONSULT_MINUTES = config('AVG_CONSULT_MINUTES',    default=7,  cast=int)
```

---

## Running the Project

```bash
# Development server
python manage.py runserver

# Run tests
pytest

# Lint
flake8 .

# Format
black .

```

---

## App-by-App Breakdown

### `accounts` — User Profiles & Auth

- **Models:** `UserProfile` (extends Django `User` via OneToOne) — stores `role`, `roll_number`, `phone`, `year_of_study`
- **Views:** Register, login, logout, role-based dashboard redirect
- **Key feature:** `role_required` decorator (in `core/decorators.py`) guards all role-specific views
- **URLs:** `accounts:register`, `accounts:login`, `accounts:dashboard`

---

### `calendar_app` — Dispensary Schedule

- **Models:** `DispensarySchedule` — `date`, `is_open`, `open_time`, `close_time`, `note`
- **Admin CRUD** for schedule management
- **Context processor** injects today's open/closed status into every template globally
- **URLs:** `calendar:month_view`

---

### `appointments` — Slots, Tokens & Queue

- **Models:**
  - `Slot` — linked to `DoctorProfile`, has `date`, `time_window`, `max_capacity`
  - `Token` — UUID token + Base64 QR image, `status` choices: `waiting / called / done / expired`, `expires_at`
- **Services:** `generate_token()`, `expire_stale_tokens()`
- **Middleware:** `TokenExpiryMiddleware` — auto-expires stale tokens on every request
- **Live queue:** `queue_poll.js` polls the counter endpoint and updates the UI without a page refresh
- **URLs:** `appointments:slot_list`, `appointments:book_slot`, `appointments:my_token`, `appointments:queue_count`

---

### `consultation` — Doctor Profiles & Prescriptions

- **Models:**
  - `DoctorProfile` — OneToOne with `User`, `specialization`, `is_available`
  - `Prescription` — OneToOne with `Token`, linked to `DoctorProfile`
  - `PrescriptionMedicine` — FK to `Prescription` + `Medicine`, stores `dosage_instructions`, `quantity`
- **Dynamic rows:** `prescription_rows.js` lets doctors add/remove medicine rows without page reload
- **Print view:** `prescription_print.html` with `@media print` CSS for clean paper output
- **URLs:** `consultation:doctor_list`, `consultation:prescription_create`, `consultation:prescription_print`

---

### `pharmacy` — Dispense Queue & Receipts

- **Models:** `DispenseRecord` — OneToOne with `Prescription`, `receipt_code` (UUID), `dispensed_at`, `quota_signed`
- **Services:** `check_quota(student)` — enforces `MONTHLY_MEDICINE_QUOTA`; `generate_receipt()` — produces a signed printable receipt
- **Stock decrement:** Dispensing a medicine automatically decrements `Stock.quantity`
- **URLs:** `pharmacy:queue`, `pharmacy:dispense`, `pharmacy:receipt`

---

### `inventory` — Medicine & Stock

- **Models:**
  - `Medicine` — `name`, `category`, `unit`, `description`
  - `Stock` — OneToOne with `Medicine`, `quantity`, `updated_at`, `season_tag`
- **Services:** `low_stock_alert()` — surfaces alerts for admin/pharmacist dashboards
- **URLs:** `inventory:stock_list`, `inventory:stock_form`

---

### `analytics` — Triage, ETA & History

- **Symptom triage:** JSON rule engine (`triage_rules.json`) maps symptom combinations to doctor specialization suggestions
- **ETA calculator:** Uses token queue position × `AVG_CONSULT_MINUTES` from env
- **History timeline:** Student's complete medicine dispensing history
- **Services:** `triage_suggest(symptoms)`, `eta_calculator(token)`
- **URLs:** `analytics:triage`, `analytics:history`

---

## Key Models & Relationships

```
User (Django built-in)
 └── UserProfile          role, roll_number, phone, year_of_study

DoctorProfile            ── User (OneToOne)
                            specialization, is_available

DispensarySchedule       date, is_open, open_time, close_time, note

Slot                     ── DoctorProfile (FK)
                            date, time_window, max_capacity

Token                    ── Slot (FK)  ── UserProfile/student (FK)
                            token_code (UUID), qr_image (Base64 TextField),
                            status [waiting|called|done|expired],
                            expires_at

Prescription             ── Token (OneToOne)  ── DoctorProfile (FK)
                            symptoms, created_at

PrescriptionMedicine     ── Prescription (FK)  ── Medicine (FK)
                            dosage_instructions, quantity

Medicine                 name, category, unit, description

Stock                    ── Medicine (OneToOne)
                            quantity, updated_at, season_tag

DispenseRecord           ── Prescription (OneToOne)  ── UserProfile/pharmacist (FK)
                            receipt_code (UUID), dispensed_at, quota_signed
```

---

## API / URL Naming Conventions

Every URL pattern must have a `name=` argument. Naming follows `<app_label>:<action>`:

```python
# accounts
accounts:register
accounts:login
accounts:dashboard

# appointments
appointments:slot_list
appointments:book_slot
appointments:my_token
appointments:queue_count

# consultation
consultation:doctor_list
consultation:prescription_create
consultation:prescription_detail
consultation:prescription_print

# pharmacy
pharmacy:queue
pharmacy:dispense
pharmacy:receipt

# inventory
inventory:stock_list
inventory:stock_form

# calendar
calendar:month_view

# analytics
analytics:triage
analytics:history
```

---

## Development Guidelines

### Models
- Every model **must** have a `__str__`, a `Meta` class with `ordering` + `verbose_name`, and explicit `on_delete` on all `ForeignKey` fields.
- Choices are defined as inner `TextChoices` classes — never bare tuples.
- No bare `CharField` without `max_length`.

### Views
- Use **CBV** (`CreateView`, `UpdateView`, `DetailView`) for anything with GET + POST.
- Use **FBV** only for simple single-action endpoints (toggle, redirect, AJAX).
- Every view touching user data must use `@login_required` / `LoginRequiredMixin` **and** `role_required` / `RoleRequiredMixin`.
- Business logic lives in `services.py` — never in views.

### Templates
- Every template extends `base.html`.
- Never hardcode URLs — always use `{% url 'namespace:name' %}`.
- Always escape user content: `{{ value|escape }}`.
- Never write inline `<style>` — all styles go in `static/css/campuscare.css`.

### Services
- Functions are pure where possible (take model instances, return values).
- All functions have type hints and a one-line docstring.

### Settings hygiene
- `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` are always read from `.env` via `python-decouple`.
- All custom constants live in `core/constants.py`, not `settings.py`.

### Timezone
- Always use `django.utils.timezone.now()` — never `datetime.now()` — to respect `USE_TZ = True`.

---

## Common Pitfalls

| Pitfall | Correct Approach |
|---|---|
| Storing QR image as a file on disk | Store as Base64 string in `TextField`; render with `data:image/png;base64,...` |
| Checking quota in the view | Call `pharmacy.services.check_quota(student)` — quota logic lives in services only |
| Using `request.user` directly in templates for role checks | Use `{% load role_tags %}` + `{% if_role 'doctor' %}` templatetag |
| Expired tokens appearing in doctor queue | `TokenExpiryMiddleware` auto-sets `status='expired'`; always filter `status='waiting'` |
| Using `datetime.now()` for slot expiry | Always use `django.utils.timezone.now()` to respect `USE_TZ = True` |
| Inline `<style>` in templates | All styles go in `static/css/campuscare.css`; print styles in `@media print` block |
| `createsuperuser` skipping `UserProfile` creation | A `post_save` signal auto-creates `UserProfile(role='admin')` for superusers |

---

## Build Steps

The project is built incrementally. Each step is self-contained and must be completed in order.

| Step | Area | Key Deliverables |
|---|---|---|
| 1 | Project scaffold | `startproject`, all `startapp` calls, `settings.py`, `requirements.txt`, `.env.example` |
| 2 | `accounts` | `UserProfile`, register, login, logout, role redirect, `role_required` decorator |
| 3 | `core` | `base.html`, Bootstrap 5 navbar, dispensary badge, messages block, `role_tags` templatetag |
| 4 | `calendar_app` | `DispensarySchedule`, admin CRUD, monthly view, today-status context processor |
| 5 | `appointments` | `Slot`, `Token`, slot listing, booking, QR generation, live queue counter, expiry middleware |
| 6 | `consultation` | `DoctorProfile`, availability toggle, doctor list, prescription form (dynamic JS rows), printable slip |
| 7 | `pharmacy` | Dispense queue, dispense action, quota check, receipt generation |
| 8 | `inventory` | `Medicine`, `Stock`, stock CRUD, low-stock alert widget |
| 9 | `analytics` | Symptom triage widget + JSON rules, queue ETA, medicine history timeline |
| 10 | Polish | Print CSS for prescriptions, mobile audit, WhiteNoise config, full `.env` setup |
---

## Approved Dependencies

```
django>=4.2,<5.0
pillow>=10.0
qrcode[pil]>=7.4
django-crispy-forms>=2.1
crispy-bootstrap5>=2023.10
pandas>=2.0
numpy>=1.24
whitenoise>=6.6
python-decouple>=3.8
```

**Dev only (`requirements-dev.txt`):**
```
black
flake8
pytest-django
factory-boy
```

---

## Contributing

1. Follow the step execution protocol — no skipping ahead, no combining steps.
2. Run `python manage.py check` before every commit.
3. All code must pass `flake8` and be formatted with `black`.
4. Every new model needs a migration — run `python manage.py makemigrations` after model changes.
5. Write tests in `pytest-django` style; use `factory-boy` for fixtures.

---

*CampusCare — keeping campus health organized, one token at a time.*