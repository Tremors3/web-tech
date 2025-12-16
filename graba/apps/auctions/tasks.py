# graba/apps/auctions/tasks.py
import json
from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Auction, WinnerOffer


def broadcast_auction_status(auction: Auction):
    """
    Broadcasts auction status update to connected WebSocket clients.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"auction_{auction.pk}",
        {
            "type": "auction_status_update",
            "status": auction.status,
            "auction_id": auction.pk,
        }
    )


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 5})
def open_auction_task(self, auction_id: int):
    """
    Opens an auction and notifies clients via WebSocket.
    Safe to retry.
    """
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return

    if auction.status != "OPEN":
        return
    
    auction.status = "OPEN"
    auction.save(update_fields=["status"])

    # Notify WebSocket
    broadcast_auction_status(auction)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 5})
def close_auction_task(self, auction_id: int):
    """
    Closes an auction, assigns the winner (if any), notifies clients with WebSocket.
    Safe to retry.
    """
    try:
        auction = Auction.objects.get(pk=auction_id)
    except Auction.DoesNotExist:
        return

    if auction.status != "OPEN":
        return

    auction.close()

    # Notify WebSocket
    broadcast_auction_status(auction)
