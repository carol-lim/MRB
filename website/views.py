from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import AddMRForm, AddBookingForm, UserCreationForm
from .models import MeetingRoom, MRBooking, MeetingType
from django.db.models import Q
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from .serializers import *
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.http import HttpResponse  
from django.shortcuts import render, redirect  
from django.contrib.auth import login, authenticate  
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from .forms import UserCreationForm
# from .forms import SignupForm  
# from django.contrib.sites.shortcuts import get_current_site  
# from django.utils.encoding import force_bytes, force_text  
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
# from django.template.loader import render_to_string  
# from django.contrib.auth.models import User  
# from django.core.mail import EmailMessage  

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to a default page
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            # Redirect to the next URL or a default page after successful login
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')  # Redirect to a default page
        else:
            # Add an error message for invalid credentials
            messages.success(request, "Invalid username or password")
            return render(request, 'login.html')
    else:
        messages.success(request, "Please login to access the system content.")
        return render(request, 'login.html')

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

@login_required
def home(request):
    # admins
    if request.user.is_staff or request.user.is_superuser: 
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
        
    # staff
    else:
        user_histories = MRBooking.objects.filter(staff=request.user).order_by('-id')
        if request.GET.get('book_success') == 'true':
            messages.success(request, "New booking added.")
            
        return render(request, 'home.html',{
            'histories': user_histories,
        })

def logout_user(request):
    logout(request)
    messages.success(request, "Logout successful.")
    return redirect('login')

@login_required
def search(request):
    # form = SearchForm(request.POST or None)
    if request.method == "POST" and request.is_ajax():
        form = AddBookingForm(request.POST)
        # booking = form.save()
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        num_attendees = request.POST.get('num_attendees')

        # Convert start_date string to a date object
        sd = datetime.strptime(start_date, '%Y-%m-%d').date()
        st = datetime.strptime(start_time, '%H:%M').time()
        ed = datetime.strptime(end_date, '%Y-%m-%d').date()
        et = datetime.strptime(end_time, '%H:%M').time()

        # Convert the date and time strings to datetime objects
        start_datetime = datetime.combine(sd, st)
        end_datetime = datetime.combine(ed, et)

        if end_datetime <= start_datetime:
            return JsonResponse("100", safe=False)
        elif end_datetime <= datetime.today() or start_datetime <= datetime.today():
            return JsonResponse("200", safe=False)
        else:
            # Serialize the available meeting rooms as JSON
            available_rooms = get_available_meeting_rooms(start_datetime, end_datetime).filter(capacity__gte = num_attendees)
            if available_rooms.count() > 0:

                # Serialize the data using the custom encoder
                room_list = []

                for room in available_rooms:
                    # Convert the MeetingRoom instance to a dictionary
                    room_dict = model_to_dict(room)

                    # Convert the ImageFieldFile to a string representation (e.g., URL or path)
                    image_url = room.mr_image.url
                    room_dict['image'] = image_url

                    # Append the updated dictionary to the room_list
                    room_list.append(room_dict)

                serialized_data = json.dumps(room_list, cls=CustomJSONEncoder)
                return JsonResponse(serialized_data, safe=False)
            else:
                messages.success(request, "No meeting room available in the selected timeframe. Please search again.")
    else:
        form = AddBookingForm()
        
    return render(request, 'search.html', {'form': form})

@login_required
def booking(request):
    if request.method == "POST" and request.is_ajax():
        
        staff = request.user
        mroom = request.POST.get('mroom')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        num_attendees = request.POST.get('num_attendees')
        type = request.POST.get('type')

        sd = datetime.strptime(start_date, '%Y-%m-%d').date()
        st = datetime.strptime(start_time, '%H:%M').time()
        ed = datetime.strptime(end_date, '%Y-%m-%d').date()
        et = datetime.strptime(end_time, '%H:%M').time()
        
        newbooking = MRBooking.objects.create(staff=staff, mroom=MeetingRoom.objects.get(id=mroom), start_date=sd, start_time=st, end_date=ed, end_time=et, num_attendees=num_attendees, type=MeetingType.objects.get(id=type))
        newbooking.save()

        return JsonResponse("1", safe=False)    

