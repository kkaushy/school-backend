from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Staff
from ..serializers import StaffSerializer


class StaffListCreateView(APIView):
    @extend_schema(
        tags=['Staff'],
        summary='List all staff members',
        responses={200: StaffSerializer(many=True)},
    )
    def get(self, request):
        staff = Staff.objects.all().order_by('name')
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Staff'],
        summary='Create a new staff member',
        request=StaffSerializer,
        responses={
            201: StaffSerializer,
            400: OpenApiResponse(description='Missing required fields'),
            409: OpenApiResponse(description='Email already exists'),
        },
    )
    def post(self, request):
        data = request.data
        name = data.get('name')
        designation = data.get('designation')
        email = data.get('email')
        phone = data.get('phone')

        if not name or not designation or not email or not phone:
            return Response({'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        if Staff.objects.filter(email=email).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_409_CONFLICT)

        staff = Staff.objects.create(name=name, designation=designation, email=email, phone=phone)
        return Response(StaffSerializer(staff).data, status=status.HTTP_201_CREATED)


class StaffDetailView(APIView):
    def get_object(self, pk):
        try:
            return Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return None

    @extend_schema(
        tags=['Staff'],
        summary='Update a staff member',
        request=StaffSerializer,
        responses={
            200: StaffSerializer,
            404: OpenApiResponse(description='Staff not found'),
            409: OpenApiResponse(description='Email already exists'),
        },
    )
    def put(self, request, pk):
        staff = self.get_object(pk)
        if not staff:
            return Response({'message': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        email = data.get('email', staff.email)

        if email != staff.email and Staff.objects.filter(email=email).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_409_CONFLICT)

        staff.name = data.get('name', staff.name)
        staff.designation = data.get('designation', staff.designation)
        staff.email = email
        staff.phone = data.get('phone', staff.phone)
        staff.save()

        return Response(StaffSerializer(staff).data)

    @extend_schema(
        tags=['Staff'],
        summary='Delete a staff member',
        responses={
            200: OpenApiResponse(description='Staff deleted'),
            404: OpenApiResponse(description='Staff not found'),
        },
    )
    def delete(self, request, pk):
        staff = self.get_object(pk)
        if not staff:
            return Response({'message': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)

        staff.delete()
        return Response({'message': 'Staff deleted'})
