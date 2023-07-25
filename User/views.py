from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model, views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse  
from django.shortcuts import render, redirect  
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from .forms import UserCreationForm1, CustomAuthenticationForm, CustomSignUpForm
from .models import Invitations
from django.db import IntegrityError
from django.views.decorators.http import require_http_methods
import uuid
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.core.mail import (EmailMessage, EmailMultiAlternatives, get_connection, send_mail)
from django.db import transaction

def authenticate(email, password):
    try:
        user = get_user_model().objects.get(email=email)
        if user.check_password(password):
            return user
    except get_user_model().DoesNotExist:
        return None

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    elif request.method == "GET":
        form = CustomAuthenticationForm()

        context = {"form": form, "title": "Meeting Room Booking", "uuid": request.GET.get("uuid")}
        return render(request, "auth/login.html", context)

    else:
        email = request.POST.get("email")
        password = request.POST.get("password")

        if email and password:
            user = authenticate(email, password)

            next_page = request.POST.get('next') or request.GET.get('next')
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    messages.success(request, "Login successful.")
                    if next_page:
                        return redirect(next_page)
                    else:
                        return redirect('home')
                else:
                    msg = """Sorry, your account is not active, please check your 
                        email inbox to verify your account."""
            else:
                msg = """Please enter the correct email and password for your
                    account. Note that both fields are case-sensitive."""
                if next_page:
                    current_url = request.get_full_path()
                    return redirect(f"{current_url}?next={next_page}")

        messages.error(request, f"{msg}")
        form = CustomAuthenticationForm(initial={"email": email})
        context = {"form": form, "title": "Meeting Room Booking - Login", "uuid": request.GET.get("uuid")}
    return render(request, "auth/login.html", context)

def signup(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == 'POST':
        form = CustomSignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
            except IntegrityError :
                msg = """This email already registered."""
                messages.error(request, msg)
                return render(request, 'auth/signup.html', {'form': form})

            auth_login(request, user)
            msg = """Login successful."""
            messages.success(request, f"{msg}")
            return redirect('home') 
        else:
            msg = """Invalid password."""
            messages.error(request, msg)
    else:
        form = CustomSignUpForm()

    return render(request, 'auth/signup.html', {'form': form})

def signup_admin(request, uuid):
    if request.user.is_authenticated:
        return redirect("home")

    uuid_obj = Invitations.objects.filter(uuid=uuid.replace("-", ""))

    if request.method == "GET":
        if uuid_obj:
            form = CustomSignUpForm()
            context = {
                "form": form,
            }
        else:
            msg = """Invalid sign up URL."""
            messages.error(request, f"{msg}")
            return redirect("login")

    else:
        form = CustomSignUpForm(request.POST)
        context = {
            "form": form,
        }
        if form.is_valid():
            email_verification = uuid_obj.filter(
                email=form.cleaned_data["email"]
            ).first()

            if email_verification:
                # create User
                user = form.save()
                try:
                    user.is_superuser = True
                    user.is_staff = True
                    with transaction.atomic():
                        user.save()  
                except IntegrityError as e:
                    msg = """This email already registered."""
                    messages.error(request, msg)

                # Login after signup
                auth_login(request, user)
                # Delete invitation after signup successfully
                email_verification.delete()
                msg = """Login successfully."""
                messages.success(request, f"{msg}")
                return redirect("home")
            else:
                msg = """Email address not found."""
                messages.error(request, f"{msg}")
        else:
            msg = """Invalid password."""
            messages.error(request, f"{msg}")

    return render(request, "auth/signup.html", context)

def logout_user(request):
    logout(request)
    messages.success(request, "Logout successful.")
    return redirect('login')

@login_required
def admin_list(request):
    if not request.user.is_staff:
        return redirect('home')
    else:
        admins=get_user_model().objects.filter(is_staff=1)
        invitations = Invitations.objects.all()

        return render(request, 'admin_list.html', {
            'administrators': admins,
            'invitations': invitations,
        })

@login_required
@require_http_methods(["POST"])
def add_admin(request):
    data = request.POST
    email = data.get("email")
    user = get_user_model().objects.filter(email=email).first()
    # Condition: user does not exist. 
    if user == None:
        # check if invited
        inviteeCheck = Invitations.objects.filter(email=email).first()

        # not invited. Send signup invitation with uuid
        if not inviteeCheck:
            invitee = Invitations.objects.create(
                email=email,
                uuid=uuid.uuid4(),
            )
        else:
            inviteeCheck.uuid = uuid.uuid4()
            inviteeCheck.save()
            invitee = inviteeCheck

        emailContent = []
        connection = get_connection(username=None, password=None, fail_silently=False)
        mail_subject = (
            "Meeting Room Booking System | Administrator Invitation"
        )
        message = render_to_string(
            "email/adminRegistrationEmail.html",
            {
                "domain": request.build_absolute_uri("/signup_admin/" + str(invitee.uuid)),
            },
        )

        currMail = EmailMultiAlternatives(mail_subject, message, to=[email])
        currMail.attach_alternative(message, "text/html")
        emailContent.append(currMail)
        try:
            connection.send_messages(emailContent)
            # already invited. resend invitation  
            if inviteeCheck:
                messages.success(request, f"Invitation email resent successfully")
            else:
                messages.success(request, f"Invitation email sent successfully")
            return redirect("admin_list")
        except:
            messages.error(request, f"Mail sending failed")
            return redirect("admin_list")
    
    # Condition: user exists 
    if user != None:
        messages.warning(request, f"User already exist.")
        return redirect("admin_list")

@login_required
def deleteInvitation(request, pk):
    if request.method == "POST":
        Invitations.objects.filter(id=pk).delete()
        messages.success(request, "Invitation is deleted successfully")
        return redirect("admin_list")
    
    return redirect("admin_list")
