from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, Role, Buyer, Seller
from auctions.models import Auction, Offer, WinnerOffer
from reviews.models import Review


class LeaveReviewTest(TestCase):

    def setUp(self):
        # Seller
        self.seller_user = User.objects.create_user(
            email="seller@email.com",
            username="seller",
            password="testpass"
        )
        seller_role = Role.objects.create(
            user=self.seller_user,
            type="SELLER"
        )
        self.seller = Seller.objects.create(
            role=seller_role,
            collection_address="Test address"
        )

        # Buyer
        self.buyer_user = User.objects.create_user(
            email="buyer@email.com",
            username="buyer",
            password="testpass"
        )
        buyer_role = Role.objects.create(
            user=self.buyer_user,
            type="BUYER"
        )
        self.buyer = Buyer.objects.create(role=buyer_role)

        # Closed auction
        self.auction = Auction.objects.create(
            seller=self.seller,
            title="Test Auction",
            status="CLOSED",
            min_price_cents=100 * 10,
        )

        # Winning offer
        self.offer = Offer.objects.create(
            auction=self.auction,
            buyer=self.buyer,
            type="BUY_NOW",
            amount_cents=100 * 10
        )
        self.winner_offer = WinnerOffer.objects.create(
            auction=self.auction,
            offer=self.offer
        )

    def test_buyer_can_leave_review_and_seller_rating_updates(self):
        self.client.login(email="buyer@email.com", password="testpass")

        response = self.client.post(
            reverse("reviews:leave_review"),
            {
                "winner_offer_id": self.winner_offer.pk,
                "rating": 5,
                "review_text": "Ottimo venditore!"
            },
            HTTP_ACCEPT="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Review.objects.count(), 1)

        review = Review.objects.first()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.seller, self.seller)

        # Seller stats
        rating_stats = self.seller.rating_stats
        self.assertEqual(rating_stats['count'], 1)
        self.assertEqual(rating_stats['avg'], 5.0)
