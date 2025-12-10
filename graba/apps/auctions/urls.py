from django.urls import path
from .views import AuctionCreateView


app_name = "auctions"


urlpatterns = [
    path("create/", AuctionCreateView.as_view(), name="create"),
]
