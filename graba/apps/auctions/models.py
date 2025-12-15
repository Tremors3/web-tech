from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models

from .scripts.misc import auction_image_upload_to

class Category(models.Model):
    name = models.CharField(primary_key=True, max_length=100)
    level = models.IntegerField(default=1, validators=[
        MinValueValidator(1),
        MaxValueValidator(2)
    ])
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        db_table_comment = "An auction category"
        ordering = ["name"]


class Auction(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        #('PENDING', 'Pending'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),
    ]

    title = models.CharField(max_length=100)
    image = models.ImageField(
        upload_to=auction_image_upload_to,
        default="placeholders/noimage.png",
        blank=True,
        null=True
    )
    description = models.TextField(blank=True, null=True)
    technical_details = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    min_price_cents = models.IntegerField()
    buy_now_price_cents = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    
    seller = models.ForeignKey('accounts.Seller', on_delete=models.CASCADE)
    category = models.ForeignKey('auctions.Category', null=True, on_delete=models.SET_NULL)

    @property
    def has_offers(self, type_:str='BID') -> bool:
        return Offer.objects.filter(auction=self, type=type_).exists()

    def get_offers_number(self, type_:str='BID') -> int:
        return Offer.objects.filter(auction=self, type=type_).count()

    def get_highest_offer_value(self, type_:str='BID') -> int | None:
        return Offer.objects.filter(auction=self, type=type_).aggregate(
            highest=models.Max('amount_cents')
        )['highest']
    
    def is_bn_enabled(self) -> bool:
        return (self.buy_now_price_cents is not None)
    
    @property
    def ftime_tag(self) -> str:
        now = timezone.now()
        return "Ended" if now > self.end_date else "Starts in" if now < self.start_date else "Finishes in"

    @property
    def ftime_left(self) -> str | None:
        now = timezone.now()

        # If the auction is ended
        if now > self.end_date:
            return None

        # Reference timestamp: start or end
        end = self.start_date if now < self.start_date else self.end_date

        # Difference in seconds
        total_seconds = int((end - now).total_seconds())

        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if not parts:
            parts.append(f"{seconds}s")

        # Show at most two units
        return " ".join(parts[:2])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Auction"
        verbose_name_plural = "Auctions"
        db_table_comment = "An auction"
        ordering = ["-start_date", "title"]


class Offer(models.Model):
    TYPE_CHOICES = [
        ('BID', 'Bid'),
        #('PROPOSE', 'Propose'),
        ('BUY_NOW', 'Buy Now'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
    ]

    offer_time = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    amount_cents = models.IntegerField()

    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    buyer = models.ForeignKey('accounts.Buyer', on_delete=models.CASCADE)

    @property
    def is_buy_now(self):
        return self.offer_type == Offer.Type.BUY_NOW

    def __str__(self):
        return f"{self.type} - {self.amount}"

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        db_table_comment = "An offer"
        ordering = ["type", "-amount_cents", "-offer_time"]


class WinnerOffer(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    
    auction = models.OneToOneField('auctions.Auction', on_delete=models.CASCADE, primary_key=True, related_name='winner_offer')
    offer = models.OneToOneField('auctions.Offer', on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return f"Winner for Auction {self.auction.id}"

    class Meta:
        verbose_name = "Winner Offer"
        verbose_name_plural = "Winner Offers"
        db_table_comment = "An offer that has won the auction"
