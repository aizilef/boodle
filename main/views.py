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
    ''' 
    Any user can only register an account on Boodle. They must give a unique username or they will be asked to input another one. A logged-in user cannot see the registration page unless they log-out of Boodle.
    '''
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

                return redirect('login')
            

        context = {'form':form}
        return render(request, 'boodlesite/templates/registration/register.html', context)

def loginPage(request):
    ''' 
    A user can only log in if they have registered account on Boodle. 
    They must input the correct password and username or else they won't be let in the site. 
    They will be redirected to Boodle's home page if credentials are valid.
    A logged-in user cannot see the log-in page unless they log-out of Boodle.
    '''
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
                messages.info(request, 'Username OR Password is incorrect')

        return render(request, 'boodlesite/templates/registration/login.html')

def logoutUser(request):
    ''' 
    Logs auser out of their Boodle account. 
    Redirects a user to the login page when activated.
    '''
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def homepage(request):
    '''
    Only a logged-in user has access to this view. 
    A logged-in user has access to the current and future auctions. They may choose from the selection on which they would like to participate in. 
    These auctions are available only at the end time set by the seller. This applies to both current and future auctions.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''
    auctions_now = Auction.objects.filter(auctionstart__lt=datetime.now(),auctionend__gt=datetime.now())
    for auction in auctions_now:
        print(auction)

    week_range = datetime.now() + timedelta(days=7)
    auctions_soon = Auction.objects.filter(auctionstart__lt=week_range).exclude(auctionstart__lte=datetime.now())

    context = {
        'auctions_now': auctions_now,
        'auctions_soon': auctions_soon,
    }

    return render(request, "boodlesite/templates/index.html",context)    

@login_required(login_url='login')
def auction(request,pk):
    '''
    Only a logged-in user has access to this view. 
    An auction is viewable only when it is ongoing. A user cannot view past nor future auctions -- they will receive an error page if they try to access future auctions. This indicates they should go back to the home screen.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''
    auction = Auction.objects.get(pk=pk)
    auction_item = auction.itemid 
    auction_host = auction_item.storeid

    auction_bids = AuctionBid.objects.filter(auctionid=pk).order_by('-bidtime')
    highest_bid = auction_item.floorprice 

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
                new_bid = AuctionBid(
                    amount=amount, bidtime=datetime.now(),
                    auctionid=auction, userid=users)
                new_bid.save()       # saves the bid by auctionid, amount, bidtime, boodleuserid
                return redirect(f"/auction/{pk}")
            except Exception as e:
                print("Error:", e)

    context = {
        'item_name':auction_item.itemname,
        'item_specs': auction_item.itemspecs,
        'auction_host':auction_host,
        'auction_bids' : auction_bids,
        'item_floor_price': auction_item.floorprice,
        'highest_bid': highest_bid,
        'auction_title': auction.title,
        'auction_end':  auction.auctionend,
        'user_profile': users,
        'form' : form,
    }

    if auction.auctionend < datetime.now():
        return render(request, "boodlesite/templates/error404/passed_error404.html")
    elif auction.auctionstart > datetime.now():
        return render(request, "boodlesite/templates/error404/notstarted_error404.html")
    else:
        return render(request, "boodlesite/templates/auction.html",context)    

@login_required(login_url='login')
def passed_auction_error404(request):
    '''
    Only a logged-in user has access to this view. 
    A user receives this view when they try to view passed auctions.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''
    return render(request, "boodlesite/templates/error404/passed_error404.html")


@login_required(login_url='login')
def future_auction_error404(request):
    '''
    Only a logged-in user has access to this view. 
    A user receives this view when they try to view future auctions.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''
    return render(request, "boodlesite/templates/error404/notstarted_error404.html")

@login_required(login_url='login')
def about(request):
    '''
    Only a logged-in user has access to this view. 
    This shows relevant information on Boodle and the creators.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''
    return render(request, "boodlesite/templates/about.html")

@login_required(login_url='login')
def help(request):
    '''
    Only a logged-in user has access to this view. 
    This shows relevant information on how to use Boodle.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''
    return render(request, "boodlesite/templates/help.html")

