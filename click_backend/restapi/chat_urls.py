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
]
