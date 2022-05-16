from django.urls import path
from .views import *

from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('', homepage, name='index'),
    path('auction', auction, name='auction'),
    path('auction/<int:pk>/',auction, name='auctionid'),
    path('error404', error404, name='error404'),
    path('store', tempstore, name='store'), # this is tempstore
    path('store/<int:pk>', mystore, name='storeid'),
    path('additem', addItem, name='additem'),
    path('additem/<int:pk>', addItem, name='additemid'),
    path('edititem/<int:pk>', editItem, name='edititemid'),
    path('jsi18n', JavaScriptCatalog.as_view(), name='js-catlog'),
    path('startauction', startAuction, name='startauction'),
    path('startauction/<int:pk>', startAuction, name='startauctionid'),
    # this is tempuser profile
    path('profile', tempProfile, name='profile'),
    path('profile/<int:pk>', profile, name='profileid'),
    path('editstore/<int:pk>', editStore, name='editstoreid'),
    path('editProfile/<int:pk>', editProfile, name='editProfile'),
    path('login', loginPage, name='login'),
    path('register', registerPage, name='register'),
    path('logout', logoutUser, name='logout')
]