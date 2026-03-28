# School ERP Backend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully replace the existing Django backend with a Node.js-aligned implementation across 7 domain apps, matching the frontend API contract exactly.

**Architecture:** Single PostgreSQL database, 7 Django apps (`api`, `branches`, `classes`, `academics`, `timetable`, `notifications`, `fees`), all views use `APIView`, JWT auth via simplejwt, role-based access via a shared `require_roles` decorator.

**Tech Stack:** Django 5.0.6, DRF 3.15.2, simplejwt 5.3.1, drf-spectacular 0.29.0, psycopg2, bcrypt (add to requirements), PostgreSQL (ArrayField for notifications).

---

## File Map

### New / Replaced Files

```
requirements.txt                          add bcrypt
school_backend/settings.py               add new apps, update SPECTACULAR enum
school_backend/urls.py                   add new app URL includes

api/models.py                            full rewrite: User, Student, Attendance
api/serializers.py                       full rewrite
api/permissions.py                       NEW: require_roles decorator + scope helpers
api/urls.py                              full rewrite
api/views/auth_views.py                  full rewrite
api/views/user_views.py                  NEW
api/views/student_views.py               full rewrite
api/views/attendance_views.py            full rewrite
api/views/dashboard_views.py            NEW
api/migrations/                          delete all, regenerate

branches/                                NEW app
  __init__.py
  apps.py
  models.py                             Branch, BranchUser
  serializers.py
  views.py
  urls.py
  migrations/

classes/                                 NEW app
  __init__.py
  apps.py
  models.py                             Class, ClassStudent, ClassTeacher
  serializers.py
  views.py
  urls.py
  migrations/

academics/                               NEW app
  __init__.py
  apps.py
  models.py                             AcademicRecord
  serializers.py
  views.py
  urls.py
  migrations/

timetable/                               NEW app
  __init__.py
  apps.py
  models.py                             TimetableSlot
  serializers.py
  views.py
  urls.py
  migrations/

notifications/                           NEW app
  __init__.py
  apps.py
  models.py                             Notification, NotificationRecipient
  serializers.py
  views.py
  urls.py
  migrations/

fees/                                    NEW app
  __init__.py
  apps.py
  models.py                             FeeHead, Payment
  serializers.py
  views.py
  urls.py
  migrations/
```

---

## Task 1: Teardown & Dependencies

**Files:**
- Modify: `requirements.txt`
- Modify: `api/migrations/` (delete migration files)

- [ ] **Step 1: Add bcrypt to requirements**

```
# requirements.txt — add this line
bcrypt==4.1.3
```

- [ ] **Step 2: Install it**

```bash
pip install bcrypt==4.1.3
```

- [ ] **Step 3: Delete old migration files (keep __init__.py)**

```bash
find /home/kaushal/repos/school_backend/api/migrations -name "*.py" ! -name "__init__.py" -delete
# Also clear __pycache__
find /home/kaushal/repos/school_backend/api/migrations -name "*.pyc" -delete
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt api/migrations/
git commit -m "chore: add bcrypt, clear old migrations for redesign"
```

---

## Task 2: Permissions & Auth Utilities

**Files:**
- Create: `api/permissions.py`

This file is a dependency for every view — implement it first.

- [ ] **Step 1: Write failing test**

Create `api/tests/test_permissions.py`:

```python
import pytest
from unittest.mock import MagicMock
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response
from api.permissions import require_roles

class MockView(APIView):
    @require_roles('company_admin', 'branch_admin')
    def get(self, request):
        return Response({'ok': True})

factory = APIRequestFactory()

def make_request(role):
    request = factory.get('/')
    request.user = MagicMock()
    request.user.role = role
    request.user.is_authenticated = True
    return request

def test_allowed_role_passes():
    view = MockView.as_view()
    request = make_request('company_admin')
    response = view(request)
    assert response.status_code == 200

def test_forbidden_role_blocked():
    view = MockView.as_view()
    request = make_request('student')
    response = view(request)
    assert response.status_code == 403

def test_unauthenticated_blocked():
    view = MockView.as_view()
    request = factory.get('/')
    request.user = MagicMock()
    request.user.is_authenticated = False
    response = view(request)
    assert response.status_code == 401
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/kaushal/repos/school_backend
python -m pytest api/tests/test_permissions.py -v
```

Expected: ImportError or AttributeError — `api/permissions.py` does not exist.

- [ ] **Step 3: Create `api/permissions.py`**

```python
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def require_roles(*roles):
    """Decorator for APIView methods. Checks request.user.role is in allowed roles."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return Response({'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            if request.user.role not in roles:
                return Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator
```

- [ ] **Step 4: Create `api/tests/__init__.py`**

```bash
mkdir -p /home/kaushal/repos/school_backend/api/tests
touch /home/kaushal/repos/school_backend/api/tests/__init__.py
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python -m pytest api/tests/test_permissions.py -v
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add api/permissions.py api/tests/
git commit -m "feat: add require_roles permission decorator"
```

---

## Task 3: New App Scaffolding

**Files:** All 6 new app directories.

- [ ] **Step 1: Create app directories and boilerplate**

```bash
cd /home/kaushal/repos/school_backend
for app in branches classes academics timetable notifications fees; do
  python manage.py startapp $app
  mkdir -p $app/tests
  touch $app/tests/__init__.py
done
```

- [ ] **Step 2: Verify structure**

```bash
ls branches/ classes/ academics/ timetable/ notifications/ fees/
```

Expected: each has `models.py`, `views.py`, `apps.py`, `admin.py`, `tests/`.

- [ ] **Step 3: Create `urls.py` stubs for each new app**

For each of `branches`, `classes`, `academics`, `timetable`, `notifications`, `fees`, create `<app>/urls.py`:

```python
from django.urls import path

urlpatterns = []
```

- [ ] **Step 4: Update `school_backend/settings.py` — add new apps**

