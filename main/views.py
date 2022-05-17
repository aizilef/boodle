from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# restricting the views to logged in users, every view we want restricted
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *

from datetime import datetime, timedelta

def registerPage(request):
    # dont want a logged in user to see this
    if request.user.is_authenticated:
        return redirect('/')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user_name = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                messages.success(request, 'Account was create for ' + user_name)

                # boodleuser_inst = BoodleUser.objects.create(displayname=user_name, pword=password, username=user_name)
                # boodleuser_inst.save()

                return redirect('login')
            

        context = {'form':form}
        return render(request, 'boodlesite/templates/registration/register.html', context)

def loginPage(request):

    # dont want a logged in user to see this
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            user_name = request.POST.get('username')
            pass_word = request.POST.get('password')
            boodle_user = authenticate(request, username=user_name, password=pass_word)
            
            if boodle_user is not None:
                login(request, boodle_user)
                return redirect('/')
            else:
                messages.info(request, 'Username OR Password is incorrect') # all msgs get sent here will be output
                
        context = {}
        return render(request, 'boodlesite/templates/registration/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
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

@login_required(login_url='login')
def auction(request,pk):

    # Current auction ID
    auction = Auction.objects.get(pk=pk)
    # Item for auction
    auction_item = auction.itemid # this is the itemfk thru auction
    # Auction bids
    auction_bids = AuctionBid.objects.filter(auctionid=pk).order_by('-bidtime')
    highest_bid = auction_item.floorprice 
    
    ## ⭐ the user that is logged in

    users = AuthUser.objects.get(id=request.user.id) 
    userid = users.id 

    if auction_bids:
        highest_bid = auction_bids[0].amount

    # PLACE BID FORM AND ADD TO FAVES FORM
    form = PlaceBidForm(initial={'auctionid':auction, 'userid':userid})
    if request.method == 'POST':
        form = PlaceBidForm(request.POST,initial={'auctionid':auction, 'userid':userid})
        if form.is_valid():
            try:
                amount = form.cleaned_data['amount']
                # saves the bid by auctionid, amount, bidtime, boodleuserid
                new_bid = AuctionBid(
                    amount=amount, bidtime=datetime.now(),
                    auctionid=auction, userid=users)
                new_bid.save()
                return redirect(f"/auction/{pk}")
            except Exception as e:
                print("Error:", e)

    context = {
        'item_name':auction_item.itemname,
        'item_specs': auction_item.itemspecs,
        'auction_bids' : auction_bids,
        'item_floor_price': auction_item.floorprice,
        'highest_bid': highest_bid,
        'auction_title': auction.title,
        'auction_end':  auction.auctionend,
        'user_profile': users,
        'form' : form,
    }

    if auction.auctionend < datetime.now():
        return HttpResponse("This auction has already passed.")
    elif auction.auctionstart > datetime.now():
        return render(request, "boodlesite/templates/error404/notstarted_error404.html")
    else:
        return render(request, "boodlesite/templates/auction.html",context)    

@login_required(login_url='login')
def error404(request):
    return render(request, "boodlesite/templates/error404/notstarted_error404.html")

@login_required(login_url='login')
def mystore(request, pk):

    #### Access to store 1 [ edit accordingly when it becomes accessible thru a user ] ####
    # pk is storeid
    current_store = Store.objects.get(pk=pk)
    store_items = Item.objects.filter(storeid=pk)

    all_auctions = Auction.objects.all()

    form = DeleteItemForm()

    if request.method == "POST":
        form = DeleteItemForm(request.POST)
        if form.is_valid():
            item_id = form.cleaned_data['itemid']
            current_item = Item.objects.get(itemid=item_id)
            for auction in all_auctions:
                if auction.itemid == current_item:
                    Auction.objects.filter(itemid=item_id).delete()
                    
            Item.objects.get(itemid=item_id).delete()

            return redirect('storeid', pk=pk)

    context = {
        'current_store':current_store,
        'store_items':store_items,
        'form':form
    }

    return render(request, "boodlesite/templates/store.html", context)

@login_required(login_url='login')
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
        'title': 'List new item',
        'current_store': current_store # access to store 1
    }

    return render(request, "boodlesite/templates/additem.html", context)

