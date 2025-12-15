from django.urls import path
from .views import (
    AuctionCreateView,
    AuctionDetailView,
    AuctionBidView,
    AuctionBuyNowView
)


app_name = "auctions"


urlpatterns = [
    path("create/", AuctionCreateView.as_view(), name="create"),
    path("auction/<int:key>/", AuctionDetailView.as_view(), name="auction-detail"),
    path("auction/<int:key>/bid/", AuctionBidView.as_view(), name="auction-bid"),
    path("auction/<int:key>/buy-now/", AuctionBuyNowView.as_view(), name="auction-buy-now"),
]
