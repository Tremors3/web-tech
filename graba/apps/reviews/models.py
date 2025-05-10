from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Review(models.Model):
    review_text = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(default=timezone.now)
    rating = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])

    auction = models.OneToOneField('auctions.WinnerOffer', on_delete=models.CASCADE)

    def __str__(self):
        return f"Review for auction {self.auction.auction_id} - Rating: {self.rating}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        db_table_comment = "A review a buyer left for a seller after winning the auction"
        ordering = ["-review_date"]