from django.urls import path
from .views import ClassListCreateView, ClassDetailView, AssignTeacherView, AssignStudentView

urlpatterns = [
    path('classes', ClassListCreateView.as_view(), name='class-list-create'),
    path('classes/assign-teacher', AssignTeacherView.as_view(), name='class-assign-teacher'),
    path('classes/assign-student', AssignStudentView.as_view(), name='class-assign-student'),
    path('classes/<uuid:pk>', ClassDetailView.as_view(), name='class-detail'),
]
