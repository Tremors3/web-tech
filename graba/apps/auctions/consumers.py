
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class AuctionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.auction_id = self.scope["url_route"]["kwargs"]["auction_id"]
        self.group_name = f"auction_{self.auction_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # NEW BID
    async def new_bid(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_bid",
            "new_bid": {
                "username": event["username"],
                "amount_cents": event["amount_cents"],
                "amount_display": event["amount_display"],
                "offer_time": event["offer_time"],
            }
        }))
    
    # BUY NOW
    async def buy_now(self, event):
        await self.send(text_data=json.dumps({
            "type": "buy_now",
            "buy_now": {
                "username": event["username"],
                "amount_display": event["amount_display"],
                "offer_time": event["offer_time"],
            }
        }))

    # AUCTION STATUS UPDATE
    async def auction_status_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "auction_status_update",
            "auction_id": event["auction_id"],
            "status": event["status"],
        }))
