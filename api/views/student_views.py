from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Student
from ..serializers import StudentSerializer


class StudentListCreateView(APIView):
    @extend_schema(
        tags=['Students'],
        summary='List all students',
        responses={200: StudentSerializer(many=True)},
    )
    def get(self, request):
        students = Student.objects.all().order_by('name')
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Students'],
        summary='Create a new student',
        request=StudentSerializer,
        responses={
            201: StudentSerializer,
            400: OpenApiResponse(description='Missing or invalid fields'),
            409: OpenApiResponse(description='Seat number already taken in this class'),
        },
    )
    def post(self, request):
        data = request.data
        name = data.get('name')
        class_name = data.get('className') or data.get('class_name')
        seat_number = data.get('seatNumber') or data.get('seat_number')
        gender = data.get('gender')

        if not name or not class_name or seat_number is None or not gender:
            return Response({'message': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            seat_number = int(seat_number)
        except (ValueError, TypeError):
            return Response({'message': 'Seat number must be a number'}, status=status.HTTP_400_BAD_REQUEST)

        if Student.objects.filter(seat_number=seat_number, class_name=class_name).exists():
            return Response(
                {'message': f'Seat number {seat_number} already exists in class {class_name}'},
                status=status.HTTP_409_CONFLICT,
            )

        student = Student.objects.create(
            name=name,
            class_name=str(class_name),
            seat_number=seat_number,
            gender=gender,
        )

        return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)


class StudentDetailView(APIView):
    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return None

    @extend_schema(
        tags=['Students'],
        summary='Update a student',
        request=StudentSerializer,
        responses={
            200: StudentSerializer,
            400: OpenApiResponse(description='Invalid seat number'),
            404: OpenApiResponse(description='Student not found'),
            409: OpenApiResponse(description='Seat number conflict'),
        },
    )
    def put(self, request, pk):
        student = self.get_object(pk)
        if not student:
            return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        name = data.get('name', student.name)
        class_name = data.get('className') or data.get('class_name') or student.class_name
        seat_number = data.get('seatNumber') or data.get('seat_number') or student.seat_number
        gender = data.get('gender', student.gender)

        try:
            seat_number = int(seat_number)
        except (ValueError, TypeError):
            return Response({'message': 'Seat number must be a number'}, status=status.HTTP_400_BAD_REQUEST)

        if Student.objects.filter(seat_number=seat_number, class_name=class_name).exclude(pk=pk).exists():
            return Response(
                {'message': f'Seat number {seat_number} already exists in class {class_name}'},
                status=status.HTTP_409_CONFLICT,
            )

        student.name = name
        student.class_name = str(class_name)
        student.seat_number = seat_number
        student.gender = gender
        student.save()

        return Response(StudentSerializer(student).data)

    @extend_schema(
        tags=['Students'],
        summary='Delete a student',
        responses={
            200: OpenApiResponse(description='Student deleted'),
            404: OpenApiResponse(description='Student not found'),
        },
    )
    def delete(self, request, pk):
        student = self.get_object(pk)
        if not student:
            return Response({'message': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        student.delete()
        return Response({'message': 'Student deleted'})
