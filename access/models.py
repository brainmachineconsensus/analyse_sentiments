from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, max_length=255)
    numero = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    is_active = models.BooleanField(default=False)
    activation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    activation_token_created_at = models.DateTimeField(default=timezone.now)
    reset_password_token = models.UUIDField(default=uuid.uuid4, null=True)
    reset_password_token_created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return self.user.username