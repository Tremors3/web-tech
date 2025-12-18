from .views import leave_review
from django.urls import path


app_name = 'reviews'


urlpatterns = [
    path('leave/', leave_review, name='leave_review'),
]
