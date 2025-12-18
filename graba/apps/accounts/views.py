from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
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

from reviews.models import Review
from auctions.models import Auction, WinnerOffer
from favorites.models import FavoriteAuction


class UserRegisterView(RedirectAuthenticatedUserMixin, FormView):
    template_name = 'accounts/signin.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        
        with transaction.atomic():
            
            user = form.save(commit=True)

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

            # Create private or shopkeeper profile
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

        # User automatic authentication
        auth_user = authenticate(
            self.request,
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'],
        )

        if auth_user:
            login(self.request, auth_user)

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
        

        # FAVORITE AUCTIONS PAGINATION
        fav_list = Auction.objects.filter(favoriteauction__user=user_obj)
        fav_page = self.request.GET.get("fav_page", 1)

        fav_paginator = Paginator(fav_list, 3)
        context["fav_page_obj"] = fav_paginator.get_page(fav_page)
        
        
        # USER AUCTIONS PAGINATION
        seller_instance = Seller.objects.filter(role__user=user_obj, role__type='SELLER').first()
        if seller_instance:
            auc_list = Auction.objects.filter(seller=seller_instance)
        else:
            auc_list = Auction.objects.none()
        auc_page = self.request.GET.get("auc_page", 1)
        
        auc_paginator = Paginator(auc_list, 3)
        context["auc_page_obj"] = auc_paginator.get_page(auc_page)


        # REVIEWS
        if seller_instance:
            context['reviews'] = seller_instance.reviews.all()
            rating_stats = seller_instance.rating_stats
            context['reviews_count'] = rating_stats.get('count')
            context['average_rating'] = float(rating_stats.get('avg') or 0)
        else:
            context['reviews'] = Review.objects.none()
            context['reviews_count'] = None
            context['average_rating'] = None


        # REVIEWABLE AUCTIONS
        context['reviewable_auctions'] = []

        if self.request.user.is_authenticated:
            try:
                buyer_instance = Buyer.objects.get(role__user=self.request.user)

                winner_offers_qs = (
                    WinnerOffer.objects
                    .filter(
                        offer__buyer=buyer_instance,
                        auction__seller=seller_instance,
                        auction__status="CLOSED"
                    )
                    .exclude(
                        review__isnull=False
                    )
                    .select_related('auction')
                )

                context['reviewable_auctions'] = [{
                    "winner_offer_id": wo.pk,
                    "auction_title": wo.auction.title
                } for wo in winner_offers_qs]

            except Buyer.DoesNotExist:
                pass


        return context
