from rest_framework import generics

from .models import User
from .serializers import CreateUserSerializer, UserSerializer


class CreateUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer


class ListUserAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class RetrieveUserAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = ["username"]

    def get_object(self):
        username = self.kwargs["username"]
        return generics.get_object_or_404(User, username=username)


class DeleteUserAPIView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = ["username"]

    def get_object(self):
        username = self.kwargs["username"]
        return generics.get_object_or_404(User, username=username)


deleteUser = DeleteUserAPIView.as_view()
retrieveUser = RetrieveUserAPIView.as_view()
listUsers = ListUserAPIView.as_view()
createUser = CreateUserAPIView.as_view()