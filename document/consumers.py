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
        self.group_name = f'doc_{self.scope["url_route"]["kwargs"]["id"]}'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.send(text_data=json.dumps({
            'message': 'You are now connected'
        }))

        self.username = User.objects.get(id=self.user_id).username
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'online_offline',
                'message': f'{self.username} joined'
            }
        )

        id = self.scope['id']
        self.user_id = self.scope['user']['id']
        self.doc = Document.objects.get(id=id)
        self.user = User.objects.get(id=self.user_id)

        self.close()

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if self.doc.owner != self.user or self.user_id not in self.doc.editors:
            self.send(json.dumps({
                'error': 'unauthorized'
            }))
        if self.doc.version == data['version']:
            self.doc.title = data['title']
            self.doc.content = data['content']
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


    def online_offline(self, event):
        self.send(
            json.dumps({'message': event['message']})
        )

        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'online_offline',
                'message': f'{self.username} left'
            }
        )