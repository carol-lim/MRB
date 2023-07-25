from django.contrib import admin
from .models import MeetingRoom, MeetingType, MRBooking

# Register your models here.
admin.site.register(MeetingRoom)
admin.site.register(MeetingType)
admin.site.register(MRBooking)