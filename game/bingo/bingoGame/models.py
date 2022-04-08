from django.db import models
from django.utils import timezone
from game.bingo.bingoRoom.models import BingoRoom
from user.models import User


class BingoGame(models.Model):  # one bingo game
    room = models.OneToOneField(BingoRoom, on_delete=models.CASCADE)  # room
    called_numbers = models.CharField(
        max_length=200, blank=False, default='')  # called numbers
    last_number = models.IntegerField(
        blank=True, default=0)  # last number
    start_date = models.DateTimeField(blank=False)  # start date time
    end_date = models.DateTimeField(blank=False)  # end date time
    total_attendees = models.IntegerField(
        blank=False)  # total attendees count
    winner = models.OneToOneField(User, on_delete=models.CASCADE)  # winner


class BingoBids(models.Model):  # one bid for bingo game
    game = models.OneToOneField(
        BingoGame, on_delete=models.CASCADE)  # bingo game
    player = models.OneToOneField(User, on_delete=models.CASCADE)  # bidder
    coin = models.IntegerField(blank=False)
    card_info = models.CharField(
        max_length=200, blank=False, default='')  # card panel info
    winning_state = models.BooleanField(
        blank=False, default=False)  # win or lose
