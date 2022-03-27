from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.core.exceptions import ValidationError


from .models import *
from .forms import *

from datetime import datetime, timedelta


def homepage(request):
    print(Auction.objects.all())

    # Filter by auctions happening right now
    auctions_now = Auction.objects.filter(auctionstart__lt=datetime.now(),auctionend__gt=datetime.now())
    for auction in auctions_now:  #
        print(auction)

    # Filter by auctions scheduled at most a week from now
    week_range = datetime.now() + timedelta(days=7)
    auctions_soon = Auction.objects.filter(auctionstart__lt=week_range).exclude(auctionstart__lte=datetime.now())
    for auction in auctions_soon:  #
        print(auction)    

    context = {
        'auctions_now': auctions_now,
        'auctions_soon': auctions_soon
    }

    return render(request, "boodlesite/templates/index.html",context)    

def auction(request, pk):
    # Current auction ID
    auction = Auction.objects.get(pk=pk)
    # Item for auction
    auction_item = auction.itemid
    # Auction bids
    auction_bids = AuctionBid.objects.filter(auctionid=pk).order_by('-bidtime')

    if not auction_bids:
        highest_bid = auction_item.floorprice
    else:
        highest_bid = auction_bids[0]
        
    print("This is the auction bids: ", auction_bids)
    prev_amt = AuctionBid.objects.latest('amount');
    print(prev_amt)

    form = PlaceBidForm()
    if request.method == 'POST':
        form = PlaceBidForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if amount > highest_bid.amount:
                new_bid = AuctionBid(amount=amount,bidtime=datetime.now(),auctionid=auction)
                new_bid.save()
                return redirect(f"/auction/{pk}")
            else:
                raise ValidationError("ERROR")


    context = {
        'item_name':auction_item.itemname,
        'item_specs': auction_item.itemspecs,
        'auction_bids' : auction_bids,
        'item_floor_price': auction_item.floorprice,
        'highest_bid':highest_bid,
        'form' : form
    }

    if auction.auctionend < datetime.now():
        return HttpResponse("This auction has already passed.")
    elif auction.auctionstart > datetime.now():
        return HttpResponse("This auction has not yet started.")
    else:
        return render(request, "boodlesite/templates/auction.html",context)    
