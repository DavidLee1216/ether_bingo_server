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
from game.bingo.bingoRoom.models import BingoRoom, BingoRoomAuctionBidHistory, BingoRoomHistory, BingoRoomSetting
from game.models import UserCoin, UserCoinBuyHistory
from user.models import User
from game.views import check_user_coin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['POST'])
@login_required
def buy_ticket(request):
    username = request.data.get("username")
    room_id = request.data.get("room_id")
    game_id = request.data.get("game_id")
    card_infos_string = request.data.get("card_info")
    card_info_len = 324
    if len(card_infos_string) % card_info_len != 0:
        return Response(data='invalid card info', status=status.HTTP_400_BAD_REQUEST)
    card_count = len(card_infos_string) / card_info_len
    card_infos = [card_infos_string[i:i+card_info_len]
                  for i in range(0, card_count, card_info_len)]
    try:
        user = User.objects.get(username=username)
        user_coin = UserCoin.objects.filter(user=user).first()
        if user_coin is None or user_coin.coin == 0:
            user_coin = UserCoin(user=user, coin=0)
            return Response(data="the user doesn't have coins", status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            room = BingoRoom.objects.get(id=room_id)
            if user_coin.coin < room.bingo_price*card_count:
                return Response(data="the user doesn't have enough coins", status=status.HTTP_402_PAYMENT_REQUIRED)
            time = datetime.datetime.utcnow()
            game = BingoGame.objects.filter(
                status='selling', room=room).first()
            if game and game.room == room and game.id == game_id:
                if check_user_coin(user=user, user_coin=user_coin):
                    for card_info in card_infos:
                        numbers = [(int(card_info[i:i+2])
                                    for i in range(0, len(card_info), 2))]
                        match_state = [[True if numbers[j*6+i] == 0 else False for i in range(
                            0, 27)] for j in range(0, 6)]
                        a_bid = BingoBids(game=game, player=user, coin=room.bingo_price,
                                          card_info=numbers, winning_state=False, time=time, match_state=match_state)
                        # a_bid.match_state = numbers
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
def get_bingo_game_general_info(request):
    room_id = request.data.get('room_id')
    try:
        room = BingoRoom.objects.get(id=room_id, hold_on=False)
        owner_history = BingoRoomHistory.objects.filter(
            id=room.owner_room_history_id).first()
        if owner_history:
            owner = owner_history.owner.username
        else:
            owner = ''
        game = BingoGame.objects.filter(
            room=room, live=True).order_by('-id').first()

        data = {'room_id': room.id, 'owner': owner, 'price': room.bingo_price}
        return Response(data=data, status=status.HTTP_200_OK)
    except BingoRoom.DoesNotExist:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def get_bingo_games_info(request):
    arr = []
    games = BingoGame.objects.filter(live=True).order_by('id')
    for game in games:
        room = game.room
        owner_history = BingoRoomHistory.objects.filter(
            id=room.owner_room_history_id).first()
        if owner_history:
            owner = owner_history.owner.username
        else:
            owner = ''
        room_setting = BingoRoomSetting.objects.filter(room=room).first()
        a_data = {'id': room.id, 'owner': owner,
                  'player_count': game.total_cards_count, 'step_type': game.status, 'time_left': room_setting.selling_time-game.elapsed_time, 'price': room.bingo_price}
        arr.append(a_data)
    data = {'data': arr}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@login_required
def get_bingo_game_info(request):  # call it per 0.2s
    room_id = request.data.get('room_id')
    room = BingoRoom.objects.filter(id=room_id, hold_on=False).first()
    owner_history = BingoRoomHistory.objects.filter(
        id=room.owner_room_history_id).first()
    if owner_history:
        owner = owner_history.owner.username
    else:
        owner = ''
    if room is None:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)
    game = BingoGame.objects.filter(room=room, live=True).first()
    if game is None:
        return Response(data='the game does not exist', status=status.HTTP_404_NOT_FOUND)
    game_status = game.status
    if game_status == 'selling':
        bids = BingoBids.objects.filter(game=game)
        arr = []
        for bid in bids:
            a_data = {'username': bid.player.username,
                      'numbers': bid.card_info}
            arr.append(a_data)
        data = {'owner': owner, 'status': game_status, 'data': arr}
        return Response(data=data, status=status.HTTP_200_OK)
    elif game_status == 'calling':
        data = {'owner': owner, 'status': game_status, 'last_number': game.last_number,
                'called_numbers': game.called_numbers}
        return Response(data=data, status=status.HTTP_200_OK)
    elif game_status == 'transition':
        data = {'owner': owner, 'status': game_status}
        return Response(data=data, status=status.HTTP_200_OK)
    else:
        data = {'owner': owner, 'status': 'ended'}
        return Response(data=data, status=status.HTTP_200_OK)
