from django.urls import path
from . import views

urlpatterns = [
    path(
        "add/",
        views.createUser,
        name="createUser",
    ),
    path(
        "get/<str:username>/",
        views.retrieveUser,
        name="retrieveUser",
    ),
    path(
        "list/",
        views.listUsers,
        name="listUsers",
    ),
    path(
        "delete/<str:username>/",
        views.deleteUser,
        name="deleteUser",
    ),
]
