from django.urls import path
from .views import *

from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('', homepage, name='index'),
    path('auction', auction, name='auction'),
    path('auction/<int:pk>/',auction, name='auctionid'),
    path('future_auction_error404', future_auction_error404, name='future_auction_error404'),
    path('passed_auction_error404', passed_auction_error404, name='passed_auction_error404'),
    path('store/<int:pk>', mystore, name='storeid'),
    path('additem', addItem, name='additem'),
    path('additem/<int:pk>', addItem, name='additemid'),
    path('edititem/<int:pk>', editItem, name='edititemid'),
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),
    path('startauction', startAuction, name='startauction'),
    path('startauction/<int:pk>', startAuction, name='startauctionid'),
    path('profile/<int:pk>', profile, name='profileid'),
    path('editstore/<int:pk>', editStore, name='editstoreid'),
    path('editProfile/<int:pk>', editProfile, name='editProfile'),
    path('login', loginPage, name='login'),
    path('register', registerPage, name='register'),
    path('logout', logoutUser, name='logout'),
    path('help', help, name='help'),
    path('about', about, name='about')
]