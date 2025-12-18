from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Review(models.Model):
    review_text = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(validators=[
        MinValueValidator(1), MaxValueValidator(5)
    ])

    seller = models.ForeignKey('accounts.Seller', on_delete=models.CASCADE, related_name='reviews')
    winner_offer = models.OneToOneField('auctions.WinnerOffer', on_delete=models.CASCADE, related_name='review')

    def __str__(self):
        return (f"Review for auction {self.winner_offer.auction.id} - Rating: {self.rating}")

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ["-review_date"]
