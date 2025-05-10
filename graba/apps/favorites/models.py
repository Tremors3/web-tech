from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class FavoriteAuction(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    auction = models.ForeignKey('auctions.Auction', on_delete=models.CASCADE)
    added_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} favorited auction {self.auction.title}"

    class Meta:
        unique_together = ('user', 'auction')
        
        verbose_name = "Favorite Auction"
        verbose_name_plural = "Favorite Auctions"
        db_table_comment = "The favourite auctions of a user"
        ordering = ["-added_on"]


class RecentlyViewedAuction(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    auction = models.ForeignKey('auctions.Auction', on_delete=models.CASCADE)
    viewed_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} viewed auction {self.auction.title}"

    class Meta:
        unique_together = ('user', 'auction')
        
        verbose_name = "Recently Viewed Auction"
        verbose_name_plural = "Recently Viewed Auctions"
        db_table_comment = "The recently viewed auctions of a user"
        ordering = ["-viewed_on"]