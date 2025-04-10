from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Notification
from .forms import NotificationForm
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

@login_required
def view_notifications(request):
    # Fetch notifications that are not closed
    notifications = Notification.objects.filter(close_notification=False).order_by('-publish_date')


    return render(request, 'view_notifications.html', {'notifications': notifications})

@login_required
def publish_notification(request):
    user = request.user
    role = "Unknown"

    if hasattr(user, 'volunteerhead'):
            role = "VolunteerHead"
    elif hasattr(user, 'camp_head'):
            role = "CampHead"
    elif hasattr(user, 'volunteer'):
            role="Volunteer"
    else:
         role = "Admin"

    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)  # Don't save yet
            notification.from1 = role  # Assign the role to from1
            notification.save()  # Now save the object
            return redirect("publish_notification")
    else:
        form = NotificationForm()

    # Fetch all notifications that are not closed (exclude closed ones from the list)
    notifications = Notification.objects.filter(close_notification=False)
    return render(request, "publish_notification.html", {"form": form, "notifications": notifications})


@login_required
def notification_detail(request, notification_id=None):
    user = request.user
    role = "Unknown"

    if hasattr(user, 'volunteerhead'):
            role = "VolunteerHead"
    elif hasattr(user, 'camp_head'):
            role = "CampHead"
    elif hasattr(user, 'volunteer'):
            role="Volunteer"
    else:
         role = "Admin"
    print(role)     




    if notification_id:
        # Fetch and show details of a specific notification
        notification = get_object_or_404(Notification, id=notification_id)

        # Ensure the user is only accessing their allowed notifications

        return render(request, "notification_detail.html", {"notification": notification,"role":role})
    else:
        # Show only notifications meant for the selected role
        notifications = Notification.objects.filter(to=role)
        return render(request, "notification_detail.html", {"notifications": notifications, "role": role})

@login_required
def Dashboard(request):
    user = request.user

    if hasattr(user, 'volunteerhead'):
        return redirect('Camp__head')
    elif hasattr(user, 'camp_head'):
        print("camphead123")
        return redirect('Volunteer')

    elif hasattr(user, 'volunteer'):
        print("volunter123")
        return redirect('volunteer1')

    else:
        return redirect('superadmin')

@login_required
def close_notification(request):
    user = request.user
    role = "Unknown"


    if hasattr(user, 'volunteerhead'):
            role = "VolunteerHead"
    elif hasattr(user, 'camp_head'):
            role = "CampHead"
    elif hasattr(user, 'volunteer'):
            role="Volunteer"
    else:
         role = "Admin"
                 
      
    if request.method == "POST":
        notification_id = request.POST.get('notification_id')
        if notification_id:
            try:
                notification = Notification.objects.get(id=notification_id)
                notification.close_notification = True
                notification.expiration_date = timezone.now().date()
                notification.save()
                messages.success(request, "Notification closed successfully.")
            except Notification.DoesNotExist:
                messages.error(request, "Notification does not exist.")
    
    # Fetch all notifications again to display the updated status
    notifications = Notification.objects.filter(from1=role).order_by('-publish_date')
    return render(request, 'close_notification.html', {'notifications': notifications})

@login_required
def delete_notification(request):
    if request.method == "POST":
        notification_id = request.POST.get('notification_id')
        if notification_id:
            try:
                notification = Notification.objects.get(id=notification_id)
                notification.delete()
                messages.success(request, "Notification deleted successfully.")
            except Notification.DoesNotExist:
                messages.error(request, "Notification does not exist.")
    
    return redirect('close_notification')  # Redirect back to the notification list after deletion
