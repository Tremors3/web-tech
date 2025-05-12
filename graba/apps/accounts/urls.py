from django.contrib.auth import views as auth_views
from .views import UserLoginView, UserRegisterView
from django.urls import path


app_name = 'accounts'


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('signin/', UserRegisterView.as_view(), name='signin'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout')
]