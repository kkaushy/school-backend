#!/usr/bin/env python3
"""
School ERP - Data Cleanup

Deletes all seeded data via the REST API, leaving only the company_admin
superuser account intact.

Deletion order (respects FK cascade):
  1. branches      → cascades: students, classes, fee-heads, payments,
                                timetable, attendance, academic records
  2. users         → non-admin users (teachers, branch-admins, parents)

Usage:
    python scripts/cleanup.py                        # hits localhost:5000
    python scripts/cleanup.py http://localhost:8000
    python scripts/cleanup.py https://school-backend-docker.onrender.com
"""

import sys
import time
import requests

BASE_URL = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else "http://localhost:5000"

G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; B = "\033[94m"; X = "\033[0m"

FAILURES = []
DELAY = 0.15

ADMIN_EMAIL    = "kkaushy@gmail.com"
ADMIN_PASSWORD = "RR5gL4zPnAM9!$#6"


def ok(m):   print(f"    {G}✓{X} {m}")
def fail(m): print(f"    {R}✗{X} {m}"); FAILURES.append(m)
def head(m): print(f"\n{B}{'─'*60}{X}\n{B}  {m}{X}\n{B}{'─'*60}{X}")
def info(m): print(f"    {Y}→{X} {m}")


def _req(method, path, token=None, expect=None, label=None):
    path = path.rstrip('/')
    hdrs = {"Content-Type": "application/json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    display = label or f"{method:<6} {path}"
    try:
        r = requests.request(method, f"{BASE_URL}{path}", headers=hdrs, timeout=30)
        time.sleep(DELAY)
        codes = expect if expect is not None else [200, 201]
        if r.status_code in codes:
            ok(f"{display} → {r.status_code}")
            try:
                return r.json()
            except Exception:
                return {}
        else:
            fail(f"{display} → {r.status_code}: {r.text[:120]}")
            return {}
    except requests.exceptions.RequestException as e:
        fail(f"{display} → {e}")
        return {}


def get(path, token=None, label=None):
    return _req("GET", path, token=token, label=label)


def delete(path, token=None, label=None):
    return _req("DELETE", path, token=token, expect=[200, 204], label=label)


def login(email, password):
    hdrs = {"Content-Type": "application/json"}
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password},
                      headers=hdrs, timeout=30)
    if r.status_code == 200:
        ok(f"LOGIN {email} → 200")
        return r.json().get("token", "")
    fail(f"LOGIN {email} → {r.status_code}")
    return ""


print(f"\n{'═'*60}")
print(f"  School ERP — Cleanup")
print(f"  Target: {BASE_URL}")
print(f"{'═'*60}")

head("Login")
token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
if not token:
    print(f"\n{R}Cannot login — aborting.{X}\n")
    sys.exit(1)

# ── 1. Delete branches (cascades everything beneath) ─────────────────────────
head("Delete Branches (cascades students, classes, fees, attendance…)")
branches = get("/api/branches", token=token, label="GET branches")
if isinstance(branches, list):
    info(f"Found {len(branches)} branch(es)")
    for b in branches:
        delete(f"/api/branches/{b['id']}", token=token,
               label=f"DELETE branch:{b['name']}")
else:
    info("No branches found or unexpected response")

# ── 2. Delete non-admin users ─────────────────────────────────────────────────
head("Delete Non-Admin Users (teachers, branch admins, parents)")
users = get("/api/users", token=token, label="GET users")
if isinstance(users, list):
    non_admin = [u for u in users if u.get('role') != 'company_admin']
    info(f"Found {len(non_admin)} non-admin user(s) (skipping company_admins)")
    for u in non_admin:
        delete(f"/api/users/{u['id']}", token=token,
               label=f"DELETE user:{u['email']} [{u['role']}]")
else:
    info("No users found or unexpected response")

# ── summary ───────────────────────────────────────────────────────────────────
head("SUMMARY")
if not FAILURES:
    print(f"\n  {G}Cleanup completed — database is clean.{X}\n")
else:
    print(f"\n  {R}{len(FAILURES)} failure(s):{X}")
    for f in FAILURES:
        print(f"    {R}•{X} {f}")

sys.exit(0 if not FAILURES else 1)