@login_required(login_url='login')
def editItem(request, pk):

    item = Item.objects.get(itemid=pk)
    current_store = item.storeid
    form = AddItemForm(instance=item)

    if request.method == 'POST':
        form = AddItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('storeid', pk=current_store)

    context = {
        'form':form,
        'title': 'Edit item information'
    }

    return render(request, "boodlesite/templates/additem.html", context)

@login_required(login_url='login')
def startAuction(request, pk):

    # pk is store id
    current_store = Store.objects.get(pk=pk)
    store_id = current_store.storeid
    # get items under this store
    store_items = Item.objects.filter(storeid=pk)
    # Current userid, change as per ⭐ whoever is logged in
    user = AuthUser.objects.get(id=request.user.id)
    userid = user.id

    # temp: all auctions
    all_auctions = Auction.objects.all()

    form = StartAuctionForm(initial={'auctionstart':datetime.now()})

    if request.method == 'POST':
        form = StartAuctionForm(request.POST)
        if form.is_valid():
            try:
                title = form.cleaned_data['title']
                info = form.cleaned_data['info']
                starttime = form.cleaned_data['auctionstart']
                endtime = form.cleaned_data['auctionend']
                current_item = form.cleaned_data['itemid']
                new_auction = Auction(title=title, info=info, auctionstart=starttime, auctionend=endtime, itemid=current_item)
                new_auction.save()
                return redirect(f"/profile/{userid}")
            except:
                pass

    context = {
        'current_store':current_store,
        'store_items': store_items,
        'all_auctions':all_auctions,
        'form':form
    }

    return render(request, "boodlesite/templates/startauction.html", context)

@login_required(login_url='login')
def profile(request, pk):
    
    current_user = AuthUser.objects.get(pk=pk)
    #auction bid user id = 3 --> bids user made --> know auctions g
    ## ⭐ the user that is logged in
    bids_by_user = AuctionBid.objects.filter(userid=pk).distinct('auctionid')

    auctions_of_user = Auction.objects.all().distinct('auctionid')
    ids_of_auction = []

    for bid in bids_by_user:
        for auction in auctions_of_user:
            if bid.auctionid == auction:
                ids_of_auction.append(bid.auctionid)
                
    # print("These are the distinct auction IDs: ", idsOfAuction)

    #💫auctionsOfUser = Auction.objects.all().distinct('auctionid')
    # get existing auctions for user's bids
    auctions = Auction.objects.all()

    # 🔥Current Store, pk here is the storeid
    current_user = AuthUser.objects.get(pk=pk)
    form = CreateStoreForm(initial={'userid':pk})

    current_store = Store.objects.filter(userid=current_user.id)
    current_storeid = None

    for i in current_store:
        current_storeid = i.storeid

    if request.method == 'POST':
        form = CreateStoreForm(request.POST, initial={'userid':pk}) 
        # putting a default value
        if form.is_valid():
            form.save()
            return redirect('profileid', pk=pk)
    # 🔥 

    context = {
        'displayname': current_user.username,
        'username': current_user.username,
        'user': current_user.id,
        'store': current_storeid,
        'bidsByUser' : bids_by_user,
        'auctions_of_user': auctions_of_user,
        'auctions': auctions,
        'ids_of_auction': ids_of_auction,
        'createStoreForm': form
    }

    return render(request, "boodlesite/templates/profile.html", context)

@login_required(login_url='login')
def editStore(request, pk):

    store= Store.objects.get(storeid=pk)
    current_store = store.storeid
    form = CreateStoreForm(instance=store)

    if request.method == 'POST':
        form = CreateStoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('storeid', pk=current_store)

    context = {
        'form': form,
        'title': 'Edit Store Information'
    }

    return render(request, "boodlesite/templates/storeForm.html", context)

@login_required(login_url='login')
def editProfile(request, pk):

    user= AuthUser.objects.get(id=pk) # authuser object
    current_user = user.id # auth user id
    form = editBoodleUserForm(instance=user)

    if request.method == 'POST':
        form = editBoodleUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profileid', pk=current_user)

    context = {
        'form': form,
        'title': 'Edit Profile Information',
    }

    return render(request, "boodlesite/templates/editBoodleUser.html", context)
