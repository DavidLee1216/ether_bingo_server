import datetime
from xmlrpc.client import DateTime
from django.db import connection
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
from game.bingo.bingoRoom.models import BingoRoom, BingoRoomAuction, BingoRoomAuctionBidHistory, BingoRoomHistory, BingoRoomSetting
from game.models import UserCoin, UserCoinBuyHistory
from user.models import User
from game.views import check_user_coin
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
import random
import pytz
from django.db.models import Q


@api_view(['POST'])
@login_required
def buy_ticket(request):
    username = request.data.get("username")
    room_id = request.data.get("room_id")
    card_infos_string = request.data.get("card_info")
    card_info_len = 324
    if len(card_infos_string) % card_info_len != 0:
        return Response(data='invalid card info', status=status.HTTP_400_BAD_REQUEST)
    card_count = int(len(card_infos_string) / card_info_len)
    card_infos = [card_infos_string[i*card_info_len:i*card_info_len+card_info_len]
                  for i in range(0, card_count)]
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
            if game:
                if check_user_coin(user=user, user_coin=user_coin):
                    for card_info in card_infos:
                        numbers = [int(card_info[i:i+2])
                                   for i in range(0, len(card_info), 2)]
                        match_state = [[True if numbers[j*27+i] == 0 else False for i in range(
                            0, 27)] for j in range(0, 6)]
                        a_bid = BingoBids(game=game, player=user, coin=room.bingo_price,
                                          card_info=numbers, winning_state=False, time=time, match_state=match_state)
                        # a_bid.match_state = numbers
                        a_bid.save()
                    user_coin.coin -= room.bingo_price*card_count
                    user_coin.save()
                    game.total_cards_count += card_count
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
    games = BingoGame.objects.filter(live=True).order_by('room')
    for game in games:
        room = game.room
        owner_history = BingoRoomHistory.objects.filter(
            id=room.owner_room_history_id).first()
        if owner_history:
            owner = owner_history.owner.username
        else:
            owner = ''
        # cursor = connection.cursor()
    # bids = BingoBids.objects.raw(
    #         f"SELECT id, COUNT(DISTINCT player_id) as count FROM game_bingobids WHERE game_id={game.id}")
        # bids = BingoBids.objects.aggregate(Count('player_id'), distinct=True)
        player_count = BingoBids.objects.filter(game=game).values(
            'player_id').distinct().count()
        room_setting = BingoRoomSetting.objects.filter(room=room).first()
        a_data = {'id': room.id, 'owner': owner,
                  'player_count': player_count, 'card_count': game.total_cards_count, 'step_type': game.status, 'time_left': room_setting.selling_time-game.elapsed_time, 'price': room.bingo_price}
        arr.append(a_data)
    data = {'data': arr}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@login_required
def get_bingo_game_player_info(request):
    def checkInUserArray(username):
        nonlocal arr
        for a_arr in arr:
            if a_arr['username'] == username:
                return True
        return False
    room_id = request.data.get('room_id')
    room = BingoRoom.objects.filter(id=room_id, hold_on=False).first()
    if room is None:
        return Response(data="the room does not exist", status=status.HTTP_404_NOT_FOUND)
    game = BingoGame.objects.filter(room=room, live=True).first()
    if game is None:
        return Response(data='the game does not exist', status=status.HTTP_404_NOT_FOUND)
    bids = BingoBids.objects.filter(game=game).order_by('-id')
    arr = []
    for bid in bids:
        if checkInUserArray(bid.player.username) == False:
            player_bids = BingoBids.objects.filter(
                game=game, player=bid.player)
            player_bid_count = len(player_bids)
            a_data = {'username': bid.player.username,
                      'count': player_bid_count}
            arr.append(a_data)
    data = {'data': arr}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@login_required
