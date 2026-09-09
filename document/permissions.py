from rest_framework.permissions import BasePermission
from .models import *

class ViewerPermission(BasePermission):
    def has_permission(self, request, view):
        doc_id = view.kwargs.get('id')
        doc = Document.objects.get(id=doc_id)
        if request.user.id in doc.viewers:
            return True

class EditorPermission(BasePermission):
    def has_permission(self, request, view):
        doc_id = view.kwargs.get('id')
        doc = Document.objects.get(id=doc_id)
        if request.user.id in doc.editors:
            return True
