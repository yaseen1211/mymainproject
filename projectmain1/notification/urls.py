# project_name/urls.py
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notification/', include('notification.urls')),  # Include notification app's URLs
]
