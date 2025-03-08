from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Notification
from .forms import NotificationForm

@login_required
def view_notifications(request):
    # Fetch notifications that are not closed
    notifications = Notification.objects.filter(close_notification=False).order_by('-publish_date')

    return render(request, 'view_notifications.html', {'notifications': notifications})

@login_required
def publish_notification(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.user = request.user  # Associate with the logged-in user
            notification.save()
            messages.success(request, 'Notification published successfully.')
            return redirect('publish_notification')  # Redirect to clear the form
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = NotificationForm()
    
    # Fetch all notifications for the current user (optional)
    notifications = Notification.objects.filter(user=request.user).order_by('-publish_date')
    
    return render(request, 'publish_notification.html', {
        'form': form,
        'notifications': notifications,  # Pass notifications to the template
    })

@login_required
def close_notification(request, notification_id):
    # Use get_object_or_404 for safer retrieval
    
    
    if request.method == "POST" and 'delete' in request.POST:
        notification = get_object_or_404(Notification, id=notification_id)
        # If the request is for deletion
        notification.delete()
        # Fetch updated list of notifications after deletion
        notifications = Notification.objects.all().order_by('-publish_date')
        # Re-render the same template with updated list of notifications
        return render(request, 'close_notification.html', {'notifications': notifications})

    # If not deleting, close the notification and set expiration date
    notification.close_notification = True
    notification.expiration_date = timezone.now().date()
    notification.save()

    # Fetch all notifications (you can modify the filter as needed)
    notifications = Notification.objects.all()
    print(notifications)

    # Render the close_notification.html template with notifications
    return render(request, 'close_notification.html', {'notifications': notifications})