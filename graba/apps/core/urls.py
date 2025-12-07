from django.urls import path
from .views import HomePageView

app_name = 'core'

urlpatterns = [
    path(r'', HomePageView.as_view(), name='home')
]
