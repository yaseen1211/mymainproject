from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class OTPVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp_verification')
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return now() > self.expires_at
