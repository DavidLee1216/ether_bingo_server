from django.db import models
from django.utils import timezone
from game.bingo.bingoRoom.models import BingoRoom
from user.models import User
from django.contrib.postgres.fields import ArrayField

# bingo game status;  'holdon', 'selling', 'transition', 'calling', 'ended'


class BingoGameStatus(models.Model):
    status = models.CharField(max_length=50, null=False)


class BingoGame(models.Model):  # one bingo game
    room = models.ForeignKey(BingoRoom, on_delete=models.CASCADE)  # room
    called_numbers = models.CharField(
        max_length=200, blank=False, default='')  # called numbers
    last_number = models.IntegerField(
        blank=True, default=0)  # last number
    start_time = models.DateTimeField(blank=False)  # start date time
    end_time = models.DateTimeField(blank=False)  # end date time
    elapsed_time = models.IntegerField(blank=False, default=0)  # seconds
    total_cards_count = models.IntegerField(
        blank=False, default=0)  # total attendees count
    winner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, default=None)  # winner
    GAME_STATUS = [('S', 'selling'), ('C', 'calling'),
                   ('T', 'transition'), ('E', 'ended')]
    status = models.CharField(
        max_length=50, null=False, choices=GAME_STATUS, default='S')  # bingo game status
    live = models.BooleanField(blank=False, default=False)


class BingoBids(models.Model):  # one bid for bingo game
    game = models.ForeignKey(
        BingoGame, on_delete=models.CASCADE)  # bingo game
    player = models.ForeignKey(User, on_delete=models.CASCADE)  # bidder
    coin = models.IntegerField(blank=False)
    card_info = ArrayField(models.IntegerField(
        default=0), size=162)  # card panel info
    time = models.DateTimeField(blank=False)
    winning_state = models.BooleanField(
        blank=False, default=False)  # win or lose
    default_match_state_row = [False]*27
    match_state = ArrayField(ArrayField(
        models.BooleanField(default=False), size=27), size=6, default=None)  # match state with called numbers
