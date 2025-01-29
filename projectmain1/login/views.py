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
           user = authenticate(username=username, password=password)  # Authenticate user
        
           
           if user: # Debugging log
            auth_login(request, user)  # Log in the user

            if remember_me:
                # Extend session expiration to 30 days
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
            else:
                # Default session expiry (browser close)
                request.session.set_expiry(0)


            if hasattr(user, 'camp_head'):
                # Get the first camp associated with the camp head
                camp_head2_first = user.camp_head.campHead2.first()
                
                if camp_head2_first:  # Handle case where no camp is assigned
                    if not camp_head2_first.is_active:  # Check if the camp is inactive
                        return render(request, 'login.html', {
                            'error': 'This volunteer is assigned to a deactivated camp. Please contact the administrator.'
                        })

                    # If the camp is active, proceed with login
                    camp_id = camp_head2_first.id
                    signer = Signer()
                    signed_value = signer.sign(camp_id)
            
                    # Redirect to CampHead dashboard
                    response = redirect('Volunteer')
                    response.set_cookie(
                        'login',  # Cookie name
                        signed_value,  # Encrypted cookie value
                        httponly=True  # Prevent JavaScript access
                    )
                    return response
                else:
                    return render(request, 'login.html', {
                        'error': 'This volunteer is not assigned to any camp.'
                    })
     
                 
                    
                    
   
               # Check if the user is a VolunteerHead
            elif hasattr(user, 'volunteerhead'):
                   zone_i= user.volunteerhead.zones.first() # Get associated zone ID
                   if zone_i:  # Handle null camp_head case
                        zone_id=zone_i.id
                        signer = Signer()
                        signed_value = signer.sign(zone_id)
                        
        
                        # Redirect to VolunteerHead dashboard
                        response = redirect('Camp__head')
                        response.set_cookie(
                            'login',  # Cookie name
                            signed_value,  # Encrypted cookie value  
                         #    max_age=3600,  # Cookie expires in 1 hour
                            httponly=True  # Prevent JavaScript access
                        )
                        return response
                   else:
                    return render(request, 'login.html', {'error': 'this volunteer not assigned any other Zone'})     
            
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
     
   
               # Redirect to login if the user is not associated with any role
            else:
                 return redirect('superadmin')
               
           else:
               
               return render(request, 'login.html', {'error': 'Invalid username or password.'})
       return render(request,'login.html')

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



