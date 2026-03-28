from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def require_roles(*roles):
    """Decorator for APIView methods. Checks request.user.role is in allowed roles or user is superuser."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return Response({'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
            if not (request.user.role in roles or request.user.is_superuser):
                return Response({'message': 'Insufficient permissions'}, status=status.HTTP_403_FORBIDDEN)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator
