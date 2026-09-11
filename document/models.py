from django.db import models
from accounts.models import User

class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.CharField()
    version = models.PositiveIntegerField()
    edited_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    viewers = models.JSONField(default=list, blank=True)
    editors = models.JSONField(default=list, blank=True)

class DocumentVersion(models.Model):
    document_id = models.PositiveIntegerField()
    version_number = models.PositiveIntegerField()
    content = models.CharField()
    title = models.CharField()
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    document_id = models.PositiveIntegerField()
    user_id = models.PositiveIntegerField()
    action = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)
