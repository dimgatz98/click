from rest_framework import status
from rest_framework.response import Response
from http.client import REQUEST_HEADER_FIELDS_TOO_LARGE
from rest_framework import generics

from .models import User
from .serializers import CreateUserSerializer, UserSerializer, ProfileSerializer


class CreateUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        print("request data:", request.POST["username"])

        resp = super().post(request, *args, **kwargs)

        print("User created successfuly")

        obj = self.queryset.get(username=request.POST["username"])

        print("User:", type(obj))

        data = {
            "user": obj.pk,
        }
        if "image" in request.POST:
            data["image"] = request.POST["image"],

        profile_serializer = ProfileSerializer(data=data)

        print("serializer:", profile_serializer)

        if profile_serializer.is_valid():
            profile_serializer.create(profile_serializer.validated_data)
            return resp

        # obj.delete()
        err_msg = {
            "message": "Profile data not valid",
        }
        return Response(data = err_msg, status=status.HTTP_400_BAD_REQUEST)

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