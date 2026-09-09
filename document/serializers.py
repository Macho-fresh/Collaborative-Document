from rest_framework import serializers
from .models import *

class DocSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        field = "__all__"