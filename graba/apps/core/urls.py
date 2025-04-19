from django.urls import path
from core.views import index


urlpatterns = [
    path(r'', index, name='index')
]
