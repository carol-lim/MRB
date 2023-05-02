from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import AddMRForm, AddBookingForm
from .models import MeetingRoom, MRBooking

def home(request):
    # Check of logging in
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
            return redirect('home')
    else:        
        return render(request, 'home.html')

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
            'histories': MRBooking.objects.all(), 

        })
    else:
        messages.success(request, "You Must Be Logged In.")
        return redirect('home')
    
def add_history(request, pk):
    form = AddBookingForm(request.POST or None)
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
			return redirect('meeting_rooms', pk1, 'update_history', pk2)
		return render(request, 'update_history.html', {
            'meeting_room': MeetingRoom.objects.get(id=pk1), 
            'history': MRBooking.objects.get(id=pk2), 
            'form':form
        })
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