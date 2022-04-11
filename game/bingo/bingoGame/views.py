import datetime
from xmlrpc.client import DateTime
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .models import BingoGame, BingoBids, BingoGameStatus
from .serializer import BingoGameSerializer, BingoBidsSerializer
from game.bingo.bingoRoom.models import BingoRoom, BingoRoomAuctionBidHistory
from game.models import UserCoin, UserCoinBuyHistory
from user.models import User
from game.views import check_user_coin


@api_view(['POST'])
@login_required
def buy_ticket(request):
    username = request.data.get("username")
    room_id = request.data.get("room_id")
    game_id = request.data.get("game_id")
    card_infos_string = request.data.get("card_info")
    card_info_len = 180
    if len(card_infos_string) % 180 != 0:
        return Response(data='invalid card info', status=status.HTTP_400_BAD_REQUEST)
    card_count = len(card_infos_string) / 180
    card_infos = [card_infos_string[i:i+180]
                  for i in range(0, card_count, card_info_len)]
    try:
        user = User.objects.get(username=username)
        user_coin = UserCoin.objects.filter(user=user).first()
        if user_coin is None or user_coin.coin == 0:
            user_coin = UserCoin(user=user, coin=0)
            return Response(data="the user doesn't have coins", status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            room = BingoRoom.objects.get(id=room_id, live=True)
            if user_coin.coin < room.bingo_price*card_count:
                return Response(data="the user doesn't have enough coins", status=status.HTTP_402_PAYMENT_REQUIRED)
            time = datetime.datetime.utcnow()
            game = BingoGame.objects.filter(
                status='selling', room=room).first()
            if game and game.room == room and game.id == game_id:
                if check_user_coin(user=user, user_coin=user_coin):
                    for card_info in card_infos:
                        a_bid = BingoBids(game=game, player=user, coin=room.bingo_price,
                                          card_info=card_info, winning_state=False, date=time)
                        a_bid.save()
                    user_coin.coin -= room.bingo_price*card_count
                    user_coin.save()
                    game.total_cards += card_count
                    game.save()
                    return Response(data="success", status=status.HTTP_200_OK)
                else:
                    return Response(data='coin checksum is not correct. abnormal action detected', status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(data="the game does not exist", status=status.HTTP_404_NOT_FOUND)
        except BingoRoom.DoesNotExist:
            return Response(data='bingo room does not exist', status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(data="user does not exist", status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def get_bingo_game_user_info(request):
    room_id = request.data.get('room_id')
    try:
        room = BingoRoom.objects.get(id=room_id, live=True)
        game = BingoGame.objects.filter(
            room=room, live=True).order_by('-id').first()
        arr = []
        total_bids = BingoBids.objects.filter(game=game)
        for bid in total_bids:
            a_data = {'username': bid.user.username,
                      'card_info': bid.card_info, 'time': bid.date}
            arr.append(a_data)
        data = {'data': arr}
        return Response(data=data, status=status.HTTP_200_OK)
    except BingoRoom.DoesNotExist:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)
