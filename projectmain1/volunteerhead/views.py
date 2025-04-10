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
from superadmin.models import VolunteerHead,Zone
from camp.models import Category
from django.core.mail import send_mail
from superadmin.forms import VolunteerRegistrationForm
from .models import CampHead,Volunteer,Camp
from .forms import CampHeadRegistrationForm
from django.core.signing import Signer, BadSignature
from django.views.decorators.cache import cache_control

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@csrf_exempt
def Camp__head(request):

    if not hasattr(request.user, 'volunteerhead'):
        return render(request, 'login.html', {'error': 'you are not Access'})
    
    signer = Signer()
    signed_value = request.COOKIES.get('login')
    zoneid = signer.unsign(signed_value)
    zone1 = Zone.objects.get(id=zoneid)

    
    
    if not hasattr(request.user, 'volunteerhead'):
        return render(request, 'login.html', {'error': 'you are not Access'})
    # user_type= request.COOKIES.get('user_type')

    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        mode = data.get('mode')
        
        print(data)
        if mode=="1": 
            
            CampHead_Id = data.get('CampHead_Id')   # Handle product editing
            
            CampHead1= get_object_or_404(CampHead, id=CampHead_Id)

            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")
            # password = data.get("password")

            try:
                # Update the linked User instance
                user = CampHead1.user
                user.username = name  # Ensure username matches email
                user.email = email
                # if password:  # Update password only if provided
                #     user.set_password(password)
                user.save()

                # Update the VolunteerHead fields
                CampHead1.name = name
                CampHead1.email = email
                CampHead1.phone = phone
                CampHead1.save()

                return JsonResponse({
                    'name': name,
                    'email': email,
                    'phone': phone,
                   })

            except IntegrityError:
                error_message = "An unexpected error occurred while updating the data."
                

        elif mode == "2":
                print("3")
        
                name = data.get("Camp_head_Name")
                email = data.get("Camp_head_Email")
                phone = data.get("Camp_head_phone")
               
                if User.objects.filter(email=email).exists():
                    return JsonResponse({'status': 'error', 'message': 'Camp_head email already exists!'})

                else:
                    
                        # Create a new User instance
                        user = User.objects.create_user(username=name, email=email)

                        # Create a new VolunteerHead instance linked to the User
                        CampHead.objects.create(user=user, name=name, email=email, phone=phone, zone1=zone1)

                        # messages.success(request, f"Volunteer {name} added successfully.")
                        return JsonResponse({'status': 'success', 'message':"Camp_head added successfully"})
                

 
        elif mode == "3":
                cumpHead1 = zone1.zone3.all()    

                cumpHead_data = list(cumpHead1.values('id', 'name', 'email', 'phone'))
                return JsonResponse({
                    'cumpHead_data': cumpHead_data,
                    })
        
        elif mode=="4":
              print("1")
              CampHead_Id = data.get('CampHead_Id')  # Get the ID from the request data
              print(CampHead_Id)
              camp_head = get_object_or_404(CampHead, id=CampHead_Id)  # Fetch the CampHead instance
              print(camp_head)
          
              # Check if the CampHead is associated with any Camp
              if camp_head.campHead2.exists(): 
                  print("2") # 'campHead2' is the related name in the Camp model
                  return JsonResponse({
                      'success': False,
                      'message': 'Cannot delete CampHead because it is associated with one or more Camps.'
                  })  # Return a bad request response
          
              # Get the associated User object and delete both CampHead and User
              user = camp_head.user
              camp_head.delete()
              user.delete()
          
              return JsonResponse({
                  'success': True,
                  'message': 'CampHead and associated User deleted successfully.'
              })
        
        elif mode=="5":#send_registration_email
               try:
                   CampHead_Id = data.get('CampHead_Id')         
                   CampHead_I = get_object_or_404(CampHead, id=CampHead_Id)
                   
           
                   CampHead_I.generate_registration_token()
           
                   registration_link = request.build_absolute_uri(
                       reverse('register_Camphead') + f'?token={CampHead_I.registration_token}'
                   )
                   
           
                   subject = "CampHead Registration"
                   message = f"Hello {CampHead_I.name},\n\nPlease complete your registration here:\n\n{registration_link}"
                   from_email = settings.EMAIL_HOST_USER
                   recipient_list = [CampHead_I.email]
           
                   send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                             
                   return JsonResponse({'message': "Registration email sent successfully."})
                
               except Exception as e:
                   return JsonResponse({'error': str(e)}, status=500)
        elif mode=="6":
             try:
                   # Get all CampHead objects
                 camp_heads = CampHead.objects.all()
             
                 for camp_head in camp_heads:
                     # Generate a unique registration token for each CampHead
                     camp_head.generate_registration_token()
             
                     # Build the registration link with the token
                     registration_link = request.build_absolute_uri(
                         reverse('register_Camphead') + f'?token={camp_head.registration_token}'
                     )
             
                     # Prepare the email content
                     subject = "CampHead Registration"
                     message = (
                         f"Hello {camp_head.name},\n\n"
                         f"Please complete your registration here:\n\n{registration_link}\n\n"
                         "Best regards,\nYour Team"
                     )
                     from_email = settings.EMAIL_HOST_USER
                     recipient_list = [camp_head.email]
             
                     # Send the email
                     send_mail(subject, message, from_email, recipient_list, fail_silently=False)
             
                 return JsonResponse({'message': "Registration emails sent successfully to all CampHeads."})
             
             except Exception as e:
                 return JsonResponse({'error': str(e)}, status=500)
                
    campHeads = zone1.zone3.all()
    camps = Camp.objects.filter(campHead1__zone1_id=zoneid).select_related('campHead1__zone1')
    volunteers = zone1.zone2.all() 
    zone_name = zone1.name                  
    return render(request, 'volunteerhead.html',{'campHeads':campHeads,'camps':camps,'volunteers':volunteers,'zone_name':zone_name})




