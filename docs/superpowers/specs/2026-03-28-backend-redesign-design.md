# School ERP Backend Redesign — Design Spec

**Date:** 2026-03-28
**Status:** Approved
**Reference:** Node.js backend at `/home/kaushal/repos/School-ERP/backend`
**Frontend:** React frontend at `/home/kaushal/repos/School-ERP/frontend`

---

## Overview

Full redesign of the Django backend to align with the existing Node.js reference implementation. The frontend is already built against the Node.js API contract — this spec ensures the Python/Django backend matches it exactly, enabling a drop-in replacement.

**Approach:** Domain app split (Option B) — one Django app per domain.

---

## App Structure

```
school_backend/
├── api/              # auth, users, students, attendance, dashboard
├── branches/         # Branch, BranchUser
├── classes/          # Class, ClassStudent, ClassTeacher
├── academics/        # AcademicRecord
├── timetable/        # TimetableSlot
├── notifications/    # Notification, NotificationRecipient
└── fees/             # FeeHead, Payment
```

---

## Data Models

### `api` app

#### User
Replaces the existing custom User model and the separate Staff model.

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| name | CharField(255) | |
| email | EmailField | unique |
| password_hash | CharField(255) | bcrypt via `django-bcrypt` or manual |
| role | CharField(50) | choices: `company_admin`, `branch_admin`, `teacher`, `parent`, `student` |
| designation | TextField | nullable |
| avatar_url | TextField | nullable, base64 data URL, max ~2MB |
| created_at | DateTimeField | auto_now_add |

- `USERNAME_FIELD = 'email'`
- `REQUIRED_FIELDS = ['name']`

#### Student
Replaces the existing Student model.

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| branch | ForeignKey(Branch) | on_delete=CASCADE |
| user | ForeignKey(User) | nullable, optional student user account |
| parent | ForeignKey(User) | nullable, related_name='children' |
| name | CharField(255) | |
| enrollment_date | DateField | default=today |
| created_at | DateTimeField | auto_now_add |

#### Attendance
Replaces the existing Attendance model (student+staff combined).

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| student | ForeignKey(Student) | on_delete=CASCADE |
| class_ref | ForeignKey(Class) | on_delete=CASCADE |
| branch | ForeignKey(Branch) | on_delete=CASCADE |
| date | DateField | |
| status | CharField(20) | choices: `present`, `absent`, `late` |
| created_at | DateTimeField | auto_now_add |

- **Unique constraint:** `(student, date, class_ref)`

---

### `branches` app

#### Branch

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| name | CharField(255) | |
| location | CharField(255) | nullable |
| company_admin | ForeignKey(User) | on_delete=CASCADE |
| created_at | DateTimeField | auto_now_add |

#### BranchUser (junction)

| Field | Type | Notes |
|-------|------|-------|
| branch | ForeignKey(Branch) | on_delete=CASCADE |
| user | ForeignKey(User) | on_delete=CASCADE |

- **Primary key:** `(branch, user)`

---

### `classes` app

#### Class

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| branch | ForeignKey(Branch) | on_delete=CASCADE |
| name | CharField(255) | |
| created_at | DateTimeField | auto_now_add |

#### ClassStudent (junction)

| Field | Type | Notes |
|-------|------|-------|
| class_ref | ForeignKey(Class) | on_delete=CASCADE |
| student | ForeignKey(Student) | on_delete=CASCADE |

- **Primary key:** `(class_ref, student)`

#### ClassTeacher (junction)

| Field | Type | Notes |
|-------|------|-------|
| class_ref | ForeignKey(Class) | on_delete=CASCADE |
| teacher | ForeignKey(User) | on_delete=CASCADE |

- **Primary key:** `(class_ref, teacher)`

---

### `academics` app

#### AcademicRecord
Grade records — replaces existing Exam model. `subject_name` is a plain string (no separate Subject model).

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| student | ForeignKey(Student) | on_delete=CASCADE |
| class_ref | ForeignKey(Class) | on_delete=CASCADE |
| branch | ForeignKey(Branch) | on_delete=CASCADE |
| term | CharField(100) | e.g. "Term 1 2024" |
| subject_name | CharField(255) | plain string |
| grade_score | DecimalField(5,2) | |
| remarks | TextField | nullable |
| created_at | DateTimeField | auto_now_add |

---

### `timetable` app

#### TimetableSlot

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| class_ref | ForeignKey(Class) | on_delete=CASCADE |
| branch | ForeignKey(Branch) | on_delete=CASCADE |
| day_of_week | CharField(10) | choices: Monday…Sunday |
| start_time | TimeField | |
| end_time | TimeField | |
| subject_name | CharField(255) | plain string |
| teacher | ForeignKey(User) | nullable, on_delete=SET_NULL |
| room | CharField(100) | nullable |
| created_at | DateTimeField | auto_now_add |

