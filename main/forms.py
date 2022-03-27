from django import forms
from django.forms import (ModelForm, 
    TextInput, Textarea, widgets)
from .models import *

class PlaceBidForm(forms.ModelForm):
    class Meta:
        model = AuctionBid
        fields = ['amount']

    def clean_amount(self):
        form_amount = self.cleaned_data.get("amount")
        prev_amt = AuctionBid.objects.latest("amount")
        prev_amt_cleaned = prev_amt.amount

        if prev_amt_cleaned > form_amount:
            raise forms.ValidationError("Please Put Higher Bid")

        return form_amount
