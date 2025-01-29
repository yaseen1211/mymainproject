from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):

    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Normal', 'Normal'),
    ]

    to = models.CharField(max_length=20)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    publish_date = models.DateTimeField(auto_now_add=True)
    close_notification = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True, blank=True)

