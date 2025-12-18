from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from django.urls import reverse

from accounts.models import Buyer
from auctions.models import WinnerOffer
from .models import Review


@login_required
@require_POST
def leave_review(request):
    user = request.user

    # Check BUYER role
    try:
        buyer = Buyer.objects.get(role__user=user)
    except Buyer.DoesNotExist:
        return JsonResponse({"error": "Only buyers can leave reviews."}, status=403)

    # Check AJAX fields
    winner_offer_id = request.POST.get("winner_offer_id")
    rating = request.POST.get("rating")
    review_text = request.POST.get("review_text", "").strip()

    if not winner_offer_id or not rating:
        return JsonResponse({"error": "Missing required fields."}, status=400)

    # Rating validation
    try:
        rating = int(rating)
        if not 1 <= rating <= 5: raise ValueError
    except ValueError:
        return JsonResponse({"error": "Invalid rating value."}, status=400)

    # Get WinnerOffer
    winner_offer = get_object_or_404(WinnerOffer, pk=winner_offer_id)

    # Check auction closed
    if winner_offer.auction.status != "CLOSED":
        return JsonResponse({"error": "Auction is not closed yet."}, status=403)

    # Check user is winner
    if winner_offer.offer.buyer != buyer:
        return JsonResponse({"error": "Cannot leave a review for this auction."}, status=403)

    # Check review already exists
    if Review.objects.filter(winner_offer=winner_offer).exists():
        return JsonResponse({"error": "Review already left for this auction."}, status=403)

    # REVIEWS
    seller_instance = winner_offer.auction.seller
    
    # Create review
    try:
        review = Review.objects.create(
            winner_offer=winner_offer,
            seller=seller_instance,
            rating=rating,
            review_text=review_text or None
        )
    except IntegrityError:
        return JsonResponse({"error": "Review already left for this auction."}, status=403)

    # Total Rating Stats
    rating_stats = seller_instance.rating_stats if seller_instance else None
    
    # Json Response
    return JsonResponse({
            "message": "Review successfully created.",
            "review": {
                "rating": review.rating,
                "date": review.review_date.strftime("%d %b %Y"),
                "text": review.review_text,
                "user": {
                    "username": user.username,
                    "url": reverse("accounts:profile", args=[user.pk])
                },
                "auction": {
                    "title": winner_offer.auction.title,
                    "url": reverse("auctions:auction-detail", args=[winner_offer.auction.pk])
                }
            },
            "total_rating": {
                "reviews_count": rating_stats.get('count'),
                "average_rating": float(rating_stats.get('avg') or 0)
            } if rating_stats else None
    }, status=200)
