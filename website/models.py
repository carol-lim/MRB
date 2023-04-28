from django.db import models

# Create your models here.
class MeetingRoom(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	modified_at = models.DateTimeField(auto_now=True)
	mroom_name = models.CharField(max_length=50)
	level = models.IntegerField()
	capacity = models.IntegerField()
	mr_image = models.ImageField(upload_to="images/", default="images\default.PNG")

	def __str__(self):
		return(f"{self.mroom_name}")