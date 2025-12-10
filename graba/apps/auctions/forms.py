from django import forms
from django.core.exceptions import ValidationError

from .models import Auction


class AuctionForm(forms.ModelForm):
    # Min price fields
    min_price_eur = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={"style": "width: 164px;"}))
    min_price_cents = forms.IntegerField(min_value=0, max_value=99, initial=1)
    
    # Buy now price fields
    buy_now_price_eur = forms.IntegerField(min_value=0, initial=0, widget=forms.NumberInput(attrs={"style": "width: 164px;"}))
    buy_now_price_cents = forms.IntegerField(min_value=0, max_value=99, initial=1)
    
    class Meta:
        model = Auction
        fields = [
            "title",
            "image",
            "description",
            "technical_details",
            "start_date",
            "end_date",
            "min_price_eur",
            "min_price_cents",
            "buy_now_price_eur",
            "buy_now_price_cents",
            "category",
        ]

        widgets = {
            "start_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        
        # Price in cents = eur * 100 + cents
        min_price_eur_only = cleaned_data.get('min_price_eur', 0)
        min_price_cents_only = cleaned_data.get('min_price_cents', 0)
        cleaned_data['min_price_cents'] = min_price_eur_only * 100 + min_price_cents_only
        
        # Price in cents = eur * 100 + cents
        buy_now_price_eur_only = cleaned_data.get('buy_now_price_eur')
        buy_now_price_cents_only = cleaned_data.get('buy_now_price_cents')
        cleaned_data['buy_now_price_cents'] = buy_now_price_eur_only * 100 + buy_now_price_cents_only

        min_price = cleaned_data.get('min_price_cents')
        buy_now = cleaned_data.get('buy_now_price_cents')

        # 1) end_date needs to be after start_date
        if start and end and end <= start:
            raise ValidationError(
                {"end_date": "End date must be later than the start date."}
            )

        # 2) min_price needs to be positive
        if min_price is not None and min_price <= 0:
            raise ValidationError(
                {"min_price_eur": "Minimum price must be greater than zero."}
            )

        # 3) buy_now_price needs to be >= min_price
        if buy_now is not None and min_price is not None and buy_now < min_price:
            raise ValidationError(
                {"buy_now_price_eur": "Buy Now price cannot be lower than the minimum price."}
            )

        return cleaned_data
