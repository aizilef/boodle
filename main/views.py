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
    for auction in auctions_soon:
        print(auction)    

    context = {
        'auctions_now': auctions_now,
        'auctions_soon': auctions_soon,
    }

    return render(request, "boodlesite/templates/index.html",context)    

def auction(request,pk):

    # Current auction ID
    auction = Auction.objects.get(pk=pk)
    # Item for auction
    auction_item = auction.itemid # this is the itemfk thru auction
    # Auction bids
    auction_bids = AuctionBid.objects.filter(auctionid=pk).order_by('-bidtime')
    highest_bid = auction_item.floorprice 
    # get boodle user ID 
    users = BoodleUser.objects.get(userid=1) 
    userid = users.userid 
    # getting the user name
    # user_profile = users.displayname

    if auction_bids:
        highest_bid = auction_bids[0].amount

    # PLACE BID FORM AND ADD TO FAVES FORM
    form = PlaceBidForm(initial={'auctionid':auction, 'boodleuserid':users})
    if request.method == 'POST':
        form = PlaceBidForm(request.POST,initial={'auctionid':auction, 'boodleuserid':users})
        if form.is_valid():
            try:
                amount = form.cleaned_data['amount']
                # saves the bid by auctionid, amount, bidtime, boodleuserid
                new_bid = AuctionBid(
                    amount=amount, bidtime=datetime.now(),
                    auctionid=auction, boodleuserid=users)
                new_bid.save()
                return redirect(f"/auction/{pk}")
            except:
                pass

    context = {
        'item_name':auction_item.itemname,
        'item_specs': auction_item.itemspecs,
        'auction_bids' : auction_bids,
        'item_floor_price': auction_item.floorprice,
        'highest_bid': highest_bid,
        'auction_end':  auction.auctionend,
        'user_profile': users.displayname,
        'form' : form,
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
    user_one =BoodleUser.objects.get(userid=1)
    user_two = BoodleUser.objects.get(userid=3)

    context = {
        'user_one':user_one, #### used for navbar, access to user1
        'user_two':user_two, #### used for navbar, access to user1
    }

    return render(request, "boodlesite/templates/tempprofile.html", context)

def profile(request, pk):
    
    current_user = BoodleUser.objects.get(pk=pk)
    #auction bid user id = 3 --> bids user made --> know auctions g
    bidsByUser = AuctionBid.objects.filter(boodleuserid=1)
    auctionsOfUser = Auction.objects.all().distinct('auctionid')


    #💫auctionsOfUser = Auction.objects.all().distinct('auctionid')
    # get existing auctions for user's bids
    auctions = Auction.objects.all()
    for auction in auctionsOfUser:
        print(auction)   

    context = {
        'displayname': current_user.displayname,
        'username':current_user.username,
        'bidsByUser' : bidsByUser,
        'auctionsOfUser': auctionsOfUser,
        'auctions': auctions,
    }

    return render(request, "boodlesite/templates/profile.html", context)
