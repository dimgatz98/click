from channels.db import database_sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
# from ..restapi.models import Chat, Message, User


class ChatRoomConsumer(AsyncWebsocketConsumer):
    # @database_sync_to_async
    # def save_message(self, text: str, room_name: str):
    #     '''
    #     Method used to save messages in db
    #     '''
    #     chat_id = Chat.objects.all().get(room_name=room_name).id
    #     msg = Message.objects.create(chat=chat_id, text=text)
    #     msg.save()
    #     return msg

    # # Chat should probably be created in frontend
    # # via axios call to restapi CreateChatView
    # @database_sync_to_async
    # def create_chat(self, participants: list, room_name: str):
    #     '''
    #     Method used to save chat in db
    #     '''
    #     chat = Chat.objects.create(
    #         room_name=room_name, participants=participants)
    #     chat.save()
    #     return chat

    # # This should probably also be checked in frontend
    # @database_sync_to_async
    # def is_participant(self, room_name: str, username: str) -> bool:
    #     '''
    #     Method used to check if user participates in chat
    #     '''
    #     participants = Chat.objects.all().get(room_name=room_name).participants
    #     user_id = User.objects.all().get(username=username).id
    #     return True if (user_id in participants) else False

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        try:
            msg = await self.save_message(text=message, room_name=self.room_name)
        except Exception as e:
            print(e)
            msg = None

        if (msg is None):
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'username': username,
            }
        )

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))
