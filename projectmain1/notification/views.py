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
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("publish_notification")
    else:
        form = NotificationForm()

    # Fetch all notifications that are not closed (exclude closed ones from the list)
    notifications = Notification.objects.filter(close_notification=False)
    return render(request, "publish_notification.html", {"form": form, "notifications": notifications})


@login_required
def notification_detail(request, notification_id=None):
    user = request.user

    # Get role from query parameter (if exists) or determine based on logged-in user
    role = request.GET.get("type")  # Get role from URL query parameter

    if not role:  # If no type is provided in the URL, use the user's role
        if user.is_superuser:
            role = "Admin"
        elif user.groups.filter(name="VolunteerHead").exists():
            role = "VolunteerHead"
        elif user.groups.filter(name="CampHead").exists():
            role = "CampHead"
        else:
            role = "Volunteer"

    if notification_id:
        # Fetch and show details of a specific notification
        notification = get_object_or_404(Notification, id=notification_id)

        # Ensure the user is only accessing their allowed notifications
        if notification.to != role:
            messages.error(request, "You are not authorized to view this notification.")
            return redirect("notification_detail")

        return render(request, "notification_detail.html", {"notification": notification})
    else:
        # Show only notifications meant for the selected role
        notifications = Notification.objects.filter(to=role)
        return render(request, "notification_detail.html", {"notifications": notifications, "role": role})


@login_required
def close_notification(request):
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
    notifications = Notification.objects.order_by('-publish_date')
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
