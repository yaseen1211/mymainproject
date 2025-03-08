import uuid
from django.db import models
from django.contrib.auth.models import User
# from adminlogin.models import Place  # Assuming Place is from the admin app
from django.contrib.auth.hashers import make_password
from superadmin.models import Zone



class CampHead(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128, default='default_password')  # Store hashed passwords
    registration_token = models.CharField(max_length=100, blank=True, null=True)  # Token field
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='camp_head')  # Unique related_name
    zone1 = models.ForeignKey(Zone, on_delete=models.CASCADE,default=1, related_name='zone3')

    def delete(self, *args, **kwargs):
        # Check if the CampHead is associated with any Camp
        if self.campHead2.exists():  # campHead2 is the related name for Camp
            raise Exception('Cannot delete CampHead because it is associated with a Camp.')
        super().delete(*args, **kwargs)


    def save(self, *args, **kwargs):
        # Ensure the password is hashed before saving
        if not self.pk or 'password' in kwargs.get('update_fields', {}):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def generate_registration_token(self):
        self.registration_token = uuid.uuid4().hex
        self.save()


class Camp(models.Model):
    name = models.CharField(max_length=150,unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    campHead1 = models.ForeignKey(CampHead, on_delete=models.SET_NULL, null=True, blank=True, related_name="campHead2")
    is_active = models.BooleanField(default=True)  # New field for active/deactive status

    def __str__(self):
        return self.name

class Volunteer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128, default='default_password')  # Store hashed passwords
    registration_token = models.CharField(max_length=100, blank=True, null=True)  # Token field
    user = models.OneToOneField(User, on_delete=models.CASCADE,default=2)
    zone1 = models.ForeignKey(Zone, on_delete=models.CASCADE,default=1, related_name='zone2')
    camp1 = models.ForeignKey(Camp, on_delete=models.CASCADE, null=True,blank=True, related_name='camp2')
    is_active = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user.username} - {self.camp.name}"
    
    def save(self, *args, **kwargs):
        # Ensure the password is hashed before saving
        if not self.pk or 'password' in kwargs.get('update_fields', {}):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def generate_registration_token(self):
        self.registration_token = uuid.uuid4().hex
        self.save()



    
    
    


