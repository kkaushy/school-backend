from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from ..models import User
from ..serializers import UserSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    @extend_schema(
        tags=['Auth'],
        summary='Register a new user',
        request=inline_serializer(
            name='RegisterRequest',
            fields={
                'name': drf_serializers.CharField(),
                'email': drf_serializers.EmailField(),
                'password': drf_serializers.CharField(),
                'role': drf_serializers.ChoiceField(choices=['student', 'parent', 'staff', 'admin']),
                'contact': drf_serializers.CharField(required=False),
                'className': drf_serializers.CharField(required=False),
                'rollNumber': drf_serializers.CharField(required=False),
            },
        ),
        responses={
            201: OpenApiResponse(response=UserSerializer, description='User registered'),
            400: OpenApiResponse(description='Missing or invalid fields'),
            409: OpenApiResponse(description='Email already exists'),
        },
    )
    def post(self, request):
        data = request.data
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        contact = data.get('contact')
        class_name = data.get('className')
        roll_number = data.get('rollNumber')

        if not name or not email or not password or not role:
            return Response({'message': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        if role == 'student':
            if not class_name or not roll_number:
                return Response(
                    {'message': 'Class and Roll Number required'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            if not contact:
                return Response({'message': 'Contact required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'message': 'Email exists'}, status=status.HTTP_409_CONFLICT)

        user = User.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            role=role,
            contact=contact if role != 'student' else None,
            class_name=str(class_name) if role == 'student' else None,
            roll_number=str(roll_number) if role == 'student' else None,
        )

        return Response(
            {'message': 'Registered successfully', 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    @extend_schema(
        tags=['Auth'],
        summary='Login and obtain JWT tokens',
        request=inline_serializer(
            name='LoginRequest',
            fields={
                'email': drf_serializers.EmailField(),
                'password': drf_serializers.CharField(),
                'role': drf_serializers.ChoiceField(choices=['student', 'parent', 'staff', 'admin']),
                'className': drf_serializers.CharField(required=False),
                'rollNumber': drf_serializers.CharField(required=False),
            },
        ),
        responses={
            200: inline_serializer(
                name='LoginResponse',
                fields={
                    'token': drf_serializers.CharField(),
                    'refresh': drf_serializers.CharField(),
                    'user': UserSerializer(),
                },
            ),
            400: OpenApiResponse(description='Missing fields'),
            401: OpenApiResponse(description='Invalid credentials'),
        },
    )
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        class_name = data.get('className')
        roll_number = data.get('rollNumber')

        if not email or not password or not role:
            return Response({'message': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if role == 'student':
                user = User.objects.get(
                    email=email,
                    role=role,
                    class_name=str(class_name),
                    roll_number=str(roll_number),
                )
            else:
                user = User.objects.get(email=email, role=role)
        except User.DoesNotExist:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = get_tokens_for_user(user)

        return Response({
            'token': tokens['access'],
            'refresh': tokens['refresh'],
            'user': UserSerializer(user).data,
        })


class LinkParentToStudentView(APIView):
    @extend_schema(
        tags=['Auth'],
        summary='Link a parent user to a student user',
        request=inline_serializer(
            name='LinkParentRequest',
            fields={
                'parentId': drf_serializers.IntegerField(),
                'studentEmail': drf_serializers.EmailField(required=False),
                'rollNumber': drf_serializers.CharField(required=False),
            },
        ),
        responses={
            200: inline_serializer(
                name='LinkParentResponse',
                fields={
                    'message': drf_serializers.CharField(),
                    'parent': UserSerializer(),
                    'student': UserSerializer(),
                },
            ),
            400: OpenApiResponse(description='Missing fields'),
            404: OpenApiResponse(description='Parent or student not found'),
        },
    )
    def post(self, request):
        data = request.data
        parent_id = data.get('parentId')
        student_email = data.get('studentEmail')
        roll_number = data.get('rollNumber')

        if not parent_id or (not student_email and not roll_number):
            return Response(
                {'message': 'Parent ID and student info required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.db.models import Q
        try:
            student = User.objects.get(
                Q(email=student_email) | Q(roll_number=roll_number),
                role='student',
            )
        except User.DoesNotExist:
            return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            parent = User.objects.get(id=parent_id, role='parent')
        except User.DoesNotExist:
            return Response({'message': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)

        parent.linked_student_user = student
        parent.save()

        return Response({
            'message': 'Parent linked to student',
            'parent': UserSerializer(parent).data,
            'student': UserSerializer(student).data,
        })
