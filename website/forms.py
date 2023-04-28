from django import forms
from .models import MeetingRoom

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
            'mroom_name': forms.TextInput(attrs={"placeholder":"Meeting Room Name", "class":"form-control", "required": "true"}),
            'level': forms.NumberInput(attrs={"placeholder":"Level", "class":"form-control", "required": "true", "min": "1"}),
            'capacity': forms.NumberInput(attrs={"placeholder":"Capacity", "class":"form-control", "required": "true", "min": "2"}),
		}