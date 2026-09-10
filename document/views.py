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
        doc = Document.objects.all()
        for i in doc:
            if user_id in i.viewers or user_id in i.editors or i.owner == user:
                serializer = DocSerializer(i)
                return Response({
                    serializer.data
                },status=status.HTTP_200_OK)
        return Response({
            'error': 'you dont have any documents'
        },status=status.HTTP_401_UNAUTHORIZED)

class GetDoc(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, id):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        doc = Document.objects.get(id=id)
        if user_id in doc.viewers or user_id in doc.editors or doc.owner == user:
            serializer = DocSerializer(doc)
            return Response({
                serializer.data
            },status=status.HTTP_200_OK)
        return Response({
            'error': 'you are not authorized to view this document'
        },status=status.HTTP_401_UNAUTHORIZED)

class PatchDoc(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, id):
        user_id = request.user.id
        title = request.data.get('title')
        content = request.data.get('content')
        user = User.objects.get(id=user_id)

        doc = Document.objects.get(id=id)
        if doc.owner != user or user_id not in doc.editors:
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
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        doc = Document.objects.get(id=id)
        if doc.owner != user:
            return Response({
                'error': 'not allowed to delete this document'
            },status=status.HTTP_401_UNAUTHORIZED)
        doc.delete()

        return Response({
            'message': 'doc deleted'
        },status=status.HTTP_200_OK)

class InviteViewer(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request, id):
        user_id = request.data.get('user_id')
        doc = Document.objects.get(id=id)
        if user_id not in doc.viewers:
            doc.viewers.append(user_id)
            doc.save()
            return Response({
                'message': 'viewer added succesfully'
            }, status=status.HTTP_200_OK)
        return Response({
            'error': 'user is already a viewer for this doc'
        })

class InviteEditor(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request, id):
        user_id = request.data.get('user_id')
        doc = Document.objects.get(id=id)
        if user_id not in doc.editors:
            doc.editors.append(user_id)
            doc.save()
            return Response({
                'message': 'editor added succesfully'
            }, status=status.HTTP_200_OK)
        return Response({
            'error': 'user is already a editor for this doc'
        })