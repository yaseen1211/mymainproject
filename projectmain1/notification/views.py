from django.shortcuts import redirect, render
from .models import Notification
from .forms import NotificationForm
from django.utils import timezone

# Create your views here.



# Publish Notification
def notification(request):
    notification_type = request.GET.get('type', 'default')
    if notification_type == 'superadmin':
        form = NotificationForm(user=notification_type)

    elif notification_type == 'zone':
        # Perform alert-specific logic
        print("zone")
    elif notification_type == 'camp':
        print("camp")
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_notifications')
    else:
        form = NotificationForm()
    return render(request, 'notificationsend.html', {'form': form})

# View Notifications
def view_notifications(request):
    notifications = Notification.objects.filter(close_notification=False).order_by('-publish_date')
    return render(request, 'notifications/view_notifications.html', {'notifications': notifications})

# Close Expired Notifications (Manual or Auto)
def close_notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    notification.close_notification = True
    notification.expiration_date = timezone.now().date()
    notification.save()
    return redirect('view_notifications')