def register_Camphead(request):
    if not hasattr(request.user, 'volunteerhead'):
        return render(request, 'login.html', {'error': 'you are not Access'})
    token = request.GET.get('token')  # Get token from the URL query parameter
    
    if token:
        try:
            # Get the volunteer based on the token
            CampHead_I = CampHead.objects.get(registration_token=token)

            if request.method == 'POST':
                form = CampHeadRegistrationForm(request.POST)
                if form.is_valid():
                    # Save the new volunteer data
                    CampHead_I.name = form.cleaned_data['name']
                    CampHead_I.email = form.cleaned_data['email']
                    CampHead_I.phone = form.cleaned_data['phone']
                    CampHead_I.password = form.cleaned_data['password']
                    CampHead_I.registration_token = None  # Clear the token once used
                    CampHead_I.save()
                    user = CampHead_I.user
                    user.username = form.cleaned_data['name']  # Ensure username matches email
                    user.email = form.cleaned_data['email']
                    user.set_password(form.cleaned_data['password'])
                
                    user.save()
                    return render(request, 'successful registration.html')  # Redirect to success page after registration
        except CampHead.DoesNotExist:
            # Token invalid or expired, handle error
            return render(request, 'successful registration.html')
    
    else:
        # Token missing from URL
        return render(request, 'invalid_request.html')

    # Show the form pre-filled with volunteer data if available
    form = CampHeadRegistrationForm(initial={'name': CampHead_I.name, 'email': CampHead_I.email, 'phone': CampHead_I.phone})
    return render(request, 'register_Camphead.html',{'form': form})




