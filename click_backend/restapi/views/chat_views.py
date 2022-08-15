from rest_framework.parsers import JSONParser
from rest_framework import status, permissions, generics
from rest_framework.response import Response

from ..models import (
    Chat,
    Message
)
from ..serializers import (
    ChatSerializer,
    MessageSerializer,
)


# Chat views


class CreateChatView(generics.CreateAPIView):
    '''
    View called to create a new chat
    '''
    parser_classes = (JSONParser,)
    permission_classes = [
        permissions.IsAuthenticated
    ]
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer


class SaveMessageView(generics.CreateAPIView):
    '''
    View called to add a new contact for a user
    '''
    parser_classes = (JSONParser,)
    permission_classes = [
        permissions.IsAuthenticated
    ]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


createChat = CreateChatView.as_view()
saveMessage = SaveMessageView.as_view()
