from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.base.models import CustomBaseModel
from apps.users.managers import CustomUserManager


class User(AbstractUser, CustomBaseModel):
    username = None
    email = models.EmailField(unique=True, blank=False, null=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
