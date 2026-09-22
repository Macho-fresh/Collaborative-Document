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

        doc = Document.objects.create(
            owner = user,
            title = title,
            content = content,
            version = 1
        )

        DocumentVersion.objects.create(
            document_id = doc.id,
            version_number = doc.version,
            content = doc.content,
            title = doc.title,
            edited_by = user_id
        )

        AuditLog.objects.create(
            document_id = doc.id,
            user_id = user_id,
            action = 'Created Document'
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
        accessible_docs = []

        for i in doc:
            if user_id in i.viewers or user_id in i.editors or i.owner == user:
                AuditLog.objects.create(
                    document_id = i.id,
                    user_id = user_id,
                    action = 'Viewed All Documents'
                )
                accessible_docs.append(i)

        if accessible_docs:
            serializer = DocSerializer(accessible_docs, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        AuditLog.objects.create(
            document_id = doc.id,
            user_id = user_id,
            action = 'Viewed One Document'
        )
        return Response({
            'error': 'you are not authorized to view this document'
        },status=status.HTTP_401_UNAUTHORIZED)


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
        
        AuditLog.objects.create(
            document_id = doc.id,
            user_id = user_id,
            action = 'Deleted Document'
        )
        doc.delete()

        return Response({
            'message': 'doc deleted'
        },status=status.HTTP_200_OK)

class InviteViewer(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request, id):
        owner_id = request.user.id
        user_id = request.data.get('user_id')
        doc = Document.objects.get(id=id)
        if user_id not in doc.viewers:
            doc.viewers.append(user_id)
            doc.save()
            AuditLog.objects.create(
                document_id = doc.id,
                user_id = owner_id,
                action = f'Invited User {user_id}'
            )
            return Response({
                'message': 'viewer added succesfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'user is already a viewer for this doc'
        })

class InviteEditor(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request, id):
        owner_id = request.user.id
        user_id = request.data.get('user_id')
        doc = Document.objects.get(id=id)
        if user_id not in doc.editors:
            doc.editors.append(user_id)
            doc.save()
            AuditLog.objects.create(
                document_id = doc.id,
                user_id = owner_id,
                action = f'Invited User {user_id}'
            )
            return Response({
                'message': 'editor added succesfully'
            }, status=status.HTTP_200_OK)
        return Response({
            'error': 'user is already a editor for this doc'
        })

class EditView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, id):
        version = request.data.get('version')
        title = request.data.get('title')
        content = request.data.get('content')
        user_id = request.data.id
        user = User.objects.get(id=user_id)

        doc = Document.objects.get(id=id)
        if doc.owner != user or user_id not in doc.editors:
            return Response({
                'error': 'invalid version_id'
            },status=status.HTTP_409_CONFLICT)
        if doc.version == version:
            doc.title = title
            doc.content = content
            doc.version += 1
            doc.save()

            DocumentVersion.objects.create(
                document_id = id,
                version_number = doc.version,
                content = doc.content,
                title = doc.title,
                edited_by = user_id
            )

            AuditLog.objects.create(
                document_id = id,
                user_id = user_id,
                action = 'Edited Document'
            )
            return Response({
                'message': 'edited succesfully'
            }, status=status.HTTP_200_OK)

class ViewAuditLog(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.user.id
        try:
            log = AuditLog.objects.filter(user_id = user_id)
            serializer = LogSerializer(log, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except AuditLog.DoesNotExist:
            return Response({'error': 'you have no logs'}, status=status.HTTP_404_NOT_FOUND)
