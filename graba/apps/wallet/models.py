from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Wallet(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, primary_key=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet of {self.user.username} - Balance: {self.balance}"

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"
        db_table_comment = "Wallet of a user"
        ordering = ["-balance"]


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('PURCHASE', 'Purchase'),
        ('WITHDRAWAL', 'Withdrawal'),
    ]

    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(default=timezone.now)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    auction = models.ForeignKey('auctions.WinnerOffer', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} by {self.user.username}"

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        db_table_comment = "A transaction"
        ordering = ["-transaction_date", "transaction_type"]