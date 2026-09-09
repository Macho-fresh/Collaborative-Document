from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from accounts.models import User
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .permissions import *

class CreateDoc(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user_id = request.user.id
        title = request.data.get('title')
        content = request.data.get('content')
        user = User.objects.get(id=user_id)

        Document.objects.create(
            owner = user,
            title = title,
            content = content,
            version = 1
        )

        return Response({
            'message': 'Document created'
        },status=status.HTTP_201_CREATED)


class GetAllDoc(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        doc = Document.objects.all(owner=user)
        serializer = DocSerializer(doc)
        return Response({
            serializer.data
        },status=status.HTTP_200_OK)

class GetDoc(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        doc = Document.objects.get(id=id, owner=user)
        serializer = DocSerializer(doc)
        return Response({
            serializer.data
        },status=status.HTTP_200_OK)

class PatchDoc(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, id):
        user_id = request.user.id
        title = request.data.get('title')
        content = request.data.get('content')
        user = User.objects.get(id=user_id)

        doc = Document.objects.get(id=id)
        if doc.owner != user:
            return Response({
                'error': 'not document owner'
            },status=status.HTTP_401_UNAUTHORIZED)
        doc.title = title
        doc.content = content
        doc.save()
        serializer = DocSerializer(doc)

        return Response({
            serializer.data
        },status=status.HTTP_202_ACCEPTED)

class DeleteDoc(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id):
        doc = Document.objects.get(id=id)
        doc.delete()

        return Response({
            'message': 'doc deleted'
        },status=status.HTTP_200_OK)