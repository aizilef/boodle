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
    for auction in auctions_now:
        print(auction)

    # Filter by auctions scheduled at most a week from now
    week_range = datetime.now() + timedelta(days=7)
    auctions_soon = Auction.objects.filter(auctionstart__lt=week_range).exclude(auctionstart__lte=datetime.now())
    for auction in auctions_soon:  #
        print(auction)    

    context = {
        'auctions_now': auctions_now,
        'auctions_soon': auctions_soon,
    }

    return render(request, "boodlesite/templates/index.html",context)    

def auction(request, pk):

    # Current auction ID
    auction = Auction.objects.get(pk=pk)
    # Item for auction
    auction_item = auction.itemid
    # Auction bids
    auction_bids = AuctionBid.objects.filter(auctionid=pk).order_by('-bidtime')

    highest_bid = auction_item.floorprice

    if auction_bids:
        highest_bid = auction_bids[0].amount

    # PLACE BID FORM
    form = PlaceBidForm(initial={'auctionid':auction})
    if request.method == 'POST':
        form = PlaceBidForm(request.POST,initial={'auctionid':auction})
        if form.is_valid():
            try:
                amount = form.cleaned_data['amount']
                new_bid = AuctionBid(amount=amount,bidtime=datetime.now(),auctionid=auction)
                new_bid.save()
                return redirect(f"/auction/{pk}")
            except:
                pass
    
    # ADD TO FAVORITES FORM
    addtofavs_form = AddToFavoritesForm()
    if request.method == 'POST':
        addtofavs_form = AddToFavoritesForm(request.POST)
        # if addtofavs_form.is_valid():
            # try:
            #     amount = addtofavs_form.cleaned_data['amount']
            #     new_bid = AuctionBid(amount=amount,bidtime=datetime.now(),auctionid=auction)
            #     new_bid.save()
            #     return redirect(f"/auction/{pk}")
            # except:
            #     pass


    context = {
        'item_name':auction_item.itemname,
        'item_specs': auction_item.itemspecs,
        'auction_bids' : auction_bids,
        'item_floor_price': auction_item.floorprice,
        'highest_bid': highest_bid,
        'auction_end':  auction.auctionend,
        'form' : form,
        'addtofavs_form': addtofavs_form,
    }

    if auction.auctionend < datetime.now():
        return HttpResponse("This auction has already passed.")
    elif auction.auctionstart > datetime.now():
        #return HttpResponse("This auction has not yet started.")
        return render(request, "boodlesite/templates/error404/notstarted_error404.html")
    else:
        return render(request, "boodlesite/templates/auction.html",context)    

def error404(request):
    return render(request, "boodlesite/templates/error404/notstarted_error404.html")

def tempstore(request): # temp view

    #### Access to store 1 [ edit accordingly when it becomes accessible thru a user ] ####
    current_store = Store.objects.get(storeid=1)

    context = {
        'current_store':current_store #### used for navbar, access to store 1

    }

    return render(request, "boodlesite/templates/tempstore.html", context)

def mystore(request, pk):

    #### Access to store 1 [ edit accordingly when it becomes accessible thru a user ] ####
    current_store = Store.objects.get(pk=pk)
    store_items = Item.objects.filter(storeid=pk)

    context = {
        'current_store':current_store,
        'store_items':store_items
    }

    return render(request, "boodlesite/templates/store.html", context)

def addItem(request, pk):

    # Current Store, pk here is the storeid
    current_store = Store.objects.get(pk=pk)

    form = AddItemForm(initial={'storeid':current_store})

    if request.method == 'POST':
        form = AddItemForm(request.POST,initial={'storeid':current_store})
        if form.is_valid():
            form.save()
            return redirect('storeid', pk=pk)

    context = {
        'form':form,
        'current_store': current_store # access to store 1
    }

    return render(request, "boodlesite/templates/additem.html", context)

def startAuction(request):

    #### Access to store 1 [ edit accordingly when it becomes accessible thru a user ] ####
    current_store = Store.objects.get(storeid=1)

    context = {
        'current_store':current_store
    }


    return render(request, "boodlesite/templates/startauction.html", context)

def tempProfile(request): # temp view

    #### Access to store 1 [ edit accordingly when it becomes accessible thru a user ] ####
    current_user =BoodleUser.objects.get(userid=1)

    context = {
        'current_user':current_user #### used for navbar, access to user1
    }

    return render(request, "boodlesite/templates/tempprofile.html", context)

def profile(request, pk):
    # filter the favorites i think from auction tapos
    # we need to add things like .add() and .remove() 
    # get the user's information
    current_user = BoodleUser.objects.get(pk=pk)
    
    context = {
        'displayname': current_user.displayname,
        'username':current_user.username,
    }

    return render(request, "boodlesite/templates/profile.html", context)
