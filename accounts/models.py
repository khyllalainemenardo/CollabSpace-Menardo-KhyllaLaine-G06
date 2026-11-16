from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        LEADER = "LEADER", "Team Leader"
        MEMBER = "MEMBER", "Member"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    contact_number = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    def __str__(self):
        return self.username