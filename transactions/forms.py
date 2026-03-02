from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile
import re

KERALA_DISTRICTS = [
    ("Thiruvananthapuram", "Thiruvananthapuram"),
    ("Kollam", "Kollam"),
    ("Pathanamthitta", "Pathanamthitta"),
    ("Alappuzha", "Alappuzha"),
    ("Kottayam", "Kottayam"),
    ("Idukki", "Idukki"),
    ("Ernakulam", "Ernakulam"),
    ("Thrissur", "Thrissur"),
    ("Palakkad", "Palakkad"),
    ("Malappuram", "Malappuram"),
    ("Kozhikode", "Kozhikode"),
    ("Wayanad", "Wayanad"),
    ("Kannur", "Kannur"),
    ("Kasaragod", "Kasaragod"),
]
# class RegisterForm(forms.ModelForm):
#     username = forms.CharField(label="Username")
#     password = forms.CharField(widget=forms.PasswordInput, label="Password")
#     email = forms.EmailField(label="Email")
#     phone_number = forms.CharField(label="Phone Number")
#     home_location = forms.ChoiceField(
#         choices=KERALA_DISTRICTS,
#         label="District"
#     )
class RegisterForm(forms.ModelForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    email = forms.EmailField(label="Email")

    phone_number = forms.CharField(label="Phone Number")

    home_location = forms.ChoiceField(
        choices=KERALA_DISTRICTS,
        label="District"
    )

    class Meta:
        model = CustomerProfile
        fields = [
            "home_location",
            "address",
            "phone_number",
            "bank_account_number",
            "upi_id",
            "balance",
        ]

    def clean_phone_number(self):
        phone = self.cleaned_data["phone_number"]
        if not re.match(r'^[0-9]{10}$', phone):
            raise forms.ValidationError("Phone number must be 10 digits")
        return phone

    def clean_bank_account_number(self):
        acc = self.cleaned_data["bank_account_number"]
        if len(acc) < 10:
            raise forms.ValidationError("Invalid account number")
        return acc