from django.urls import path
from .views.auth_views import RegisterView, LoginView, LinkParentToStudentView
from .views.student_views import StudentListCreateView, StudentDetailView
from .views.staff_views import StaffListCreateView, StaffDetailView
from .views.parent_views import ParentDashboardView
from .views.attendance_views import (
    MarkAttendanceView,
    StudentAttendanceView,
    StudentsByClassView,
    StaffAttendanceView,
    ParentStudentAttendanceView,
)
from .views.admission_views import AdmissionListCreateView, AdmissionDetailView
from .views.contact_views import ContactListCreateView, ContactDetailView
from .views.fee_views import StudentsByClassFeeView, StudentFeesView

urlpatterns = [
    # Auth
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/link-student', LinkParentToStudentView.as_view(), name='link-student'),

    # Students
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:pk>', StudentDetailView.as_view(), name='student-detail'),

    # Staff
    path('staff/', StaffListCreateView.as_view(), name='staff-list-create'),
    path('staff/<int:pk>', StaffDetailView.as_view(), name='staff-detail'),

    # Parent
    path('parent/dashboard', ParentDashboardView.as_view(), name='parent-dashboard'),

    # Attendance
    path('attendance/mark', MarkAttendanceView.as_view(), name='mark-attendance'),
    path('attendance/students', StudentAttendanceView.as_view(), name='student-attendance'),
    path('attendance/students/by-class', StudentsByClassView.as_view(), name='students-by-class'),
    path('attendance/staff', StaffAttendanceView.as_view(), name='staff-attendance'),
    path('attendance/parent/<int:parent_id>', ParentStudentAttendanceView.as_view(), name='parent-attendance'),

    # Admissions
    path('admission/create', AdmissionListCreateView.as_view(), name='admission-create'),
    path('admission/', AdmissionListCreateView.as_view(), name='admission-list'),
    path('admission/<int:pk>', AdmissionDetailView.as_view(), name='admission-detail'),
    path('admission/update/<int:pk>', AdmissionDetailView.as_view(), name='admission-update'),
    path('admission/delete/<int:pk>', AdmissionDetailView.as_view(), name='admission-delete'),

    # Contacts
    path('contact/', ContactListCreateView.as_view(), name='contact-list-create'),
    path('contact/<int:pk>', ContactDetailView.as_view(), name='contact-detail'),

    # Fees
    path('fees/students/<str:class_name>', StudentsByClassFeeView.as_view(), name='fees-students-by-class'),
    path('fees/student/<int:pk>', StudentFeesView.as_view(), name='student-fees'),
]
