from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('AUCT_WON', 'Auction Won'),
        ('AUCT_END', 'Auction Ending'),
        ('GENERIC', 'Generic Notification'),
    ]

    notification_text = models.TextField()
    read_status = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='GENERIC')
    notification_date = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"Notification for {self.user.username} - Type: {self.notification_type}"

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        db_table_comment = "A user notification"
        ordering = ["-notification_date"]
