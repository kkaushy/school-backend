#!/usr/bin/env python3
"""
School ERP — Data Seeder

Creates a realistic hierarchy of data via the REST API:
  company_admin → branches → branch_admins → teachers → parents → students
  → classes → assignments → academics → timetable → fee heads → payments → notifications

Usage:
    python scripts/seed.py                        # hits localhost:5000
    python scripts/seed.py http://localhost:8000  # custom URL
    python scripts/seed.py https://your-app.onrender.com

The script is idempotent where possible (409 on duplicate email is treated as OK).
"""

import sys
import time
import json
import datetime
import requests

BASE_URL = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else "http://localhost:5000"

# ── colours ───────────────────────────────────────────────────────────────────
G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; B = "\033[94m"; X = "\033[0m"

FAILURES = []
STATE = {}  # persists IDs/tokens across steps
DELAY = 0.15  # seconds between requests


def ok(m):   print(f"    {G}✓{X} {m}")
def fail(m): print(f"    {R}✗{X} {m}"); FAILURES.append(m)
def head(m): print(f"\n{B}{'─'*60}{X}\n{B}  {m}{X}\n{B}{'─'*60}{X}")
def info(m): print(f"    {Y}→{X} {m}")


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _req(method, path, body=None, token=None, params=None, expect=None, label=None):
    hdrs = {"Content-Type": "application/json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    display = label or f"{method:<6} {path}"
    try:
        r = requests.request(
            method, f"{BASE_URL}{path}",
            json=body, headers=hdrs, params=params, timeout=30,
        )
        time.sleep(DELAY)
        default_ok = [200, 201, 400] if method == "POST" else [200, 201]
        codes = expect if expect is not None else default_ok
        if r.status_code in codes:
            ok(f"{display} → {r.status_code}")
            try:
                return r.json()
            except Exception:
                return {}
        else:
            fail(f"{display} → {r.status_code}: {r.text[:160]}")
            return {}
    except requests.exceptions.Timeout:
        fail(f"{display} → timeout")
        return {}
    except requests.exceptions.RequestException as e:
        fail(f"{display} → {e}")
        return {}


def post(path, body, token=None, expect=None, label=None):
    return _req("POST", path, body=body, token=token, expect=expect, label=label)


def get(path, token=None, params=None, label=None):
    return _req("GET", path, token=token, params=params, label=label)


def put(path, body, token=None, label=None):
    return _req("PUT", path, body=body, token=token, label=label)


def delete(path, token=None, label=None):
    return _req("DELETE", path, token=token, expect=[200], label=label)


# ── login helper ──────────────────────────────────────────────────────────────

def login(email, password):
    res = post("/api/auth/login/", {"email": email, "password": password},
               expect=[200], label=f"LOGIN {email}")
    return res.get("token", "")


# ── seed data ─────────────────────────────────────────────────────────────────

ADMIN_EMAIL    = "kkaushy@gmail.com"
ADMIN_PASSWORD = "RR5gL4zPnAM9!$#6"

BRANCHES = [
    {"name": "Main Campus",   "location": "Bangalore, MG Road"},
    {"name": "North Campus",  "location": "Bangalore, Hebbal"},
]

BRANCH_ADMINS = [
    {"name": "Priya Nair",    "email": "priya.admin@school.com",  "password": "Pass@1234", "role": "branch_admin", "designation": "Branch Head"},
    {"name": "Suresh Kumar",  "email": "suresh.admin@school.com", "password": "Pass@1234", "role": "branch_admin", "designation": "Branch Head"},
]

TEACHERS = [
    {"name": "Dr. Anita Sharma",  "email": "anita@school.com",  "password": "Pass@1234", "role": "teacher", "designation": "Math Teacher"},
    {"name": "Mr. Ravi Verma",    "email": "ravi@school.com",   "password": "Pass@1234", "role": "teacher", "designation": "Science Teacher"},
    {"name": "Ms. Kavya Reddy",   "email": "kavya@school.com",  "password": "Pass@1234", "role": "teacher", "designation": "English Teacher"},
    {"name": "Mr. Arjun Singh",   "email": "arjun@school.com",  "password": "Pass@1234", "role": "teacher", "designation": "History Teacher"},
]

PARENTS = [
    {"name": "Ramesh Patel",   "email": "ramesh.p@school.com", "password": "Pass@1234", "role": "parent"},
    {"name": "Sunita Sharma",  "email": "sunita.s@school.com", "password": "Pass@1234", "role": "parent"},
    {"name": "Vijay Mehta",    "email": "vijay.m@school.com",  "password": "Pass@1234", "role": "parent"},
    {"name": "Geeta Iyer",     "email": "geeta.i@school.com",  "password": "Pass@1234", "role": "parent"},
]

CLASSES = [
    {"name": "Class 8A"},
    {"name": "Class 9A"},
    {"name": "Class 10A"},
    {"name": "Class 11A"},
    {"name": "Class 12A"},
]

STUDENTS = [
    {"name": "Aarav Patel"},
    {"name": "Diya Mehta"},
    {"name": "Karan Joshi"},
    {"name": "Sneha Gupta"},
    {"name": "Rohan Das"},
    {"name": "Ananya Iyer"},
    {"name": "Vivek Tiwari"},
    {"name": "Pooja Verma"},
    {"name": "Amit Singh"},
    {"name": "Riya Sharma"},
    {"name": "Aryan Nair"},
    {"name": "Priya Das"},
]

TIMETABLE_SLOTS = [
    {"day_of_week": "Monday",    "start_time": "08:00:00", "end_time": "09:00:00", "subject_name": "Mathematics"},
    {"day_of_week": "Monday",    "start_time": "09:00:00", "end_time": "10:00:00", "subject_name": "Science"},
    {"day_of_week": "Tuesday",   "start_time": "08:00:00", "end_time": "09:00:00", "subject_name": "English"},
    {"day_of_week": "Tuesday",   "start_time": "09:00:00", "end_time": "10:00:00", "subject_name": "History"},
    {"day_of_week": "Wednesday", "start_time": "08:00:00", "end_time": "09:00:00", "subject_name": "Mathematics"},
    {"day_of_week": "Wednesday", "start_time": "09:00:00", "end_time": "10:00:00", "subject_name": "Computer Science"},
    {"day_of_week": "Thursday",  "start_time": "08:00:00", "end_time": "09:00:00", "subject_name": "Science"},
    {"day_of_week": "Friday",    "start_time": "08:00:00", "end_time": "09:00:00", "subject_name": "English"},
]

FEE_HEADS = [
    {"name": "Tuition Fee",     "amount": "15000.00", "frequency": "monthly",     "description": "Monthly tuition"},
    {"name": "Lab Fee",         "amount": "3000.00",  "frequency": "quarterly",   "description": "Science lab usage"},
    {"name": "Annual Fee",      "amount": "25000.00", "frequency": "yearly",      "description": "Annual school fee"},
    {"name": "Exam Fee",        "amount": "500.00",   "frequency": "one-time",    "description": "Examination registration"},
]

ACADEMIC_RECORDS = [
    {"term": "Term 1 2024", "subject_name": "Mathematics",      "grade_score": "87.50", "remarks": "Good performance"},
    {"term": "Term 1 2024", "subject_name": "Science",          "grade_score": "91.00", "remarks": "Excellent"},
    {"term": "Term 1 2024", "subject_name": "English",          "grade_score": "78.00", "remarks": "Needs improvement in writing"},
    {"term": "Term 2 2024", "subject_name": "Mathematics",      "grade_score": "92.50", "remarks": "Outstanding"},
    {"term": "Term 2 2024", "subject_name": "History",          "grade_score": "85.00", "remarks": "Well researched answers"},
    {"term": "Term 2 2024", "subject_name": "Computer Science", "grade_score": "95.00", "remarks": "Top of class"},
]


# ── steps ─────────────────────────────────────────────────────────────────────

def step_admin_login():
    head("1 · Admin Login")
    token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if token:
        STATE["admin_token"] = token
        ok("Admin token stored")
    else:
        info("Admin login failed — attempting to create admin user")
        # Try to create the admin user
        admin_data = {
            "name": "Admin User",
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD,
            "role": "company_admin"
        }
        res = post("/api/auth/register/", admin_data, expect=[200, 201, 400, 409])
        if res.get("message") or res.get("id"):
            ok("Admin user created")
            # Now try login again
            token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
            if token:
                STATE["admin_token"] = token
                ok("Admin token stored")
            else:
                fail("Admin login failed after creation — cannot continue seeding")
                sys.exit(1)
        else:
            fail("Admin user creation failed — cannot continue seeding")
            sys.exit(1)


def step_branches():
    head("2 · Branches")
    token = STATE["admin_token"]
    branch_ids = []

    for b in BRANCHES:
        res = post("/api/branches/", b, token=token, expect=[200, 201, 400],
                   label=f"POST branch:{b['name']}")
        if res.get("id"):
            branch_ids.append(res["id"])
            info(f"Branch id: {res['id']}")

    # If all already existed, fetch them
    if not branch_ids:
        all_branches = get("/api/branches/", token=token)
        if isinstance(all_branches, list):
            branch_ids = [b["id"] for b in all_branches]

    STATE["branch_ids"] = branch_ids
    info(f"Using {len(branch_ids)} branch(es): {branch_ids}")


def step_users():
    head("3 · Users (branch admins, teachers, parents)")
    token = STATE["admin_token"]
    branch_ids = STATE.get("branch_ids", [])
    if not branch_ids:
        fail("No branch IDs — skipping user creation")
        return

    branch_admin_ids = []
    teacher_ids = []
    parent_ids = []

    # Create branch admins — one per branch
    for i, user_data in enumerate(BRANCH_ADMINS):
        bid = branch_ids[i % len(branch_ids)]
        body = {**user_data, "branch_id": bid}
        res = post("/api/users/", body, token=token, expect=[200, 201, 400],
                   label=f"POST user:{user_data['email']}")
        if res.get("id"):
            branch_admin_ids.append(res["id"])

    # Create teachers — spread across branches
    for i, user_data in enumerate(TEACHERS):
        bid = branch_ids[i % len(branch_ids)]
        body = {**user_data, "branch_id": bid}
        res = post("/api/users/", body, token=token, expect=[200, 201, 400],
                   label=f"POST user:{user_data['email']}")
        if res.get("id"):
            teacher_ids.append(res["id"])

    # Create parents
    for i, user_data in enumerate(PARENTS):
        bid = branch_ids[i % len(branch_ids)]
        body = {**user_data, "branch_id": bid}
        res = post("/api/users/", body, token=token, expect=[200, 201, 400],
                   label=f"POST user:{user_data['email']}")
        if res.get("id"):
            parent_ids.append(res["id"])

    # Fetch all users if creation returned 400 (already exists)
    all_users = get("/api/users/", token=token)
    if isinstance(all_users, list):
        for u in all_users:
            if u["role"] == "branch_admin" and u["id"] not in branch_admin_ids:
                branch_admin_ids.append(u["id"])
            elif u["role"] == "teacher" and u["id"] not in teacher_ids:
                teacher_ids.append(u["id"])

    all_parents = get("/api/users/parents/", token=token)
    if isinstance(all_parents, list) and not parent_ids:
        parent_ids = [p["id"] for p in all_parents]

    STATE["teacher_ids"] = teacher_ids
    STATE["parent_ids"] = parent_ids
    info(f"Teachers: {len(teacher_ids)}, Parents: {len(parent_ids)}")


def step_students():
    head("4 · Students")
    token = STATE["admin_token"]
    branch_ids = STATE.get("branch_ids", [])
    parent_ids = STATE.get("parent_ids", [])
    if not branch_ids:
        fail("No branch IDs — skipping student creation")
        return

    student_ids = []
    for i, s in enumerate(STUDENTS):
        bid = branch_ids[i % len(branch_ids)]
        parent_id = parent_ids[i % len(parent_ids)] if parent_ids else None
        body = {"name": s["name"], "branch_id": bid}
        if parent_id:
            body["parent_id"] = parent_id
        res = post("/api/students/", body, token=token, expect=[200, 201, 400],
                   label=f"POST student:{s['name']}")
        if res.get("id"):
            student_ids.append(res["id"])

    if not student_ids:
        all_students = get("/api/students/", token=token)
        if isinstance(all_students, list):
            student_ids = [s["id"] for s in all_students]

    STATE["student_ids"] = student_ids
    info(f"Total students: {len(student_ids)}")


def step_classes():
    head("5 · Classes + Assignments")
    token = STATE["admin_token"]
    branch_ids = STATE.get("branch_ids", [])
    teacher_ids = STATE.get("teacher_ids", [])
    student_ids = STATE.get("student_ids", [])

    if not branch_ids:
        fail("No branch IDs — skipping class creation")
        return

    class_ids = []
    for i, c in enumerate(CLASSES):
        bid = branch_ids[i % len(branch_ids)]
        res = post("/api/classes/", {"name": c["name"], "branch_id": bid},
                   token=token, expect=[200, 201, 400],
                   label=f"POST class:{c['name']}")
        if res.get("id"):
            class_ids.append(res["id"])

    if not class_ids:
        all_classes = get("/api/classes/", token=token)
        if isinstance(all_classes, list):
            class_ids = [c["id"] for c in all_classes]

    STATE["class_ids"] = class_ids
    info(f"Total classes: {len(class_ids)}")

    # Assign teachers to classes
    for i, cid in enumerate(class_ids):
        if teacher_ids:
            tid = teacher_ids[i % len(teacher_ids)]
            post("/api/classes/assign-teacher/", {"class_id": cid, "teacher_id": tid},
                 token=token, expect=[200, 201, 400],
                 label=f"ASSIGN teacher→class[{i}]")

    # Assign students to classes (distribute evenly)
    students_per_class = max(1, len(student_ids) // max(len(class_ids), 1))
    for i, sid in enumerate(student_ids):
        cid = class_ids[i % len(class_ids)]
        post("/api/classes/assign-student/", {"class_id": cid, "student_id": sid},
             token=token, expect=[200, 201, 400],
             label=f"ASSIGN student[{i}]→class")


def step_timetable():
    head("6 · Timetable")
    token = STATE["admin_token"]
    class_ids = STATE.get("class_ids", [])
    teacher_ids = STATE.get("teacher_ids", [])

    if not class_ids:
        info("No classes — skipping timetable")
        return

    # Add timetable slots for the first 2 classes
    slot_ids = []
    for cid in class_ids[:2]:
        for i, slot in enumerate(TIMETABLE_SLOTS):
            tid = teacher_ids[i % len(teacher_ids)] if teacher_ids else None
            body = {**slot, "class_id": cid}
            if tid:
                body["teacher_id"] = tid
            res = post("/api/timetable/", body, token=token, expect=[200, 201, 400],
                       label=f"POST slot:{slot['day_of_week']} {slot['start_time']}")
            if res.get("id"):
                slot_ids.append(res["id"])

    STATE["timetable_slot_ids"] = slot_ids

    # Query timetable
    if class_ids:
        get("/api/timetable/", token=token, params={"class_id": class_ids[0]},
            label="GET timetable?class_id=...")


def step_academics():
    head("7 · Academic Records")
    token = STATE["admin_token"]
    student_ids = STATE.get("student_ids", [])
    class_ids = STATE.get("class_ids", [])

    if not student_ids or not class_ids:
        info("No students or classes — skipping academic records")
        return

    for i, sid in enumerate(student_ids[:6]):
        cid = class_ids[i % len(class_ids)]
        for rec in ACADEMIC_RECORDS[:2]:
            body = {
                "student_id": sid,
                "class_id": cid,
                **rec,
            }
            post("/api/academics/", body, token=token, expect=[200, 201, 400],
                 label=f"POST academic:{rec['subject_name']} student[{i}]")

    get("/api/academics/", token=token, label="GET academics")


def step_attendance():
    head("8 · Attendance")
    token = STATE["admin_token"]
    class_ids = STATE.get("class_ids", [])
    student_ids = STATE.get("student_ids", [])

    if not class_ids or not student_ids:
        info("No classes or students — skipping attendance")
        return

    today = datetime.date.today()
    dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(5)]

    # Mark attendance for first 2 classes over last 5 days
    for cid in class_ids[:2]:
        # Get students in this class
        class_student_ids = [
            student_ids[j]
            for j in range(len(student_ids))
            if j % len(class_ids) == class_ids.index(cid)
        ][:6]
        if not class_student_ids:
            class_student_ids = student_ids[:4]

        for i, date in enumerate(dates):
            records = [
                {
                    "student_id": sid,
                    "status": "present" if (j + i) % 5 != 4 else "absent"
                }
                for j, sid in enumerate(class_student_ids)
            ]
            post("/api/attendance/", {
                "class_id": cid,
                "date": date,
                "records": records,
            }, token=token, expect=[200, 201, 400],
            label=f"POST attendance class[0] {date}")

    # Query attendance
    if class_ids:
        get("/api/attendance/", token=token,
            params={"class_id": class_ids[0], "date": dates[0]},
            label="GET attendance?class_id=&date=")


def step_fees():
    head("9 · Fee Heads + Payments")
    token = STATE["admin_token"]
    branch_ids = STATE.get("branch_ids", [])
    student_ids = STATE.get("student_ids", [])

    if not branch_ids:
        info("No branches — skipping fees")
        return

    fee_head_ids = []
    for fh in FEE_HEADS:
        bid = branch_ids[0]
        res = post("/api/fee-heads/", {**fh, "branch_id": bid},
                   token=token, expect=[200, 201, 400],
                   label=f"POST fee-head:{fh['name']}")
        if res.get("id"):
            fee_head_ids.append(res["id"])

    if not fee_head_ids:
        all_fh = get("/api/fee-heads/", token=token)
        if isinstance(all_fh, list):
            fee_head_ids = [fh["id"] for fh in all_fh]

    STATE["fee_head_ids"] = fee_head_ids
    info(f"Fee heads: {len(fee_head_ids)}")

    # Generate invoices from first fee head for all students in branch
    if fee_head_ids:
        due_date = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        post("/api/fee-heads/generate-invoices/", {
            "fee_head_id": fee_head_ids[0],
            "due_date": due_date,
        }, token=token, expect=[200, 201, 400], label="POST generate-invoices")

    # Fetch payments
    all_payments = get("/api/payments/", token=token, label="GET payments")
    payment_ids = []
    if isinstance(all_payments, list):
        payment_ids = [p["id"] for p in all_payments]
        info(f"Total payments: {len(payment_ids)}")

    STATE["payment_ids"] = payment_ids

    # Mark 2 payments as paid
    for pid in payment_ids[:2]:
        put(f"/api/payments/{pid}/pay/", {}, token=token, label=f"PUT payment pay")


def step_notifications():
    head("10 · Notifications")
    token = STATE["admin_token"]
    branch_ids = STATE.get("branch_ids", [])
    class_ids = STATE.get("class_ids", [])

    notifications = [
        {
            "title": "School Annual Day",
            "message": "Annual day celebrations on 15th December. All students must attend.",
            "target_roles": ["student", "parent", "teacher"],
        },
        {
            "title": "Fee Reminder",
            "message": "Monthly tuition fee for November is due. Please pay by 10th.",
            "target_roles": ["parent"],
            "target_branch_id": branch_ids[0] if branch_ids else None,
        },
        {
            "title": "Staff Meeting",
            "message": "Mandatory staff meeting on Friday at 4 PM in the conference room.",
            "target_roles": ["teacher", "branch_admin"],
        },
        {
            "title": "Exam Schedule",
            "message": "Mid-term exams start from 20th November. Timetable posted on the noticeboard.",
            "target_roles": ["student"],
            "target_class_id": class_ids[0] if class_ids else None,
        },
    ]

    notification_ids = []
    for n in notifications:
        # Remove None values
        body = {k: v for k, v in n.items() if v is not None}
        res = post("/api/notifications/", body, token=token, expect=[200, 201, 400],
                   label=f"POST notification:{n['title'][:30]}")
        if res.get("id"):
            notification_ids.append(res["id"])

    STATE["notification_ids"] = notification_ids

    # Fetch notifications (as admin — admin sees own recipients list)
    get("/api/notifications/", token=token, label="GET notifications")

    # Mark one as read — use a teacher token since the first notification targets teachers
    teacher_token = None
    login_res = post("/api/auth/login/", {"email": TEACHERS[0]["email"], "password": TEACHERS[0]["password"]},
                     expect=[200], label="LOGIN teacher for notification test")
    if login_res.get("token"):
        teacher_token = login_res["token"]

    if notification_ids and teacher_token:
        put(f"/api/notifications/{notification_ids[0]}/read/", {}, token=teacher_token,
            label="PUT notification mark-read")
    elif notification_ids:
        fail("PUT notification mark-read — could not get teacher token")

    # Mark all as read (as teacher)
    if teacher_token:
        put("/api/notifications/read-all/", {}, token=teacher_token,
            label="PUT notifications read-all")


def step_profile():
    head("11 · Auth Profile Endpoints")
    token = STATE["admin_token"]

    get("/api/auth/profile/", token=token, label="GET profile")
    put("/api/auth/profile/", {"name": "Admin User", "email": ADMIN_EMAIL},
        token=token, label="PUT profile")
    put("/api/auth/password/", {
        "current_password": ADMIN_PASSWORD,
        "new_password": ADMIN_PASSWORD,
    }, token=token, label="PUT password (no-op change)")


def step_dashboard():
    head("12 · Dashboard Stats")
    token = STATE["admin_token"]
    get("/api/dashboard/stats/", token=token, label="GET dashboard/stats")


# ── summary ───────────────────────────────────────────────────────────────────

def summary():
    head("SUMMARY")
    total = len(FAILURES)
    if total == 0:
        print(f"\n  {G}All steps completed successfully!{X}")
    else:
        print(f"\n  {R}{total} failure(s):{X}")
        for f in FAILURES:
            print(f"    {R}•{X} {f}")

    print(f"\n  {B}State seeded:{X}")
    print(f"    Branches:      {len(STATE.get('branch_ids', []))}")
    print(f"    Teachers:      {len(STATE.get('teacher_ids', []))}")
    print(f"    Parents:       {len(STATE.get('parent_ids', []))}")
    print(f"    Students:      {len(STATE.get('student_ids', []))}")
    print(f"    Classes:       {len(STATE.get('class_ids', []))}")
    print(f"    Fee Heads:     {len(STATE.get('fee_head_ids', []))}")
    print(f"    Payments:      {len(STATE.get('payment_ids', []))}")
    print(f"    Notifications: {len(STATE.get('notification_ids', []))}")
    print(f"\n  {B}API Docs:{X} {BASE_URL}/api/docs/\n")


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{'═'*60}")
    print(f"  School ERP — Data Seeder")
    print(f"  Target: {BASE_URL}")
    print(f"{'═'*60}")

    step_admin_login()
    step_branches()
    step_users()
    step_students()
    step_classes()
    step_timetable()
    step_academics()
    step_attendance()
    step_fees()
    step_notifications()
    step_profile()
    step_dashboard()
    summary()

    sys.exit(0 if not FAILURES else 1)
