from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView, UpdateView
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.db import transaction


from .forms import UserRegistrationForm, CustomLoginForm, UserProfileForm
from .models import User, Role, Buyer, Seller, Private, Shopkeeper
from .mixins import RedirectAuthenticatedUserMixin


class UserRegisterView(RedirectAuthenticatedUserMixin, FormView):
    template_name = 'accounts/signin.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.save()

            # Create the selected roles
            for role_type in form.cleaned_data['role_types']:
                
                role = Role.objects.create(user=user, type=role_type)
                
                if role_type == 'BUYER':
                    Buyer.objects.create(
                        role=role,
                        shipping_address=form.cleaned_data['shipping_address']
                    )
                elif role_type == 'SELLER':
                    Seller.objects.create(
                        role=role,
                        collection_address=form.cleaned_data['collection_address']
                    )

            # Create Private or Shopkeeper user
            if user.legal_type == 'PRIVATE':
                Private.objects.create(
                    user=user,
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    fiscal_code=form.cleaned_data['fiscal_code']
                )
            elif user.legal_type == 'SHOPKEEPER':
                Shopkeeper.objects.create(
                    user=user,
                    business_name=form.cleaned_data['business_name'],
                    iva_number=form.cleaned_data['iva_number'],
                    headquarters_address=form.cleaned_data['headquarters_address']
                )
        
        return super().form_valid(form)


class UserLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse('core:home')

class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user