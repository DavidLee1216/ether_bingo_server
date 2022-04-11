from django.db import models
from django.utils import timezone
from user.models import User


class BingoRoom(models.Model):  # room information
    id = models.IntegerField(
        primary_key=True, unique=True)  # room number
    bingo_price = models.IntegerField(blank=False)  # bingo price in coin
    auction_start_price = models.DecimalField(
        max_digits=8, decimal_places=5, blank=True)  # bingo room auction start price
    owner = models.OneToOneField(
        to=User, on_delete=models.CASCADE, null=True)  # room owner
    from_date = models.DateTimeField(blank=False)  # ownership start date time
    # date time expiring the ownership of the owner
    to_date = models.DateTimeField(null=True)
    winned_bid = models.IntegerField(
        null=True)  # BingoRoomAuctionBidHistory id for checksum  # for system, it is null


class BingoRoomHistory(models.Model):  # room ownership history
    room = models.OneToOneField(
        BingoRoom, on_delete=models.CASCADE, blank=False)  # room number
    owner = models.OneToOneField(User, on_delete=models.CASCADE)  # room owner
    paid_eth = models.DecimalField(
        max_digits=8, decimal_places=5, blank=True)  # price the owner paid
    # date time started the ownership
    from_date = models.DateTimeField(blank=False)
    to_date = models.DateTimeField(null=True)  # date time ended the ownership


class BingoRoomAuction(models.Model):  # room auction
    room = models.OneToOneField(
        BingoRoom, on_delete=models.CASCADE)  # room number
    # cumulated id of the order of the room auction(ex. first of 1st room, second of 1st room)
    room_auction_id = models.IntegerField(blank=False)
    start_date = models.DateTimeField(
        null=False, blank=False)  # auction start date time
    end_date = models.DateTimeField(null=True)  # auction end date time
    start_price = models.DecimalField(
        max_digits=8, decimal_places=5, blank=False)  # start price of the auction
    coin_per_bid = models.IntegerField(
        blank=False)  # coin per one bid
    price_per_bid = models.DecimalField(
        max_digits=8, decimal_places=5, blank=False)  # price per bid
    winner = models.OneToOneField(
        User, on_delete=models.DO_NOTHING)  # final winner of the auction
    # whether the auction is live or not
    live = models.BooleanField(blank=False)


class BingoRoomAuctionBidHistory(models.Model):  # room auction bid history
    id = models.IntegerField(blank=False, primary_key=True)
    room_auction = models.OneToOneField(
        BingoRoomAuction, on_delete=models.CASCADE)  # room auction info
    bidder = models.OneToOneField(User, on_delete=models.DO_NOTHING)  # bidder
    bid_id_of_auction = models.IntegerField(
        blank=False)  # the order of bid of the auction
    bid_price = models.DecimalField(
        max_digits=8, decimal_places=5, blank=False)  # bid price of the bidder
    bid_time = models.DateTimeField(blank=False)
    win_state = models.BooleanField(blank=False)  # winning state of the bidder
