from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
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


# CRUD views


class CreateUserAPIView(generics.CreateAPIView):
    '''
    View called to register a new user and retrieve AuthToken for this user
    '''
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)

        except Exception as e:
            print(e)

            err_msg = {
                "message": "Couldn't create user. Invalid data"
            }
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        try:
            login_serializer = LoginSerializer(data=request.data)
            login_serializer.is_valid(raise_exception=True)
            user = login_serializer.validated_data
            token = AuthToken.objects.create(user)

            obj = self.queryset.get(username=request.data["username"])

            data = request.data.copy()
            data["user"] = obj.pk

            profile_serializer = ProfileSerializer(data=data,)

            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.create(profile_serializer.validated_data)

            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": token[1]
            })

        except Exception as e:
            print(e)

            # Delete user if profile failed to be created
            obj.delete()
            err_msg = {
                "Error": "Profile data not valid",
            }
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)


class SignInAPIView(generics.GenericAPIView):
    '''
    View called to retrieve token
    '''
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data
            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": AuthToken.objects.create(user)[1]
            })
        except Exception as e:
            print(e)

            err_msg = {
                "message": "Invalid data"
            }
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)


class SignOutAPIView(generics.GenericAPIView):
    '''
    View called to delete token
    '''
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def post(self, request, *args, **kwargs):

        knox_object, err_msg = get_token(
            request.headers.copy(), *args, **kwargs)
        if not err_msg is None:
            return Response(
                data={"message": err_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        knox_object.delete()

        return Response(
            data={"message": "Token deleted successfuly"},
            status=status.HTTP_200_OK,
        )


class ListUserAPIView(generics.ListAPIView):
    '''
    View called to list all existing users
    '''
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class RetrieveUserAPIView(generics.RetrieveAPIView):
    '''
    View called to retrieve data for a single user
    '''
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
    '''
    View called by a user to delete his account
    '''
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = ["username"]

    def delete(self, request, *args, **kwargs):
        user = self.get_object()

        knox_object, err_msg = get_token(
            request.headers.copy(), *args, **kwargs)
        if not err_msg is None:
            return Response(
                data={"message": err_msg},
                status=status.HTTP_400_BAD_REQUEST
            )

        # A user is only allowed to delete the account if they have the corresponding token
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


def get_token(headers, *args, **kwargs):
    '''
    Function to retrieve valid token from request headers
    '''
    if "Authorization" not in headers:
        err_msg = {
            "Error": 'Token should be provided in header as follows: "Authorization: Token <digest>"'
        }
        return None, err_msg

    if not headers["Authorization"].startswith("Token "):
        err_msg = {
            "Error": 'Token should be provided in header as follows: "Authorization: Token <digest>"'
        }
        return None, err_msg

    token = headers["Authorization"].split(" ")[1]
    knox_object = AuthToken.objects.filter(
        token_key__startswith=token[:8]).first()

    if knox_object is None:
        err_msg = {
            "Error": "Invalid token"
        }
        return None, err_msg

    return knox_object, None


signIn = SignInAPIView.as_view()
signOut = SignOutAPIView.as_view()
deleteUser = DeleteUserAPIView.as_view()
retrieveUser = RetrieveUserAPIView.as_view()
listUsers = ListUserAPIView.as_view()
createUser = CreateUserAPIView.as_view()
