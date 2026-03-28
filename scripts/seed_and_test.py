#!/usr/bin/env python3
"""
Full API test + dashboard data seeder for School ERP.

Creates realistic data across all entities, then hits every endpoint to verify.

Usage:
    python scripts/seed_and_test.py                        # production
    python scripts/seed_and_test.py http://localhost:8000  # local
"""

import sys
import time
import json
import datetime
import requests

BASE_URL = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else "https://school-backend-docker.onrender.com"

# ── colours ──────────────────────────────────────────────────────────────────
G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; B = "\033[94m"; X = "\033[0m"
def ok(m):   print(f"    {G}✓{X} {m}")
def fail(m): print(f"    {R}✗{X} {m}"); FAILURES.append(m)
def head(m): print(f"\n{B}{'─'*55}{X}\n{B}  {m}{X}\n{B}{'─'*55}{X}")
def info(m): print(f"    {Y}→{X} {m}")

FAILURES = []
STATE = {}   # persists IDs across steps


# ── helpers ───────────────────────────────────────────────────────────────────
DELAY = 0.3   # seconds between requests (avoids overwhelming free-tier Render)


def _request(method, path, body=None, token=None, params=None, expect=None, timeout=30):
    hdrs = {"Content-Type": "application/json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    label = f"{method:<4} {path}"
    try:
        r = requests.request(method, f"{BASE_URL}{path}", json=body, headers=hdrs,
                             params=params, timeout=timeout)
        time.sleep(DELAY)
        codes = expect or ([200, 201, 409] if method == "POST" else [200, 201])
        if r.status_code in codes:
            ok(f"{label} → {r.status_code}")
            return r.json() if r.text else {}
        else:
            fail(f"{label} → {r.status_code}: {r.text[:120]}")
            return {}
    except requests.exceptions.Timeout:
        fail(f"{label} → timeout")
        return {}
    except requests.exceptions.RequestException as e:
        fail(f"{label} → {e}")
        return {}


def post(path, body, token=None, expect=None):
    return _request("POST", path, body=body, token=token, expect=expect)

def get(path, token=None, params=None):
    return _request("GET", path, token=token, params=params)

def put(path, body, token=None):
    return _request("PUT", path, body=body, token=token)


# ── seed data ─────────────────────────────────────────────────────────────────
CLASSES   = ["8", "9", "10", "11", "12"]
SUBJECTS  = ["Mathematics", "Science", "English", "History", "Computer Science"]
EXAM_TYPES = ["Unit Test", "Mid-Term", "Final"]

STAFF_SEED = [
    {"name": "Dr. Anita Sharma",  "designation": "Principal",        "email": "anita@school.test",  "phone": "9111000001"},
    {"name": "Mr. Ravi Kumar",    "designation": "Math Teacher",     "email": "ravi@school.test",   "phone": "9111000002"},
    {"name": "Ms. Priya Nair",    "designation": "Science Teacher",  "email": "priya@school.test",  "phone": "9111000003"},
    {"name": "Mr. Arjun Singh",   "designation": "English Teacher",  "email": "arjun@school.test",  "phone": "9111000004"},
    {"name": "Ms. Kavya Reddy",   "designation": "History Teacher",  "email": "kavya@school.test",  "phone": "9111000005"},
]

STUDENT_SEED = [
    {"name": "Aarav Patel",    "className": "10", "seatNumber": 1,  "gender": "Male"},
    {"name": "Diya Mehta",     "className": "10", "seatNumber": 2,  "gender": "Female"},
    {"name": "Karan Joshi",    "className": "10", "seatNumber": 3,  "gender": "Male"},
    {"name": "Sneha Gupta",    "className": "9",  "seatNumber": 1,  "gender": "Female"},
    {"name": "Rohan Das",      "className": "9",  "seatNumber": 2,  "gender": "Male"},
    {"name": "Ananya Iyer",    "className": "9",  "seatNumber": 3,  "gender": "Female"},
    {"name": "Vivek Sharma",   "className": "11", "seatNumber": 1,  "gender": "Male"},
    {"name": "Pooja Verma",    "className": "11", "seatNumber": 2,  "gender": "Female"},
    {"name": "Amit Tiwari",    "className": "12", "seatNumber": 1,  "gender": "Male"},
    {"name": "Riya Singh",     "className": "12", "seatNumber": 2,  "gender": "Female"},
]

ADMISSION_SEED = [
    {"studentName": "Rahul Bansal",  "classApplying": "8",  "gender": "Male",   "mobile": "9200000001",
     "fatherName": "Suresh Bansal", "motherName": "Meena Bansal",  "dob": "2012-05-15", "email": "rahul.b@test.com"},
    {"studentName": "Simran Kaur",   "classApplying": "9",  "gender": "Female", "mobile": "9200000002",
     "fatherName": "Gurpreet Kaur", "motherName": "Harjit Kaur",   "dob": "2011-08-22", "email": "simran.k@test.com"},
    {"studentName": "Dev Malhotra",  "classApplying": "10", "gender": "Male",   "mobile": "9200000003",
     "fatherName": "Anil Malhotra", "motherName": "Sunita Malhotra","dob": "2010-11-30", "email": "dev.m@test.com"},
    {"studentName": "Preethi Rao",   "classApplying": "11", "gender": "Female", "mobile": "9200000004",
     "fatherName": "Venkat Rao",    "motherName": "Lakshmi Rao",   "dob": "2009-03-10"},
    {"studentName": "Farhan Sheikh", "classApplying": "12", "gender": "Male",   "mobile": "9200000005",
     "fatherName": "Imran Sheikh",  "motherName": "Nadia Sheikh",  "dob": "2008-07-18"},
]

CONTACT_SEED = [
    {"name": "Rajesh Patel",   "email": "rajesh@test.com", "phone": "9300000001",
     "subject": "Fee Structure",    "message": "Please share the fee structure for Class 10."},
    {"name": "Sunita Mishra",  "email": "sunita@test.com", "phone": "9300000002",
     "subject": "Admission Query",  "message": "What are the admission requirements for Class 8?"},
    {"name": "Harish Nambiar", "email": "harish@test.com", "phone": "9300000003",
     "subject": "Transport Facility","message": "Is school bus available from Koramangala area?"},
]


# ─────────────────────────────────────────────────────────────────────────────
def step_auth():
    head("1 · AUTH — Register & Login")

    # Admin
    post("/api/auth/register", {"name": "Admin User", "email": "admin@school.test",
                                "password": "Admin@1234", "role": "admin", "contact": "9000000001"})
    res = post("/api/auth/login", {"email": "admin@school.test", "password": "Admin@1234", "role": "admin"}, expect=[200])
    STATE["token"] = res.get("token", "")
    if STATE["token"]:
        ok(f"Admin JWT obtained")
    else:
        fail("Admin login failed — subsequent tests may fail")

    # Staff user
    post("/api/auth/register", {"name": "Staff User", "email": "staff@school.test",
                                "password": "Staff@1234", "role": "staff", "contact": "9000000002"})
    post("/api/auth/login",    {"email": "staff@school.test", "password": "Staff@1234", "role": "staff"}, expect=[200])

    # Parent + Student for linking
    post("/api/auth/register", {"name": "Parent Sharma", "email": "parent@school.test",
                                "password": "Parent@1234", "role": "parent", "contact": "9000000003"})
    res_p = post("/api/auth/login", {"email": "parent@school.test", "password": "Parent@1234", "role": "parent"}, expect=[200])
    STATE["parent_id"] = res_p.get("user", {}).get("id")

    post("/api/auth/register", {"name": "Student Sharma", "email": "stu@school.test",
                                "password": "Stu@1234", "role": "student",
                                "className": "10", "rollNumber": "99"})
    post("/api/auth/login",    {"email": "stu@school.test", "password": "Stu@1234",
                                "role": "student", "className": "10", "rollNumber": "99"}, expect=[200])

    # Link parent → student
    if STATE.get("parent_id"):
        post("/api/auth/link-student", {"parentId": STATE["parent_id"], "rollNumber": "99"}, expect=[200, 400])


def step_staff():
    head("2 · STAFF — Create & List")
    staff_ids = []
    for s in STAFF_SEED:
        res = post("/api/staff/", s, expect=[201, 409])
        if res.get("id"):
            staff_ids.append(res["id"])

    all_staff = get("/api/staff/")
    STATE["staff_ids"] = [s["id"] for s in all_staff] if all_staff else staff_ids

    if STATE["staff_ids"]:
        sid = STATE["staff_ids"][0]
        put(f"/api/staff/{sid}", {"name": STAFF_SEED[0]["name"], "designation": "Head of School",
                                  "email": STAFF_SEED[0]["email"], "phone": STAFF_SEED[0]["phone"]})


def step_students():
    head("3 · STUDENTS — Create & List")
    for s in STUDENT_SEED:
        res = post("/api/students/", s, expect=[201, 409])
        if res.get("id") and "student_ids" not in STATE:
            STATE.setdefault("student_ids_by_class", {})

    all_students = get("/api/students/")
    if all_students:
        STATE["student_ids"] = [s["id"] for s in all_students]
        for s in all_students:
            STATE.setdefault("student_ids_by_class", {}).setdefault(s["class_name"], []).append(s["id"])
        ok(f"Total students in DB: {len(all_students)}")

    # Update one student
    if STATE.get("student_ids"):
        sid = STATE["student_ids"][0]
        put(f"/api/students/{sid}", {"name": "Aarav Patel (Updated)", "className": "10",
                                     "seatNumber": 1, "gender": "Male"})


def step_admissions():
    head("4 · ADMISSIONS — Create & List")
    admission_ids = []
    for a in ADMISSION_SEED:
        res = post("/api/admission/create", a, expect=[201, 400])
        if res.get("id"):
            admission_ids.append(res["id"])

    all_adm = get("/api/admission/")
    STATE["admission_ids"] = [a["id"] for a in all_adm] if all_adm else admission_ids
    ok(f"Total admissions in DB: {len(STATE['admission_ids'])}")

    # Detail + update one
    if STATE["admission_ids"]:
        aid = STATE["admission_ids"][0]
        get(f"/api/admission/{aid}")
        put(f"/api/admission/update/{aid}", {**ADMISSION_SEED[0], "address": "123 MG Road, Bangalore"})


def step_contacts():
    head("5 · CONTACTS — Submit & List")
    for c in CONTACT_SEED:
        post("/api/contact/", c, expect=[201])

    all_contacts = get("/api/contact/")
    STATE["contact_ids"] = [c["id"] for c in all_contacts] if all_contacts else []
    ok(f"Total contacts in DB: {len(STATE['contact_ids'])}")

    if STATE["contact_ids"]:
        get(f"/api/contact/{STATE['contact_ids'][0]}")


def step_attendance():
    head("6 · ATTENDANCE — Mark & Query")
    token = STATE.get("token", "")
    today = datetime.date.today()
    dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(7)]

    # Mark student attendance for last 7 days
    student_ids = STATE.get("student_ids", [])[:5]  # first 5 students
    for sid in student_ids:
        for i, date in enumerate(dates):
            att_status = "Present" if i % 5 != 4 else "Absent"   # 80% present
            post("/api/attendance/mark", {"userId": sid, "userType": "Student",
                                          "date": date, "status": att_status},
                 token=token, expect=[200])

    # Mark staff attendance for last 7 days
    staff_ids = STATE.get("staff_ids", [])[:3]
    for sfid in staff_ids:
        for i, date in enumerate(dates):
            att_status = "Present" if i % 6 != 5 else "Absent"   # ~83% present
            post("/api/attendance/mark", {"userId": sfid, "userType": "Staff",
                                          "date": date, "status": att_status},
                 token=token, expect=[200])

    # Query endpoints
    get("/api/attendance/students", token=token)
    get("/api/attendance/students", token=token, params={"className": "10", "date": dates[0]})
    get("/api/attendance/students/by-class", token=token, params={"className": "10"})
    get("/api/attendance/staff", token=token)
    get("/api/attendance/staff", token=token, params={"date": dates[0]})

    # Parent attendance view (requires a Student with parent_id set — informational only)
    if STATE.get("parent_id"):
        r = _request("GET", f"/api/attendance/parent/{STATE['parent_id']}", token=token, expect=[200, 404])
        if isinstance(r, dict) and r.get("message") == "No student linked to this parent":
            info("Parent attendance: no student linked via Student.parent_id (expected for seeded data)")


