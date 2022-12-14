from statistics import mode
from wsgiref import validate
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from .models import (
    User,
    Profile,
    Chat,
    Message,
    FriendRequest,
)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = "__all__"


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'email',
            'first_name',
            'last_name'
        )
        extra_kwargs = {
            'first_name': {
                'required': True
            },
            'last_name': {
                'required': True
            }
        }

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError('Incorrect credentials.')


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = "__all__"

    def create(self, validated_data):
        chat = Chat.objects.create(
            room_name=validated_data['room_name'],
            last_message=validated_data['last_message'],
        )
        chat.participants.set(validated_data['participants'])
        chat.save()

        return chat


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = "__all__"

    def create(self, validated_data):

        message = Message.objects.create(
            text=validated_data['text'],
            chat=validated_data['chat'],
            sent_from=validated_data['sent_from']
        )

        message.save()

        return message


class ContactsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("contacts",)


class ChatLastMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
        fields = ("last_message",)


class FriendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = '__all__'

    def create(self, validated_data):

        friendRequest = FriendRequest.objects.create(
            sent_from=validated_data['sent_from'],
            received_from=validated_data['received_from'],
        )

        friendRequest.save()

        return friendRequest


class ListRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    sent_from_id = serializers.UUIDField()
    sent_from_username = serializers.CharField()
    received_from_id = serializers.UUIDField()
    received_from_username = serializers.CharField()
