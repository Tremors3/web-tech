from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404

from .forms import UserRegistrationForm, CustomLoginForm, UserProfileForm
from .models import User, Role, Buyer, Seller, Private, Shopkeeper
from .mixins import RedirectAuthenticatedUserMixin
from auctions.models import Auction
from favorites.models import FavoriteAuction


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


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "accounts/edit.html"
    success_url = reverse_lazy("accounts:edit")

    def get_object(self):
        return self.request.user


class UserProfileDetailView(TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super(UserProfileDetailView, self).get_context_data(**kwargs)

        # Adding the profile user to the context (if exists)
        profile_user_pk = self.kwargs.get("pk")
        try:
            user_obj = User.objects.get(pk=profile_user_pk)
        except User.DoesNotExist:
            raise Http404("User not found")
        context["profile_user"] = user_obj


        # Copy GET and remove 'page'
        params = self.request.GET.copy()
        params._mutable = True
        params.pop('fav_page', None)
        params.pop('auc_page', None)

        # Querystring clear for pagination
        context['querystring'] = params.urlencode()
        
        # Add favorites to context ONLY if user is authenticated
        context['user_favorites'] = set(
            FavoriteAuction.objects.filter(user=user_obj)
            .values_list('auction_id', flat=True)
        )
        

        # --- FAVORITE AUCTIONS PAGINATION ---
        fav_list = Auction.objects.filter(favoriteauction__user=user_obj)
        fav_page = self.request.GET.get("fav_page", 1)

        fav_paginator = Paginator(fav_list, 3)
        context["fav_page_obj"] = fav_paginator.get_page(fav_page)
        
        # --- USER AUCTIONS PAGINATION ---
        auc_list = Auction.objects.filter(seller_id=user_obj.id)
        auc_page = self.request.GET.get("auc_page", 1)

        auc_paginator = Paginator(auc_list, 3)
        context["auc_page_obj"] = auc_paginator.get_page(auc_page)

        return context
