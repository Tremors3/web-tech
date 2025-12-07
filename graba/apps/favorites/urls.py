from .views import toggle_favorite
from django.urls import path


app_name = 'favorites'


urlpatterns = [
    path('<int:auction_id>/toggle/', toggle_favorite, name='toggle'),
]
