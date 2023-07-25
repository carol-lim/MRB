from django import forms
from django.contrib.auth.models import User  
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.exceptions import ValidationError  
import re
from django.contrib.auth.forms import SetPasswordForm
import smtplib
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, AuthenticationForm, UserCreationForm
from django.contrib.auth.forms import SetPasswordForm

User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):

    email = forms.CharField(
        required=True,
        widget=forms.EmailInput(
            {"class": "form-control", "placeholder": "Email"}
        ),
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            {"class": "form-control", "placeholder": "Password"}
        ),
    )

class CustomSignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput({"class": "form-control", "placeholder": "First Name"}),
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput({"class": "form-control", "placeholder": "Last Name"}),
    )
    email = forms.CharField(
        required=True,
        widget=forms.TextInput({"class": "form-control", "placeholder": "Email"}),
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput({"class": "form-control", "placeholder": "Password"}),
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput({"class": "form-control", "placeholder": "Confirm Password"}),
    )

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]
	
class UserCreationForm1(forms.ModelForm):
	class Meta:
		model = User
		fields = [
			'username', 
			'first_name', 
			'last_name', 
			'email'
		]
		labels = {
			'username': 'Username',
			'first_name':'First Name',
			'last_name':'Last Name',
			'email':'Email'
		}
		widgets = {
			'username': forms.TextInput(attrs={ "class":"form-control", "required": "true"}),
			'first_name': forms.TextInput(attrs={ "class":"form-control", "required": "true"}),
			'last_name': forms.TextInput(attrs={ "class":"form-control", "required": "true"}),
			'email': forms.EmailInput(attrs={ "class":"form-control", "required": "true"})
		}
		
	def username_clean(self):  
		username = self.cleaned_data['username'].lower()  
		new = User.objects.filter(username = username)  
		pattern = r'^[a-zA-Z0-9@.+_-]+$'

		if not re.match(pattern, username):
			raise ValidationError('Invalid input.')

		if new.count():
			raise ValidationError("User Already Exist")
		
		return username  
