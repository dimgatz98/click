from email.policy import HTTP
from functools import partial
from os import stat
from rest_framework.parsers import JSONParser
from rest_framework import status, permissions, generics
from rest_framework.response import Response

from ..models import (
    Chat,
    FriendRequest,
    Message,
    User,
)
from ..serializers import (
    ChatSerializer,
    MessageSerializer,
    ChatLastMessageSerializer,
    FriendRequestSerializer,
    ListRequestSerializer,
)

from ..utils.utils import (
    chat_exists,
    get_user_from_token,
    request_exists
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

    # Delete this method when in production
    def post(self, request):
        try:
            if len(request.data["participants"]) == 0:
                return Response(
                    {
                        "Error":
                        "Participants list can't be empty"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            s = set()
            for participant in request.data["participants"]:
                if participant not in s:
                    s.add(participant)
                    continue
                return Response(
                    {
                        "Error":
                        "Each user can be included in the chat at most once"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if (chat_exists(list(request.data["participants"]))):
                return Response(
                    {
                        "Error":
                        "Chat already exists"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

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
    lookup_field = ["chat_id"]

    def get_object(self):
        chat_id = self.kwargs["chat_id"]
        return generics.get_object_or_404(Chat, id=chat_id)


class ListChatsAPIView(generics.ListAPIView):
    '''
    View called to list all chats for a user
    '''
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = ChatSerializer
    lookup_field = ["username"]

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)

            data = list([dict(x) for x in serializer.data])
            for i, chat in enumerate(serializer.data):
                participant_usernames = []
                for participant in dict(chat)["participants"]:
                    user = User.objects.get(id=participant)
                    participant_usernames.append(user.username)
                data[i]["participants"] = participant_usernames

            return Response(data)
        except Exception as e:
            print(e)
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        username = self.kwargs["username"]
        chat_ids = []
        for chat in Chat.objects.all():
            if username in [x.username for x in chat.participants.all()]:
                chat_ids.append(chat.id)

        return Chat.objects.filter(id__in=chat_ids).order_by('-last_message')


class UpdateLastMessageChatView(generics.UpdateAPIView):
    '''
    View called to update chat's data from users who participate in this chat
    '''
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = ChatLastMessageSerializer
    lookup_field = ["chat_id"]

    def patch(self, request, *args, **kwargs):
        try:
            user, err = get_user_from_token(request.headers.copy())
            if (err is not None):
                return Response(data=err, status=status.HTTP_400_BAD_REQUEST)
            chat = Chat.objects.get(id=kwargs["chat_id"])
            for participant in chat.participants.all():
                if participant.id == user.id:
                    return super().patch(request, *args, **kwargs)
            err_msg = {
                "Error": "You are not allowed to modify this chat"
            }
            return Response(data=err_msg, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        chat_id = self.kwargs["chat_id"]
        return generics.get_object_or_404(Chat, id=chat_id)


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

    # Delete this method when in production
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
    lookup_field = ["chat_id"]

    def get_queryset(self):
        chat_id = self.kwargs["chat_id"]
        return Message.objects.filter(chat=chat_id).order_by('created')


class SendRequestView(generics.CreateAPIView):
    '''
    View called to send friend request to a user
    '''
    parser_classes = (JSONParser,)
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = FriendRequestSerializer

    def post(self, request, *args, **kwargs):
        try:
            data = request.data.copy()
            user, err = get_user_from_token(
                request.headers.copy(), *args, **kwargs
            )
            if (err is not None):
                return Response(data=err, status=status.HTTP_400_BAD_REQUEST)

            data["received_from"] = User.objects.get(
                username=data["received_from"]
            ).id
            data["sent_from"] = user.id
            if (data["sent_from"] == data["received_from"]):
                err_msg = {
                    "Error": "Sender and receiver have to be different"
                }
                return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

            if (chat_exists([data["sent_from"], data["received_from"]])):
                return Response({"Error": "Chat exists"}, status=status.HTTP_400_BAD_REQUEST)

            if (request_exists(data["sent_from"], data["received_from"])):
                return Response({"Error": "Request exists"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(e)
            err_msg = {
                "Error": "Invalid data"
            }
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)


class ListRequestsView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ListRequestSerializer

    def get(self, request, *args, **kwargs):
        try:
            self.kwargs["headers"] = request.headers.copy()
            queryset = self.filter_queryset(self.get_queryset())

            for query in queryset:
                query.sent_from_username = User.objects.get(
                    id=query.sent_from.id
                ).username
                query.received_from_username = User.objects.get(
                    id=query.received_from.id
                ).username

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(e)
            err_msg = {
                "Error": "Invalid data"
            }
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self, *args, **kwargs):
        user, _ = get_user_from_token(self.kwargs["headers"])
        return FriendRequest.objects.filter(received_from=user.id).order_by('-created')


class DeleteRequestView(generics.DestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def delete(self, request, *args, **kwargs):
        try:
            print(request.data)
            self.kwargs["id"] = request.data['id']
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            print(e)
            err_msg = {
                "Error": "Invalid data"
            }
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, *args, **kwargs):
        return FriendRequest.objects.get(id=self.kwargs["id"])


createChat = CreateChatView.as_view()
saveMessage = SaveMessageView.as_view()
retrieveChat = RetrieveChatView.as_view()
listMessages = ListMessagesAPIView.as_view()
listChats = ListChatsAPIView.as_view()
updateLastMessageChat = UpdateLastMessageChatView.as_view()
sendRequest = SendRequestView.as_view()
listRequests = ListRequestsView.as_view()
deleteRequest = DeleteRequestView.as_view()
