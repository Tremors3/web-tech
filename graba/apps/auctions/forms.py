from django import forms
from django.core.exceptions import ValidationError

from .models import Auction


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = [
            "title",
            "image",
            "description",
            "technical_details",
            "start_date",
            "end_date",
            "min_price_cents",
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
        min_price = cleaned_data.get("min_price_cents")
        buy_now = cleaned_data.get("buy_now_price_cents")

        # 1) end_date needs to be after start_date
        if start and end and end <= start:
            raise ValidationError(
                {"end_date": "La data di fine deve essere successiva a quella di inizio."}
            )

        # 2) min_price needs to be positive
        if min_price is not None and min_price <= 0:
            raise ValidationError(
                {"min_price_cents": "Il prezzo minimo deve essere maggiore di zero."}
            )

        # 3) buy_now_price needs to be >= min_price
        if buy_now and min_price and buy_now < min_price:
            raise ValidationError(
                {"buy_now_price_cents": "Il prezzo Buy Now deve essere almeno pari al prezzo minimo."}
            )

        return cleaned_data
