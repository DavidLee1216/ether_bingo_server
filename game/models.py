from tabnanny import verbose
from django.db import models
from user.models import User


class UserProfile(models.Model):  # user profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # user
    country = models.CharField(max_length=200, blank=False)  # country
    city = models.CharField(max_length=200, blank=False)  # city
    birthday = models.DateField(blank=False)  # birthday
    SEX_CHOICES = (('M', 'Male'), ('F', 'Female'))
    sex = models.CharField(max_length=20, blank=False, default='M',
                           choices=SEX_CHOICES)  # sex
    main_wallet = models.CharField(max_length=255, blank=False, default='')

    def __str__(self) -> str:
        return f'user: {self.user}, country: {self.country}, city: {self.city}, birthday: {self.birthday}, sex: {self.sex}, main_wallet: {self.main_wallet}'


class UserCoin(models.Model):  # user coin
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # user
    coin = models.IntegerField(
        blank=True, default=0)  # current coin amount

    def __str__(self) -> str:
        return f'user: {self.user},    coins: {self.coin}'


# current user coin + total consumed amount = total bought amount = coin amount of block
class UserCoinBuyHistory(models.Model):  # user's coin purchase history
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # user
    amount = models.IntegerField(
        blank=False, default=0)  # amount
    date = models.DateTimeField(auto_now=True, blank=False)  # puchase date
    # wallet address used for purchase
    wallet_address = models.CharField(max_length=100, blank=False)

    def __str__(self) -> str:
        return f'user: {self.user}, amount: {self.amount}, date: {self.date}, wallet_address: {self.wallet_address}'


class GameSettings(models.Model):  # game global settings
    key = models.CharField(max_length=255, blank=False)  # key of variable
    value = models.CharField(max_length=255, blank=True)  # value of variable

    def __str__(self) -> str:
        return f'{self.key} = {self.value}'
