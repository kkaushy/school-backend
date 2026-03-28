#!/usr/bin/env python3
"""
Test script: creates users for each role and validates them via the auth API.
Usage:
    python scripts/test_auth.py                        # uses production URL
    python scripts/test_auth.py http://localhost:8000  # uses local server
"""

import sys
import requests

BASE_URL = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else "https://school-backend-docker.onrender.com"

REGISTER = f"{BASE_URL}/api/auth/register"
LOGIN    = f"{BASE_URL}/api/auth/login"

USERS = [
    {
        "name": "Admin User",
        "email": "admin@school.test",
        "password": "Admin@1234",
        "role": "admin",
        "contact": "9000000001",
    },
    {
        "name": "Staff Member",
        "email": "staff@school.test",
        "password": "Staff@1234",
        "role": "staff",
        "contact": "9000000002",
    },
    {
        "name": "Parent User",
        "email": "parent@school.test",
        "password": "Parent@1234",
        "role": "parent",
        "contact": "9000000003",
    },
    {
        "name": "Student One",
        "email": "student@school.test",
        "password": "Student@1234",
        "role": "student",
        "className": "10",
        "rollNumber": "101",
    },
]

LOGIN_EXTRAS = {
    "student@school.test": {"className": "10", "rollNumber": "101"},
}

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

def ok(msg):  print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg): print(f"  {RED}✗{RESET} {msg}")
def info(msg): print(f"  {YELLOW}→{RESET} {msg}")


def register(user):
    print(f"\n[REGISTER] {user['role'].upper()} — {user['email']}")
    r = requests.post(REGISTER, json=user, timeout=30)
    if r.status_code == 201:
        ok(f"Registered  (id={r.json()['user']['id']})")
        return True
    elif r.status_code == 409:
        info(f"Already exists — skipping")
        return True
    else:
        fail(f"HTTP {r.status_code}: {r.text}")
        return False


def login(user):
    print(f"\n[LOGIN]    {user['role'].upper()} — {user['email']}")
    payload = {
        "email":    user["email"],
        "password": user["password"],
        "role":     user["role"],
        **LOGIN_EXTRAS.get(user["email"], {}),
    }
    r = requests.post(LOGIN, json=payload, timeout=30)
    if r.status_code == 200:
        data = r.json()
        ok(f"Token obtained")
        ok(f"User: {data['user']['name']} | role={data['user']['role']}")
        return True
    else:
        fail(f"HTTP {r.status_code}: {r.text}")
        return False


def main():
    print(f"\n{'='*55}")
    print(f"  School ERP — Auth API Test")
    print(f"  Target: {BASE_URL}")
    print(f"{'='*55}")

    passed = failed = 0

    for user in USERS:
        if register(user):
            passed += 1
        else:
            failed += 1

        if login(user):
            passed += 1
        else:
            failed += 1

    print(f"\n{'='*55}")
    print(f"  Results: {GREEN}{passed} passed{RESET}  {RED}{failed} failed{RESET}")
    print(f"{'='*55}\n")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
