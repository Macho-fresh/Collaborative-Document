from rest_framework import serializers
from .models import *

class DocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = "__all__"

class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"