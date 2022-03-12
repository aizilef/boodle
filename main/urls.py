from django.urls import path
from .views import *


urlpatterns = [
    path('', homepage, name='index'),
    path('auction', auction, name='auction'),
    path('auction/<int:pk>/',auction,name='auctionid'),
]