@login_required(login_url='login')
def mystore(request, pk):
    '''
    Only a logged-in user has access to this view. 
    This shows the store owned by a user. If a user has not made a store, this view is not available to them. The store contains items they want to/currently put on auction.
    This view is where a user [seller] can start an auction to be put up in the homepage for every user [buyers and sellers] to see.
    The user [seller] can also edit the item details and store details in this view.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''
    current_store = Store.objects.get(pk=pk)
    store_owner = current_store.userid
    store_items = Item.objects.filter(storeid=pk)

    all_auctions = Auction.objects.all()
    all_bids = AuctionBid.objects.all()

    form = DeleteItemForm()

    if request.method == "POST":
        form = DeleteItemForm(request.POST)
        if form.is_valid():
            item_id = form.cleaned_data['itemid']
            current_item = Item.objects.get(itemid=item_id)
            for auction in all_auctions:
                if auction.itemid == current_item:

                    for bids in all_bids:
                        if bids.auctionid == auction:
                            AuctionBid.objects.filter(auctionid=auction.auctionid).delete()

                    Auction.objects.filter(itemid=item_id).delete()
                    
            Item.objects.get(itemid=item_id).delete()

            return redirect('storeid', pk=pk)

    context = {
        'current_store':current_store,
        'store_owner':store_owner,
        'store_items':store_items,
        'form':form
    }

    return render(request, "boodlesite/templates/store.html", context)

@login_required(login_url='login')
def addItem(request, pk):
    '''
    Only a logged-in user has access to this view. 
    This view is a form wherin users [sellers] can add items to their store. After successfully making the item, they will be redirected back to the store.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''
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
    '''
    Only a logged-in user has access to this view. 
    This view is a form wherin users [sellers] can edit item details on their store. After successfully editing the item, they will be redirected back to the store.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''

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
    '''
    Only a logged-in user has access to this view. 
    This view is a form wherin users [sellers] can start an auction to be viewed and accessed by the public.
    They will have to fill in the details of their auction such as when they want it to start and end, and the particular item that is up for grabs.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''

    current_store = Store.objects.get(pk=pk)
    store_id = current_store.storeid
    store_items = Item.objects.filter(storeid=store_id)
    user = AuthUser.objects.get(id=request.user.id)
    userid = user.id

    form = StartAuctionForm(initial={'auctionstart':datetime.now()})
    form.fields["itemid"].queryset = store_items

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
    '''
    Only a logged-in user has access to this view. 
    This view is where the user can see the details of their profile. They have the option to make a store, access their store (only when they've made one) and edit their profile details.
    The user can also see the auctions they have participated in.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''
    current_user = AuthUser.objects.get(pk=pk)
    bids_by_user = AuctionBid.objects.filter(userid=pk).distinct('auctionid')

    auctions_of_user = Auction.objects.all().distinct('auctionid')
    ids_of_auction = []

    for bid in bids_by_user:
        for auction in auctions_of_user:
            if bid.auctionid == auction:
                ids_of_auction.append(bid.auctionid)
    auctions = Auction.objects.all()

    # ITEMS USER BID ON
    current_date = datetime.now()
    won_itemids = []
    won_auctions = []

    for aucid in ids_of_auction:
        tempAuction = Auction.objects.get(pk=aucid.auctionid)
        auctionend = tempAuction.auctionend

        if auctionend < current_date:
            bids = AuctionBid.objects.filter(auctionid=aucid).order_by('-bidtime')
            highest_bidder = bids[0].userid

            if highest_bidder.id == current_user.id:
                itemid = aucid.itemid
                itemid.sellprice = bids[0].amount
                won_auctions.append(aucid)
                won_itemids.append(itemid)


    current_user = AuthUser.objects.get(pk=pk)
    form = CreateStoreForm(initial={'userid':pk})

    current_store = Store.objects.filter(userid=current_user.id)
    current_storeid = None

    for i in current_store:
        current_storeid = i.storeid

    if request.method == 'POST':
        form = CreateStoreForm(request.POST, initial={'userid':pk})
        if form.is_valid():
            form.save()
            return redirect('profileid', pk=pk)

    context = {
        'displayname': current_user.username,
        'username': current_user.username,
        'user': current_user.id,
        'store': current_storeid,
        'bidsByUser' : bids_by_user,
        'auctions_of_user': auctions_of_user,
        'won_items': won_itemids,
        'won_auctions': won_auctions,
        'auctions': auctions,
        'ids_of_auction': ids_of_auction,
        'createStoreForm': form
    }

    return render(request, "boodlesite/templates/profile.html", context)

@login_required(login_url='login')
def editStore(request, pk):
    '''
    Only a logged-in user has access to this view. 
    This view is a form wherin users [sellers] can edit their store details such as the name of the store and the store description. After successfully saving, the user is redirected to the store page.
    AA user also has access to the other parts of the site from here through the navigation bar.
    '''

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
    '''
    Only a logged-in user has access to this view. 
    This view is a form wherin users [sellers] can edit their profile details. 
    After successfully saving, the user is redirected to their profile page.
    A user also has access to the other parts of the site from here through the navigation bar.
    '''

    user= AuthUser.objects.get(id=pk)
    current_user = user.id
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
