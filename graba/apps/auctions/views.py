from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, DetailView
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.views import View

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from decimal import Decimal

from .mixins import SellerRequiredMixin
from .models import Auction, Offer
from .forms import AuctionForm

from accounts.models import Seller, Role
from favorites.models import FavoriteAuction
from core.templatetags import custom_filters


class AuctionCreateView(SellerRequiredMixin, CreateView):
    model = Auction
    form_class = AuctionForm
    template_name = "auctions/create.html"

    def form_valid(self, form):
        auction = form.instance
        user = self.request.user

        # Get the active Seller Role
        try:
            seller_role = Role.objects.get(user=user, type="SELLER", state="ACTIVE")
            seller_obj = Seller.objects.get(role=seller_role)
        except (Role.DoesNotExist, Seller.DoesNotExist):
            form.add_error(None, "Impossibile trovare il profilo Seller per questo utente.")
            return self.form_invalid(form)

        # Link the Auction to the Seller
        auction.seller = seller_obj

        auction.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("accounts:profile", kwargs={"pk": self.request.user.pk})


class AuctionDetailView(DetailView):
    model = Auction
    pk_url_kwarg = "key"
    template_name = "auctions/auction.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auction = self.get_object()
        user = self.request.user

        # Auction and Seller context variables
        context["is_seller"] = user.is_authenticated and user == auction.seller.role.user
        context["is_buyer"] = user.is_authenticated and not context["is_seller"]

        context["highest_bid"] = auction.get_highest_offer_value(type_='BID')
        context["buy_now_offer"] = auction.get_highest_offer_value(type_='BUY_NOW')
        
        context["has_offers"] = auction.has_offers
        context["is_bn_enabled"] = auction.is_bn_enabled()
        
        context["bids"] = Offer.objects.filter(auction=auction, type='BID').order_by("-amount_cents")
        context["auction_id"] = auction.pk

        # Other context variables
        
        # Copy GET and remove 'page'
        params = self.request.GET.copy()
        params._mutable = True
        params.pop('page', None)

        # Querystring clear for pagination
        context['querystring'] = params.urlencode()
        
        # Add favorites to context ONLY if user is authenticated
        context['user_favorites'] = set(
            FavoriteAuction.objects.filter(user=self.request.user)
            .values_list('auction_id', flat=True)
        ) if self.request.user.is_authenticated else set()
        
        return context


class AuctionBidView(View):

    def post(self, request, key):
        auction = get_object_or_404(Auction, pk=key)

        # Seller cannot bid on own auction
        if request.user == auction.seller.role.user:
            return JsonResponse({"error": "Sellers cannot bid on their own auction."}, status=403)

        # Must be a buyer
        buyer_role = request.user.role_set.filter(type="BUYER").first()
        if not buyer_role:
            return JsonResponse({"error": "User is not a buyer."}, status=403)
        buyer = buyer_role.buyer

        # Extract amount
        amount_str = request.POST.get("amount")
        if not amount_str:
            return JsonResponse({"error": "No amount provided."}, status=400)

        try: amount = Decimal(amount_str)
        except: return JsonResponse({"error": "Invalid amount."}, status=400)

        if amount <= 0:
            return JsonResponse({"error": "Bid must be greater than zero."}, status=400)

        amount_cents = int(amount * 100)

        # Highest bid check (robusto)
        highest_cents = auction.get_highest_offer_value(type_='BID')
        if amount_cents <= highest_cents:
            return JsonResponse({"error": "Bid must be higher than the current highest bid."}, status=400)

        # TODO: 
        # 1) Fix in-page current highest offer not updating when receiving the WebSocket msg;
        # 2) Show in-page error dialogs when sending an JsonResponse({"error": "..."}, status=4XX).

        # Create offer
        offer = Offer.objects.create(
            auction=auction,
            buyer=buyer,
            type="BID",
            amount_cents=amount_cents
        )

        # Broadcast to WS
        payload = {
            "type": "new_bid",
            "username": offer.buyer.role.user.username,
            "amount_cents": amount_cents,
            "amount_display": custom_filters.cents_to_price(amount_cents),
            "offer_time": offer.offer_time.isoformat(timespec='seconds'),
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"auction_{auction.pk}", payload)

        # JSON response
        return JsonResponse({"success": True, **payload})
