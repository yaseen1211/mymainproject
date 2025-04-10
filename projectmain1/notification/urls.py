from django.urls import path
from notification import views as notification_views

urlpatterns = [
    path('view/', notification_views.close_notification, name='close_notification'),
    path('close/', notification_views.view_notifications, name='view_notifications'),
    path('publish/', notification_views.publish_notification, name='publish_notification'),
    path('Dashboard/', notification_views.Dashboard, name='Dashboard'),
    path('delete-notification/', notification_views.delete_notification, name='delete_notification'),
    path('notifications/', notification_views.notification_detail, name='notification_detail'),
    path('notification/<int:notification_id>/', notification_views.notification_detail, name='notification_detail'),
]
