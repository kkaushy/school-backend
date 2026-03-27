from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Contact
from ..serializers import ContactSerializer


class ContactListCreateView(APIView):
    @extend_schema(
        tags=['Contacts'],
        summary='List all contact messages',
        responses={200: ContactSerializer(many=True)},
    )
    def get(self, request):
        contacts = Contact.objects.all().order_by('-created_at')
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=['Contacts'],
        summary='Submit a contact message',
        request=ContactSerializer,
        responses={
            201: ContactSerializer,
            400: OpenApiResponse(description='name, email, and message are required'),
        },
    )
    def post(self, request):
        data = request.data
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not name or not email or not message:
            return Response({'message': 'name, email, and message are required'}, status=status.HTTP_400_BAD_REQUEST)

        contact = Contact.objects.create(
            name=name,
            email=email,
            phone=data.get('phone'),
            subject=data.get('subject'),
            message=message,
        )

        return Response(ContactSerializer(contact).data, status=status.HTTP_201_CREATED)


class ContactDetailView(APIView):
    def get_object(self, pk):
        try:
            return Contact.objects.get(pk=pk)
        except Contact.DoesNotExist:
            return None

    @extend_schema(
        tags=['Contacts'],
        summary='Retrieve a contact message',
        responses={
            200: ContactSerializer,
            404: OpenApiResponse(description='Contact not found'),
        },
    )
    def get(self, request, pk):
        contact = self.get_object(pk)
        if not contact:
            return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ContactSerializer(contact).data)

    @extend_schema(
        tags=['Contacts'],
        summary='Delete a contact message',
        responses={
            200: OpenApiResponse(description='Contact deleted'),
            404: OpenApiResponse(description='Contact not found'),
        },
    )
    def delete(self, request, pk):
        contact = self.get_object(pk)
        if not contact:
            return Response({'message': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)

        contact.delete()
        return Response({'message': 'Contact deleted'})