@login_required
def meeting_rooms(request):
    return render(request, 'meeting_rooms.html', {'meeting_rooms': MeetingRoom.objects.all(), 'count':MeetingRoom.objects.all().count()})
    
@login_required
def add_mr(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        form = AddMRForm(request.POST or None, request.FILES or None)
        if request.method == "POST":
            if form.is_valid():
                add_mr = form.save()
                messages.success(request, "New meeting room added.")
                return redirect('meeting_rooms')
        return render(request, 'add_mr.html', {'form':form})

@login_required
def update_mr(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    else:
        current_record = MeetingRoom.objects.get(id=pk)
        form = AddMRForm(request.POST or None, request.FILES or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.success(request, "Meeting Room Has Been Updated")
            return redirect('meeting_rooms')
        return render(request, 'update_mr.html', {'form':form})

@login_required
def history(request, pk):
    return render(request, 'history.html', {
        'meeting_room': MeetingRoom.objects.get(id=pk), 
        'histories': MRBooking.objects.filter(mroom=pk), 
    })
    
@login_required
def add_history(request, pk):
    if not request.user.is_staff:
        return redirect('home')
    else:
        initial_data = {'mroom':pk}
        form = AddBookingForm(request.POST or None, initial=initial_data)
        if request.method == "POST":
            if form.is_valid():
                add_history = form.save()
                messages.success(request, "New booking history for the meeting room is added.")
                return redirect('history', pk)
        return render(request, 'add_history.html', {'meeting_room': MeetingRoom.objects.get(id=pk), 'form':form})
    
@login_required
def update_history(request, pk1, pk2):
    if not request.user.is_staff:
        return redirect('home')
    else:
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

@login_required
def available_now(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        start_datetime = datetime.today()
        end_datetime = datetime.today() + timedelta(hours=1)
        availabile_now = get_available_meeting_rooms(start_datetime, end_datetime)
        return render(request, 'available_now.html', {'available_now': availabile_now, 'count': availabile_now.count()})
    
@login_required
def scheduled(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        start_datetime = datetime.today()
        end_datetime = datetime.today() + timedelta(hours=1)
        bookings = get_scheduled_meeting_rooms_bookings(start_datetime, end_datetime)
        rooms_id = get_scheduled_meeting_rooms_id(bookings)
        booked_rooms = get_scheduled_meeting_rooms(rooms_id)
        count = booked_rooms.count()

        return render(request, 'scheduled.html', {'bookings': bookings, 'rooms': booked_rooms, 'count': count})
    
@login_required
def now_in_use(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        start_datetime = datetime.today()
        end_datetime = datetime.today() + timedelta(hours=1)
        bookings = get_in_use_meeting_rooms_bookings(start_datetime, end_datetime)
        rooms_id = get_in_use_meeting_rooms_id(bookings)
        booked_rooms = get_in_use_meeting_rooms(rooms_id)
        count = booked_rooms.count()
        return render(request, 'now_in_use.html', {'bookings': bookings,'rooms': booked_rooms , 'count': count})

@login_required
def admin_list(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        if request.GET.get('add_admin_success') == 'true':
            messages.success(request, "New admin added. An invitation email has been sent to new admin to set password.")
            
        return render(request, 'admin_list.html', {
            'administrators': get_user_model().objects.filter(is_staff=1),
        })

@login_required
def add_admin(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_unusable_password()  # Set an unusable password
            user.is_staff = True
            user.is_active = True
            user.save()
            
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            set_password_url = reverse('set_password', kwargs={'uidb64': uidb64, 'token': token})
            
            # Customize the email subject and message as per your requirements
            subject = f"[Meeting Room Booking System] New Admin Password Setting - {user.first_name} {user.last_name}"
            message = f"Please click the link below to set your password:\n\n{request.build_absolute_uri(set_password_url)}\n\nThank you!"
            from_email = 'carollim.dev@gmail.com'  # Set your sender email address
            recipient_list = [user.email]
            
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
            return redirect('/admin_list/?add_admin_success=true')  # Redirect to a success page or login page
            
    else:
        form = UserCreationForm()
    
    return render(request, 'add_admin.html', {'form': form})
