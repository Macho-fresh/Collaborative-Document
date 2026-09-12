from .models import AuditLog
from accounts.models import User

class Middleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        AuditLog.objects.create(
            
        )
        return self.get_response(request)