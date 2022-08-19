from django.contrib import admin
from .models import (
    FriendRequest,
    User,
    Profile,
    Chat,
    Message,
)

# Register your models here.

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(FriendRequest)
