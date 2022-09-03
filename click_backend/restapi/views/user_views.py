from django.http import QueryDict
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from knox.models import AuthToken
from rest_framework import status, permissions, generics
from rest_framework.response import Response

from ..utils.utils import get_user_from_token, get_token, validate_contact
from ..models import User, Profile
from ..serializers import (
    CreateUserSerializer,
    UserSerializer,
    ProfileSerializer,
    LoginSerializer,
    ContactsSerializer,
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
                "Error": "Couldn't create user. Invalid data"
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
                "token": token[1],
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
                "Error": "Invalid credentials"
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
            request.headers.copy(), *args, **kwargs,
        )
        if not err_msg is None:
            return Response(
                data=err_msg,
                status=status.HTTP_400_BAD_REQUEST
            )

        knox_object.delete()

        data = {
            "Error": "Token deleted successfuly"
        }
        return Response(
            data=data,
            status=status.HTTP_200_OK,
        )


class ListUsersAPIView(generics.ListAPIView):
    '''
    View called to list all existing users
    '''
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
    ]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class RetrieveUserAPIView(generics.RetrieveAPIView):
    '''
    View called to retrieve data for a single user
    '''
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser,
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

        token_user, err = get_user_from_token(
            request.headers.copy(), *args, **kwargs
        )

        if not err is None:
            return Response(
                data=err,
                status=status.HTTP_400_BAD_REQUEST
            )

        # A user is only allowed to delete an account if they have the corresponding token
        if user.username == token_user.username:
            resp = super().delete(self, request, *args, **kwargs)
            return resp

        err_msg = {
            "Error": "Operation not permitted"
        }
        return Response(data=err_msg, status=status.HTTP_401_UNAUTHORIZED)

    def get_object(self):
        username = self.kwargs["username"]
        return generics.get_object_or_404(User, username=username)


class AddContactView(generics.UpdateAPIView):
    parser_classes = (MultiPartParser, JSONParser)
    serializer_class = ContactsSerializer
    queryset = Profile.objects.all()
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def put(self, request, *args, **kwargs):
        user, err = get_user_from_token(
            request.headers.copy(), *args, **kwargs
        )
        if (err is not None):
            return Response(data=err, status=status.HTTP_400_BAD_REQUEST)
        self.kwargs["username"] = user.username

        err = validate_contact(request.data.copy())
        if (err is not None):
            return Response(data=err, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        # Old contacts
        contacts = list([x.id for x in instance.contacts.all()])
        # New contacts
        new_contacts = request.data.getlist('contacts') if isinstance(
            request.data, QueryDict) else request.data['contacts']
        contacts.extend(new_contacts)

        data = {
            "contacts": contacts
        }
        serializer = self.get_serializer(
            instance, data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get_object(self):
        username = self.kwargs["username"]
        user_id = User.objects.all().get(username=username).id
        return generics.get_object_or_404(Profile, user=user_id)


class RetrieveProfileView(generics.RetrieveAPIView):
    '''
    View called to retrieve profile for a specific user based on authorization header
    '''
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        user, err = get_user_from_token(request.headers.copy())
        if (err is not None):
            return Response(data=err, status=status.HTTP_400_BAD_REQUEST)

        self.kwargs["user"] = user
        return super().get(request, *args, **kwargs)

    def get_object(self):
        user_id = self.kwargs["user"].id
        return generics.get_object_or_404(Profile, user=user_id)


class ListContactsAPIView(generics.RetrieveAPIView):
    '''
    View called to list all contacts of a specific user
    '''
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = ContactsSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        user, err = get_user_from_token(
            request.headers.copy(), *args, **kwargs
        )
        if (err is not None):
            return Response(data=err, status=status.HTTP_400_BAD_REQUEST)
        self.kwargs["username"] = user.username

        return super().get(request, *args, **kwargs)

    def get_object(self):
        username = self.kwargs["username"]
        user_id = User.objects.all().get(username=username).id
        return generics.get_object_or_404(Profile, user=user_id)


signIn = SignInAPIView.as_view()
signOut = SignOutAPIView.as_view()
deleteUser = DeleteUserAPIView.as_view()
retrieveUser = RetrieveUserAPIView.as_view()
listUsers = ListUsersAPIView.as_view()
createUser = CreateUserAPIView.as_view()
addContact = AddContactView.as_view()
listContacts = ListContactsAPIView.as_view()
retrieveProfile = RetrieveProfileView.as_view()
