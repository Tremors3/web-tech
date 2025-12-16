from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import CreateView, DetailView
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View

from django_celery_beat.models import ClockedSchedule, PeriodicTask
import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from decimal import Decimal

from .mixins import SellerRequiredMixin
from .models import Auction, Offer, WinnerOffer
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
            form.add_error(None, "Cannot find the Seller profile for this user.")
            return self.form_invalid(form)

        # Link the Auction to the Seller
        auction.seller = seller_obj

        auction.save()

        # AUCTION CLOSURE SCHEDULING
        clocked, _ = ClockedSchedule.objects.get_or_create(
            clocked_time=auction.end_date
        )

        PeriodicTask.objects.create(
            clocked=clocked,
            one_off=True,
            name=f"close_auction_{auction.pk}",
            task="auctions.tasks.close_auction_task",
            args=json.dumps([auction.pk]),
        )

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
        context["is_seller"] = user.is_authenticated and user.has_role('SELLER') and user == auction.seller.role.user
        context["is_buyer"] = user.is_authenticated and user.has_role('BUYER') and not context["is_seller"]

        context["highest_bid"] = auction.get_highest_offer_value(type_='BID')
        context["buy_now_offer"] = auction.get_highest_offer_value(type_='BUY_NOW')
        
        context["has_offers"] = auction.has_offers
        context["is_bn_enabled"] = auction.is_bn_enabled()
        
        context["bids"] = Offer.objects.filter(auction=auction, type='BID').order_by("-amount_cents")
        context["auction_id"] = auction.pk

        # Other context variables
        
        # Add the winner offer if exists
        context["winner_offer"] = auction.winner_offer if auction.status == "CLOSED" else None
        
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
            return JsonResponse({"error": "No amount provided."}, status=403)

        try: amount = Decimal(amount_str)
        except: return JsonResponse({"error": "Invalid amount."}, status=403)

        if amount <= 0:
            return JsonResponse({"error": "Bid must be greater than zero."}, status=403)

        amount_cents = int(amount * 100)

        # Highest bid check
        highest_cents = auction.get_highest_offer_value(type_='BID')
        if highest_cents and amount_cents <= highest_cents:
            return JsonResponse({"error": "Bid must be higher than the current highest bid."}, status=403)

        # Minimum price check
        minimuum_cents = auction.min_price_cents
        if amount_cents <= minimuum_cents:
            return JsonResponse({"error": "Bid must be higher than the minimum price."}, status=403)

        # Auction must be active
        if auction.status in ("CLOSED", "CANCELLED"):
            return JsonResponse({"error": "Auction is not active."}, status=403)

        now = timezone.now()

        # Auction not started yet
        if now < auction.start_date:
            return JsonResponse({"error": "Auction has not started yet."}, status=403)

        # Auction already ended
        if now > auction.end_date:
            return JsonResponse({"error": "Auction has already ended."}, status=403)

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

class AuctionBuyNowView(View):

    def post(self, request, key):
        auction = get_object_or_404(Auction, pk=key)

        # Auction must be OPEN
        if auction.status != "OPEN":
            return JsonResponse({"error": "Auction is not active."}, status=403)

        # Buy Now must be enabled
        if not auction.is_bn_enabled():
            return JsonResponse({"error": "Buy Now is not available for this auction."}, status=403)

        # No BID offers allowed
        if auction.has_offers:
            return JsonResponse({"error": "Buy Now is disabled because bids already exist."}, status=403)

        # Seller cannot buy own auction
        if request.user == auction.seller.role.user:
            return JsonResponse({"error": "Sellers cannot buy their own auction."}, status=403)

        # Must be a buyer
        buyer_role = request.user.role_set.filter(type="BUYER").first()
        if not buyer_role:
            return JsonResponse({"error": "User is not a buyer."}, status=403)
        buyer = buyer_role.buyer

        now = timezone.now()

        if now < auction.start_date:
            return JsonResponse({"error": "Auction has not started yet."}, status=403)

        if now > auction.end_date:
            return JsonResponse({"error": "Auction has already ended."}, status=403)

        # Prevent double winner
        if hasattr(auction, "winneroffer"):
            return JsonResponse({"error": "Auction already has a winner."}, status=403)

        # Create BUY_NOW offer
        offer = Offer.objects.create(
            auction=auction,
            buyer=buyer,
            type="BUY_NOW",
            amount_cents=auction.buy_now_price_cents
        )

        # Create WinnerOffer
        WinnerOffer.objects.create(
            auction=auction,
            offer=offer
        )

        # Close auction
        auction.status = "CLOSED"
        auction.save(update_fields=["status"])

        # Broadcast via WS
        payload = {
            "type": "buy_now",
            "username": offer.buyer.role.user.username,
            "amount_display": custom_filters.cents_to_price(offer.amount_cents),
            "offer_time": offer.offer_time.isoformat(timespec="seconds"),
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"auction_{auction.pk}", payload
        )

        return JsonResponse({
            "success": True,
            "message": "Auction successfully bought.",
            **payload
        })
