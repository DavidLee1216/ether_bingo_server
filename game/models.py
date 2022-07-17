from tabnanny import verbose
from django.db import models
from game.bingo.bingoGame.models import BingoGame
from user.models import User


class UserProfile(models.Model):  # user profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # user
    country = models.CharField(max_length=200, blank=False)  # country
    city = models.CharField(max_length=200, blank=False)  # city
    SEX_CHOICES = (('M', 'Male'), ('F', 'Female'))
    sex = models.CharField(max_length=20, blank=False, default='M',
                           choices=SEX_CHOICES)  # sex
    main_wallet = models.CharField(max_length=255, blank=False, default='')
    earning_verified = models.BooleanField(default=False, blank=False)

    def __str__(self) -> str:
        return f'username: {self.user.username}, country: {self.country}, city: {self.city}, sex: {self.sex}, main_wallet: {self.main_wallet}, earning_verified: {self.earning_verified}'


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


class UserEarnings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_id = models.IntegerField(blank=False, default=0)
    GAME_KIND = [('B', 'bingo'), ]
    game_kind = models.CharField(
        max_length=255, choices=GAME_KIND, blank=False, default='B')
    is_owner = models.BooleanField(default=False, blank=False)
    earning = models.DecimalField(
        max_digits=8, decimal_places=5, default=0, blank=False)
    verified = models.BooleanField(default=False, blank=False)
    withdrawn = models.BooleanField(default=False, blank=False)

    def __str__(self) -> str:
        return f'user: {self.user}, game_id: {self.game_id}, game_kind: {self.game_kind}, is_owner: {self.is_owner}, earning: {self.earning}, verified: {self.verified}, withdrawn: {self.withdrawn}'


class WithdrawHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(blank=False)
    amount = models.DecimalField(
        max_digits=8, decimal_places=5, default=0, blank=False)

    def __str__(self) -> str:
        return f'user: {self.user}, time: {self.time}, amount: {self.amount}'


class GameSettings(models.Model):  # game global settings
    key = models.CharField(max_length=255, blank=False)  # key of variable
    value = models.CharField(max_length=255, blank=True)  # value of variable

    def __str__(self) -> str:
        return f'{self.key} = {self.value}'


class UserContactUs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.DateTimeField(blank=False)
    content = models.TextField(default='', max_length=50000, blank=False)

    def __str__(self) -> str:
        return f'user: {self.user}, time: {self.time}, content: {self.content}'
