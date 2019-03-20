# main/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path('rotw/signup/', views.SignUp.as_view(), name='signup'),
]