from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from .mixins import SellerRequiredMixin
from .models import Auction
from .forms import AuctionForm
from accounts.models import Seller, Role


class AuctionCreateView(SellerRequiredMixin, CreateView):
    model = Auction
    form_class = AuctionForm
    template_name = "auctions/create.html"

    def form_valid(self, form):
        auction = form.instance

        # Euros to cents conversion
        auction.min_price_cents = int(form.cleaned_data['min_price_eur'] * 100)
        buy_now = form.cleaned_data.get('buy_now_price_eur')
        auction.buy_now_price_cents = int(buy_now * 100) if buy_now else None

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
