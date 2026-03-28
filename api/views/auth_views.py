from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from ..models import User
from ..serializers import UserSerializer
from ..permissions import require_roles


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'message': 'email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({'message': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({'message': 'Account is deactivated'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({
            'token': get_tokens_for_user(user),
            'user': UserSerializer(user).data,
        })


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        user = request.user
        name = request.data.get('name')
        email = request.data.get('email')
        if not name or not email:
            return Response({'message': 'name and email are required'}, status=status.HTTP_400_BAD_REQUEST)
        if email != user.email and User.objects.filter(email=email).exists():
            return Response({'message': 'Email already in use'}, status=status.HTTP_409_CONFLICT)
        user.name = name
        user.email = email
        user.save()
        return Response(UserSerializer(user).data)


class PasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not current_password or not new_password:
            return Response({'message': 'current_password and new_password are required'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({'message': 'new_password must be at least 6 characters'}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.check_password(current_password):
            return Response({'message': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new_password)
        request.user.save()
        return Response({'message': 'Password updated successfully'})


class AvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        avatar_url = request.data.get('avatar_url')
        if not avatar_url:
            return Response({'message': 'avatar_url is required'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.avatar_url = avatar_url
        request.user.save()
        return Response(UserSerializer(request.user).data)
