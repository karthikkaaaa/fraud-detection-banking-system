from django.db import models
from django.contrib.auth.models import User
# from django.db import models

# from django.db import models
# from django.contrib.auth.models import User
import random

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    home_location = models.CharField(max_length=100)
    address = models.CharField(max_length=200, blank=True)

    phone_number = models.CharField(max_length=15)

    bank_account_number = models.CharField(max_length=20, unique=True)
    upi_id = models.CharField(max_length=100)

    balance = models.FloatField(default=50000)

    def __str__(self):
        return self.user.username
# class CustomerProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     home_location = models.CharField(max_length=100)
#     balance = models.FloatField(default=50000)
#     address = models.TextField(default="Not Provided")
#     phone_number = models.CharField(max_length=15,default="0000000000")
#     bank_account_number = models.CharField(max_length=20, default="000000000000") 
#     upi_id = models.CharField(max_length=50, default="000000000000")
#     def __str__(self):
#         return self.user.username   


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    location = models.CharField(max_length=100)
    risk_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
    



class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    is_you = models.CharField(max_length=10)
    problem = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="New")

    def __str__(self):
        return f"{self.user.username} - {self.status}"   