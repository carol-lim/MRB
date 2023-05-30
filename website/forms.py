from django import forms
from .models import MeetingRoom, MRBooking
from django.utils import timezone
from datetime import datetime
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

User = get_user_model()

class UserCreationForm(forms.ModelForm):
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

class DateInput(forms.DateInput):
	input_type = 'date'

class TimeInput(forms.TimeInput):
	input_type = 'time'

class AddMRForm(forms.ModelForm):
	class Meta:
		model = MeetingRoom
		fields = ['mroom_name','level','capacity', 'mr_image']
		labels = {
			'mroom_name': 'Meeting Room Name',
			'level': 'Level',
			'capacity': 'Capacity',
			'mr_image': 'Meeting Room Image'
        }
		widgets = {
            'mroom_name': forms.TextInput(attrs={ "class":"form-control", "required": "true"}),
            'level': forms.NumberInput(attrs={ "class":"form-control", "required": "true", "min": "1"}),
            'capacity': forms.NumberInput(attrs={ "class":"form-control", "required": "true", "min": "2"}),
		}
    
class AddBookingForm(forms.ModelForm):
	class Meta:
		current_date = timezone.now().date()
		model = MRBooking
		fields = [
			'mroom',
			'staff',
			'num_attendees',
			'type',
			'start_date',
			'end_date',
			'start_time',
			'end_time'
		]
		labels = {
			'mroom':'',
			'staff':'Staff',
			'num_attendees':'Number of Attendees',
			'type':'Type of Meeting',
			'start_date':'Start Date',
			'end_date':'End Date',
			'start_time':'Start Time',
			'end_time':'End Time'
        }
		widgets = {
			'mroom':forms.HiddenInput(),
            'staff':forms.Select(attrs={"class":"form-control", "required": "true"}),
			'num_attendees':forms.NumberInput(attrs={ "class":"form-control", "required": "true", "min": "2", "id": "num_attendees"}),
            'type': forms.Select(attrs={ "class":"form-control", "required": "true", "id": "type"}),
	    
			'start_date':DateInput(attrs={ "class":"form-control", 'type': 'date', 'min': current_date, "required": "true", "id": "start-date"}),
			'end_date':DateInput(attrs={"class":"form-control", 'type': 'date', 'min': current_date,"required": "true", "id": "end-date"}),
			'start_time':forms.Select(choices=[(f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}') for hour in range(8, 19) for minute in (0, 30)], 
				  attrs={"class":"form-select form-control", "required": "true", "id": "start-time"}),
			'end_time':forms.Select(choices=[(f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}') for hour in range(8, 19) for minute in (0, 30)],
				attrs={"class":"form-select form-control", "required": "true", "id": "end-time"}),

			# 'start_date':DateInput(attrs={ "class":"form-control", "required": "true"}),
			# 'end_date':DateInput(attrs={"class":"form-control","required":"true"}),
			# 'start_time':TimeInput(attrs={ "class":"form-control","required":"true",}),
			# 'end_time':TimeInput(attrs={ "class":"form-control","required":"true"}),
		}

   
