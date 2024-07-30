"""FirstPrj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from FirstApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.base, name = "views-base"),
    path('home', views.base),
    path('login_frame', views.login_frame),
    path('register_frame', views.register_frame),
    path('register_form_frame', views.register_form_frame),
    path('reservations_frame', views.reservations_frame),
    path('reserve_form_frame', views.reserve_form_frame),
    path('do_register', views.do_register),
    path('do_check_regform', views.do_check_regform),
    path('do_login', views.do_login),
    path('do_logout', views.do_logout),
    path('do_check_seats', views.do_check_seats),
    path('seats_form_frame', views.seats_form_frame),
    path('do_reserve', views.do_reserve),
    path('past_reservations', views.past_reservations),
]