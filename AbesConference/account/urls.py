from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import *

urlpatterns = [
    path('login', Login.as_view(), name='login'),
    path('signup', Signup.as_view(), name='signup'),
    path('logout', login_required(logout), name='logout'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('forget-password/<uidb64>/<token>',ResetPassword.as_view(), name='forget-password'),
    path('profile', login_required(Profile.as_view()), name='profile'),
    path('edit-profile', login_required(Profile.as_view()), name='edit_profile'),
    path('change-username', login_required(ChangeUsername.as_view()), name='change_username'),
    path('change-password', login_required(ChangePassword.as_view()), name='change_password'),
]
