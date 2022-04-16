from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from user.models import User


class BingoRoom(models.Model):  # room information
    id = models.IntegerField(
        primary_key=True, unique=True)  # room number
    bingo_price = models.IntegerField(blank=False)  # bingo price in coin
    hold_on = models.BooleanField(default=True)  # room is enalble or disable


class BingoRoomSetting(models.Model):
    room = models.OneToOneField(BingoRoom, on_delete=models.CASCADE)
    min_attendee_count = models.IntegerField(default=10)
    selling_time = models.IntegerField(default=600, verbose_name='ticket selling time(s)', validators=[
        MaxValueValidator(1800),
        MinValueValidator(180)
    ])
    calling_time = models.IntegerField(default=10, verbose_name='number calling time(s)', validators=[
                                       MaxValueValidator(60), MinValueValidator(5)])
    auction_start_price = models.DecimalField(
        max_digits=8, decimal_places=5, blank=True)  # bingo room auction start price
    auction_price_interval_per_bid = models.DecimalField(
        max_digits=8, decimal_places=5, blank=False)
    auction_coin_per_bid = models.IntegerField(default=10)
    auction_win_time_limit = models.IntegerField(default=3600)  # second


class BingoRoomAuction(models.Model):  # room auction
    room = models.ForeignKey(
        BingoRoom, on_delete=models.CASCADE)  # room number
    start_date = models.DateTimeField(
        null=False, blank=False)  # auction start date time
    end_date = models.DateTimeField(
        null=True, default=None)  # auction end date time
    start_price = models.DecimalField(
        max_digits=8, decimal_places=5, blank=False)  # start price of the auction
    coin_per_bid = models.IntegerField(
        blank=False)  # coin per one bid
    price_per_bid = models.DecimalField(
        max_digits=8, decimal_places=5, blank=False)  # price per bid
    winner = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, default=None)  # final winner of the auction
    # whether the auction is live or not
    live = models.BooleanField(blank=False)  # auction is live or not
    # time in second until bidder wins
    time_limit = models.IntegerField(default=3600)
    last_bid_elapsed_time = models.IntegerField(
        default=0)  # time after last bid


class BingoRoomAuctionBidHistory(models.Model):  # room auction bid history
    id = models.IntegerField(blank=False, primary_key=True)
    room_auction = models.ForeignKey(
        BingoRoomAuction, on_delete=models.CASCADE)  # room auction info
    bidder = models.ForeignKey(User, on_delete=models.DO_NOTHING)  # bidder
    bid_id_of_auction = models.IntegerField(
        blank=False)  # the order of bid of the auction
    bid_price = models.DecimalField(
        max_digits=8, decimal_places=5, blank=False)  # bid price of the bidder
    bid_time = models.DateTimeField(blank=False)
    win_state = models.BooleanField(blank=False)  # winning state of the bidder


# room ownership history, it must be registered after pay
class BingoRoomHistory(models.Model):
    room = models.ForeignKey(
        BingoRoom, on_delete=models.DO_NOTHING, blank=False)  # room number
    auction = models.ForeignKey(
        BingoRoomAuction, on_delete=models.DO_NOTHING, default=None)  # auction the owner won
    owner = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, null=True, default=None)  # room owner
    paid_eth = models.DecimalField(
        max_digits=8, decimal_places=5, blank=True)  # price the owner paid
    # date time started the ownership
    from_date = models.DateTimeField(blank=False)
    to_date = models.DateTimeField(null=True)  # date time ended the ownership
    # BingoRoomAuctionBidHistory id for checksum  # for system, it is null
    winned_bid = models.ForeignKey(
        BingoRoomAuctionBidHistory, on_delete=models.DO_NOTHING, default=None)
    # room ownership is available or not
    live = models.BooleanField(default=False)
