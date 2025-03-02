from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from volunteerhead.models import Camp
from superadmin.models import Zone
from django.core.signing import Signer, BadSignature
from django.utils.timezone import now, timedelta
from .models import OTPVerification
import random
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.cache import cache_control

# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login(request):
    if request.POST:
        username = request.POST['username']  # Getting username and password
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')

        # Hardcoded superadmin credentials
        SUPERADMIN_USERNAME = "shahin"
        SUPERADMIN_PASSWORD = "12345678"

        # Check if the provided credentials are for the superadmin
        if username == SUPERADMIN_USERNAME and password == SUPERADMIN_PASSWORD:
            # Log in the superadmin directly
            user = authenticate(username=SUPERADMIN_USERNAME, password=SUPERADMIN_PASSWORD)
            if not user:
                # Create or fetch a superadmin user (ensure they exist in the database)
                from django.contrib.auth.models import User
                user, created = User.objects.get_or_create(username=SUPERADMIN_USERNAME)
                if created:
                    user.set_password(SUPERADMIN_PASSWORD)
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
            auth_login(request, user)

            # Set session expiration based on "remember_me"
            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
            else:
                request.session.set_expiry(0)

            # Redirect to the superadmin dashboard
            return redirect('superadmin')

        # Authenticate other users
        user = authenticate(username=username, password=password)

        if user:
            auth_login(request, user)

            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
            else:
                request.session.set_expiry(0)

            if hasattr(user, 'camp_head'):
                # Get the first camp associated with the camp head
                camp_head2_first = user.camp_head.campHead2.first()

                if camp_head2_first:
                    if not camp_head2_first.is_active:
                        return render(request, 'login.html', {
                            'error': 'This volunteer is assigned to a deactivated camp. Please contact the administrator.'
                        })

                    camp_id = camp_head2_first.id
                    signer = Signer()
                    signed_value = signer.sign(camp_id)

                    response = redirect('Volunteer')
                    response.set_cookie(
                        'login',
                        signed_value,
                        httponly=True
                    )
                    return response
                else:
                    return render(request, 'login.html', {
                        'error': 'This volunteer is not assigned to any camp.'
                    })

            elif hasattr(user, 'volunteerhead'):
                zone_i = user.volunteerhead.zones.first()
                if zone_i:
                    zone_id = zone_i.id
                    signer = Signer()
                    signed_value = signer.sign(zone_id)

                    response = redirect('Camp__head')
                    response.set_cookie(
                        'login',
                        signed_value,
                        httponly=True
                    )
                    return response
                else:
                    return render(request, 'login.html', {'error': 'This volunteer is not assigned to any Zone'})

            elif hasattr(user, 'volunteer'):
                assigned_camp = user.volunteer.camp1

                if assigned_camp:  # Check if the volunteer is assigned a camp

                    # If the camp is active, proceed with login
                    camp_id = assigned_camp.id
                    signer = Signer()
                    signed_value = signer.sign(camp_id)

                    # Redirect to CampHead dashboard
                    response = redirect('volunteer1')
                    response.set_cookie(
                        'login',  # Cookie name
                        signed_value,  # Encrypted cookie value
                        httponly=True  # Prevent JavaScript access
                    )
                    return response
                else:
                    return render(request, 'volunteers.html', {
                        'error': 'your not assigned to a camp. Please contact the administrator.'
                    })

            else:
                return redirect('superadmin')

        else:
            return render(request, 'login.html', {'error': 'Invalid username or password.'})

    return render(request, 'login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def front(request):
    Zones  = Zone.objects.all()
    return render(request,'front.html',{'Zones':Zones})

@login_required
def volunteer1(request):
    # Get the logged-in user
    user = request.user
    
    # Check if the user is a volunteer
    if hasattr(user, 'volunteer'):
        volunteer = user.volunteer
        camp_name = volunteer.camp1.name if volunteer.camp1 else "No camp assigned"

        return render(request, 'volunteers.html', {'camp_name': camp_name})

def logout_view(request):
    logout(request)
    response = redirect('login')
    response.delete_cookie('login')
    
    return response 
      








def forget(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:

            user = User.objects.get(email=email)
            
            
            # Generate OTP
            otp = random.randint(100000, 999999)
            
            # Save OTP in the database with a timestamp
            OTPVerification.objects.update_or_create(
                user=user,
                defaults={'otp': otp, 'expires_at': now() + timedelta(minutes=10)}
            )
            
            # Send OTP to the user's email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                'no-reply@example.com',
                [email],
                fail_silently=False,
            )
            return render(request, 'otp_sent.html', {'message': 'OTP sent to your email'})
        except User.DoesNotExist:
            return render(request, 'forget.html', {'error': 'Email not registered'})
    return render(request, 'forget.html')

def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        password = request.POST.get('password')
        try:
            otp_entry = OTPVerification.objects.get(otp=otp, expires_at__gte=now())
            
            # Update the user's password
            user = otp_entry.user
            user.password = make_password(password)
            user.save()
            
            # Delete the OTP entry
            otp_entry.delete()
            
            return render(request, 'login.html', {'error': 'Password has been reset successfully'})
        except OTPVerification.DoesNotExist:
            return render(request, 'forget.html', {'error': 'Invalid or expired OTP'})
    return render(request, 'forget.html')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login
from django.core.signing import Signer
import json

@csrf_exempt
def login1(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            print("1")
            print(data)
            username = data.get('username')
            password = data.get('password')
            remember_me = data.get('remember_me', False)

            # Authenticate the user
            user = authenticate(username=username, password=password)

            if user and hasattr(user, 'camp_head'):  # Only allow camp_head users
                # Get the first camp associated with the camp head
                camp_head2_first = user.camp_head.campHead2.first()

                if camp_head2_first:
                    if not camp_head2_first.is_active:
                        return JsonResponse({
                            "error": "This volunteer is assigned to a deactivated camp. Please contact the administrator."
                        }, status=400)

                    camp_id = camp_head2_first.id
                    print(camp_id)
                    return JsonResponse({
                        "message": "Login successful",
                        "redirect": "Volunteer",
                        "camp_id": camp_id
                    })
                else:
                    return JsonResponse({
                        "error": "This volunteer is not assigned to any camp."
                    }, status=400)
            else:
                return JsonResponse({
                    "error": "Invalid username or password, or you do not have permission to log in."
                }, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)