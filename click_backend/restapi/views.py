from knox.models import AuthToken
from rest_framework import status, permissions, generics
from rest_framework.response import Response

from .models import User
from .serializers import (
                CreateUserSerializer,
                UserSerializer,
                ProfileSerializer,
                LoginSerializer,
            )


class CreateUserAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token = AuthToken.objects.create(user)

        obj = self.queryset.get(username=request.POST["username"])

        data = {
            "user": obj.pk,
        }
        if "image" in request.POST:
            data["image"] = request.POST["image"],

        profile_serializer = ProfileSerializer(data=data)

        if profile_serializer.is_valid():
            profile_serializer.create(profile_serializer.validated_data)
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": token[1]
            })

        obj.delete()
        err_msg = {
            "Error": "Profile data not valid",
        }
        return Response(data = err_msg, status=status.HTTP_400_BAD_REQUEST)


class SignInAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class ListUserAPIView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class RetrieveUserAPIView(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = ["username"]

    def get_object(self):
        username = self.kwargs["username"]
        return generics.get_object_or_404(User, username=username)


class DeleteUserAPIView(generics.DestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = ["username"]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if not token.startswith("Token "):
            err_msg = {
                "Error": 'Token should be provided in header as follows: "Authorization: Token <digest>"'
            }
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        token = request.headers["Authorization"].split(" ")[1]
        knox_object = AuthToken.objects.filter(token_key__startswith=token[:8]).first()

        if knox_object is None:
            err_msg = {
                "Error": "Invalid token"
            }
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        if user.username == knox_object.user.username:
            resp = super().delete(self, request, *args, **kwargs)
            return resp
        err_msg = {
            "Error": "Operation not permitted"
        }
        return Response(data=err_msg, status=status.HTTP_401_UNAUTHORIZED)

    def get_object(self):
        username = self.kwargs["username"]
        return generics.get_object_or_404(User, username=username)


signIn = SignInAPIView.as_view()
deleteUser = DeleteUserAPIView.as_view()
retrieveUser = RetrieveUserAPIView.as_view()
listUsers = ListUserAPIView.as_view()
createUser = CreateUserAPIView.as_view()
