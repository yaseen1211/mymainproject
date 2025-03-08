from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from volunteerhead.models import Camp

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
        
class product(models.Model):
    product_Name = models.CharField(max_length=255)  # Define max_length
    product_unit = models.CharField(max_length=50)  # Define max_length
    product_Category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    product_Quantity=models.IntegerField(null=True)
    product_Limit=models.IntegerField(null=True)
    
    camp1 = models.ForeignKey(Camp, on_delete=models.CASCADE, null=True, blank=True, related_name='products')
