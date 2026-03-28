from unittest.mock import MagicMock
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

def test_list_branches_requires_auth():
    view = BranchListCreateView.as_view()
    request = factory.get('/api/branches/')
    request.user = MagicMock(is_authenticated=False)
    response = view(request)
    assert response.status_code == 401

def test_create_branch_requires_company_admin():
    view = BranchListCreateView.as_view()
    request = factory.post('/api/branches/', {'name': 'Main', 'location': 'City'}, format='json')
    request.user = make_user('teacher')
    response = view(request)
    assert response.status_code == 403
