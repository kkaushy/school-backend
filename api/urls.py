from django.urls import path
from .views.auth_views import LoginView, ProfileView, PasswordView, AvatarView
from .views.user_views import UserListCreateView, UserDetailView, ParentListView
from .views.student_views import StudentListCreateView, StudentDetailView
from .views.attendance_views import AttendanceView
from .views.dashboard_views import DashboardStatsView

urlpatterns = [
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/profile', ProfileView.as_view(), name='profile'),
    path('auth/password', PasswordView.as_view(), name='password'),
    path('auth/avatar', AvatarView.as_view(), name='avatar'),

    path('users', UserListCreateView.as_view(), name='user-list-create'),
    path('users/parents', ParentListView.as_view(), name='user-parents'),
    path('users/<uuid:pk>', UserDetailView.as_view(), name='user-detail'),

    path('students', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<uuid:pk>', StudentDetailView.as_view(), name='student-detail'),

    path('attendance', AttendanceView.as_view(), name='attendance'),

    path('dashboard/stats', DashboardStatsView.as_view(), name='dashboard-stats'),
]
