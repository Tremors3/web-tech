from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


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
        ('PENDING', 'Pending'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),
    ]

    title = models.CharField(max_length=100)
    image_url = models.URLField()
    description = models.TextField(blank=True, null=True)
    technical_details = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    buy_now_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    
    seller = models.ForeignKey('accounts.Seller', on_delete=models.CASCADE)
    category = models.ForeignKey('auctions.Category', null=True, on_delete=models.SET_NULL)

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
        ('PROPOSE', 'Propose'),
        ('BUY_NOW', 'Buy Now'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
    ]

    offer_time = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    buyer = models.ForeignKey('accounts.Buyer', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.type} - {self.amount}"

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
        db_table_comment = "An offer"
        ordering = ["-offer_time", "type"]


class WinnerOffer(models.Model):
    auction = models.OneToOneField('auctions.Auction', on_delete=models.CASCADE, primary_key=True)
    offer = models.OneToOneField('auctions.Offer', on_delete=models.CASCADE, unique=True)

    def __str__(self):
        return f"Winner for Auction {self.auction.id}"

    class Meta:
        verbose_name = "Winner Offer"
        verbose_name_plural = "Winner Offers"
        db_table_comment = "An offer that has won the auction"