from django.db import models
import uuid

# Create your models here.
class Invitations(models.Model):
    def __str__(self):
        return self.email
    
    email = models.EmailField(max_length=100)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)