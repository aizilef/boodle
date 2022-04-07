from datetime import datetime
from django import forms
from django.forms import (ModelForm, 
    TextInput, Textarea, widgets)
from django.utils.translation import gettext_lazy as _
from .models import *

from django.core.exceptions import ValidationError
    
class PlaceBidForm(forms.ModelForm):
    class Meta:
        model = AuctionBid
        fields = ['amount','auctionid']
        widgets = {'auctionid': forms.HiddenInput()}

    def clean(self):
        super().clean()
        form_amount = self.cleaned_data.get('amount')
        auction = self.cleaned_data.get('auctionid')

        auction_item = Item.objects.get(auction=auction)

        auction_bids = AuctionBid.objects.filter(auctionid=auction)
        
        if not auction_bids:
            highest_bid = auction_item.floorprice
            if form_amount < highest_bid:
                raise ValidationError('Please enter an amount greater than or equal to the floorprice.')
        else:
            highest_bid = auction_bids.latest('bidtime').amount
            if form_amount <= highest_bid:
                raise ValidationError('Please enter an amount higher than the current highest bid.')

class AddItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['itemname','itemspecs','floorprice','storeid']
        widgets = {'storeid': forms.HiddenInput()}

        labels = {
            'itemname': _('Item Name'),
            'itemspecs': _('Item Description'),
            'floorprice': _('Floor Price')
        }

class StartAuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = '__all__'

        labels = {
            'title': _('Auction Title'),
            'info': _('Auction Description'),
            'auctionstart': _('Starting time'),
            'auctionend': _('Closing time'),
            'itemid': _('Item up for auction')
        }

        # datetime_format = ['%Y-%m-%d %H:%M']
        # widgets = { 'auctionstart' : forms.DateTimeInput(input_formats=['%Y-%m-%d %H:%M']), 'auctionend' : forms.DateTimeInput(input_formats=['%Y-%m-%d %H:%M'])}
        # vv fix later, is missing time widget
        # widgets = { 'auctionstart' : forms.SelectDateWidget, 'auctionend':forms.SelectDateWidget}
        # 'itemid': forms.HiddenInput()}
        