In `INSTALLED_APPS`, replace `'api'` section:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',
    'api',
    'branches',
    'classes',
    'academics',
    'timetable',
    'notifications',
    'fees',
]
```

Also update `SPECTACULAR_SETTINGS` enum overrides:

```python
'ENUM_NAME_OVERRIDES': {
    'UserRoleEnum': ['company_admin', 'branch_admin', 'teacher', 'parent', 'student'],
},
```

- [ ] **Step 5: Update `school_backend/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/', include('branches.urls')),
    path('api/', include('classes.urls')),
    path('api/', include('academics.urls')),
    path('api/', include('timetable.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('fees.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

- [ ] **Step 6: Commit**

```bash
git add branches/ classes/ academics/ timetable/ notifications/ fees/ school_backend/settings.py school_backend/urls.py
git commit -m "feat: scaffold 6 new domain apps"
```

---

## Task 4: `api` App — User & Student Models

**Files:**
- Modify: `api/models.py` (full rewrite)
- Modify: `api/serializers.py` (full rewrite)

- [ ] **Step 1: Rewrite `api/models.py`**

```python
import uuid
import bcrypt
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'company_admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('name', 'Admin')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('company_admin', 'Company Admin'),
        ('branch_admin', 'Branch Admin'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    designation = models.TextField(blank=True, null=True)
    avatar_url = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def set_password(self, raw_password):
        hashed = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashed.decode('utf-8')

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} ({self.role})"


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='students')
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_profile')
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children', limit_choices_to={'role': 'parent'})
    name = models.CharField(max_length=255)
    enrollment_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'students'

    def __str__(self):
        return self.name


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    class_ref = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='attendance_records')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance'
        unique_together = ('student', 'date', 'class_ref')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
```

- [ ] **Step 2: Rewrite `api/serializers.py`**

```python
from rest_framework import serializers
from .models import User, Student, Attendance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'designation', 'avatar_url', 'created_at']


class StudentSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, default=None)

    class Meta:
        model = Student
        fields = ['id', 'name', 'branch_id', 'branch_name', 'parent_id', 'parent_name', 'enrollment_date', 'created_at']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'student_id', 'class_ref_id', 'branch_id', 'date', 'status', 'created_at']
```

- [ ] **Step 3: Check for circular import issues by running Django check**

```bash
python manage.py check
```

Expected: May fail because `branches` app models don't exist yet — that's fine. Proceed to Task 5.

- [ ] **Step 4: Commit**

```bash
git add api/models.py api/serializers.py
git commit -m "feat: rewrite api User, Student, Attendance models"
```

---

## Task 5: `branches` App — Models & Views

**Files:**
- Create: `branches/models.py`
- Create: `branches/serializers.py`
- Create: `branches/views.py`
- Modify: `branches/urls.py`

- [ ] **Step 1: Write `branches/models.py`**

```python
import uuid
from django.db import models


class Branch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    company_admin = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='branches')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'branches'

    def __str__(self):
        return self.name


class BranchUser(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch_users')
    user = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='branch_memberships')

    class Meta:
        db_table = 'branch_users'
        unique_together = ('branch', 'user')
```

- [ ] **Step 2: Write `branches/serializers.py`**

```python
from rest_framework import serializers
from .models import Branch


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'location', 'company_admin_id', 'created_at']
```

- [ ] **Step 3: Write failing test for branches views**

Create `branches/tests/test_views.py`:

```python
import pytest
from unittest.mock import MagicMock, patch
import uuid
from rest_framework.test import APIRequestFactory
from branches.views import BranchListCreateView

factory = APIRequestFactory()

def make_user(role):
    user = MagicMock()
    user.id = uuid.uuid4()
    user.role = role
    user.is_authenticated = True
    return user

@pytest.mark.django_db
def test_list_branches_requires_auth():
    view = BranchListCreateView.as_view()
    request = factory.get('/api/branches/')
    request.user = MagicMock(is_authenticated=False)
    response = view(request)
    assert response.status_code == 401

@pytest.mark.django_db
def test_create_branch_requires_company_admin():
    view = BranchListCreateView.as_view()
    request = factory.post('/api/branches/', {'name': 'Main', 'location': 'City'}, format='json')
    request.user = make_user('teacher')
    response = view(request)
    assert response.status_code == 403
```

- [ ] **Step 4: Run test to verify it fails**

```bash
python -m pytest branches/tests/test_views.py -v
```

Expected: ImportError — `branches/views.py` has no `BranchListCreateView`.

- [ ] **Step 5: Write `branches/views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Branch, BranchUser
from .serializers import BranchSerializer
from api.permissions import require_roles


class BranchListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'company_admin':
            branches = Branch.objects.filter(company_admin=user)
        else:
            branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
            branches = Branch.objects.filter(id__in=branch_ids)
        return Response(BranchSerializer(branches, many=True).data)

    @require_roles('company_admin')
    def post(self, request):
        name = request.data.get('name')
        if not name:
            return Response({'message': 'name is required'}, status=status.HTTP_400_BAD_REQUEST)
        branch = Branch.objects.create(
            name=name,
            location=request.data.get('location'),
            company_admin=request.user,
        )
        return Response(BranchSerializer(branch).data, status=status.HTTP_201_CREATED)


class BranchDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _get_branch(self, pk, user):
        try:
            branch = Branch.objects.get(pk=pk)
        except Branch.DoesNotExist:
            return None, Response({'message': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)
        if user.role == 'company_admin' and branch.company_admin != user:
            return None, Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        return branch, None

    @require_roles('company_admin')
    def put(self, request, pk):
        branch, err = self._get_branch(pk, request.user)
        if err:
            return err
        if 'name' in request.data:
            branch.name = request.data['name']
        if 'location' in request.data:
            branch.location = request.data['location']
        branch.save()
        return Response(BranchSerializer(branch).data)

    @require_roles('company_admin')
    def delete(self, request, pk):
        branch, err = self._get_branch(pk, request.user)
        if err:
            return err
        branch.delete()
        return Response({'message': 'Branch deleted successfully'})
```

- [ ] **Step 6: Update `branches/urls.py`**

```python
from django.urls import path
from .views import BranchListCreateView, BranchDetailView

urlpatterns = [
    path('branches/', BranchListCreateView.as_view(), name='branch-list-create'),
    path('branches/<uuid:pk>/', BranchDetailView.as_view(), name='branch-detail'),
]
```

- [ ] **Step 7: Create `branches/tests/__init__.py`**

```bash
touch /home/kaushal/repos/school_backend/branches/tests/__init__.py
```

- [ ] **Step 8: Run tests**

```bash
python -m pytest branches/tests/test_views.py -v
```

Expected: 2 passed.

- [ ] **Step 9: Commit**

```bash
git add branches/
git commit -m "feat: add branches app with CRUD endpoints"
```

---

## Task 6: `classes` App — Models & Views

**Files:**
- Create: `classes/models.py`
- Create: `classes/serializers.py`
- Create: `classes/views.py`
- Modify: `classes/urls.py`

- [ ] **Step 1: Write `classes/models.py`**

```python
import uuid
from django.db import models


class Class(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classes'

    def __str__(self):
        return f"{self.name} ({self.branch.name})"


class ClassStudent(models.Model):
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_students')
    student = models.ForeignKey('api.Student', on_delete=models.CASCADE, related_name='class_enrollments')

    class Meta:
        db_table = 'class_students'
        unique_together = ('class_ref', 'student')


class ClassTeacher(models.Model):
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='class_teachers')
    teacher = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='teaching_classes')

    class Meta:
        db_table = 'class_teachers'
        unique_together = ('class_ref', 'teacher')
```

- [ ] **Step 2: Write `classes/serializers.py`**

```python
from rest_framework import serializers
from .models import Class


class ClassSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Class
        fields = ['id', 'name', 'branch_id', 'branch_name', 'created_at']
```

- [ ] **Step 3: Write `classes/views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Class, ClassStudent, ClassTeacher
from .serializers import ClassSerializer
from api.permissions import require_roles
from branches.models import BranchUser


def get_accessible_classes(user):
    if user.role == 'company_admin':
        branch_ids = user.branches.values_list('id', flat=True)
        return Class.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'branch_admin':
        branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
        return Class.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'teacher':
        class_ids = ClassTeacher.objects.filter(teacher=user).values_list('class_ref_id', flat=True)
        return Class.objects.filter(id__in=class_ids)
    return Class.objects.none()


class ClassListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        classes = get_accessible_classes(request.user)
        return Response(ClassSerializer(classes, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        name = request.data.get('name')
        branch_id = request.data.get('branch_id')
        if not name or not branch_id:
            return Response({'message': 'name and branch_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        cls = Class.objects.create(name=name, branch_id=branch_id)
        return Response(ClassSerializer(cls).data, status=status.HTTP_201_CREATED)


class ClassDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            cls = Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            return Response({'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        cls.delete()
        return Response({'message': 'Class deleted successfully'})


class AssignTeacherView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        class_id = request.data.get('class_id')
        teacher_id = request.data.get('teacher_id')
        if not class_id or not teacher_id:
            return Response({'message': 'class_id and teacher_id required'}, status=status.HTTP_400_BAD_REQUEST)
        ClassTeacher.objects.get_or_create(class_ref_id=class_id, teacher_id=teacher_id)
        return Response({'message': 'Teacher assigned successfully'})


class AssignStudentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin', 'teacher')
    def post(self, request):
        class_id = request.data.get('class_id')
        student_id = request.data.get('student_id')
        if not class_id or not student_id:
            return Response({'message': 'class_id and student_id required'}, status=status.HTTP_400_BAD_REQUEST)
        ClassStudent.objects.get_or_create(class_ref_id=class_id, student_id=student_id)
        return Response({'message': 'Student assigned successfully'})
```

- [ ] **Step 4: Update `classes/urls.py`**

```python
from django.urls import path
from .views import ClassListCreateView, ClassDetailView, AssignTeacherView, AssignStudentView

urlpatterns = [
    path('classes/', ClassListCreateView.as_view(), name='class-list-create'),
    path('classes/<uuid:pk>/', ClassDetailView.as_view(), name='class-detail'),
    path('classes/assign-teacher/', AssignTeacherView.as_view(), name='class-assign-teacher'),
    path('classes/assign-student/', AssignStudentView.as_view(), name='class-assign-student'),
]
```

- [ ] **Step 5: Commit**

```bash
git add classes/
git commit -m "feat: add classes app with CRUD and assign endpoints"
```

---

## Task 7: `academics` App

**Files:**
- Create: `academics/models.py`
- Create: `academics/serializers.py`
- Create: `academics/views.py`
- Modify: `academics/urls.py`

- [ ] **Step 1: Write `academics/models.py`**

```python
import uuid
from django.db import models


class AcademicRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('api.Student', on_delete=models.CASCADE, related_name='academic_records')
    class_ref = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='academic_records')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE)
    term = models.CharField(max_length=100)
    subject_name = models.CharField(max_length=255)
    grade_score = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'academic_records'

    def __str__(self):
        return f"{self.student.name} - {self.subject_name} ({self.term})"
```

- [ ] **Step 2: Write `academics/serializers.py`**

```python
from rest_framework import serializers
from .models import AcademicRecord


class AcademicRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    class_name = serializers.CharField(source='class_ref.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = AcademicRecord
        fields = ['id', 'student_id', 'student_name', 'class_ref_id', 'class_name',
                  'branch_id', 'branch_name', 'term', 'subject_name', 'grade_score', 'remarks', 'created_at']
```

- [ ] **Step 3: Write `academics/views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import AcademicRecord
from .serializers import AcademicRecordSerializer
from api.permissions import require_roles
from branches.models import BranchUser
from classes.models import ClassTeacher, ClassStudent


def get_accessible_records(user):
    if user.role == 'company_admin':
        branch_ids = user.branches.values_list('id', flat=True)
        return AcademicRecord.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'branch_admin':
        branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
        return AcademicRecord.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'teacher':
        class_ids = ClassTeacher.objects.filter(teacher=user).values_list('class_ref_id', flat=True)
        return AcademicRecord.objects.filter(class_ref_id__in=class_ids)
    elif user.role == 'parent':
        student_ids = user.children.values_list('id', flat=True)
        return AcademicRecord.objects.filter(student_id__in=student_ids)
    elif user.role == 'student':
        try:
            return AcademicRecord.objects.filter(student=user.student_profile)
        except Exception:
            return AcademicRecord.objects.none()
    return AcademicRecord.objects.none()


class AcademicRecordListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        records = get_accessible_records(request.user)
        return Response(AcademicRecordSerializer(records, many=True).data)

    @require_roles('company_admin', 'branch_admin', 'teacher')
    def post(self, request):
        required = ['student_id', 'class_id', 'term', 'subject_name', 'grade_score']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        cls_id = request.data['class_id']
        from classes.models import Class
        try:
            cls = Class.objects.get(pk=cls_id)
        except Class.DoesNotExist:
            return Response({'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        record = AcademicRecord.objects.create(
            student_id=request.data['student_id'],
            class_ref_id=cls_id,
            branch=cls.branch,
            term=request.data['term'],
            subject_name=request.data['subject_name'],
            grade_score=request.data['grade_score'],
            remarks=request.data.get('remarks'),
        )
        return Response(AcademicRecordSerializer(record).data, status=status.HTTP_201_CREATED)
```

- [ ] **Step 4: Update `academics/urls.py`**

```python
from django.urls import path
from .views import AcademicRecordListCreateView

urlpatterns = [
    path('academics/', AcademicRecordListCreateView.as_view(), name='academic-list-create'),
]
```

- [ ] **Step 5: Commit**

```bash
git add academics/
git commit -m "feat: add academics app with grade record endpoints"
```

---

## Task 8: `timetable` App

**Files:**
- Create: `timetable/models.py`
- Create: `timetable/serializers.py`
- Create: `timetable/views.py`
- Modify: `timetable/urls.py`

- [ ] **Step 1: Write `timetable/models.py`**

```python
import uuid
from django.db import models

DAY_CHOICES = [
    ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday'),
]


class TimetableSlot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_ref = models.ForeignKey('classes.Class', on_delete=models.CASCADE, related_name='timetable_slots')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject_name = models.CharField(max_length=255)
    teacher = models.ForeignKey('api.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='timetable_slots')
    room = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'timetable_slots'
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.class_ref.name} - {self.day_of_week} {self.start_time}"
```

- [ ] **Step 2: Write `timetable/serializers.py`**

```python
from rest_framework import serializers
from .models import TimetableSlot


class TimetableSlotSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='class_ref.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True, default=None)
    teacher_designation = serializers.CharField(source='teacher.designation', read_only=True, default=None)

    class Meta:
        model = TimetableSlot
        fields = ['id', 'class_ref_id', 'class_name', 'branch_id', 'branch_name',
                  'day_of_week', 'start_time', 'end_time', 'subject_name',
                  'teacher_id', 'teacher_name', 'teacher_designation', 'room', 'created_at']
```

- [ ] **Step 3: Write `timetable/views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import TimetableSlot
from .serializers import TimetableSlotSerializer
from api.permissions import require_roles
from branches.models import BranchUser
from classes.models import ClassTeacher, ClassStudent


def get_accessible_slots(user, class_id=None):
    if user.role == 'company_admin':
        branch_ids = user.branches.values_list('id', flat=True)
        qs = TimetableSlot.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'branch_admin':
        branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
        qs = TimetableSlot.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'teacher':
        class_ids = ClassTeacher.objects.filter(teacher=user).values_list('class_ref_id', flat=True)
        qs = TimetableSlot.objects.filter(class_ref_id__in=class_ids)
    elif user.role == 'parent':
        student_ids = user.children.values_list('id', flat=True)
        class_ids = ClassStudent.objects.filter(student_id__in=student_ids).values_list('class_ref_id', flat=True)
        qs = TimetableSlot.objects.filter(class_ref_id__in=class_ids)
    elif user.role == 'student':
        try:
            class_ids = ClassStudent.objects.filter(student=user.student_profile).values_list('class_ref_id', flat=True)
            qs = TimetableSlot.objects.filter(class_ref_id__in=class_ids)
        except Exception:
            qs = TimetableSlot.objects.none()
    else:
        qs = TimetableSlot.objects.none()
    if class_id:
        qs = qs.filter(class_ref_id=class_id)
    return qs


class TimetableListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        class_id = request.query_params.get('class_id')
        slots = get_accessible_slots(request.user, class_id)
        return Response(TimetableSlotSerializer(slots, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        required = ['class_id', 'day_of_week', 'start_time', 'end_time', 'subject_name']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        from classes.models import Class
        try:
            cls = Class.objects.get(pk=request.data['class_id'])
        except Class.DoesNotExist:
            return Response({'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        slot = TimetableSlot.objects.create(
            class_ref=cls,
            branch=cls.branch,
            day_of_week=request.data['day_of_week'],
            start_time=request.data['start_time'],
            end_time=request.data['end_time'],
            subject_name=request.data['subject_name'],
            teacher_id=request.data.get('teacher_id'),
            room=request.data.get('room'),
        )
        return Response(TimetableSlotSerializer(slot).data, status=status.HTTP_201_CREATED)


class TimetableDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            slot = TimetableSlot.objects.get(pk=pk)
        except TimetableSlot.DoesNotExist:
            return Response({'message': 'Slot not found'}, status=status.HTTP_404_NOT_FOUND)
        slot.delete()
        return Response({'message': 'Slot removed'})
```

- [ ] **Step 4: Update `timetable/urls.py`**

```python
from django.urls import path
from .views import TimetableListCreateView, TimetableDetailView

urlpatterns = [
    path('timetable/', TimetableListCreateView.as_view(), name='timetable-list-create'),
    path('timetable/<uuid:pk>/', TimetableDetailView.as_view(), name='timetable-detail'),
]
```

- [ ] **Step 5: Commit**

```bash
git add timetable/
git commit -m "feat: add timetable app"
```

---

## Task 9: `fees` App

**Files:**
- Create: `fees/models.py`
- Create: `fees/serializers.py`
- Create: `fees/views.py`
- Modify: `fees/urls.py`

- [ ] **Step 1: Write `fees/models.py`**

```python
import uuid
from django.db import models

FREQUENCY_CHOICES = [
    ('monthly', 'Monthly'), ('quarterly', 'Quarterly'),
    ('yearly', 'Yearly'), ('one-time', 'One-Time'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue'),
]


class FeeHead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE, related_name='fee_heads')
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_heads'
        ordering = ['name']

    def __str__(self):
        return self.name


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('api.Student', on_delete=models.CASCADE, related_name='payments')
    branch = models.ForeignKey('branches.Branch', on_delete=models.CASCADE)
    fee_head = models.ForeignKey(FeeHead, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.student.name} - {self.amount} ({self.status})"
```

- [ ] **Step 2: Write `fees/serializers.py`**

```python
from rest_framework import serializers
from .models import FeeHead, Payment


class FeeHeadSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = FeeHead
        fields = ['id', 'branch_id', 'branch_name', 'name', 'amount', 'frequency', 'description', 'is_active', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'student_id', 'student_name', 'branch_id', 'branch_name',
                  'fee_head_id', 'amount', 'description', 'status', 'due_date', 'paid_date', 'created_at']
```

- [ ] **Step 3: Write `fees/views.py`**

```python
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import FeeHead, Payment
from .serializers import FeeHeadSerializer, PaymentSerializer
from api.permissions import require_roles
from branches.models import BranchUser


def get_admin_branch_ids(user):
    if user.role == 'company_admin':
        return list(user.branches.values_list('id', flat=True))
    return list(BranchUser.objects.filter(user=user).values_list('branch_id', flat=True))


class FeeHeadListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def get(self, request):
        branch_ids = get_admin_branch_ids(request.user)
        fee_heads = FeeHead.objects.filter(branch_id__in=branch_ids, is_active=True)
        return Response(FeeHeadSerializer(fee_heads, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        required = ['branch_id', 'name', 'amount', 'frequency']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        fee_head = FeeHead.objects.create(
            branch_id=request.data['branch_id'],
            name=request.data['name'],
            amount=request.data['amount'],
            frequency=request.data['frequency'],
            description=request.data.get('description'),
        )
        return Response(FeeHeadSerializer(fee_head).data, status=status.HTTP_201_CREATED)


class FeeHeadDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            fee_head = FeeHead.objects.get(pk=pk)
        except FeeHead.DoesNotExist:
            return Response({'message': 'Fee head not found'}, status=status.HTTP_404_NOT_FOUND)
        fee_head.is_active = False
        fee_head.save()
        return Response({'message': 'Fee head deactivated'})


class GenerateInvoicesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        fee_head_id = request.data.get('fee_head_id')
        due_date = request.data.get('due_date')
        student_ids = request.data.get('student_ids', [])
        if not fee_head_id or not due_date:
            return Response({'message': 'fee_head_id and due_date are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            fee_head = FeeHead.objects.get(pk=fee_head_id)
        except FeeHead.DoesNotExist:
            return Response({'message': 'Fee head not found'}, status=status.HTTP_404_NOT_FOUND)
        from api.models import Student
        if student_ids:
            students = Student.objects.filter(id__in=student_ids, branch=fee_head.branch)
        else:
            students = Student.objects.filter(branch=fee_head.branch)
        with transaction.atomic():
            payments = [
                Payment(
                    student=student,
                    branch=fee_head.branch,
                    fee_head=fee_head,
                    amount=fee_head.amount,
                    description=fee_head.name,
                    due_date=due_date,
                )
                for student in students
            ]
            Payment.objects.bulk_create(payments)
        return Response({'message': f'Generated {len(payments)} invoices', 'count': len(payments)}, status=status.HTTP_201_CREATED)


class PaymentListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role in ('company_admin', 'branch_admin'):
            branch_ids = get_admin_branch_ids(user)
            payments = Payment.objects.filter(branch_id__in=branch_ids)
        elif user.role == 'parent':
            student_ids = user.children.values_list('id', flat=True)
            payments = Payment.objects.filter(student_id__in=student_ids)
        elif user.role == 'student':
            try:
                payments = Payment.objects.filter(student=user.student_profile)
            except Exception:
                payments = Payment.objects.none()
        else:
            return Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
        return Response(PaymentSerializer(payments, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        required = ['student_id', 'branch_id', 'amount', 'due_date']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        payment = Payment.objects.create(
            student_id=request.data['student_id'],
            branch_id=request.data['branch_id'],
            amount=request.data['amount'],
            description=request.data.get('description'),
            due_date=request.data['due_date'],
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentPayView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def put(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'message': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        payment.status = 'paid'
        payment.paid_date = datetime.date.today()
        payment.save()
        return Response(PaymentSerializer(payment).data)
```

- [ ] **Step 4: Update `fees/urls.py`**

```python
from django.urls import path
from .views import FeeHeadListCreateView, FeeHeadDetailView, GenerateInvoicesView, PaymentListCreateView, PaymentPayView

urlpatterns = [
    path('fee-heads/', FeeHeadListCreateView.as_view(), name='fee-head-list-create'),
    path('fee-heads/<uuid:pk>/', FeeHeadDetailView.as_view(), name='fee-head-detail'),
    path('fee-heads/generate-invoices/', GenerateInvoicesView.as_view(), name='generate-invoices'),
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<uuid:pk>/pay/', PaymentPayView.as_view(), name='payment-pay'),
]
```

- [ ] **Step 5: Commit**

```bash
git add fees/
git commit -m "feat: add fees app with fee heads and payments"
```

---

## Task 10: `notifications` App

**Files:**
- Create: `notifications/models.py`
- Create: `notifications/serializers.py`
- Create: `notifications/views.py`
- Modify: `notifications/urls.py`

- [ ] **Step 1: Write `notifications/models.py`**

```python
import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey('api.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    target_roles = ArrayField(models.CharField(max_length=50), default=list)
    target_branch = models.ForeignKey('branches.Branch', on_delete=models.SET_NULL, null=True, blank=True)
    target_class = models.ForeignKey('classes.Class', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'

    def __str__(self):
        return self.title


class NotificationRecipient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name='notification_recipients')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notification_recipients'
        unique_together = ('notification', 'user')
```

- [ ] **Step 2: Write `notifications/serializers.py`**

```python
from rest_framework import serializers
from .models import Notification, NotificationRecipient


class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.name', read_only=True, default=None)
    sender_role = serializers.CharField(source='sender.role', read_only=True, default=None)
    is_read = serializers.SerializerMethodField()
    read_at = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'created_at', 'sender_name', 'sender_role', 'is_read', 'read_at']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        try:
            recipient = obj.recipients.get(user=request.user)
            return recipient.is_read
        except NotificationRecipient.DoesNotExist:
            return False

    def get_read_at(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        try:
            recipient = obj.recipients.get(user=request.user)
            return recipient.read_at
        except NotificationRecipient.DoesNotExist:
            return None
```

- [ ] **Step 3: Write `notifications/views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from .models import Notification, NotificationRecipient
from .serializers import NotificationSerializer
from api.permissions import require_roles
from api.models import User
from branches.models import BranchUser
from classes.models import ClassStudent, ClassTeacher

ROLE_TARGET_MAP = {
    'company_admin': ['company_admin', 'branch_admin', 'teacher', 'parent', 'student'],
    'branch_admin': ['branch_admin', 'teacher', 'parent', 'student'],
    'teacher': ['student', 'branch_admin'],
}


def resolve_recipients(target_roles, target_class_id, target_branch_id):
    user_ids = set()
    if target_class_id:
        student_ids = ClassStudent.objects.filter(class_ref_id=target_class_id).values_list('student__user_id', flat=True)
        user_ids.update(uid for uid in student_ids if uid)
        teacher_ids = ClassTeacher.objects.filter(class_ref_id=target_class_id).values_list('teacher_id', flat=True)
        user_ids.update(teacher_ids)
        from api.models import Student
        parent_ids = Student.objects.filter(
            id__in=ClassStudent.objects.filter(class_ref_id=target_class_id).values_list('student_id', flat=True)
        ).exclude(parent=None).values_list('parent_id', flat=True)
        user_ids.update(parent_ids)
        users = User.objects.filter(id__in=user_ids, role__in=target_roles)
    elif target_branch_id:
        user_ids_in_branch = BranchUser.objects.filter(branch_id=target_branch_id).values_list('user_id', flat=True)
        users = User.objects.filter(id__in=user_ids_in_branch, role__in=target_roles)
    else:
        users = User.objects.filter(role__in=target_roles)
    return users


class NotificationListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notification_ids = NotificationRecipient.objects.filter(
            user=request.user
        ).values_list('notification_id', flat=True)
        notifications = Notification.objects.filter(id__in=notification_ids).order_by('-created_at')[:100]
        serializer = NotificationSerializer(notifications, many=True, context={'request': request})
        return Response(serializer.data)

    @require_roles('company_admin', 'branch_admin', 'teacher')
    def post(self, request):
        title = request.data.get('title')
        message = request.data.get('message')
        target_roles = request.data.get('target_roles', [])
        if not title or not message or not target_roles:
            return Response({'message': 'title, message, and target_roles are required'}, status=status.HTTP_400_BAD_REQUEST)
        allowed = ROLE_TARGET_MAP.get(request.user.role, [])
        invalid = [r for r in target_roles if r not in allowed]
        if invalid:
            return Response({'message': f'Cannot target roles: {invalid}'}, status=status.HTTP_403_FORBIDDEN)
        target_branch_id = request.data.get('target_branch_id')
        target_class_id = request.data.get('target_class_id')
        with transaction.atomic():
            notification = Notification.objects.create(
                sender=request.user,
                title=title,
                message=message,
                target_roles=target_roles,
                target_branch_id=target_branch_id,
                target_class_id=target_class_id,
            )
            recipients = resolve_recipients(target_roles, target_class_id, target_branch_id)
            NotificationRecipient.objects.bulk_create([
                NotificationRecipient(notification=notification, user=user)
                for user in recipients
            ], ignore_conflicts=True)
        return Response({
            'id': str(notification.id),
            'sender_id': str(request.user.id),
            'title': notification.title,
            'message': notification.message,
            'target_roles': notification.target_roles,
            'target_branch_id': str(target_branch_id) if target_branch_id else None,
            'target_class_id': str(target_class_id) if target_class_id else None,
            'created_at': notification.created_at,
            'recipients_count': recipients.count(),
        }, status=status.HTTP_201_CREATED)


class NotificationMarkReadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            recipient = NotificationRecipient.objects.get(notification_id=pk, user=request.user)
        except NotificationRecipient.DoesNotExist:
            return Response({'message': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
        recipient.is_read = True
        recipient.read_at = timezone.now()
        recipient.save()
        return Response({'message': 'Marked as read'})


class NotificationMarkAllReadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        NotificationRecipient.objects.filter(user=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({'message': 'All marked as read'})
```

- [ ] **Step 4: Update `notifications/urls.py`**

```python
from django.urls import path
from .views import NotificationListCreateView, NotificationMarkReadView, NotificationMarkAllReadView

urlpatterns = [
    path('notifications/', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/<uuid:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('notifications/read-all/', NotificationMarkAllReadView.as_view(), name='notification-read-all'),
]
```

- [ ] **Step 5: Commit**

```bash
git add notifications/
git commit -m "feat: add notifications app with in-app notification endpoints"
```

---

## Task 11: `api` App — Auth, Users, Students, Attendance, Dashboard Views

**Files:**
- Rewrite: `api/views/auth_views.py`
- Create: `api/views/user_views.py`
- Rewrite: `api/views/student_views.py`
- Rewrite: `api/views/attendance_views.py`
- Create: `api/views/dashboard_views.py`
- Rewrite: `api/urls.py`
- Delete: `api/views/staff_views.py`, `api/views/parent_views.py`, `api/views/admission_views.py`, `api/views/contact_views.py`, `api/views/fee_views.py`

- [ ] **Step 1: Rewrite `api/views/auth_views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import User
from ..serializers import UserSerializer
from ..permissions import require_roles


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'message': 'email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'token': get_tokens_for_user(user),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        user = request.user
        name = request.data.get('name')
        email = request.data.get('email')
        if not name or not email:
            return Response({'message': 'name and email are required'}, status=status.HTTP_400_BAD_REQUEST)
        if email != user.email and User.objects.filter(email=email).exists():
            return Response({'message': 'Email already in use'}, status=status.HTTP_409_CONFLICT)
        user.name = name
        user.email = email
        user.save()
        return Response(UserSerializer(user).data)


class PasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not current_password or not new_password:
            return Response({'message': 'current_password and new_password are required'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({'message': 'new_password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.check_password(current_password):
            return Response({'message': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new_password)
        request.user.save()
        return Response({'message': 'Password updated successfully'})


class AvatarView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        avatar_url = request.data.get('avatar_url')
        if not avatar_url:
            return Response({'message': 'avatar_url is required'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.avatar_url = avatar_url
        request.user.save()
        return Response(UserSerializer(request.user).data)
```

- [ ] **Step 2: Create `api/views/user_views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from ..models import User
from ..serializers import UserSerializer
from ..permissions import require_roles
from branches.models import BranchUser


class UserListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def get(self, request):
        user = request.user
        if user.role == 'company_admin':
            branch_ids = user.branches.values_list('id', flat=True)
            user_ids = BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True)
            users = User.objects.filter(id__in=user_ids).exclude(id=user.id)
        else:
            branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
            user_ids = BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True)
            users = User.objects.filter(id__in=user_ids, role__in=['teacher', 'branch_admin'])
        return Response(UserSerializer(users, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        required = ['name', 'email', 'password', 'role']
        for field in required:
            if not request.data.get(field):
                return Response({'message': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=request.data['email']).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        branch_id = request.data.get('branch_id')
        if not branch_id and request.user.role == 'branch_admin':
            branch_ids = BranchUser.objects.filter(user=request.user).values_list('branch_id', flat=True)
            branch_id = str(branch_ids.first()) if branch_ids else None
        with transaction.atomic():
            new_user = User(
                name=request.data['name'],
                email=request.data['email'],
                role=request.data['role'],
                designation=request.data.get('designation'),
            )
            new_user.set_password(request.data['password'])
            new_user.save()
            if branch_id:
                BranchUser.objects.create(branch_id=branch_id, user=new_user)
        return Response(UserSerializer(new_user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'message': 'User deleted'})


class ParentListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def get(self, request):
        user = request.user
        if user.role == 'company_admin':
            branch_ids = user.branches.values_list('id', flat=True)
            user_ids = BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True)
            parents = User.objects.filter(id__in=user_ids, role='parent')
        else:
            branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
            user_ids = BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True)
            parents = User.objects.filter(id__in=user_ids, role='parent')
        result = []
        for parent in parents:
            children = parent.children.all()
            result.append({
                'id': str(parent.id),
                'name': parent.name,
                'email': parent.email,
                'created_at': parent.created_at,
                'children': [
                    {'id': str(c.id), 'name': c.name, 'branch': c.branch.name}
                    for c in children
                ],
            })
        return Response(result)
```

- [ ] **Step 3: Rewrite `api/views/student_views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import Student
from ..serializers import StudentSerializer
from ..permissions import require_roles
from branches.models import BranchUser
from classes.models import ClassTeacher, ClassStudent


def get_accessible_students(user):
    if user.role == 'company_admin':
        branch_ids = user.branches.values_list('id', flat=True)
        return Student.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'branch_admin':
        branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)
        return Student.objects.filter(branch_id__in=branch_ids)
    elif user.role == 'teacher':
        class_ids = ClassTeacher.objects.filter(teacher=user).values_list('class_ref_id', flat=True)
        student_ids = ClassStudent.objects.filter(class_ref_id__in=class_ids).values_list('student_id', flat=True)
        return Student.objects.filter(id__in=student_ids)
    elif user.role == 'parent':
        return Student.objects.filter(parent=user)
    elif user.role == 'student':
        try:
            return Student.objects.filter(user=user)
        except Exception:
            return Student.objects.none()
    return Student.objects.none()


class StudentListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        students = get_accessible_students(request.user)
        return Response(StudentSerializer(students, many=True).data)

    @require_roles('company_admin', 'branch_admin')
    def post(self, request):
        name = request.data.get('name')
        branch_id = request.data.get('branch_id')
        if not name or not branch_id:
            return Response({'message': 'name and branch_id are required'}, status=status.HTTP_400_BAD_REQUEST)
        student = Student.objects.create(
            name=name,
            branch_id=branch_id,
            parent_id=request.data.get('parent_id'),
        )
        return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)


class StudentDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin')
    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        student.delete()
        return Response({'message': 'Student deleted successfully'})
```

- [ ] **Step 4: Rewrite `api/views/attendance_views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from ..models import Student, Attendance
from ..permissions import require_roles
from classes.models import Class, ClassStudent


class AttendanceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        class_id = request.query_params.get('class_id')
        date = request.query_params.get('date')
        if not class_id or not date:
            return Response({'message': 'class_id and date are required'}, status=status.HTTP_400_BAD_REQUEST)
        student_ids = ClassStudent.objects.filter(class_ref_id=class_id).values_list('student_id', flat=True)
        students = Student.objects.filter(id__in=student_ids)
        attendance_map = {
            a.student_id: a
            for a in Attendance.objects.filter(class_ref_id=class_id, date=date, student_id__in=student_ids)
        }
        result = [
            {
                'student_id': str(s.id),
                'student_name': s.name,
                'attendance_status': attendance_map[s.id].status if s.id in attendance_map else None,
                'attendance_id': str(attendance_map[s.id].id) if s.id in attendance_map else None,
            }
            for s in students
        ]
        return Response(result)

    @require_roles('company_admin', 'branch_admin', 'teacher')
    def post(self, request):
        class_id = request.data.get('class_id')
        date = request.data.get('date')
        records = request.data.get('records', [])
        if not class_id or not date:
            return Response({'message': 'class_id and date are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cls = Class.objects.get(pk=class_id)
        except Class.DoesNotExist:
            return Response({'message': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
        with transaction.atomic():
            for record in records:
                Attendance.objects.update_or_create(
                    student_id=record['student_id'],
                    date=date,
                    class_ref_id=class_id,
                    defaults={'status': record['status'], 'branch': cls.branch},
                )
        return Response({'message': 'Attendance recorded successfully'})
```

- [ ] **Step 5: Create `api/views/dashboard_views.py`**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import Student
from ..permissions import require_roles
from branches.models import Branch, BranchUser
from fees.models import Payment


class DashboardStatsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @require_roles('company_admin', 'branch_admin', 'teacher')
    def get(self, request):
        user = request.user
        if user.role == 'company_admin':
            branch_ids = user.branches.values_list('id', flat=True)
        else:
            branch_ids = BranchUser.objects.filter(user=user).values_list('branch_id', flat=True)

        students = Student.objects.filter(branch_id__in=branch_ids).count()
        branches = Branch.objects.filter(id__in=branch_ids).count()
        from api.models import User as UserModel
        staff = UserModel.objects.filter(
            id__in=BranchUser.objects.filter(branch_id__in=branch_ids).values_list('user_id', flat=True),
            role__in=['teacher', 'branch_admin'],
        ).count()
        from django.db.models import Sum
        revenue = Payment.objects.filter(
            branch_id__in=branch_ids, status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({'students': students, 'branches': branches, 'staff': staff, 'revenue': float(revenue)})
```

- [ ] **Step 6: Rewrite `api/urls.py`**

```python
from django.urls import path
from .views.auth_views import LoginView, ProfileView, PasswordView, AvatarView
from .views.user_views import UserListCreateView, UserDetailView, ParentListView
from .views.student_views import StudentListCreateView, StudentDetailView
from .views.attendance_views import AttendanceView
from .views.dashboard_views import DashboardStatsView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/password/', PasswordView.as_view(), name='password'),
    path('auth/avatar/', AvatarView.as_view(), name='avatar'),

    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/parents/', ParentListView.as_view(), name='user-parents'),

    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<uuid:pk>/', StudentDetailView.as_view(), name='student-detail'),

    path('attendance/', AttendanceView.as_view(), name='attendance'),

    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
```

- [ ] **Step 7: Delete old view files no longer needed**

```bash
rm /home/kaushal/repos/school_backend/api/views/staff_views.py
rm /home/kaushal/repos/school_backend/api/views/parent_views.py
rm /home/kaushal/repos/school_backend/api/views/admission_views.py
rm /home/kaushal/repos/school_backend/api/views/contact_views.py
rm /home/kaushal/repos/school_backend/api/views/fee_views.py
```

- [ ] **Step 8: Commit**

```bash
git add api/
git commit -m "feat: rewrite api app views for auth, users, students, attendance, dashboard"
```

---

## Task 12: Migrations & Database Setup

- [ ] **Step 1: Run Django system check**

```bash
cd /home/kaushal/repos/school_backend
python manage.py check
```

Expected: No errors. Fix any import errors before continuing.

- [ ] **Step 2: Create migrations in dependency order**

```bash
python manage.py makemigrations api
python manage.py makemigrations branches
python manage.py makemigrations classes
python manage.py makemigrations academics
python manage.py makemigrations timetable
python manage.py makemigrations notifications
python manage.py makemigrations fees
```

Expected: each creates `0001_initial.py`.

- [ ] **Step 3: Apply migrations**

```bash
python manage.py migrate
```

Expected: all migrations applied with no errors.

- [ ] **Step 4: Create initial superuser**

```bash
python manage.py shell -c "
from api.models import User
u = User(name='Admin', email='admin@school.com', role='company_admin', is_staff=True, is_superuser=True)
u.set_password('admin123')
u.save()
print('Superuser created:', u.email)
"
```

- [ ] **Step 5: Commit**

```bash
git add api/migrations/ branches/migrations/ classes/migrations/ academics/migrations/ timetable/migrations/ notifications/migrations/ fees/migrations/
git commit -m "feat: add fresh migrations for full schema redesign"
```

---

## Task 13: Smoke Test — Server Startup & Login

- [ ] **Step 1: Start the server**

```bash
python manage.py runserver 5000
```

Expected: server starts on port 5000 with no errors.

- [ ] **Step 2: Test login endpoint**

```bash
curl -s -X POST http://localhost:5000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@school.com","password":"admin123"}' | python -m json.tool
```

Expected: `{ "token": "...", "user": { "id": "...", "role": "company_admin", ... } }`

- [ ] **Step 3: Test profile endpoint**

```bash
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@school.com","password":"admin123"}' | python -c "import sys,json; print(json.load(sys.stdin)['token'])")

curl -s http://localhost:5000/api/auth/profile/ \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

Expected: user profile JSON.

- [ ] **Step 4: Commit smoke test confirmation**

```bash
git commit --allow-empty -m "chore: smoke test passed — login and profile endpoints working"
```

---

## Task 14: Fix `notifications/urls.py` URL Order

The `read-all` path must come before `<uuid:pk>/read/` to avoid routing conflicts.

- [ ] **Step 1: Verify urls are correct order**

```python
# notifications/urls.py — final correct order
from django.urls import path
from .views import NotificationListCreateView, NotificationMarkReadView, NotificationMarkAllReadView

urlpatterns = [
    path('notifications/', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/read-all/', NotificationMarkAllReadView.as_view(), name='notification-read-all'),
    path('notifications/<uuid:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
]
```

- [ ] **Step 2: Also fix `fees/urls.py` — `generate-invoices/` before `<uuid:pk>/`**

```python
# fees/urls.py — final correct order
from django.urls import path
from .views import FeeHeadListCreateView, FeeHeadDetailView, GenerateInvoicesView, PaymentListCreateView, PaymentPayView

urlpatterns = [
    path('fee-heads/', FeeHeadListCreateView.as_view(), name='fee-head-list-create'),
    path('fee-heads/generate-invoices/', GenerateInvoicesView.as_view(), name='generate-invoices'),
    path('fee-heads/<uuid:pk>/', FeeHeadDetailView.as_view(), name='fee-head-detail'),
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<uuid:pk>/pay/', PaymentPayView.as_view(), name='payment-pay'),
]
```

- [ ] **Step 3: Also fix `api/urls.py` — `users/parents/` before `users/<uuid:pk>/`**

```python
# api/urls.py — correct order (parents before <uuid:pk>)
from django.urls import path
from .views.auth_views import LoginView, ProfileView, PasswordView, AvatarView
from .views.user_views import UserListCreateView, UserDetailView, ParentListView
from .views.student_views import StudentListCreateView, StudentDetailView
from .views.attendance_views import AttendanceView
from .views.dashboard_views import DashboardStatsView

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/password/', PasswordView.as_view(), name='password'),
    path('auth/avatar/', AvatarView.as_view(), name='avatar'),

    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/parents/', ParentListView.as_view(), name='user-parents'),
    path('users/<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),

    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<uuid:pk>/', StudentDetailView.as_view(), name='student-detail'),

    path('attendance/', AttendanceView.as_view(), name='attendance'),

    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
```

- [ ] **Step 4: Commit**

```bash
git add notifications/urls.py fees/urls.py api/urls.py
git commit -m "fix: correct URL ordering to prevent routing conflicts"
```

---

## Self-Review

**Spec coverage check:**
- ✅ All 7 apps scaffolded
- ✅ All models match spec (UUID PKs, correct fields, correct FK targets)
- ✅ All endpoints implemented
- ✅ Role-based access on every view
- ✅ Atomic transactions: user creation, attendance upsert, invoice generation, notification+recipients
- ✅ bcrypt password hashing via custom `set_password`/`check_password`
- ✅ Soft delete on FeeHead
- ✅ Dashboard revenue = sum of paid payments
- ✅ Notifications: resolve recipients by class > branch > global
- ✅ Migration strategy: delete old, fresh makemigrations in order
- ✅ URL ordering fixed (static paths before dynamic)

**Placeholder scan:** None found. All steps have complete code.

**Type consistency:**
- `class_ref` used consistently (avoids Python keyword clash with `class`)
- `branch_id`, `class_ref_id`, `student_id` used consistently as FK accessor names
- `require_roles` decorator signature consistent across all views
