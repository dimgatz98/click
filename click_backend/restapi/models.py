import uuid
from PIL import Image

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.id}"


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.OneToOneField(
        User,
        unique=True,
        related_name="profile",
        on_delete=models.CASCADE
    )
    image = models.ImageField(default="default.jpeg", upload_to="profile_pics")
    contacts = models.ManyToManyField(
        User,
        related_name="contact",
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    # admin = models.ForeignKey(User)
    participants = models.ManyToManyField(User, related_name='chat')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    room_name = models.CharField(max_length=50, unique=True)
    last_message = models.DateTimeField()

    def __str__(self):
        return f"{self.id}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="message",
    )
    sent_from = models.CharField(max_length=150)
    text = models.TextField(max_length=1000)

    def __str__(self):
        return f"{self.id}"
