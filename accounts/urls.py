from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('verify-otp/<str:username>/', views.verify_otp_view, name='verify_otp'),
    path('signin/', views.signin_view, name='signin'),
    path('signout/', views.signout_view, name='signout'),
    path('profile/settings/', views.profile_settings_view, name='profile_settings'),
]
