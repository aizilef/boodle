# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Item(models.Model):
    itemid = models.AutoField(primary_key=True)
    itemname = models.CharField(max_length=255)
    itemspecs = models.CharField(max_length=700)
    floorprice = models.FloatField()
    sellprice = models.FloatField()
    class Meta:
        managed = False
        db_table = 'item'

class Auction(models.Model):
    auctionid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    info = models.CharField(max_length=255)
    auctionstart = models.DateTimeField()
    auctionend = models.DateTimeField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        managed = False
        db_table = 'auction'


class AuctionBid(models.Model):
    bidno = models.AutoField(primary_key=True)
    amount = models.FloatField()
    bidtime = models.DateTimeField()
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    class Meta:
        managed = False
        db_table = 'auction_bid'