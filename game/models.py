from django.db import models
from user.models import User


class HistoryKind(models.Model):  # kind (ex. bingoroom auction, bingo game bid)
    kind = models.CharField(max_length=10, blank=False)


class UserProfile(models.Model):  # user profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # user
    country = models.CharField(max_length=200, blank=False)  # country
    city = models.CharField(max_length=200, blank=False)  # city
    birthday = models.DateField(blank=False)  # birthday
    sex = models.CharField(max_length=20, blank=False)  # sex


class UserCoin(models.Model):  # user coin
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # user
    coin = models.IntegerField(
        blank=True, default=0)  # current coin amount


# current user coin + total consumed amount = total bought amount = coin amount of block
class UserCoinBuyHistory(models.Model):  # user's coin purchase history
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # user
    amount = models.IntegerField(
        blank=False, default=0)  # amount
    date = models.DateTimeField(blank=False)  # puchase date
    # wallet address used for purchase
    wallet_address = models.CharField(max_length=100, blank=False)


class UserCoinConsumeHistory(models.Model):  # user's coin consume history
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # user
    amount = models.IntegerField(
        blank=False, default=0)  # amount
    kind = models.OneToOneField(
        HistoryKind, null=True, on_delete=models.SET_NULL)  # kind
    date = models.DateTimeField(blank=False)  # date time
    # id of history table according to consume kind
    consume_history_id = models.IntegerField(blank=False, default=0)
