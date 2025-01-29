import uuid
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

# Create your models here.
class VolunteerHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,)  # Link to User model
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128, default='default_password')  # Store hashed passwords
    registration_token = models.CharField(max_length=100, blank=True, null=True)  # Token field

    def save(self, *args, **kwargs):
        # Ensure the password is hashed before saving
        if not self.pk or 'password' in kwargs.get('update_fields', {}):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

    def generate_registration_token(self):
        self.registration_token = uuid.uuid4().hex
        self.save()

    def delete(self, *args, **kwargs):
        if self.zones.exists():
            raise ValueError("Cannot delete VolunteerHead while it is associated with one or more Zones.")
        super().delete(*args, **kwargs) 





class Zone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    volunteer_head = models.ForeignKey(VolunteerHead, on_delete=models.SET_NULL, null=True, blank=True, related_name="zones")

    def __str__(self):
        return self.name