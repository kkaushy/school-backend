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
