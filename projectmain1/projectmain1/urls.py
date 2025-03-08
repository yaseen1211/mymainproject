"""
URL configuration for projectmain1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# from login1 import views as login_views
from camp import views as Camp_views
from superadmin import views as superadmin_views
from volunteerhead import views as volunteerhead_views
from Users import views as Users_views
from login import views as login_views
from notification import views as notification_views
from django.urls import include, path


urlpatterns = [
    path('admin/'                  , admin.site.urls),
    path('login/'                  , login_views.login                        , name='login'),
    path('front/'                  , login_views.front                        , name='front'),
    path(''                        , login_views.front                        , name='front'),
    path('logout/'                 , login_views.logout_view                  , name='logout'),
    path('forget/'                 , login_views.forget                       , name='forget'),
    path('verify-otp/'             , login_views.verify_otp                   , name='verify_otp'),
    path('volunteer1/'             , login_views.volunteer1                 , name='volunteer1'),

    path('superadmin/'             , superadmin_views.superadmin              , name='superadmin'),
    path('register-volunteer/'     , superadmin_views.register_volunteer      , name='register_volunteer'),  
    path('zonemanage/'             , superadmin_views.zonemanage              , name='zonemanage'),
    path('DeleteCategoryItem/'     , superadmin_views.DeleteCategoryItem      , name='DeleteCategoryItem'),

    path('register_volunteers/'    , volunteerhead_views.register_volunteers  , name='register_volunteers'),
    path('register_Camphead/'      , volunteerhead_views.register_Camphead    , name='register_Camphead'),
    path('volunteers/'             , volunteerhead_views.volunteers           , name='volunteers'),
    path('Camp__head/'             , volunteerhead_views.Camp__head           , name='Camp__head'),
    path('campmanage/'             , volunteerhead_views.campmanage          , name='campmanage'),

    path('Volunteer/'              , Camp_views.Volunteer                     , name='Volunteer'),

    path('Users/'                  , Users_views.Users                        , name='Users'),


    path('notifications/', include('notification.urls')),






]

