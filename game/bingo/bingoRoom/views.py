from datetime import datetime
from game.models import UserCoin
from game.tasks import assign_room_ownership
from game.views import check_user_coin
from user.models import User
from .models import BingoRoom, BingoRoomHistory, BingoRoomAuction, BingoRoomAuctionBidHistory, BingoRoomSetting
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import datetime
from rest_framework.permissions import IsAuthenticated, AllowAny
from game.etherfunc import check_room_ownership
import pytz


@api_view(['POST'])
@login_required
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
            if last_bid_history and last_bid_history.bidder == user:
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
                    room_auction.last_bid_elapsed_time = 0
                    room_auction.save()
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
        if room_auction:
            total_bids = BingoRoomAuctionBidHistory.objects.filter(
                room_auction=room_auction, bid_id_of_auction__gt=last_id).order_by('id')
            if total_bids:
                arr = []
                win_bid = None
                for bid in total_bids:
                    a_data = {'bid_id_of_auction': bid.bid_id_of_auction, 'username': bid.bidder.username,
                              'bid_price': bid.bid_price, 'bid_time': bid.bid_time}
                    arr.append(a_data)
                    if bid.win_state == True:
                        win_bid = bid
                data = {'data': arr, 'winner': None,
                        'elapsed_time': room_auction.last_bid_elapsed_time}
                if win_bid is not None:
                    data['winner'] = {'username': win_bid.bidder.username,
                                      'bid_price': win_bid.bid_price}
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                win_bid = BingoRoomAuctionBidHistory.objects.filter(
                    room_auction=room_auction, win_state=True).first()
                data = {'data': [], 'winner': None,
                        'elapsed_time': room_auction.last_bid_elapsed_time}
                if win_bid:
                    data['winner'] = {
                        'username': win_bid.bidder.username, 'bid_price': win_bid.bid_price}
                return Response(data=data, status=status.HTTP_200_OK)
        else:
            return Response(data='the auction does not exist', status=status.HTTP_404_NOT_FOUND)
    except BingoRoom.DoesNotExist:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def get_room_setting(request):
    room_id = request.data.get('room_id')
    try:
        room = BingoRoom.objects.get(id=room_id)
        room_setting = BingoRoomSetting.objects.get(room=room)
        room_history = BingoRoomHistory.objects.filter(
            room=room, live=True).first()
        if room_history:
            owner = room_history.owner.username
            ownership_deadtime = room_history.to_date
        else:
            owner = None
            ownership_deadtime = None
        data = {'bingo_price': room.bingo_price,
                'min_attendee_count': room_setting.min_attendee_count, 'selling_time': room_setting.selling_time, 'auction_start_price': room_setting.auction_start_price, 'auction_price_interval_per_bid': room_setting.auction_price_interval_per_bid, 'auction_coin_per_bid': room_setting.auction_coin_per_bid, 'auction_win_time_limit': room_setting.auction_win_time_limit, 'curr_owner': owner, 'ownership_deadtime': ownership_deadtime}
        return Response(data=data, status=status.HTTP_200_OK)
    except BingoRoom.DoesNotExist:
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)
    except BingoRoomSetting.DoesNotExist:
        return Response(data='the setting does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def pay_for_winner(request):
    username = request.data.get('username')
    room_id = request.data.get('room_id')
    amount_to_pay = request.data.get('amount')
    try:
        user = User.objects.get(username=username)
        room = BingoRoom.objects.filter(id=room_id).first()
        winned_bingo_bids = BingoRoomAuctionBidHistory.objects.filter(
            bidder=user, win_state=True, paid_state=0)
        winned_bingo_bid = next(
            filter(lambda x: x.room_auction.room.id == room_id, winned_bingo_bids), None)
        if winned_bingo_bid:
            room_history = BingoRoomHistory.objects.filter(
                room=room, owner=user, auction=winned_bingo_bid.room_auction).first()
            from_time = int(round(room_history.from_date.timestamp()))
            to_time = int(round(room_history.to_date.timestamp()))
            res = check_room_ownership(user.id, room_id, from_time, to_time)
            if res:
                winned_bingo_bid.paid_state = 1
                winned_bingo_bid.save()
                return Response(data='Successfully done', status=status.HTTP_200_OK)
            else:
                return Response(data='contract check failed', status=status.HTTP_402_PAYMENT_REQUIRED)
        return Response(data='the winneed bid does not exist', status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(data='the user does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def assign_ownership(request):
    username = request.data.get('username')
    room_id = request.data.get('room_id')
    amount_to_pay = request.data.get('amount')
    try:
        user = User.objects.get(username=username)
        winned_bingo_bids = BingoRoomAuctionBidHistory.objects.filter(
            bidder=user, win_state=True, paid_state=0)
        winned_bingo_bid = next(
            filter(lambda x: x.room_auction.room.id == room_id, winned_bingo_bids), None)
        if winned_bingo_bid:
            room_history = assign_room_ownership(
                username, room_id, amount_to_pay, winned_bingo_bid.room_auction, winned_bingo_bid)
            data = {'from': room_history.from_date, 'to': room_history.to_date}
            return Response(data=data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(data='the user does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def remove_ownership(request):
    username = request.data.get('username')
    room_id = request.data.get('room_id')
    from_time = request.data.get('from_time')
    to_time = request.data.get('to_time')
    try:
        user = User.objects.get(username=username)
        room = BingoRoom.objects.filter(id=room_id).first()
        if room:
            winned_bingo_bids = BingoRoomAuctionBidHistory.objects.filter(
                bidder=user, win_state=True, paid_state=0)
            winned_bingo_bid = next(
                filter(lambda x: x.room_auction.room.id == room_id, winned_bingo_bids), None)
            if winned_bingo_bid:
                winned_bingo_bid.room_auction.live = True
                winned_bingo_bid.room_auction.save()
            room_history = BingoRoomHistory.objects.filter(
                room=room, owner=user, auction=winned_bingo_bid.room_auction, from_date=from_time, to_date=to_time).first()
            if room_history:
                if room_history.id == room.owner_room_history_id:
                    room.owner_room_history_id = 0
                    room.save()
                room_history.delete()
                return Response(data='successfully deleted', status=status.HTTP_200_OK)
            return Response(data='the room history does not exist', status=status.HTTP_404_NOT_FOUND)
        return Response(data='the room does not exist', status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(data='the user does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes((AllowAny, ))
def arrange_room_auctions(request):
    data = []
    room_auctions = BingoRoomAuction.objects.filter(
        live=True).order_by('room')
    for auction in room_auctions:
        last_bid = BingoRoomAuctionBidHistory.objects.filter(
            room_auction=auction).order_by('-id').first()
        if last_bid:
            auction_data = {'room_id': auction.room.id, 'last_bid_id': last_bid.bid_id_of_auction,
                            'username': last_bid.bidder.username, 'bid_price': last_bid.bid_price, 'elapsed_time': auction.last_bid_elapsed_time, 'time_limit': auction.time_limit, 'coin_per_bid': auction.coin_per_bid, 'price_per_bid': auction.price_per_bid, 'winner': auction.winner.username if auction.winner is not None else None}
        else:
            auction_data = {'room_id': auction.room_id,
                            'last_bid_id': 0, 'username': '', 'bid_price': auction.start_price, 'elapsed_time': 0, 'time_limit': auction.time_limit, 'coin_per_bid': auction.coin_per_bid, 'price_per_bid': auction.price_per_bid, 'winner': None}
        data.append(auction_data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@login_required
def get_won_room_auction(request):
    username = request.data.get('username')
    user = User.objects.filter(username=username).first()
    if user is None:
        return Response(data="the user does not exist", status=status.HTTP_404_NOT_FOUND)
    data = []
    room_auctions = BingoRoomAuction.objects.filter(
        live=True, winner=user).order_by('room')
    for room_auction in room_auctions:
        won_room_auction_history = BingoRoomAuctionBidHistory.objects.filter(
            win_state=True, bidder=user, room_auction=room_auction).first()
        if won_room_auction_history is None:
            return Response(data='invalid data', status=status.HTTP_403_FORBIDDEN)
        expire_date = room_auction.end_date + datetime.timedelta(days=1)
        a_data = {'room_id': room_auction.room.id,
                  'won_price': won_room_auction_history.bid_price, 'expire_date': expire_date}
        data.append(a_data)
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
@login_required
def get_own_room(request):
    username = request.data.get('username')
    user = User.objects.filter(username=username).first()
    if user is None:
        return Response(data="the user does not exist", status=status.HTTP_404_NOT_FOUND)
    data = []
    curr_time = datetime.datetime.utcnow()
    curr_time = pytz.utc.localize(curr_time)

    owner_room_histories = BingoRoomHistory.objects.filter(
        live=True, owner=user, from_date__lte=curr_time, to_date__gte=curr_time)
    for owner_room_history in owner_room_histories:
        if owner_room_history.room.owner_room_history_id != owner_room_history.id:
            return Response(data="invalid data", status=status.HTTP_403_FORBIDDEN)
        a_data = {'room_id': owner_room_history.room.id}
        data.append(a_data)
    return Response(data=data, status=status.HTTP_200_OK)
