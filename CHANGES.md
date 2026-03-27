# School Backend — Django Rewrite Summary

Original project: `/home/kaushal/school_backend` (Node.js + Express + MongoDB)
Rewritten project: `/home/kaushal/repos/school_backend` (Django + DRF + PostgreSQL)

---

## Stack Changes

| Layer | Before | After |
|-------|--------|-------|
| Runtime | Node.js (ES Modules) | Python 3 |
| Framework | Express 5 | Django 5.0.6 + Django REST Framework 3.15.2 |
| Database | MongoDB Atlas (Mongoose) | PostgreSQL 16 (psycopg2) |
| Auth | jsonwebtoken (manual JWT) | djangorestframework-simplejwt |
| Password hashing | bcryptjs | Django's built-in `make_password` / `check_password` |
| CORS | cors npm package | django-cors-headers |
| Config | dotenv | python-decouple |
| DB container | None | Docker (`postgres:16-alpine`) |

---

## Project Structure

### Before (Node.js)
```
school_backend/
├── src/
│   ├── config/db.js
│   ├── models/          (8 Mongoose schemas)
│   ├── controllers/     (9 controller files)
│   ├── routes/          (9 route files)
│   └── middleware/authMiddleware.js
├── server.js
└── package.json
```

### After (Django)
```
school_backend/
├── school_backend/      (Django project config)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── api/                 (single Django app)
│   ├── models.py        (all 8 models)
│   ├── serializers.py   (all serializers)
│   ├── admin.py         (Django admin for all models)
│   ├── urls.py          (all routes)
│   ├── migrations/
│   └── views/
│       ├── auth_views.py
│       ├── student_views.py
│       ├── staff_views.py
│       ├── parent_views.py
│       ├── attendance_views.py
│       ├── admission_views.py
│       ├── contact_views.py
│       └── fee_views.py
├── manage.py
├── requirements.txt
└── .env
```

---

## Model Changes

### User
- Replaced Mongoose schema with Django `AbstractBaseUser` + `PermissionsMixin`
- Added custom `UserManager` with `create_user` / `create_superuser`
- `email` is the `USERNAME_FIELD` (login identifier), `username` field removed
- `studentId` (ref: User) → renamed to `linked_student_user` (ForeignKey to self, `role='student'`)
- Snake_case field names: `className` → `class_name`, `rollNumber` → `roll_number`

### Student
- `className` → `class_name`
- `seatNumber` → `seat_number`
- `parentId` → `parent` (ForeignKey to User, `role='parent'`)
- Unique constraint on `(seat_number, class_name)` — enforced at DB level

### Staff
- No structural changes, direct mapping

### Attendance
- Replaced MongoDB polymorphic `refPath` with two nullable ForeignKeys:
  - `student` → ForeignKey to `Student` (null if Staff record)
  - `staff_member` → ForeignKey to `Staff` (null if Student record)
- Unique DB constraints per type:
  - `unique_student_attendance_per_day` on `(student, date)`
  - `unique_staff_attendance_per_day` on `(staff_member, date)`
- `date` changed from `String` to `DateField`

### Admission
- `studentName` → `student_name`, `classApplying` → `class_applying`, etc.
- `dob` stored as `DateField` instead of plain `Date`

### Exam & Fee
- `studentId` → `student` (ForeignKey to `Student`)
- All fields snake_cased

### Contact
- No structural changes, direct mapping

---

## API Changes

All original endpoints preserved. Minor differences:

| Original (Node.js) | Django |
|---|---|
| `req.body.className` | accepts both `className` and `class_name` |
| `req.body.seatNumber` | accepts both `seatNumber` and `seat_number` |
| MongoDB `_id` (ObjectId string) | PostgreSQL `id` (integer) |
| `timestamps: true` → `createdAt/updatedAt` | `created_at` / `updated_at` |
| JWT payload: `{ id, role }` | JWT payload: `{ user_id }` (simplejwt standard) |
| Token key in response: `token` | Same: `token` + added `refresh` token |

### Endpoints (unchanged)
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/link-student

GET    /api/students/
POST   /api/students/
PUT    /api/students/:id
DELETE /api/students/:id

GET    /api/staff/
POST   /api/staff/
PUT    /api/staff/:id
DELETE /api/staff/:id

GET    /api/parent/dashboard          (JWT required)

POST   /api/attendance/mark           (JWT required)
GET    /api/attendance/students       (JWT required)
GET    /api/attendance/students/by-class  (JWT required)
GET    /api/attendance/staff          (JWT required)
GET    /api/attendance/parent/:id     (JWT required)

POST   /api/admission/create
GET    /api/admission/
GET    /api/admission/:id
PUT    /api/admission/update/:id
DELETE /api/admission/delete/:id

POST   /api/contact/
GET    /api/contact/
GET    /api/contact/:id
DELETE /api/contact/:id

GET    /api/fees/students/:className
GET    /api/fees/student/:id
```

---

## Auth Changes

| Aspect | Before | After |
|--------|--------|-------|
| Token generation | `jwt.sign({ id, role }, JWT_SECRET)` | `RefreshToken.for_user(user)` from simplejwt |
| Token verification | Manual middleware extracting Bearer token | `JWTAuthentication` class (DRF default) |
| Password hashing | `bcrypt.hash(password, 10)` | `make_password(password)` (PBKDF2 by default) |
| Password check | `bcrypt.compare(plain, hash)` | `check_password(plain, hash)` |
| Protected routes | `protect` middleware on route | `permission_classes = [IsAuthenticated]` on view |

---

## Key Logic Preserved

- **Student login** requires `email + role + className + rollNumber`
- **Attendance UPSERT** — `update_or_create()` replaces Mongoose `findOneAndUpdate({ upsert: true })`
- **Attendance clear** — `Not Marked` status deletes the record
- **Fee summary** — calculates `totalFees`, `paidFees`, `pendingFees` by iterating fee records
- **Parent dashboard** — returns linked student info + exams + fee summary (JWT protected)
- **Duplicate checks** — email uniqueness, seat number uniqueness per class

---

## New Additions

- **Django Admin** — all 8 models registered with list display, filters, and search
- **Migrations** — full schema managed via `api/migrations/0001_initial.py`
- **Refresh token** — login response now also returns a `refresh` token
- **Docker setup** — PostgreSQL runs in `school_postgres` Docker container

---

## Setup

```bash
cd /home/kaushal/repos/school_backend

# Start PostgreSQL
docker run -d --name school_postgres \
  -e POSTGRES_DB=school_db -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres123 -p 5432:5432 postgres:16-alpine

# Install & run
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit credentials
python manage.py migrate
python manage.py runserver 8080
```
