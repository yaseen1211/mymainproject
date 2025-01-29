from pyexpat.errors import messages
import re
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User, Group
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import VolunteerHead,Zone
from camp.models import Category
from django.core.mail import send_mail
from .forms import VolunteerRegistrationForm
from django.views.decorators.cache import cache_control

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@csrf_exempt
def superadmin(request):
    if not request.user.is_superuser:
        return render(request, 'login.html', {'error': 'you are not Access'})

    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        mode = data.get('mode')
        
        print(data)
        if mode=="1": 
            
            volunteerHead_id = data.get('volunteerHead_id')   # Handle product editing
            
            volunteer = get_object_or_404(VolunteerHead, id=volunteerHead_id)

            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")
            # password = data.get("password")

            try:
                # Update the linked User instance
                user = volunteer.user
                user.username = name  # Ensure username matches email
                user.email = email
                # if password:  # Update password only if provided
                #     user.set_password(password)
                user.save()

                # Update the VolunteerHead fields
                volunteer.name = name
                volunteer.email = email
                volunteer.phone = phone
                volunteer.save()

                return JsonResponse({
                    'name': name,
                    'email': email,
                    'phone': phone,
                   })

            except IntegrityError:
                error_message = "An unexpected error occurred while updating the data."
                

        elif mode == "2": #add a new product
                print("3")
        
                name = data.get("volunteer_head_Name")
                email = data.get("volunteer_head_Email")
                phone = data.get("volunteer_head_phone")
               
                if VolunteerHead.objects.filter(email=email).exists():
                    return JsonResponse({'status': 'error', 'message': 'Volunteer_head email already exists!'})

                else:
                    
                        # Create a new User instance
                        user = User.objects.create_user(username=name, email=email)

                        # Create a new VolunteerHead instance linked to the User
                        VolunteerHead.objects.create(user=user, name=name, email=email, phone=phone)

                        # messages.success(request, f"Volunteer {name} added successfully.")
                        return JsonResponse({'status': 'success', 'message':"Volunteer_head added successfully"})
                

 
        elif mode == "3":
        
                volunteerHead  = VolunteerHead.objects.all() 
                volunteerHead_data = list(volunteerHead.values('id', 'name', 'email', 'phone'))
                return JsonResponse({
                    'volunteerHead_data': volunteerHead_data,
                    })
        
        elif mode=="4":

            volunteer_head_id = data.get('volunteerHead_data1_id')
            volunteer_head = get_object_or_404(VolunteerHead, id=volunteer_head_id)
            if volunteer_head.zones.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot delete VolunteerHead while it is associated with one or more Zones.'
                })
            user = volunteer_head.user
            volunteer_head.delete()
            user.delete()
            return JsonResponse({
                'success': True,
                'message': 'VolunteerHead deleted successfully.'
            })
        
        elif mode=="5":#send_registration_email
               try:
                   volunteerHead_data1_id = data.get('volunteerHead_data1_id')         
                   volunteer = get_object_or_404(VolunteerHead, id=volunteerHead_data1_id)
                   
           
                   volunteer.generate_registration_token()
           
                   registration_link = request.build_absolute_uri(
                       reverse('register_volunteer') + f'?token={volunteer.registration_token}'
                   )
                   
           
                   subject = "Volunteer Registration"
                   message = f"Hello {volunteer.name},\n\nPlease complete your registration here:\n\n{registration_link}"
                   from_email = settings.EMAIL_HOST_USER
                   recipient_list = [volunteer.email]
           
                   send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                             
                   return JsonResponse({'message': "Registration email sent successfully."})
                
               except Exception as e:
                   return JsonResponse({'error': str(e)}, status=500)
        
                         
    categories  = Category.objects.all()      
    volunteerHeads = VolunteerHead.objects.all()
    return render(request, 'admin.html',{'volunteerHeads':volunteerHeads})