def step_fees():
    head("7 · FEES — Seed via Django ORM & Query")
    info("Fees are created via Django ORM (no REST create endpoint) — querying existing data")

    # Try to seed fee records directly if DB is accessible
    try:
        import os, django
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_backend.settings")
        django.setup()
        from api.models import Student, Fee
        from decimal import Decimal

        fee_data = [
            (Decimal("15000"), "Paid"),
            (Decimal("15000"), "Paid"),
            (Decimal("15000"), "Pending"),
            (Decimal("3000"),  "Paid"),
            (Decimal("2000"),  "Pending"),
        ]
        count = 0
        for student in Student.objects.all()[:5]:
            for amount, fee_status in fee_data:
                Fee.objects.get_or_create(student=student, amount=amount, status=fee_status)
                count += 1
        ok(f"Seeded {count} fee records via ORM")
    except Exception as e:
        info(f"ORM seed skipped (not running inside Django env): {e}")

    # Query fee endpoints
    for class_name in ["10", "9", "11"]:
        get(f"/api/fees/students/{class_name}")

    for sid in STATE.get("student_ids", [])[:3]:
        get(f"/api/fees/student/{sid}")


def summary():
    head("SUMMARY")
    total = len(FAILURES)
    if total == 0:
        print(f"\n  {G}All tests passed!{X} Dashboard data seeded successfully.\n")
        print(f"  {B}API Docs:{X} {BASE_URL}/api/docs/")
    else:
        print(f"\n  {R}{total} failure(s):{X}")
        for f in FAILURES:
            print(f"    {R}•{X} {f}")
    print()


# ── main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'═'*55}")
    print(f"  School ERP — Full API Test + Data Seeder")
    print(f"  Target: {BASE_URL}")
    print(f"{'═'*55}")

    step_auth()
    step_staff()
    step_students()
    step_admissions()
    step_contacts()
    step_attendance()
    step_fees()
    summary()

    sys.exit(0 if not FAILURES else 1)
