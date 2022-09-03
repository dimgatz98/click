from django.urls import path
from .views import user_views as views

urlpatterns = [
    # CRUD
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
    path(
        "login/",
        views.signIn,
        name="signIn",
    ),
    path(
        "logout/",
        views.signOut,
        name="signOut",
    ),
    path(
        "contacts/add/",
        views.addContact,
        name="addContact",
    ),
    path(
        "contacts/list/",
        views.listContacts,
        name="listContacts",
    ),
    path(
        "profiles/retrieve/",
        views.retrieveProfile,
        name="retrieveProfile",
    ),
]
