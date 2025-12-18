from typing import Dict, Any

from django.db import models
from django.utils import timezone
from django.db.models import Count, Avg
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import ( 
    RegexValidator, MinValueValidator, MaxValueValidator, EmailValidator
)


class User(AbstractUser):
    EMAIL_VALIDATORS = [
        EmailValidator(
            message="Enter a valid email address."
        ),
        RegexValidator(
            regex=r'^.+@.+\..+$',
            message="Enter a valid email address."
        )
    ]

    STATE_CHOICES = [('ACTIVE', 'Active'), ('SUSPENDED', 'Suspended')]
    LEGAL_TYPE_CHOICES = [('PRIVATE', 'Private'), ('SHOPKEEPER', 'Shopkeeper')]

    email = models.EmailField(unique=True, validators=EMAIL_VALIDATORS)
    username = models.CharField(max_length=100)
    bio = models.CharField(max_length=100)
    #password_hash = models.CharField(max_length=255)
    registration_date = models.DateTimeField(default=timezone.now)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='ACTIVE')
    legal_type = models.CharField(max_length=10, choices=LEGAL_TYPE_CHOICES, default='PRIVATE')

    def has_role(self, role_name: str) -> bool:
        return Role.objects.filter(user=self, type=role_name).exists()
    
    def get_role_instances(self) -> Dict[str, Any]:
        roles = Role.objects.filter(user=self, state='ACTIVE')
        instances: Dict[str, Any] = {}
        
        ROLE_TYPE_MAP = {
            'BUYER': Buyer,
            'SELLER': Seller
        }
        
        for role in roles:
            model = ROLE_TYPE_MAP.get(role.type)
            if model:
                instance = model.object.filter(role=role).first()
                if instance:
                    instances[role.type] = instance

        return instances
    
    def __str__(self):
        return self.username
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table_comment = "Registered user of the application"
        ordering = ["-registration_date", "username"]


class Role(models.Model):
    ROLE_TYPE_CHOICES = [('BUYER', 'Buyer'), ('SELLER', 'Seller')]
    STATE_CHOICES = [('ACTIVE', 'Active'), ('SUSPENDED', 'Suspended')]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=ROLE_TYPE_CHOICES)
    activation_date = models.DateTimeField(default=timezone.now)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='ACTIVE')

    def __str__(self):
        return f"{self.user.username} - {self.type}"
    
    class Meta:
        unique_together = ('user', 'type')
        
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        db_table_comment = "Role assigned to a user"
        ordering = ["-activation_date", "type"]


class Buyer(models.Model):
    role = models.OneToOneField('accounts.Role', on_delete=models.CASCADE, primary_key=True, 
                                limit_choices_to={'type': 'BUYER'})
    shipping_address = models.TextField()

    def __str__(self):
        return f"Buyer {self.role.user.username}"

    class Meta:
        verbose_name = "Buyer"
        verbose_name_plural = "Buyers"
        db_table_comment = "Buyer role of a user"


class Seller(models.Model):
    role = models.OneToOneField('accounts.Role', on_delete=models.CASCADE, primary_key=True, 
                                limit_choices_to={'type': 'SELLER'})
    collection_address = models.TextField()
    
    @property
    def rating_stats(self):
        return self.reviews.aggregate(
            count=Count('id'),
            avg=Avg('rating')
        )

    def __str__(self):
        return f"Seller {self.role.user.username}"
    
    class Meta:
        verbose_name = "Seller"
        verbose_name_plural = "Sellers"
        db_table_comment = "Seller assigned to a user"


class Private(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    fiscal_code = models.CharField(max_length=16, unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Private Vendor"
        verbose_name_plural = "Private Vendors"
        db_table_comment = "A private vendor"
        ordering = ["first_name", "last_name"]


class Shopkeeper(models.Model):
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, primary_key=True)
    business_name = models.CharField(max_length=100)
    iva_number = models.CharField(max_length=11, unique=True)
    headquarters_address = models.TextField()

    def __str__(self):
        return self.business_name
    
    class Meta:
        verbose_name = "Shopkeeper"
        verbose_name_plural = "Shopkeepers"
        db_table_comment = "A shopkeeper"
        ordering = ["business_name"]
