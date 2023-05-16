from django import forms
from .models import MeetingRoom, MRBooking
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget

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
	start_date=forms.DateField(widget=forms.DateInput(attrs={"class":"form-control", "required": "true", "id": "start-date-input"})),
	end_date=forms.DateField(widget=forms.DateInput(attrs={"class":"form-control", "required": "true", "id": "end-date-input"})),
	start_time=forms.TimeField(widget=forms.TimeInput(attrs={"class":"form-control", "required": "true", "id": "start-time-input"})),
	end_time=forms.TimeField(widget=forms.TimeInput(attrs={"class":"form-control", "required": "true", "id": "end-time-input"})),

class NewBookingForm(forms.ModelForm):
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