@csrf_exempt
def volunteers(request):
    if not hasattr(request.user, 'volunteerhead'):
        return render(request, 'login.html', {'error': 'you are not Access'})
    
    signer = Signer()
    signed_value = request.COOKIES.get('login')
    zoneid = signer.unsign(signed_value)
    zone1 = Zone.objects.get(id=zoneid)
    print(zone1)

    
    
    if not hasattr(request.user, 'volunteerhead'):
        
        return redirect('login')
    # user_type= request.COOKIES.get('user_type')

    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        mode = data.get('mode')
        
        print(data)
        if mode=="1": 
            
            volunteers_id = data.get('volunteers_id')   # Handle product editing
            
            volunteers1= get_object_or_404(Volunteer, id=volunteers_id)

            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")
            # password = data.get("password")

            try:
                # Update the linked User instance
                user = volunteers1.user
                user.username = name  # Ensure username matches email
                user.email = email
                # if password:  # Update password only if provided
                #     user.set_password(password)
                user.save()

                # Update the VolunteerHead fields
                volunteers1.name = name
                volunteers1.email = email
                volunteers1.phone = phone
                volunteers1.save()

                return JsonResponse({
                    'name': name,
                    'email': email,
                    'phone': phone,
                   })

            except IntegrityError:
                error_message = "An unexpected error occurred while updating the data."
                

        elif mode == "2": #add a new product
                print("3")
        
                name = data.get("volunteers_Name")
                email = data.get("volunteers_Email")
                phone = data.get("volunteers_phone")    
               
                if User.objects.filter(email=email).exists():
                    return JsonResponse({'status': 'error', 'message': 'Volunteer email already exists!'})

                else:
                    
                        # Create a new User instance
                        user = User.objects.create_user(username=name, email=email)

                        # Create a new VolunteerHead instance linked to the User
                        Volunteer.objects.create(user=user, name=name, email=email, phone=phone, zone1=zone1)

                        # messages.success(request, f"Volunteer {name} added successfully.")
                        return JsonResponse({'status': 'success', 'message':"Volunteer added successfully"})
                

 
        elif mode == "3":
        
                volunteers = zone1.zone2.all()  
                volunteers_data = list(volunteers.values('id', 'name', 'email', 'phone','is_active'))
                return JsonResponse({
                    'volunteers_data': volunteers_data,
                    })
        
        elif mode=="4":

            volunteers_Id = data.get('volunteers_Id')
            volunteers1 = get_object_or_404(Volunteer, id=volunteers_Id)
            user = volunteers1.user  # Get the associated User object
             
            # Delete the VolunteerHead and User
            volunteers1.delete()
            user.delete()
            return JsonResponse({'message': 'volunteers deleted successfully'}, status=200)
        
        elif mode=="5":#send_registration_email
               try:
                   volunteers_Id = data.get('volunteers_Id')         
                   volunteers_I = get_object_or_404(Volunteer, id=volunteers_Id)
                   
           
                   volunteers_I.generate_registration_token()
           
                   registration_link = request.build_absolute_uri(
                       reverse('register_volunteers') + f'?token={volunteers_I.registration_token}'
                   )
                   
           
                   subject = "volunteers Registration"
                   message = f"Hello {volunteers_I.name},\n\nPlease complete your registration here:\n\n{registration_link}"
                   from_email = settings.EMAIL_HOST_USER
                   recipient_list = [volunteers_I.email]
           
                   send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                             
                   return JsonResponse({'message': "Registration email sent successfully."})
                
               except Exception as e:
                   return JsonResponse({'error': str(e)}, status=500)
        elif mode=="6":
             try:
    # Get all CampHead objects
                 volunteers = Volunteer.objects.all()
             
                 for volunteer2 in volunteers:
                     # Generate a unique registration token for each CampHead
                     volunteer2.generate_registration_token()
             
                     # Build the registration link with the token
                     registration_link = request.build_absolute_uri(
                         reverse('register_volunteers') + f'?token={volunteer2.registration_token}'
                     )
             
                     # Prepare the email content
                     subject = "volunteers Registration"
                     message = (
                         f"Hello {volunteer2.name},\n\n"
                         f"Please complete your registration here:\n\n{registration_link}\n\n"
                         "Best regards,\nYour Team"
                     )
                     from_email = settings.EMAIL_HOST_USER
                     recipient_list = [volunteer2.email]
             
                     # Send the email
                     send_mail(subject, message, from_email, recipient_list, fail_silently=False)
             
                 return JsonResponse({'message': "Registration emails sent successfully to all volunteers."})
             
             except Exception as e:
                 return JsonResponse({'error': str(e)}, status=500)
             
        elif mode=="7":
             camp_id = data.get('camp_id')  # Get the selected camp ID
             volunteer_ids = data.get('volunteer_ids')
          
             try:
                 # Get the camp object using the provided camp_id
                 camp = Camp.objects.get(id=camp_id)

                 already_assigned_volunteers = Volunteer.objects.filter(id__in=volunteer_ids, camp1__isnull=False)
  
                 # Update volunteers' camp1 relationship (associate them with the selected camp)
                 volunteers_to_assign  = Volunteer.objects.filter(id__in=volunteer_ids, camp1__isnull=True)


                 volunteers_to_assign.update(camp1=camp)

                 

                 return JsonResponse({'success': 'Volunteers successfully assigned to the camp'})
     
             except Camp.DoesNotExist:
                 return JsonResponse({'error': 'Camp not found'}, status=404)
             except Exception as e:
                 return JsonResponse({'error': str(e)}, status=500)
             
        elif mode=="8":
             camp_id = data.get('campId')  # Get the selected camp ID
             

             camp = Camp.objects.get(id=camp_id)
             associated_volunteers = camp.camp2.all()
             
             # Prepare data to send to the frontend
             volunteers_data = list(associated_volunteers.values('id', 'name', 'email', 'phone'))
             
             return JsonResponse({
                    'volunteers_data': volunteers_data,
                    })
        elif mode=="9":
             volunteerid = data.get('volunteerid')  # Get the selected camp ID
             

             volunteer = Volunteer.objects.get(id=volunteerid)
             volunteer.camp1 = None
             volunteer.save()
             
             
             return JsonResponse({'message': 'volunteers deleted successfully'}, status=200)
        
        elif mode == "10":
        
                unassigned_volunteers = zone1.zone2.filter(camp1__isnull=True, is_active=True)  
                volunteers_data = list(unassigned_volunteers.values('id', 'name', 'email', 'phone'))
                return JsonResponse({
                    'volunteers_data': volunteers_data,
                    })
        elif mode == "10":
                zone_name = zone1.name
          
             
                       
 
        
                        




