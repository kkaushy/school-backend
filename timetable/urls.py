from django.urls import path
from .views import TimetableListCreateView, TimetableDetailView

urlpatterns = [
    path('timetable', TimetableListCreateView.as_view(), name='timetable-list-create'),
    path('timetable/<uuid:pk>', TimetableDetailView.as_view(), name='timetable-detail'),
]
