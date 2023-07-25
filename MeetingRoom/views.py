from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import MRForm, bookingForm, TypeForm
from .models import MeetingRoom, MRBooking, MeetingType
from django.db.models import Q
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required
from .serializers import *
from django.shortcuts import render, redirect  

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

@login_required
def search(request):
    # form = SearchForm(request.POST or None)
    if request.method == "POST" and request.is_ajax():
        form = bookingForm(request.POST)
        # booking = form.save()
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('start_date')
        end_time = request.POST.get('end_time')
        num_attendees = request.POST.get('num_attendees')
        selectedType = request.POST.get('type')
        selectedTypeName = MeetingType.objects.get(id=selectedType).type

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
            available_rooms = get_available_meeting_rooms(start_datetime, end_datetime).filter(capacity__gte = num_attendees, type=selectedType)
            if available_rooms.count() > 0:

                # Serialize the data using the custom encoder
                room_list = []

                for room in available_rooms:
                    # Convert the MeetingRoom instance to a dictionary
                    room_dict = model_to_dict(room)

                    # Convert the ImageFieldFile to a string representation (e.g., URL or path)
                    # image_url = room.mr_image.url
                    typeName = room.type.type
                    # room_dict['image'] = image_url
                    room_dict['meetingType'] = typeName
                    room_dict['selectedTypeName'] = selectedTypeName

                    # Append the updated dictionary to the room_list
                    room_list.append(room_dict)

                serialized_data = json.dumps(room_list, cls=CustomJSONEncoder)
                return JsonResponse(serialized_data, safe=False)
            else:
                return JsonResponse("300", safe=False)
                # messages.warning(request, "No meeting room available in the selected timeframe. Please search again.")
    else:
        form = bookingForm()
        
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
        form = MRForm(request.POST or None, request.FILES or None)
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
        form = MRForm(request.POST or None, request.FILES or None, instance=current_record)
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
        form = bookingForm(request.POST or None, initial=initial_data)
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
        form = bookingForm(request.POST or None, instance=current_record)
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
        return render(request, 'availability/available_now.html', {'available_now': availabile_now, 'count': availabile_now.count()})
    
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

        return render(request, 'availability/scheduled.html', {'bookings': bookings, 'rooms': booked_rooms, 'count': count})
    
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
        return render(request, 'availability/now_in_use.html', {'bookings': bookings,'rooms': booked_rooms , 'count': count})

@login_required
def meeting_type(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        form = TypeForm(request.POST or None)
        types = MeetingType.objects.all().order_by('id')
        return render(request, 'meeting_type.html', {'form':form, 'types':types})
    
@login_required
def add_type(request):
    if request.method == "POST":
        form = TypeForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, "New meeting type added successfully.")
            return redirect('meeting_type')
        else:
            messages.warning(request, "Meeting type already exists.")
            return redirect('meeting_type')
    else:
        form = TypeForm()
    
    return redirect('meeting_type')

@login_required
def update_type(request, pk):
    current_type = MeetingType.objects.get(id=pk)
    form = TypeForm(request.POST or None, instance=current_type)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Meeting type updated successfully.")
            return redirect('meeting_type')
        else:
            messages.error(request, "Unable to submit.")
        
    context = {
        'type': current_type,
        'form': form, 
        "title": "Update Meeting Type: "+current_type.type
        }
    return render(request, 'update_type.html', context=context)
