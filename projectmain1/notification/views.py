from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Notification
from .forms import NotificationForm
import logging

@login_required
def view_notifications(request):
    # Fetch notifications that are not closed
    notifications = Notification.objects.filter(close_notification=True).order_by('-publish_date')

    return render(request, 'view_notifications.html', {'notifications': notifications})

@login_required
def publish_notification(request):
    """Publish a notification to specific users based on role."""
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)

            # Find recipients based on the selected role
            if notification.to == "Admin":
                recipients = User.objects.filter(is_superuser=True)
            elif notification.to == "VolunteerHead":
                recipients = User.objects.filter(groups__name="VolunteerHead")
            elif notification.to == "CampHead":
                recipients = User.objects.filter(groups__name="CampHead")
            elif notification.to == "Volunteer":
                recipients = User.objects.filter(groups__name="Volunteer")
            else:
                recipients = User.objects.none()

            # Save notification and assign recipients
            notification.save()
            notification.recipients.set(recipients)  # Assign multiple users to the notification

            return redirect("publish_notification")
    else:
        form = NotificationForm()

    # Show notifications only meant for the logged-in user
    notifications = Notification.objects.filter(recipients=request.user, close_notification=False)

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
    notifications = Notification.objects.filter(close_notification=False).order_by('-publish_date')
    return render(request, 'close_notification.html', {'notifications': notifications})


logger = logging.getLogger(__name__)

@login_required
def delete_notification(request):
    """Delete a notification only if it belongs to the user."""
    if request.method == "POST":
        notification_id = request.POST.get('notification_id')
        logger.debug(f"Attempting to delete notification with ID: {notification_id} for user: {request.user}")

        if notification_id:
            try:
                # Attempt to retrieve the notification without recipient check
                notification = Notification.objects.get(id=notification_id)
                logger.debug(f"Notification found: {notification}")
                
                # Delete the notification
                notification.delete()
                messages.success(request, "Notification deleted successfully.")
                logger.debug(f"Notification with ID: {notification_id} deleted.")
            except Notification.DoesNotExist:
                messages.error(request, "Notification does not exist.")
                logger.error(f"Notification with ID: {notification_id} does not exist.")
            except Exception as e:
                messages.error(request, "An error occurred while deleting the notification.")
                logger.error(f"Error deleting notification: {e}")
    
    return redirect('view_notifications')
