from django import forms
from .models import MeetingRoom, MRBooking
from django.utils import timezone
from datetime import datetime

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
			'num_attendees':forms.NumberInput(attrs={ "class":"form-control", "required": "true", "min": "2"}),
            'type': forms.Select(attrs={ "class":"form-control", "required": "true"}),
			'start_date':DateInput(attrs={ "class":"form-control", "required": "true"}),
			'end_date':DateInput(attrs={"class":"form-control","required":"true"}),
			'start_time':TimeInput(attrs={ "class":"form-control","required":"true",}),
			'end_time':TimeInput(attrs={ "class":"form-control","required":"true"}),
		}

class SearchForm(forms.Form):
	current_date = timezone.now().date()
	
	start_date = forms.DateField(widget=forms.DateInput(attrs={"class":"form-control mb-2", 'type': 'date', 'min': current_date, "required": "true", "id": "start-date"}))
	
	start_time = forms.ChoiceField(
		choices=[(f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}') for hour in range(8, 19) for minute in (0, 30)],
		widget=forms.Select(attrs={"class":"form-select form-control mb-2", "required": "true", "id": "start-time"}))
	
	end_date = forms.DateField(widget=forms.DateInput(attrs={"class":"form-control mb-2", 'type': 'date', 'min': current_date,"required": "true", "id": "end-date"}))
	
	end_time = forms.ChoiceField(
		choices=[(f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}') for hour in range(8, 19) for minute in (30, 0) if hour < 18 or (hour == 18 and minute == 30)], 
		widget=forms.Select(attrs={"class":"form-select form-control mb-2", "required": "true", "id": "end-time"}))