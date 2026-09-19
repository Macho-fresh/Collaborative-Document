from django.urls import path
from .views import *

urlpatterns=[
    path('create-doc/', CreateDoc.as_view()),
    path('get-all-doc/', GetAllDoc.as_view()),
    path('get-doc/<int:id>/', GetDoc.as_view()),
    path('delete-doc/<int:id>/', DeleteDoc.as_view()),
    path('invite-viewer/<int:id>/', InviteViewer.as_view()),
    path('invite-editor/<int:id>/', InviteEditor.as_view()),
    path('view-logs/', ViewAuditLog.as_view())
]