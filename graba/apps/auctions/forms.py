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

        # Convert Euro + Cents (min_price)
        eur = cleaned_data.get('min_price_eur')
        cents = cleaned_data.get('min_price_cents')
        if eur is None or cents is None:
            self.add_error('min_price_cents', "Insert valid euro and cent values.")
        else:
            cleaned_data['min_price_cents'] = eur * 100 + cents
        
        # Convert Euro + Cents (buy_now_price)
        eur_bn = cleaned_data.get('buy_now_price_eur')
        cents_bn = cleaned_data.get('buy_now_price_cents')
        if eur_bn is None or cents_bn is None:
            self.add_error('buy_now_price_cents', "Insert valid euro and cent values.")
        else:
            cleaned_data['buy_now_price_cents'] = eur_bn * 100 + cents_bn
        
        # Other validations
        min_price = cleaned_data.get('min_price_cents')
        buy_now = cleaned_data.get('buy_now_price_cents')

        # Date validation
        if start and end and end <= start:
            self.add_error("end_date", "End date must be later than start date.")

        # Price validation
        if min_price is not None and min_price <= 0:
            self.add_error("min_price_cents", "Minimum price must be greater than zero.")

        if buy_now is not None and min_price is not None and buy_now < min_price:
            self.add_error(
                "buy_now_price_cents",
                "Buy Now price cannot be lower than the minimum price."
            )

        return cleaned_data

