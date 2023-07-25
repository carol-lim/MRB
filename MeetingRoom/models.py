from django.contrib.auth.models import User
from django.db import models

class MeetingType(models.Model):
	type = models.CharField(max_length=100, unique=True)
	
	def __str__(self):
		return self.type
	
class MeetingRoom(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(auto_now=True)
	mroom_name = models.CharField(max_length=50)
	level = models.IntegerField()
	capacity = models.IntegerField()
	mr_image = models.ImageField(upload_to="images/", default="images\default.PNG")
	type = models.ForeignKey(MeetingType, on_delete=models.CASCADE, related_name='meetingroom')

	def __str__(self):
		return(f"{self.mroom_name}")

class MRBooking(models.Model):
	mroom = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, related_name='mrbookings')
	staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mrbookings')
	num_attendees = models.IntegerField()
	type = models.ForeignKey(MeetingType, on_delete=models.CASCADE, related_name='mrbookings')
	start_date = models.DateField()
	end_date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	created_at = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(auto_now=True)