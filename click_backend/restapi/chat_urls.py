from django.urls import path
from .views import chat_views as views

urlpatterns = [
    path(
        "create/",
        views.createChat,
        name="createChat",
    ),
    path(
        "save_message/",
        views.saveMessage,
        name="saveMessage",
    ),
    path(
        "retrieve/<str:chat_id>/",
        views.retrieveChat,
        name="retrieveChat",
    ),
    path(
        "messages/list/<str:chat_id>/",
        views.listMessages,
        name="listMessages",
    ),
    path(
        "list/<str:username>/",
        views.listChats,
        name="listChats",
    ),
    path(
        "update/<str:chat_id>/",
        views.updateLastMessageChat,
        name="updateLastMessageChat",
    ),
]