def register_volunteer(request):
    if not request.user.is_superuser:
        return render(request, 'login.html', {'error': 'you are not Access'})
    token = request.GET.get('token')  # Get token from the URL query parameter
    
    if token:
        try:
            # Get the volunteer based on the token
            volunteer = VolunteerHead.objects.get(registration_token=token)

            if request.method == 'POST':
                form = VolunteerRegistrationForm(request.POST)
                if form.is_valid():
                    # Save the new volunteer data
                    volunteer.name = form.cleaned_data['name']
                    volunteer.email = form.cleaned_data['email']
                    volunteer.phone = form.cleaned_data['phone']
                    volunteer.password = form.cleaned_data['password']
                    volunteer.registration_token = None  # Clear the token once used
                    volunteer.save()
                    user = volunteer.user
                    user.username = form.cleaned_data['name']  # Ensure username matches email
                    user.email = form.cleaned_data['email']
                    user.set_password(form.cleaned_data['password'])
                
                    user.save()
                    return render(request, 'successful registration.html')  # Redirect to success page after registration
        except VolunteerHead.DoesNotExist:
            # Token invalid or expired, handle error
            return render(request, 'successful registration.html')
    
    else:
        # Token missing from URL
        return render(request, 'invalid_request.html')

    # Show the form pre-filled with volunteer data if available
    form = VolunteerRegistrationForm(initial={'name': volunteer.name, 'email': volunteer.email, 'phone': volunteer.phone})
    return render(request, 'register_volunteer.html',{'form': form})


@csrf_exempt
def zonemanage(request):
    if not request.user.is_superuser:
        return render(request, 'login.html', {'error': 'you are not Access'})


    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        mode = data.get('mode')
        
                

        if mode == "2": #add a new product
                print("3")
                print(data)
        
                zone_name = data.get("zone_name")
                zone_description = data.get("zone_description")
                volunteer_head_id = data.get("volunteer_head_id")
               
                if zone_name:
                # Assign volunteer head if selected
                     volunteer_head = None
                     if volunteer_head_id:
                         volunteer_head = get_object_or_404(VolunteerHead, id=volunteer_head_id)
                     Zone.objects.create(name=zone_name, description=zone_description, volunteer_head=volunteer_head)
                     return JsonResponse({'status': 'success', 'message':"zone added successfully"})
                
                

 
        elif mode == "3":
        
                zones = Zone.objects.select_related('volunteer_head').all() 
                zone_data = []
                for zone in zones:
                    zone_data.append({
                        'id': zone.id,
                        'name': zone.name,
                        'description': zone.description,
                        'volunteer_head': {
                            'id': zone.volunteer_head.id if zone.volunteer_head else None,
                            'name': zone.volunteer_head.name if zone.volunteer_head else None,
                           
                }
            })
                return JsonResponse({
                    'zones': zone_data,
                    })
        
        elif mode=="4":

            zoneid = data.get('zoneid')
            zone = get_object_or_404(Zone, id=zoneid)
            zone.delete()
            return JsonResponse({'success': True, 'message': 'Zone deleted successfully.'})
        
        elif mode=="5":#mange category_name
            print(data)

            category_name = data.get('category_name')
            Category.objects.create(name=category_name)
            return JsonResponse({'success': True, 'message': 'category new item added successfully.'})
            

    return render(request, 'admin.html')

@csrf_exempt
def DeleteCategoryItem(request):
    if not request.user.is_superuser:
        return render(request, 'login.html', {'error': 'you are not Access'})
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        mode = data.get('mode')


        if mode=="2":#mange category_name
            print(data)

            category_name = data.get('category_name')
            Category.objects.create(name=category_name)
            return JsonResponse({'success': True, 'message': 'category new item added successfully.'})


        elif mode == "3":
                categories  = Category.objects.all() 
                categories1 = list(categories.values('id', 'name'))
                return JsonResponse({
                    'categories1': categories1,
                    })
        elif mode=="4":
            print(data)
            

            category_id = data.get('category_id')
            Category1 = get_object_or_404(Category, id=category_id)
            Category1.delete()
            return JsonResponse({'success': True, 'message': 'categoryItem deleted successfully.'})
        
       