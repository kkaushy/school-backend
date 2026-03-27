from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Admission
from ..serializers import AdmissionSerializer


class AdmissionListCreateView(APIView):
    @extend_schema(
        tags=['Admissions'],
        summary='List all admission applications',
        responses={200: AdmissionSerializer(many=True)},
    )
    def get(self, request):
        admissions = Admission.objects.all().order_by('-created_at')
        serializer = AdmissionSerializer(admissions, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Admissions'],
        summary='Submit a new admission application',
        request=AdmissionSerializer,
        responses={
            201: AdmissionSerializer,
            400: OpenApiResponse(description='studentName, classApplying, and mobile are required'),
        },
    )
    def post(self, request):
        data = request.data
        student_name = data.get('studentName') or data.get('student_name')
        class_applying = data.get('classApplying') or data.get('class_applying')
        mobile = data.get('mobile')

        if not student_name or not class_applying or not mobile:
            return Response({'message': 'studentName, classApplying, and mobile are required'}, status=status.HTTP_400_BAD_REQUEST)

        admission = Admission.objects.create(
            student_name=student_name,
            gender=data.get('gender'),
            dob=data.get('dob') or None,
            class_applying=class_applying,
            father_name=data.get('fatherName') or data.get('father_name'),
            mother_name=data.get('motherName') or data.get('mother_name'),
            mobile=mobile,
            email=data.get('email'),
            address=data.get('address'),
        )

        return Response(AdmissionSerializer(admission).data, status=status.HTTP_201_CREATED)


class AdmissionDetailView(APIView):
    def get_object(self, pk):
        try:
            return Admission.objects.get(pk=pk)
        except Admission.DoesNotExist:
            return None

    @extend_schema(
        tags=['Admissions'],
        summary='Retrieve an admission application',
        responses={
            200: AdmissionSerializer,
            404: OpenApiResponse(description='Admission not found'),
        },
    )
    def get(self, request, pk):
        admission = self.get_object(pk)
        if not admission:
            return Response({'message': 'Admission not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AdmissionSerializer(admission).data)

    @extend_schema(
        tags=['Admissions'],
        summary='Update an admission application',
        request=AdmissionSerializer,
        responses={
            200: AdmissionSerializer,
            404: OpenApiResponse(description='Admission not found'),
        },
    )
    def put(self, request, pk):
        admission = self.get_object(pk)
        if not admission:
            return Response({'message': 'Admission not found'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        admission.student_name = data.get('studentName') or data.get('student_name') or admission.student_name
        admission.gender = data.get('gender', admission.gender)
        admission.dob = data.get('dob') or admission.dob
        admission.class_applying = data.get('classApplying') or data.get('class_applying') or admission.class_applying
        admission.father_name = data.get('fatherName') or data.get('father_name') or admission.father_name
        admission.mother_name = data.get('motherName') or data.get('mother_name') or admission.mother_name
        admission.mobile = data.get('mobile', admission.mobile)
        admission.email = data.get('email', admission.email)
        admission.address = data.get('address', admission.address)
        admission.save()

        return Response(AdmissionSerializer(admission).data)

    @extend_schema(
        tags=['Admissions'],
        summary='Delete an admission application',
        responses={
            200: OpenApiResponse(description='Admission deleted'),
            404: OpenApiResponse(description='Admission not found'),
        },
    )
    def delete(self, request, pk):
        admission = self.get_object(pk)
        if not admission:
            return Response({'message': 'Admission not found'}, status=status.HTTP_404_NOT_FOUND)

        admission.delete()
        return Response({'message': 'Admission deleted'})
