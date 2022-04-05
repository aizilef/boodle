from django.urls import path
from .views import *


urlpatterns = [
    path('', homepage, name='index'),
    path('auction', auction, name='auction'),
    path('auction/<int:pk>/',auction, name='auctionid'),
    path('error404', error404, name='error404'),
    path('store', tempstore, name='store'), # this is tempstore
    path('store/<int:pk>', mystore, name='storeid'),
    path('additem', addItem, name='additem'),
    path('additem/<int:pk>', addItem, name='additemid'),
    path('startauction', startAuction, name='startauction'),
    # this is tempuser profile
    path('profile', tempProfile, name='profile'),
    path('profile/<int:pk>', profile, name='profileid'),
]