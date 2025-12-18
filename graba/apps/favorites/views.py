from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import FavoriteAuction


@login_required
def toggle_favorite(request, auction_id):
    
    fav, created = FavoriteAuction.objects.get_or_create(
        user=request.user,
        auction_id=auction_id
    )

    if not created:
        fav.delete()
        is_favorite = False
    else:
        is_favorite = True

    return JsonResponse({"favorite": is_favorite})
