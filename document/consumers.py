from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import *
from accounts.models import *
from channels.generic.websocket import WebsocketConsumer
from django.db import transaction

class MyConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        # check if that user is an editor or viewere of this particlar document
        doc = Document.objects.get(id=(self.scope["url_route"]["kwargs"]["id"]))
        self.accept()
        if user.id not in doc.editors or user.id not in doc.viewers:
            print('user not in viewers or editors')
            # self.close()
            self.send(text_data=json.dumps({
                'message': 'You not an editor or viewer of this document'
            }))
        else:
            self.group_name = f'doc_{self.scope["url_route"]["kwargs"]["id"]}'
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )

            self.doc_id = self.scope["url_route"]["kwargs"]["id"]
            print(self.scope['user'])
            print(self.scope["url_route"]["kwargs"]["id"])


            self.send(text_data=json.dumps({
                'message': 'You are now connected'
            }))
            self.user_id = user.id

            self.username = user.username
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    'type': 'online_offline',
                    'message': f'{self.username} joined'
                }
            )

            # id = self.scope['id']
            self.user_id = self.scope['user'].id
            self.doc = Document.objects.get(id=self.doc_id)
            self.user = user


    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if self.doc.owner != self.user or self.user_id not in self.doc.editors or self.user_id not in self.doc.viewers:
            self.send(json.dumps({
                'error': 'unauthorized'
            }))
        elif self.doc.version == data['version']:
            with transaction.atomic():
                    self.doc.title = data['title']
                    self.doc.content = data['content']
                    self.doc.version += 1
                    print('changes made')
                    self.doc.save()

                    DocumentVersion.objects.create(
                        document_id = self.scope["url_route"]["kwargs"]["id"],
                        version_number = self.doc.version,
                        content = self.doc.content,
                        title = self.doc.title,
                        edited_by = self.user_id
                    )

                    AuditLog.objects.create(
                        document_id = self.scope["url_route"]["kwargs"]["id"],
                        user_id = self.user_id,
                        action = 'Edited Document'
                    )
                    self.send(text_data="Changes Added")
        else:
            self.send(text_data="Invalid version")


    def online_offline(self, event):
        self.send(
            json.dumps({'message': event['message']})
        )

        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'online_offline',
                'message': f'{self.username} left'
            }
        )