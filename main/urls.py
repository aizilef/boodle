from django.urls import path
from .views import *


urlpatterns = [
    path('', homepage, name='index'),
    path('auction', auction, name='auction'),
    path('auction/<int:pk>/',auction,name='auctionid'),
    path('error404', error404, name='error404'),
    path('store',mystore,name='store'),
    path('additem',addItem,name='additem'),
    path('startauction',startAuction,name='startauction'),

]