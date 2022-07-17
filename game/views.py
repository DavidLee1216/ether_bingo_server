import datetime
import stat
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required

from game.bingo.bingoGame.models import BingoBids, BingoGame
from game.bingo.bingoRoom.models import BingoRoomAuctionBidHistory, BingoRoomHistory, BingoRoomSetting
from .models import GameSettings, UserEarnings, UserProfile, UserCoin, UserCoinBuyHistory, UserContactUs
from user.models import User
from .serializer import UserProfileSerializer, UserCoinSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from game.etherfunc import send_user_balance


@api_view(['POST'])
@login_required
def set_profile(request):
    username = request.data.get('username')
    country = request.data.get('country')
    city = request.data.get('city')
    sex = request.data.get('sex')
    main_wallet = request.data.get('wallet')
    user = User.objects.filter(username=username).first()
    other_user_with_same_wallet = UserProfile.objects.filter(
        main_wallet=main_wallet).exclude(user=user).first()
    if other_user_with_same_wallet:
        return Response(data='main wallet conflict', status=status.HTTP_409_CONFLICT)
    if main_wallet == "":
        return Response(data="main wallet can not be empty", status=status.HTTP_400_BAD_REQUEST)

    if user is not None:
        profiles = UserProfile.objects.filter(user=user)
        if len(profiles) > 0:
            profile = profiles[0]
            profile.country = country
            profile.city = city
            profile.sex = sex
            profile.main_wallet = main_wallet
        else:
            profile = UserProfile(user=user, country=country,
                                  city=city, sex=sex, main_wallet=main_wallet)
        if user.wallet_address == "":
            user.wallet_address = main_wallet
            user.save()
        profile.save()

        return Response(data='success', status=status.HTTP_200_OK)
    else:
        return Response(data='user does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def get_profile(request):
    username = request.data.get('username')
    user = User.objects.filter(username=username).first()
    if user is not None:
        try:
            profile = UserProfile.objects.get(user=user)
            profile_serialized = UserProfileSerializer(profile)
            return Response(data=profile_serialized.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response(data='profile does not exist', status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(data='user does not exist', status=status.HTTP_404_NOT_FOUND)


def buy_coin_transaction(user, amount, address):  # register coin buy history
    user_coin_buy_history = UserCoinBuyHistory(
        user=user, amount=amount, wallet_address=address)
    user_coin_buy_history.save()


@api_view(['POST'])
@login_required
def buy_coin(request):  # api to update coin when user buy
    username = request.data.get('username')
    amount = request.data.get('amount')  # ether amount
    address = request.data.get('address')  # user's wallet address
    try:
        user = User.objects.get(username=username)
        coin_amount = int(amount)
        buy_coin_transaction(user, coin_amount, address)
        try:
            usercoin = UserCoin.objects.get(user=user)
            usercoin.coin += coin_amount  # coin_amount
            usercoin.save()
            userCoinSerialized = UserCoinSerializer(usercoin)
            return Response(data=userCoinSerialized.data, status=status.HTTP_202_ACCEPTED)
        except UserCoin.DoesNotExist:
            usercoin = UserCoin(user=user, coin=coin_amount)
            usercoin.save()
            userCoinSerialized = UserCoinSerializer(usercoin)
            return Response(data=userCoinSerialized.data, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response(data='user does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def get_coin(request):
    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)
        usercoin = UserCoin.objects.get(user=user)
        userCoinSerialized = UserCoinSerializer(usercoin)

        return Response(data=userCoinSerialized.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(data='user does not exist', status=status.HTTP_404_NOT_FOUND)
    except UserCoin.DoesNotExist:
        return Response(data='user does not have coin', status=status.HTTP_204_NO_CONTENT)


def check_user_coin(user, user_coin):  # check coin to prevent hacking
    user_coin_buy_history = UserCoinBuyHistory.objects.filter(user=user)
    bought_coins = sum([x.amount for x in user_coin_buy_history])
    user_bingo_play_history = BingoBids.objects.filter(player=user)
    bingo_consumed_coins = sum([x.coin for x in user_bingo_play_history])
    user_room_auction_history = BingoRoomAuctionBidHistory.objects.filter(
        bidder=user)
    room_auction_consumed_coins = sum(
        [x.room_auction.coin_per_bid for x in user_room_auction_history])
    if user_coin.coin == (bought_coins-bingo_consumed_coins-room_auction_consumed_coins):
        return True
    return False


@api_view(['POST'])
@login_required
def get_earnings(request):
    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)
        user_earnings = UserEarnings.objects.filter(user=user).order_by('-id')
        arr = []
        total_earning = 0
        withdrawable_earning = 0
        verified = True
        for user_earning in user_earnings:
            if user_earning.game_kind == 'bingo':
                game = BingoGame.objects.filter(
                    id=user_earning.game_id).first()
                if game:
                    time = game.end_time
                    earning_type = 'owner earning' if user_earning.is_owner else 'won'
                    a_arr = {'id': user_earning.id, 'time': time, 'kind': 'bingo',
                             'type': earning_type, 'amount': str(user_earning.earning), 'verified': user_earning.verified, 'withdrawn': user_earning.withdrawn}
                    verified &= user_earning.verified
                    total_earning += user_earning.earning
                    withdrawable_earning += user_earning.earning if user_earning.withdrawn == False else 0
                    arr.append(a_arr)
        data = {'total': total_earning,
                'withdrawable': withdrawable_earning, 'verified': verified, 'history': arr}
        return Response(data=data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(data='user does not exist', status=status.HTTP_404_NOT_FOUND)


coin_price = 0.001


@api_view(['POST'])
@login_required
def verify(request):
    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)
        user_earnings = UserEarnings.objects.filter(user=user, verified=False)
        verify_result = True
        total_earning = 0
        for user_earning in user_earnings:
            game_id = user_earning.game_id
            game_kind = user_earning.game_kind
            is_owner = user_earning.is_owner
            earning = float(format(user_earning.earning, '.5f'))
            if game_kind == 'bingo':
                bingo_game = BingoGame.objects.filter(id=game_id).first()
                if bingo_game is None:
                    return Response(data='game does not exist', status=status.HTTP_404_NOT_FOUND)
                if is_owner == False:
                    bid = BingoBids.objects.filter(
                        game=bingo_game, winning_state=True, player=user).first()
                    if bid and bid.earning == earning:
                        if user in bingo_game.winners.all():
                            user_earning.verified = True
                            user_earning.save()
                else:
                    roomHistories = BingoRoomHistory.objects.filter(
                        room=bingo_game.room, owner=user)
                    for roomHistory in roomHistories:
                        if roomHistory.from_date <= bingo_game.end_time and bingo_game.end_time < roomHistory.to_date:
                            comp_earning = float(format(
                                bingo_game.total_cards_count*bingo_game.room.bingo_price*coin_price*0.1, '.5f'))
                            if earning == comp_earning:
                                user_earning.verified = True
                                user_earning.save()
                                break
            verified = user_earning.verified
            verify_result &= verified
            if verified:
                total_earning += earning
        if verify_result:
            send_user_balance(user.id, total_earning)
        else:
            user.is_active = False
            user.auth_code = int(user.auth_code) ^ 0x56
            user.save()
        return Response(data={'res': verify_result}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response(data='user does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def withdraw(request):
    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)
        user_earnings = UserEarnings.objects.filter(user=user, withdrawn=False)
        for user_earning in user_earnings:
            user_earning.withdrawn = True
            user_earning.save()
        return Response(status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(data='user does not exist', status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@login_required
def contact(request):
    username = request.data.get('username')
    time = datetime.datetime.utcnow()
    content = request.data.get('content')
    try:
        user = User.objects.get(username=username)
        contact = UserContactUs.objects.create(
            user=user, time=time, content=content)
        return Response(status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(data='user does not exist', status=status.HTTP_404_NOT_FOUND)
