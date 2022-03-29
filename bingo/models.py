from tkinter import CASCADE
from django.db import models
from user.models import User


class BingoRoom(models.Model):
    room_number = models.IntegerField(unique=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return super().__str__()
