from datetime import datetime
from turtle import delay
from django.shortcuts import render
from game.models import UserCoin
from game.tasks import assign_room_ownership
from game.views import check_user_coin

from user.models import User
from .models import BingoRoom, BingoRoomHistory, BingoRoomAuction, BingoRoomAuctionBidHistory
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import send_mail
import datetime


@api_view(['POST'])
def bid(request):
    room_id = request.data.get('room_id')
    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)
        room = BingoRoom.objects.get(id=room_id)
        room_auction = BingoRoomAuction.objects.filter(
            room=room, live=1).first()
        if room_auction:
            last_bid_history = BingoRoomAuctionBidHistory.objects.filter(
                room_auction=room_auction).order_by('-id').first()
            if last_bid_history.bidder == user:
                return Response(data='already applied bid', status=status.HTTP_409_CONFLICT)
            try:
                user_coin = UserCoin.objects.get(user=user)
                if check_user_coin(user=user, user_coin=user_coin):
                    if last_bid_history is None:
                        bid_price = room_auction.start_price
                        bid_id_of_auction = 1
                    else:
                        curr_price = last_bid_history.bid_price
                        bid_price = curr_price + room_auction.price_per_bid
                        bid_id_of_auction = last_bid_history.bid_id_of_auction+1
                    bid_time = datetime.datetime.utcnow()
                    bid = BingoRoomAuctionBidHistory(
                        room_auction=room_auction, bidder=user, bid_id_of_auction=bid_id_of_auction, bid_price=bid_price, bid_time=bid_time, win_state=False)
                    bid.save()
                    user_coin.coin -= room_auction.coin_per_bid
                    user_coin.save()
                    return Response(data='success', status=status.HTTP_200_OK)
                else:
                    return Response(data='coin checksum is not correct. abnormal action detected', status=status.HTTP_403_FORBIDDEN)
            except UserCoin.DoesNotExist:
                return Response(data='the user coin does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response(data='the auction does not exist', status=status.HTTP_404_NOT_FOUND)
    except BingoRoom.DoesNotExist:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(data='the user does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def get_room_auction_user_info(request):
    room_id = request.data.get('room_id')
    last_id = request.data.get('last_id')
    try:
        room = BingoRoom.objects.get(id=room_id)
        room_auction = BingoRoomAuction.objects.filter(
            room=room, live=True).order_by('-id').first()
        total_bids = BingoRoomAuctionBidHistory.objects.filter(
            room_auction=room_auction, bid_id_of_auction__gt=last_id)
        if total_bids:
            arr = []
            win_bid = None
            for bid in total_bids:
                a_data = {'bid_id_of_auction': bid.bid_id_of_auction, 'username': bid.bidder.username,
                          'bid_price': bid.bid_price, 'bid_time': bid.bid_time}
                arr.append(a_data)
                if bid.win_state == True:
                    win_bid = bid
            data = {'data': arr, 'winner': None}
            if win_bid is not None:
                data.winner = {'username': win_bid.bidder.username,
                               'bid_price': win_bid.bid_price}
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data='success', status=status.HTTP_204_NO_CONTENT)
    except BingoRoom.DoesNotExist:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def pay_for_winner(request):
    username = request.data.get('username')
    room_id = request.data.get('room_id')
    amount_to_pay = request.data.get('amount')
    try:
        user = User.objects.get(username=username)
        winned_bingo_bid = BingoRoomAuctionBidHistory.objects.filter(
            bidder=user, win_state=True, paid_state=0)
        if winned_bingo_bid:
            auction = winned_bingo_bid.room_auction
            auction.live = False
            room_history = assign_room_ownership(
                username, room_id, amount_to_pay, winned_bingo_bid.room_auction)
            data = {'from': room_history.from_date, 'to': room_history.to_date}
            return Response(data=data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(data='the user does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def arrange_room_auctions(request):
    data = []
    room_auctions = BingoRoomAuction.objects.filter(live=True, winner=None)
    for auction in room_auctions:
        last_bid = BingoRoomAuctionBidHistory.objects.filter(
            room_auction=auction).order_by('-id').first()
        auction_data = {'room_id': auction.room.id, 'last_bid_id': last_bid.bid_id_of_auction,
                        'username': last_bid.bidder.username, 'bid_price': last_bid.bid_price, 'elapsed_time': auction.last_bid_elapsed_time}
        data.append(auction_data)
    return Response(data=data, status=status.HTTP_200_OK)
