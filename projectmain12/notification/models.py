from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    TO_CHOICES = [
        ('VolunteerHead', 'Volunteer Head'),
        ('Volunteer', 'Volunteer'),
        ('User', 'User'),
    ]

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Normal', 'Normal'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    to = models.CharField(max_length=20, choices=TO_CHOICES)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    publish_date = models.DateTimeField(auto_now_add=True)
    close_notification = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.subject
