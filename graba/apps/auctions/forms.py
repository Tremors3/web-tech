from django import forms
from django.core.exceptions import ValidationError

from .models import Auction


class AuctionForm(forms.ModelForm):
    
    min_price_eur = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        label="Minimum Price (€)"
    )
    buy_now_price_eur = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        label="Buy Now Price (€)",
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('min_price_eur', 'buy_now_price_eur'):
            self.fields[field_name].widget.attrs.update({
                'type': 'number',
                'step': '0.01',
                'min': '0.01',
            })
    
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
            "buy_now_price_eur",
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
        min_price = cleaned_data.get('min_price_eur')
        buy_now = cleaned_data.get('buy_now_price_eur')

        # 1) end_date needs to be after start_date
        if start and end and end <= start:
            raise ValidationError(
                {"end_date": "End date must be later than the start date."}
            )

        # 2) min_price needs to be positive
        if min_price is not None and min_price <= 0:
            raise ValidationError(
                {"min_price_cents": "Minimum price must be greater than zero."}
            )

        # 3) buy_now_price needs to be >= min_price
        if buy_now is not None and min_price is not None and buy_now < min_price:
            raise ValidationError(
                {"buy_now_price_cents": "Buy Now price cannot be lower than the minimum price."}
            )

        return cleaned_data