def get_bingo_game_info(request):  # call it per 0.2s
    def checkInUserArray(username):
        nonlocal arr
        for a_arr in arr:
            if a_arr['username'] == username:
                return True
        return False
    try:
        room_id = request.data.get('room_id')
        room = BingoRoom.objects.filter(id=room_id, hold_on=False).first()
        if room is None:
            return Response(data="the room does not exist", status=status.HTTP_404_NOT_FOUND)
        room_setting = BingoRoomSetting.objects.filter(room=room).first()
        owner_history = BingoRoomHistory.objects.filter(
            id=room.owner_room_history_id).first()
        if owner_history:
            owner = owner_history.owner.username
        else:
            owner = ''
        game = BingoGame.objects.filter(room=room, live=True).first()
        if game is None:
            return Response(data='the game does not exist', status=status.HTTP_404_NOT_FOUND)
        game_status = game.status
        if game_status == 'selling':
            bids = BingoBids.objects.filter(game=game).order_by('-id')
            arr = []
            for bid in bids:
                if checkInUserArray(bid.player.username) == False:
                    player_bids = BingoBids.objects.filter(
                        game=game, player=bid.player)
                    player_bid_count = len(player_bids)
                    a_data = {'username': bid.player.username,
                              'count': player_bid_count}
                    arr.append(a_data)
            data = {'owner': owner, 'status': game_status,
                    'time_left': room_setting.selling_time-game.elapsed_time, 'data': arr}
            return Response(data=data, status=status.HTTP_200_OK)
        elif game_status == 'calling':
            data = {'owner': owner, 'status': game_status, 'last_number': game.last_number,
                    'called_numbers': game.called_numbers}
            return Response(data=data, status=status.HTTP_200_OK)
        elif game_status == 'transition':
            data = {'owner': owner, 'status': game_status}
            return Response(data=data, status=status.HTTP_200_OK)
        else:  # ended
            winned_bids = BingoBids.objects.filter(
                game=game, winning_state=True)
            arr = []
            for bid in winned_bids:
                a_data = {'username': bid.player.username,
                          'card_info': bid.card_info}
                arr.append(a_data)
            data = {'owner': owner, 'status': 'ended', 'last_number': game.last_number,
                    'called_numbers': game.called_numbers, 'winners': arr}
            return Response(data=data, status=status.HTTP_200_OK)
    except BingoRoom.DoesNotExist:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def get_my_bingo_tickets(request):
    room_id = request.data.get('room_id')
    username = request.data.get('username')
    room = BingoRoom.objects.filter(id=room_id, hold_on=False).first()
    game = BingoGame.objects.filter(room=room, live=True).first()
    try:
        user = User.objects.get(username=username)
        bids = BingoBids.objects.filter(game=game, player=user).order_by('id')
        arr = []
        for bid in bids:
            a_data = {'numbers': bid.card_info}
            arr.append(a_data)
        data = {'data': arr}
        return Response(data=data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(data="user does not exist", status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def get_bingo_tickets(request):
    cursor = connection.cursor()
    card_ids = []
    card_cnt = 0
    card_cnt_limit = 10
    card_id_start = 1
    card_id_end = 411180
    while card_cnt <= card_cnt_limit:
        id = random.randint(card_id_start, card_id_end)
        while id in card_ids:
            id = random.randint(card_id_start, card_id_end)
        card_ids.append(str(id))
        card_cnt += 1
    arr_str = '(' + ','.join(card_ids) + ')'
    query = f"SELECT numbers FROM panels where card_id IN {arr_str}"
    cursor.execute(query)
    rows = cursor.fetchall()
    tickets = [row[0] for row in rows]
    data = {'data': tickets}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@login_required
def get_bingo_room_winner_history(request):
    room_id = request.data.get('room_id')
    try:
        room = BingoRoom.objects.get(id=room_id, hold_on=False)
        now = datetime.datetime.utcnow()
        from_date = now - datetime.timedelta(hours=24)
        to_date = now
        games = BingoGame.objects.filter(
            room=room, live=False, end_time__gte=from_date, end_time__lte=to_date).order_by('-id')
        arr = []
        for game in games:
            winner_bids = BingoBids.objects.filter(
                game=game, winning_state=True)
            for bid in winner_bids:
                a_data = {'username': bid.player.username,
                          'earning': bid.earning, 'time': game.end_time}
                arr.append(a_data)
        data = {'data': arr}
        return Response(data=data, status=status.HTTP_200_OK)
    except BingoRoom.DoesNotExist:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((AllowAny,))
def get_bingo_winner_history(request):
    from_time = request.data.get('from_time')
    if from_time != '' and from_time != None:
        from_date = datetime.datetime.strptime(
            from_time, '%Y-%m-%d %H:%M:%S.%f')
        from_date = pytz.utc.localize(from_date)

    else:
        from_date = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        from_date = pytz.utc.localize(from_date)

    games = BingoGame.objects.filter(
        live=False, end_time__gte=from_date).order_by('-id')
    arr = []
    for game in games:
        winner_bids = BingoBids.objects.filter(game=game, winning_state=True)
        for bid in winner_bids:
            a_data = {'kind': 'bingo', 'username': bid.player.username,
                      'earning': bid.earning, 'room': bid.game.room.id, 'time': game.end_time}
            arr.append(a_data)
    auctions = BingoRoomAuction.objects.filter(
        ~Q(winner=None), end_date__gte=from_date)
    for auction in auctions:
        a_data = {'kind': 'room_won', 'username': auction.winner.username,
                  'earning': 0, 'room': auction.room.id, 'time': auction.end_date}
        arr.append(a_data)
    auctions = BingoRoomAuction.objects.filter(
        ~Q(winner=None), pay_date__gte=from_date)
    for auction in auctions:
        a_data = {'kind': 'room_pay', 'username': auction.winner.username,
                  'earning': 0, 'room': auction.room.id, 'time': auction.pay_date}
        arr.append(a_data)
    arr.sort(key=lambda x: x['time'], reverse=True)
    data = {'data': arr}
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def get_room_owner_earning(request):
    room_id = request.data.get('room_id')
    try:
        room = BingoRoom.objects.get(id=room_id, hold_on=False)
        owner_history = BingoRoomHistory.objects.filter(
            id=room.owner_room_history_id).first()
        if owner_history:
            owner = owner_history.owner.username
        else:
            return Response(data='no owner', status=status.HTTP_204_NO_CONTENT)
        games = BingoGame.objects.filter(
            end_time__gte=owner_history.from_date, end_time__lt=owner_history.to_date, live=False)
        total_earning = 0
        for game in games:
            earning = game.total_cards_count*room.bingo_price*0.001*0.1
            total_earning += earning
        curr_time = datetime.datetime.utcnow()
        curr_time_timezone_aware = pytz.utc.localize(curr_time)
        period = str(curr_time_timezone_aware -
                     owner_history.from_date).split('.', 2)[0]  # time delta
        data = {'earning': str(total_earning), 'period': period}
        return Response(data=data, status=status.HTTP_200_OK)

    except BingoRoom.DoesNotExist:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)
