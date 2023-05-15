from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import AddMRForm, AddBookingForm
from .models import MeetingRoom, MRBooking
from django.db.models import Q
from datetime import datetime, timedelta

def get_available_meeting_rooms(start_datetime, end_datetime):
    booked_rooms = MRBooking.objects.filter(
        start_date__lte=end_datetime.date(), 
        end_date__gte=start_datetime.date(),
        start_time__lte=end_datetime.time(),
        end_time__gte=start_datetime.time()
    ).values_list('mroom', flat=True)

    available_rooms = MeetingRoom.objects.exclude(id__in=booked_rooms)
    return available_rooms

def get_scheduled_meeting_rooms_bookings(start_datetime, end_datetime):
    bookings = MRBooking.objects.filter(
        Q(start_date__lte=end_datetime.date()) & Q(end_date__gte=start_datetime.date()) &
        Q(start_time__gt=start_datetime.time()) & Q(start_time__lte=end_datetime.time()) & Q(end_time__gt=start_datetime.time()) 
    )
    return bookings

def get_scheduled_meeting_rooms_id(bookings):
    booked_rooms = bookings.values_list('mroom', flat=True)
    return booked_rooms

def get_scheduled_meeting_rooms(booked_rooms):
    scheduled_rooms = MeetingRoom.objects.filter(id__in=booked_rooms)
    return scheduled_rooms

def get_in_use_meeting_rooms_bookings(start_datetime, end_datetime):
    bookings = MRBooking.objects.filter(
        Q(start_date__lte=end_datetime.date()) & Q(end_date__gte=start_datetime.date()) &
        Q(start_time__lte=start_datetime.time()) & Q(end_time__gte=start_datetime.time())   
    )
    return bookings

def get_in_use_meeting_rooms_id(bookings):
    booked_rooms = bookings.values_list('mroom', flat=True)
    return booked_rooms

def get_in_use_meeting_rooms(booked_rooms):
    in_use_rooms = MeetingRoom.objects.filter(id__in=booked_rooms)
    return in_use_rooms

def home(request):
    # Check if logging in
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # Auth
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in")
            return redirect('home')
        
        else:
            messages.success(request, "Error log in, Please try again")
            return redirect('home', )
    else:        
        # start_datetime = datetime(2023, 5, 12, 9, 0)  # Example start datetime
        # end_datetime = datetime(2023, 5, 12, 11, 0)  # Example end datetime
        start_datetime = datetime.today()
        end_datetime = datetime.today() + timedelta(hours=1)
        count_availabile_now = get_available_meeting_rooms(start_datetime, end_datetime).count()

        bookings_scheduled = get_scheduled_meeting_rooms_bookings(start_datetime, end_datetime)
        rooms_scheduled = get_scheduled_meeting_rooms_id(bookings_scheduled)
        count_scheduled = get_scheduled_meeting_rooms(rooms_scheduled).count()
        
        bookings_in_use = get_in_use_meeting_rooms_bookings(start_datetime, end_datetime)
        rooms_in_use = get_in_use_meeting_rooms_id(bookings_in_use)
        count_in_use = get_in_use_meeting_rooms(rooms_in_use).count()

        return render(request, 'home.html',{
            'available_now': count_availabile_now,
            'scheduled': count_scheduled,
            'in_use': count_in_use,
        })

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('home')

def meeting_rooms(request):
    if request.user.is_authenticated:
        return render(request, 'meeting_rooms.html', {'meeting_rooms': MeetingRoom.objects.all()})
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')
    
def add_mr(request):
    form = AddMRForm(request.POST or None, request.FILES or None)
    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                add_mr = form.save()
                messages.success(request, "New meeting room added.")
                return redirect('meeting_rooms')
        return render(request, 'add_mr.html', {'form':form})
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')

def update_mr(request, pk):
	if request.user.is_authenticated:
		current_record = MeetingRoom.objects.get(id=pk)
		form = AddMRForm(request.POST or None, request.FILES or None, instance=current_record)
		if form.is_valid():
			form.save()
			messages.success(request, "Meeting Room Has Been Updated")
			return redirect('meeting_rooms')
		return render(request, 'update_mr.html', {'form':form})
	else:
		messages.success(request, "You Must Be Logged In.")
		return redirect('home')

def history(request, pk):
    if request.user.is_authenticated:
        return render(request, 'history.html', {
            'meeting_room': MeetingRoom.objects.get(id=pk), 
            'histories': MRBooking.objects.filter(mroom=pk), 
        })
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')
    
def add_history(request, pk):
    initial_data = {'mroom':pk}
    form = AddBookingForm(request.POST or None, initial=initial_data)
    if request.user.is_authenticated:
        if request.method == "POST":
            if form.is_valid():
                add_history = form.save()
                messages.success(request, "New booking history for the meeting room is added.")
                return redirect('history', pk)
        return render(request, 'add_history.html', {'meeting_room': MeetingRoom.objects.get(id=pk), 'form':form})
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')
    
def update_history(request, pk1, pk2):
    if request.user.is_authenticated:
        current_record = MRBooking.objects.get(id=pk2)
        form = AddBookingForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.success(request, "History Has Been Updated")
            return redirect('update_history', pk1, pk2)
        return render(request, 'update_history.html', {
            'meeting_room': MeetingRoom.objects.get(id=pk1), 
            'history': MRBooking.objects.get(id=pk2), 
            'form':form
        })
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')

def available_now(request):
    if request.user.is_authenticated:
        start_datetime = datetime.today()
        end_datetime = datetime.today() + timedelta(hours=1)
        availabile_now = get_available_meeting_rooms(start_datetime, end_datetime)
        return render(request, 'available_now.html', {'available_now': availabile_now, 'count': availabile_now.count()})
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')
    
def scheduled(request):
    if request.user.is_authenticated:
        start_datetime = datetime.today()
        end_datetime = datetime.today() + timedelta(hours=1)
        bookings = get_scheduled_meeting_rooms_bookings(start_datetime, end_datetime)
        rooms_id = get_scheduled_meeting_rooms_id(bookings)
        booked_rooms = get_scheduled_meeting_rooms(rooms_id)
        count = booked_rooms.count()
        
        return render(request, 'scheduled.html', {'bookings': bookings, 'rooms': booked_rooms, 'count': count})
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')
    
def now_in_use(request):
    if request.user.is_authenticated:
        start_datetime = datetime.today()
        end_datetime = datetime.today() + timedelta(hours=1)
        bookings = get_in_use_meeting_rooms_bookings(start_datetime, end_datetime)
        rooms_id = get_in_use_meeting_rooms_id(bookings)
        booked_rooms = get_in_use_meeting_rooms(rooms_id)
        count = booked_rooms.count()
        return render(request, 'now_in_use.html', {'bookings': bookings,'rooms': booked_rooms , 'count': count})
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')

def admin_list(request):
    if request.user.is_authenticated:
        return render(request, 'admin_list.html')
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')

def add_admin(request):
	# form = AddMRForm(request.POST or None, request.FILES or None)
    if request.user.is_authenticated:
        return render(request, 'add_admin.html',)
	# 	if request.method == "POST":
	# 		if form.is_valid():
	# 			add_mr = form.save()
	# 			messages.success(request, "New meeting room added.")
	# 			return redirect('meeting_rooms')
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')