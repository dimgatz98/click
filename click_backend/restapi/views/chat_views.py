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

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(e)
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


class RetrieveChatView(generics.RetrieveAPIView):
    '''
    View called to retrieve information for a chat
    '''
    permission_classes = [
        permissions.IsAuthenticated
    ]
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    lookup_field = ["room_name"]

    def get_object(self):
        room_name = self.kwargs["room_name"]
        return generics.get_object_or_404(Chat, room_name=room_name)


class ListChatsAPIView(generics.ListAPIView):
    '''
    View called to list all chats for a user
    '''
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = ChatSerializer
    lookup_field = ["username"]

    def get_queryset(self):
        username = self.kwargs["username"]
        chat_ids = []
        for chat in Chat.objects.all():
            if username in [x.username for x in chat.participants.all()]:
                chat_ids.append(chat.id)

        return Chat.objects.filter(id__in=chat_ids).order_by('last_message')


class SaveMessageView(generics.CreateAPIView):
    '''
    View called to save a message in db
    '''
    parser_classes = (JSONParser,)
    permission_classes = [
        permissions.IsAuthenticated
    ]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(e)
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


class ListMessagesAPIView(generics.ListAPIView):
    '''
    View called to list all messages from a chat
    '''
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = MessageSerializer
    lookup_field = ["room_name"]

    def get_queryset(self):
        room_name = self.kwargs["room_name"]
        chat_id = Chat.objects.get(room_name=room_name).id
        return Message.objects.filter(chat=chat_id).order_by('created')


createChat = CreateChatView.as_view()
saveMessage = SaveMessageView.as_view()
retrieveChat = RetrieveChatView.as_view()
listMessages = ListMessagesAPIView.as_view()
listChats = ListChatsAPIView.as_view()