def register_volunteers(request):
    # if not hasattr(request.user, 'volunteerhead'):
    #     return render(request, 'login.html', {'error': 'you are not Access'})
    
    token = request.GET.get('token')  # Get token from the URL query parameter
    
    if token:
        try:
            # Get the volunteer based on the token
            volunteers_I = Volunteer.objects.get(registration_token=token)

            if request.method == 'POST':
                form = CampHeadRegistrationForm(request.POST)
                if form.is_valid():
                    # Save the new volunteer data
                    volunteers_I.name = form.cleaned_data['name']
                    volunteers_I.email = form.cleaned_data['email']
                    volunteers_I.phone = form.cleaned_data['phone']
                    volunteers_I.password = form.cleaned_data['password']
                    volunteers_I.is_active = True  # Automatically activate the volunteer
                    volunteers_I.registration_token = None  # Clear the token once used
                    volunteers_I.save()
                    user = volunteers_I.user
                    user.username = form.cleaned_data['name']  # Ensure username matches email
                    user.email = form.cleaned_data['email']
                    user.set_password(form.cleaned_data['password'])
                
                    user.save()
                    return render(request, 'successful registration.html')  # Redirect to success page after registration
        except Volunteer.DoesNotExist:
            # Token invalid or expired, handle error
            return render(request, 'successful registration.html')
    
    else:
        # Token missing from URL
        return render(request, 'invalid_request.html')

    # Show the form pre-filled with volunteer data if available
    form = CampHeadRegistrationForm(initial={'name': volunteers_I.name, 'email': volunteers_I.email, 'phone': volunteers_I.phone})
    return render(request, 'register_volunteers.html',{'form': form})


@csrf_exempt
def campmanage(request):
    
    if not hasattr(request.user, 'volunteerhead'):
        return render(request, 'login.html', {'error': 'you are not Access'})
    
    signer = Signer()
    signed_value = request.COOKIES.get('login')
    zoneid = signer.unsign(signed_value)
    

    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        mode = data.get('mode')
        if mode == "1": #add a new product
                print("3")
                print(data)
        
                campId1 = data.get("campId1")
                is_active = data.get("is_active")

                camp = get_object_or_404(Camp, id=campId1)
                camp.is_active=is_active
                camp.save()
                return JsonResponse({"status": "success", "is_active": camp.is_active})
               
     
        if mode == "2": #add a new product
                print("3")
                print(data)
        
                camp_name = data.get("camp_name")
                camp_description = data.get("camp_description")
                camp_head_id = data.get("camp_head_id")
               
                if camp_name:
                # Assign volunteer head if selected
                     camp_head = None
                     if camp_head_id:
                         camp_head = get_object_or_404(CampHead, id=camp_head_id)
                     Camp.objects.create(name=camp_name, description=camp_description, campHead1=camp_head)
                     return JsonResponse({'status': 'success', 'message':"camp added successfully"})
                
                

 
        elif mode == "3":
        
                camps = Camp.objects.filter(campHead1__zone1_id=zoneid).select_related('campHead1__zone1')  # Use 'campHead1', not 'volunteer_head'
                camp_data = []
                for camp in camps:
                    camp_data.append({
                        'id': camp.id,
                        'name': camp.name,
                        'description': camp.description,
                        'is_active': camp.is_active,
                        'camphead': {
                            'id': camp.campHead1.id if camp.campHead1 else None,  # Use 'campHead1'
                            'name': camp.campHead1.name if camp.campHead1 else None,  # Use 'campHead1'
                        }
                    })
                return JsonResponse({
                    'camps': camp_data,
                })
                
        
        elif mode=="4":

            campid = data.get('campid')
            camp = get_object_or_404(Camp, id=campid)
            camp.delete()
            return JsonResponse({'success': True, 'message': 'camp deleted successfully.'})
        
        elif mode=="5":#mange category_name
            print(data)

            category_name = data.get('category_name')
            Category.objects.create(name=category_name)
            return JsonResponse({'success': True, 'message': 'category new item added successfully.'})
        elif mode == "6":
            
                camps1 = Camp.objects.filter(campHead1__zone1_id=zoneid).select_related('campHead1__zone1')  # Use 'campHead1', not 'volunteer_head'
                camp_data = list(camps1.values('id', 'name'))
                return JsonResponse({
                    'camps': camp_data,
                })
        

@csrf_exempt
def DeleteCategoryItem(request):
    if not hasattr(request.user, 'volunteerhead'):
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
        
       