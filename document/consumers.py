from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import *
from accounts.models import *

# connect to document to edit ex: api/document/12
# edit functionality is here 
# basically its: user1 edits and sends, 
# backend updates but i want a way for users to see the doc update in real time
# user 2 wants to edit, sends version number alongside edit, that doc is then changed to that
# show online users


from channels.generic.websocket import WebsocketConsumer

class MyConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()

        # self.send(text_data=json.dumps({
        #     'type': 'connection_established',
        #     'message': 'You are now connected'
        # }))
        id = self.scope['id']
        self.user_id = self.scope['user']['id']
        self.doc = Document.objects.get(id=id)
        self.user = User.objects.get(id=self.user_id)

        self.close()

    def receive(self, text_data=None, bytes_data=None):
        if self.doc.owner != self.user or self.user_id not in self.doc.editors:
            self.send(text_data="Invalid version")
        if self.doc.version == text_data['version']:
            self.doc.title = text_data['title']
            self.doc.content = text_data['content']
            self.doc.version += 1
            self.doc.save()

            DocumentVersion.objects.create(
                document_id = id,
                version_number = self.doc.version,
                content = self.doc.content,
                title = self.doc.title,
                edited_by = self.user_id
            )

            AuditLog.objects.create(
                document_id = id,
                user_id = self.user_id,
                action = 'Edited Document'
            )
            self.send(text_data="Invalid version")

        self.send(text_data="Hello world!")
        
        

    def disconnect(self, close_code):
        self.close()