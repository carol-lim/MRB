from django import forms
from .models import MeetingRoom, MRBooking, MeetingType
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class DateInput(forms.DateInput):
	input_type = 'date'

class TimeInput(forms.TimeInput):
	input_type = 'time'

class MRForm(forms.ModelForm):
	class Meta:
		model = MeetingRoom
		fields = ['mroom_name','level','capacity',  'type', 'mr_image']
		labels = {
			'mroom_name': 'Meeting Room Name',
			'level': 'Level',
			'capacity': 'Capacity',
			'type': 'Meeting Type',
			'mr_image': 'Meeting Room Image',
        }
		widgets = {
            'mroom_name': forms.TextInput(attrs={ "class":"form-control", "required": "true"}),
            'level': forms.NumberInput(attrs={ "class":"form-control", "required": "true", "min": "1"}),
            'capacity': forms.NumberInput(attrs={ "class":"form-control", "required": "true", "min": "2"}),
            'type': forms.Select(attrs={ "class":"form-control", "required": "true"}),
		}

class bookingForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		staff_choices = [(staff.id, f"{staff.first_name} {staff.last_name}") for staff in User.objects.all()]
		self.fields['staff'].choices = staff_choices

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
			'start_date':'Date',
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
			'end_date':DateInput(attrs={"class":"form-control", 'type': 'date', 'min': current_date, "id": "end-date"}),
			'start_time':forms.Select(choices=[(f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}') for hour in range(8, 19) for minute in (0, 30)], 
				  attrs={"class":"form-select form-control", "required": "true", "id": "start-time"}),
			'end_time':forms.Select(choices=[(f'{hour:02d}:{minute:02d}', f'{hour:02d}:{minute:02d}') for hour in range(8, 19) for minute in (0, 30)],
				attrs={"class":"form-select form-control", "required": "true", "id": "end-time"}),
		}

			
		# 'start_date':DateInput(attrs={ "class":"form-control", "required": "true"}),
		# 'end_date':DateInput(attrs={"class":"form-control","required":"true"}),
		# 'start_time':TimeInput(attrs={ "class":"form-control","required":"true",}),
		# 'end_time':TimeInput(attrs={ "class":"form-control","required":"true"}),
   
class TypeForm(forms.ModelForm):
	class Meta:
		model = MeetingType
		fields = ['type']
		labels = {
			'type': 'type',
        }
		widgets = {
            'type': forms.TextInput(attrs={ "class":"form-control", "required": "true"}),
		}
    