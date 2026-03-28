from django.urls import path
from .views import NotificationListCreateView, NotificationMarkReadView, NotificationMarkAllReadView

urlpatterns = [
    path('notifications', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/read-all', NotificationMarkAllReadView.as_view(), name='notification-read-all'),
    path('notifications/<uuid:pk>/read', NotificationMarkReadView.as_view(), name='notification-mark-read'),
]
