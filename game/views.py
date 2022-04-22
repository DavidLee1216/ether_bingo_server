import stat
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required

from game.bingo.bingoGame.models import BingoBids
from game.bingo.bingoRoom.models import BingoRoomAuctionBidHistory
from .models import GameSettings, UserProfile, UserCoin, UserCoinBuyHistory
from user.models import User
from .serializer import UserProfileSerializer, UserCoinSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['POST'])
@login_required
def set_profile(request):
    username = request.data.get('username')
    country = request.data.get('country')
    city = request.data.get('city')
    sex = request.data.get('sex')
    main_wallet = request.data.get('wallet')
    user = User.objects.filter(username=username).first()

    if user is not None:
        profiles = UserProfile.objects.filter(user_id=user)
        if len(profiles) > 0:
            profile = profiles[0]
            profile.country = country
            profile.city = city
            profile.sex = sex
            profile.main_wallet = main_wallet
        else:
            profile = UserProfile(user=user, country=country,
                                  city=city, sex=sex, main_wallet=main_wallet)
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
    bingo_consumed_coins = sum([x.amount for x in user_bingo_play_history])
    user_room_auction_history = BingoRoomAuctionBidHistory.objects.filter(
        bidder=user)
    room_auction_consumed_coins = sum(
        [x.room_auction.coin_per_bid for x in user_room_auction_history])
    if user_coin == (bought_coins-bingo_consumed_coins-room_auction_consumed_coins):
        return True
    return False
