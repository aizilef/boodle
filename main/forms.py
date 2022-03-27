from django import forms
from django.forms import (ModelForm, 
    TextInput, Textarea, widgets)
from .models import *

class PlaceBidForm(forms.ModelForm):
    class Meta:
        model = AuctionBid
        fields = ['amount']