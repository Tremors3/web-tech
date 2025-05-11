from django.urls import path
from core import views


urlpatterns = [
    path(r'', views.home, name='home')
]
