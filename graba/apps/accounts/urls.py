from .views import UserLoginView, UserRegisterView, UserProfileUpdateView, UserProfileDetailView
from django.contrib.auth import views as auth_views
from django.urls import path


app_name = 'accounts'


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('signin/', UserRegisterView.as_view(), name='signin'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='edit'),
    path('profile/<int:pk>/', UserProfileDetailView.as_view(), name='profile'),
]