---

### `notifications` app

#### Notification

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| sender | ForeignKey(User) | nullable, on_delete=SET_NULL |
| title | CharField(255) | |
| message | TextField | |
| target_roles | ArrayField(CharField) | postgres array |
| target_branch | ForeignKey(Branch) | nullable |
| target_class | ForeignKey(Class) | nullable |
| created_at | DateTimeField | auto_now_add |

#### NotificationRecipient (junction)

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| notification | ForeignKey(Notification) | on_delete=CASCADE |
| user | ForeignKey(User) | on_delete=CASCADE |
| is_read | BooleanField | default=False |
| read_at | DateTimeField | nullable |

- **Unique constraint:** `(notification, user)`

---

### `fees` app

#### FeeHead
Replaces existing Fee model.

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| branch | ForeignKey(Branch) | on_delete=CASCADE |
| name | CharField(255) | |
| amount | DecimalField(10,2) | |
| frequency | CharField(20) | choices: `monthly`, `quarterly`, `yearly`, `one-time` |
| description | TextField | nullable |
| is_active | BooleanField | default=True |
| created_at | DateTimeField | auto_now_add |

#### Payment

| Field | Type | Notes |
|-------|------|-------|
| id | UUIDField (PK) | default=uuid4 |
| student | ForeignKey(Student) | on_delete=CASCADE |
| branch | ForeignKey(Branch) | on_delete=CASCADE |
| fee_head | ForeignKey(FeeHead) | nullable, on_delete=SET_NULL |
| amount | DecimalField(10,2) | |
| description | CharField(255) | nullable |
| status | CharField(20) | choices: `pending`, `paid`, `overdue` |
| due_date | DateField | |
| paid_date | DateField | nullable |
| created_at | DateTimeField | auto_now_add |

---

## API Endpoints

All endpoints prefixed with `/api/`. All protected routes require `Authorization: Bearer <token>`.

### Authentication

| Method | Path | Auth | Body / Notes |
|--------|------|------|-------------|
| POST | `/auth/login/` | None | `{ email, password }` → `{ token, user }` |
| GET | `/auth/profile/` | ✅ | → current user object |
| PUT | `/auth/profile/` | ✅ | `{ name, email }` |
| PUT | `/auth/password/` | ✅ | `{ current_password, new_password }` (min 6 chars) |
| PUT | `/auth/avatar/` | ✅ | `{ avatar_url }` (base64, max ~2MB) |

### Users

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/users/` | company_admin, branch_admin | role-scoped list |
| GET | `/users/parents/` | company_admin, branch_admin | parents + their children |
| POST | `/users/` | company_admin, branch_admin | `{ name, email, password, role, branch_id?, designation? }` |
| DELETE | `/users/{id}/` | company_admin, branch_admin | |

### Students

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/students/` | all | role-scoped; includes branch_name, parent_name |
| POST | `/students/` | company_admin, branch_admin | `{ name, branch_id, parent_id? }` |
| DELETE | `/students/{id}/` | company_admin, branch_admin | |

### Attendance

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/attendance/?class_id=&date=` | all | all students in class with status (LEFT JOIN) |
| POST | `/attendance/` | company_admin, branch_admin, teacher | `{ class_id, date, records:[{student_id, status}] }` — atomic upsert |

### Dashboard

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/dashboard/stats/` | company_admin, branch_admin, teacher | `{ students, branches, staff, revenue }` |

### Branches

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/branches/` | all | role-scoped |
| POST | `/branches/` | company_admin | `{ name, location? }` |
| PUT | `/branches/{id}/` | company_admin | `{ name?, location? }` |
| DELETE | `/branches/{id}/` | company_admin | |

### Classes

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/classes/` | all | role-scoped; includes branch_name |
| POST | `/classes/` | company_admin, branch_admin | `{ name, branch_id }` |
| POST | `/classes/assign-teacher/` | company_admin, branch_admin | `{ class_id, teacher_id }` — idempotent |
| POST | `/classes/assign-student/` | company_admin, branch_admin, teacher | `{ class_id, student_id }` — idempotent |
| DELETE | `/classes/{id}/` | company_admin, branch_admin | |

### Academics

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/academics/` | all | role-scoped; includes student_name, class_name, branch_name |
| POST | `/academics/` | company_admin, branch_admin, teacher | `{ student_id, class_id, term, subject_name, grade_score, remarks? }` |

### Timetable

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/timetable/?class_id=` | all | role-scoped; ordered by day+time; includes teacher_name, class_name |
| POST | `/timetable/` | company_admin, branch_admin | `{ class_id, day_of_week, start_time, end_time, subject_name, teacher_id?, room? }` |
| DELETE | `/timetable/{id}/` | company_admin, branch_admin | |

