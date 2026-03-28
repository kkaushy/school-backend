from django.urls import path
from .views import FeeHeadListCreateView, FeeHeadDetailView, GenerateInvoicesView, PaymentListCreateView, PaymentPayView

urlpatterns = [
    path('fee-heads', FeeHeadListCreateView.as_view(), name='fee-head-list-create'),
    path('fee-heads/generate-invoices', GenerateInvoicesView.as_view(), name='generate-invoices'),
    path('fee-heads/<uuid:pk>', FeeHeadDetailView.as_view(), name='fee-head-detail'),
    path('payments', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/<uuid:pk>/pay', PaymentPayView.as_view(), name='payment-pay'),
]
