from django import forms
from .models import MeetingRoom, MRBooking

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
			'staff',
			'num_attendees',
			'type',
			'start_date',
			'end_date',
			'start_time',
			'end_time'
		]
		labels = {
			'staff':'Staff',
			'num_attendees':'Number of Attendees',
			'type':'Type of Meeting',
			'start_date':'Start Date',
			'end_date':'End Date',
			'start_time':'Start Time',
			'end_time':'End Time'
        }
		widgets = {
            'staff': forms.TextInput(attrs={"class":"form-control", "required": "true"}),
			'num_attendees':forms.NumberInput(attrs={ "class":"form-control", "required": "true", "min": "2"}),
            'type': forms.TextInput(attrs={ "class":"form-control", "required": "true"}),
			'start_date':forms.DateInput(attrs={ "class":"form-control","required":"true",}),
			'end_date':forms.DateInput(attrs={"class":"form-control","required":"true"}),
			'start_time':forms.TimeInput(attrs={ "class":"form-control","required":"true",}),
			'end_time':forms.TimeInput(attrs={ "class":"form-control","required":"true"}),
		}