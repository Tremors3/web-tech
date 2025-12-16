from celery import shared_task
from django.utils import timezone

from .models import Auction


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 5})
def close_auction_task(self, auction_id: int):
    """
    Closes an auction and assigns the winner (if any).
    Safe to retry.
    """
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return

    # TODO: Integrare WebSocket e Notifiche

    auction.close()