### Fee Heads

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/fee-heads/` | company_admin, branch_admin | includes branch_name |
| POST | `/fee-heads/` | company_admin, branch_admin | `{ branch_id, name, amount, frequency, description? }` |
| DELETE | `/fee-heads/{id}/` | company_admin, branch_admin | soft delete: `is_active=False` |
| POST | `/fee-heads/generate-invoices/` | company_admin, branch_admin | `{ fee_head_id, due_date, student_ids? }` — atomic bulk payment creation |

### Payments

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/payments/` | company_admin, branch_admin, parent, student | role-scoped; includes student_name, branch_name |
| POST | `/payments/` | company_admin, branch_admin | `{ student_id, branch_id, amount, description?, due_date }` |
| PUT | `/payments/{id}/pay/` | company_admin, branch_admin | sets status=paid, paid_date=today |

### Notifications

| Method | Path | Roles | Notes |
|--------|------|-------|-------|
| GET | `/notifications/` | all | user's notifications, limit 100; includes sender_name, is_read |
| POST | `/notifications/` | company_admin, branch_admin, teacher | `{ title, message, target_roles[], target_branch_id?, target_class_id? }` — atomic: insert + resolve recipients |
| PUT | `/notifications/{id}/read/` | all | marks one as read |
| PUT | `/notifications/read-all/` | all | marks all as read for user |

---

## Authorization Logic

### Role Hierarchy

```
company_admin  → sees all entities they own (all branches)
branch_admin   → sees entities in their assigned branches
teacher        → sees classes they teach + related students
parent         → sees own children's data
student        → sees own data only
```

### Reusable Auth Utilities

```python
# api/permissions.py
def require_roles(*roles):
    """Decorator that checks req.user.role is in allowed roles. Returns 403 if not."""

def get_user_branches(user):
    """Returns Branch queryset scoped to the user's role."""

def get_user_students(user):
    """Returns Student queryset scoped to the user's role."""
```

---

## Business Logic

### Attendance (POST)
- Fetch `branch_id` from Class
- For each record in `records[]`: `UPDATE_OR_CREATE` Attendance on `(student, date, class_ref)`
- Wrapped in `transaction.atomic()`

### Generate Invoices (POST `/fee-heads/generate-invoices/`)
- Fetch FeeHead → get `amount`, `name`, `branch`
- If `student_ids` provided: filter Students by those IDs + branch
- If empty: all Students in that branch
- For each student: create Payment with `status=pending`, `fee_head=fee_head`, `description=fee_head.name`
- Wrapped in `transaction.atomic()`
- Response: `{ message: "Generated X invoices", count: X }`

### Create Notification (POST `/notifications/`)
- Role can only target roles ≤ their own level (matches Node.js matrix)
- Resolve recipients by `target_class_id` > `target_branch_id` > global, filtered by `target_roles`
- Insert Notification + NotificationRecipient rows in `transaction.atomic()`
- Response includes `recipients_count`

### Create User (POST `/users/`)
- Bcrypt hash password
- `branch_admin` auto-assigns to their own branch if `branch_id` not provided
- Insert User + BranchUser in `transaction.atomic()`

---

## Migration Strategy

The existing models are dropped and replaced:

| Old Model | Replaced By |
|-----------|-------------|
| `api.User` | `api.User` (redesigned) |
| `api.Student` | `api.Student` (redesigned) |
| `api.Staff` | `api.User` with `role=teacher` or `role=branch_admin` |
| `api.Attendance` | `api.Attendance` (redesigned) |
| `api.Exam` | `academics.AcademicRecord` |
| `api.Fee` | `fees.Payment` |
| `api.Admission` | Removed (not in Node.js reference / frontend) |
| `api.Contact` | Removed (not in Node.js reference / frontend) |

Steps:
1. Delete all migration files under `api/migrations/` (keep `__init__.py`)
2. Remove old app entries from `INSTALLED_APPS` and add new domain apps
3. Run `makemigrations` for all apps in dependency order: `api` → `branches` → `classes` → `academics` → `timetable` → `notifications` → `fees`
4. Run `migrate` against a fresh (or reset) PostgreSQL database
5. Create a superuser with `role=company_admin` for initial access

---

## Error Response Format

All error responses:
```json
{ "message": "error description" }
```

HTTP status codes:
- `400` — missing/invalid fields
- `401` — no token
- `403` — insufficient role
- `404` — not found
- `409` — conflict (e.g. duplicate email)
- `500` — server error

---

## Validation Rules

| Field | Rule |
|-------|------|
| email | unique, valid email format |
| password (change) | min 6 characters |
| avatar_url | base64 string, validated by size (~2MB max) |
| role | must be one of the 5 defined roles |
| attendance status | `present`, `absent`, or `late` only |
| day_of_week | `Monday` through `Sunday` only |
| fee frequency | `monthly`, `quarterly`, `yearly`, `one-time` only |
| grade_score | numeric decimal |
| amount | numeric decimal |
