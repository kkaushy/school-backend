from django.urls import path
from .views import AcademicRecordListCreateView

urlpatterns = [
    path('academics', AcademicRecordListCreateView.as_view(), name='academic-list-create'),
]
