from __future__ import absolute_import, unicode_literals
import string
import datetime
from django.db.models import Q

from pytz import utc
import pytz
from user.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from celery import shared_task
from game.bingo.bingoGame.models import BingoBids, BingoGame

from game.bingo.bingoRoom.models import BingoRoom, BingoRoomAuction, BingoRoomAuctionBidHistory, BingoRoomHistory, BingoRoomSetting
from game.models import GameSettings, UserEarnings
import random


@shared_task
def create_random_user_accounts(total):
    print('create_random_user_accounts called')
    for i in range(total):
        username = 'user_{}'.format(
            get_random_string(10, string.ascii_letters))
        email = '{}@example.com'.format(username)
        password = get_random_string(50)
        User.objects.create_user(
            username=username, email=email, password=password, active=True)
    return '{} random users created with success!'.format(total)


@shared_task
def create_bingo_rooms(count):  # initial bingo rooms create
    for i in range(1, count+1):
        room = BingoRoom.objects.create(id=i, bingo_price=i, hold_on=False)
        room_setting = BingoRoomSetting.objects.filter(room=room).first()
        if room_setting is None:
            room_setting = BingoRoomSetting.objects.create(
                room=room, auction_start_price=i*0.1, auction_price_interval_per_bid=i*0.01)


# create_bingo_rooms.delay(30)


@shared_task
def assign_room_ownership(username, room_id, paid_eth, auction=None, winned_bid=None, from_date=None, period=30):
    try:
        user = User.objects.get(username=username)
        room = BingoRoom.objects.get(id=room_id)
        curr_owner_room_history = BingoRoomHistory.objects.filter(
            id=room.id, live=True).first()
        if from_date is None:
            if curr_owner_room_history is None:
                from_date = datetime.datetime.now(timezone.utc)
            else:
                from_date = curr_owner_room_history.to_date
        end_time = from_date+datetime.timedelta(days=period)
        # if curr_owner_room_history:
        #     curr_owner_room_history.live = False
        history_live = False
        if curr_owner_room_history is None:
            history_live = True
        room_history = BingoRoomHistory.objects.create(
            room=room, owner=user, paid_eth=paid_eth, auction=auction, from_date=from_date, to_date=end_time, winned_bid=winned_bid, live=history_live)
        if curr_owner_room_history is None:
            room.owner_room_history_id = room_history.id
            room.save()
        if auction:
            pay_time = datetime.datetime.utcnow()
            auction.pay_date = pay_time
            auction.live = False
            auction.save()
        return room_history
    except User.DoesNotExist:
        return None


def check_auction_available(room):
    auction_history = BingoRoomHistory.objects.filter(
        room=room, live=True).first()
    if auction_history is None:
        return True
    curr_time = datetime.datetime.utcnow()
    end_time = auction_history.to_date
    time_difference = (end_time-curr_time).total_seconds()
    if time_difference > 86400:
        return False
    if time_difference < 0:
        auction_history.live = False
        auction_history.save()
        return True
    return True


@shared_task
def create_bingo_room_auction():  # create bingo room auction
    curr_time = datetime.datetime.utcnow()
    last_bingo_auction = BingoRoomAuction.objects.order_by('-id').first()
    last_room = last_bingo_auction.room
    new_auction_bingo_rooms = BingoRoom.objects.filter(
        hold_on=False).order_by('id')
    auction_available = False
    for new_auction_bingo_room in new_auction_bingo_rooms:
        if check_auction_available(new_auction_bingo_room) and new_auction_bingo_room != last_room:
            auction_available = True
            break
    if auction_available == False:
        return
    try:
        room_setting = BingoRoomSetting.objects.get(
            room=new_auction_bingo_room)
    except BingoRoomSetting.DoesNotExist:
        room_setting = BingoRoomSetting.objects.create(room=new_auction_bingo_room, min_attendee_count=game_setting_min_attendee_count,
                                                       selling_time=game_setting_selling_time, calling_time=game_setting_calling_time, auction_start_price=0.1, auction_price_interval_per_bid=0.01, auction_coin_per_bid=10, auction_win_time_limit=3600)

    new_bingo_room_auction = BingoRoomAuction.objects.create(room=new_auction_bingo_room, start_date=curr_time,
                                                             start_price=room_setting.auction_start_price, coin_per_bid=room_setting.auction_coin_per_bid, price_per_bid=room_setting.auction_price_interval_per_bid, live=True, time_limit=room_setting.auction_win_time_limit, last_bid_elapsed_time=0)


@shared_task
def create_custom_room_auction(room_id):
    try:
        curr_time = datetime.datetime.utcnow()
        room = BingoRoom.objects.get(id=room_id)
        room_setting = BingoRoomSetting.objects.filter(room=room).first()
        if room_setting is None:
            room_setting = BingoRoomSetting.objects.create(room=room, min_attendee_count=game_setting_min_attendee_count, selling_time=game_setting_selling_time,
                                                           calling_time=game_setting_calling_time, auction_start_price=0.1, auction_price_interval_per_bid=0.01, auction_coin_per_bid=10, auction_win_time_limit=3600)
        room_auction = BingoRoomAuction.objects.create(room=room, start_date=curr_time,
                                                       start_price=room_setting.auction_start_price, coin_per_bid=room_setting.auction_coin_per_bid,
                                                       price_per_bid=room_setting.auction_price_interval_per_bid, live=True, time_limit=room_setting.auction_win_time_limit, last_bid_elapsed_time=0)
    except BingoRoom.DoesNotExist:
        pass


# create_custom_room_auction(1)
# create_custom_room_auction(2)
# create_custom_room_auction(3)
# create_custom_room_auction(4)
# create_custom_room_auction(5)


def get_bingo_game_settings():
    game_setting_end_caching_time = GameSettings.objects.filter(
        key='end_caching_time').first()
    game_setting_end_caching_time = 1*60 if game_setting_end_caching_time is None else int(
        game_setting_end_caching_time.value)
    game_setting_selling_calling_transition_time = GameSettings.objects.filter(
        key='selling_calling_transition_time').first()
    game_setting_selling_calling_transition_time = 1 * \
        60 if game_setting_selling_calling_transition_time is None else int(
            game_setting_selling_calling_transition_time.value)
    game_setting_selling_time = GameSettings.objects.filter(
        key='selling_time').first()
    game_setting_selling_time = 15*60 if game_setting_selling_time is None else int(
        game_setting_selling_time.value)
    game_setting_calling_time = GameSettings.objects.filter(
        key='calling_time').first()
    game_setting_calling_time = 10 if game_setting_calling_time is None else int(
        game_setting_calling_time.value)
    game_setting_min_attendee_count = GameSettings.objects.filter(
        key='min_attendee_count').first()
    game_setting_min_attendee_count = 10 if game_setting_min_attendee_count is None else int(
        game_setting_min_attendee_count.value)
    return game_setting_selling_time, game_setting_selling_calling_transition_time, game_setting_calling_time, game_setting_end_caching_time, game_setting_min_attendee_count


def match_game_number(number, game):
    res = False
    bingo_bids = BingoBids.objects.filter(game=game)
    for bingo_bid in bingo_bids:
        card_info = bingo_bid.card_info
        try:
            idx = card_info.index(number)
            m, n = int(idx/27), idx % 27
            bingo_bid.match_state[m][n] = True
            if all(bingo_bid.match_state[m]):
                res = True
                bingo_bid.winning_state = True
            bingo_bid.save()
        except ValueError:
            pass
    return res


global game_setting_selling_time, game_setting_selling_calling_transition_time, game_setting_calling_time, game_setting_end_caching_time, game_setting_min_attendee_count
game_setting_selling_time, game_setting_selling_calling_transition_time, game_setting_calling_time, game_setting_end_caching_time, game_setting_min_attendee_count = get_bingo_game_settings()


@shared_task
def get_game_settings():
    global game_setting_selling_time, game_setting_selling_calling_transition_time, game_setting_calling_time, game_setting_end_caching_time, game_setting_min_attendee_count
    game_setting_selling_time, game_setting_selling_calling_transition_time, game_setting_calling_time, game_setting_end_caching_time, game_setting_min_attendee_count = get_bingo_game_settings()


def manage_one_auction(auction, curr_time):  # returns if the auction winned or not
    last_bid = BingoRoomAuctionBidHistory.objects.filter(
        room_auction=auction).order_by('-id').first()
    if last_bid:
        auction.last_bid_elapsed_time += 1
        auction.save()
        if auction.last_bid_elapsed_time > auction.time_limit:
            auction.end_date = curr_time
            auction.winner = last_bid.bidder
            auction.save()
            last_bid.win_state = True
            last_bid.save()
            res = {'winner': last_bid.bidder.username,
                   'end_bid_price': last_bid.bid_price}
            return res
    return None


@shared_task
def manage_bingo_room_auctions():
    curr_time = datetime.datetime.utcnow()
    curr_time = pytz.utc.localize(curr_time)
    roomAuctions = BingoRoomAuction.objects.filter(live=True, winner=None)
    for roomAuction in roomAuctions:
        res = manage_one_auction(roomAuction, curr_time)

    winned_room__auctions = BingoRoomAuction.objects.filter(
        ~Q(winner=None), live=True)
    for winned_room_auction in winned_room__auctions:
        expire_date = winned_room_auction.end_date + datetime.timedelta(days=1)
        if expire_date < curr_time:
            winned_room_auction.end_date = None
            winned_room_auction.winner = None
            winned_room_auction.last_bid_elapsed_time = 0
            winned_room_auction.save()
            winned_bid = BingoRoomAuctionBidHistory.objects.filter(
                room_auction=winned_room_auction, win_state=True).first()
            if winned_bid:
                winned_bid.win_state = False
                winned_bid.save()

    rooms = BingoRoom.objects.filter(hold_on=False)
    for room in rooms:
        owner_history_id = room.owner_room_history_id
        if owner_history_id > 0:
            owner_history = BingoRoomHistory.objects.filter(
                id=owner_history_id).first()
            if owner_history and owner_history.to_date < curr_time:
                room.owner_room_history_id = 0
                owner_history.live = False
                owner_history.save()
            last_owner_history = BingoRoomHistory.objects.filter(room=room,
                                                                 from_date__lte=curr_time, to_date__gt=curr_time).first()
            if last_owner_history:
                room.owner_room_history_id = last_owner_history.id
                last_owner_history.live = True
                last_owner_history.save()
            room.save()


@shared_task
def manage_bingo_game():
    global game_setting_selling_time, game_setting_selling_calling_transition_time, game_setting_calling_time, game_setting_end_caching_time, game_setting_min_attendee_count
    rooms = BingoRoom.objects.filter(hold_on=False)
    now_time = datetime.datetime.utcnow()
    now_time = pytz.utc.localize(now_time)

    for room in rooms:
        selling_time = game_setting_selling_time
        calling_time = game_setting_calling_time
        min_attendee_count = game_setting_min_attendee_count
        room_setting = BingoRoomSetting.objects.filter(room=room).first()
        if room_setting:
            selling_time = room_setting.selling_time
            calling_time = room_setting.calling_time
            min_attendee_count = room_setting.min_attendee_count

        game = BingoGame.objects.filter(room=room, live=True).first()
        if game is None:
            end_time = now_time+datetime.timedelta(minutes=30)
            game = BingoGame.objects.create(room=room, called_numbers=[], start_time=now_time,
                                            end_time=end_time, status='selling', live=True)
        else:
            elapsed_time = game.elapsed_time+1
            # if game.end_time < now_time and game.status != 'ended':  # exception, force to end game
            #     game.live = False
            #     game.end_time = now_time
            #     game.elapsed_time = elapsed_time
            #     game.status = 'ended'
            if game.status == 'ended':
                if elapsed_time >= game_setting_end_caching_time:
                    game.live = False
                    game.elapsed_time = 0
                    # set user, owner earnings
                    winner_bids = BingoBids.objects.filter(
                        game=game, winning_state=True)
                    winner_earning = float(format(
                        room.bingo_price*0.001*game.total_cards_count*0.85/len(winner_bids), '.5f'))
                    owner_earning = float(format(
                        room.bingo_price*0.001*game.total_cards_count*0.1, '.5f'))
                    if room.owner_room_history_id != 0:
                        owner_history = BingoRoomHistory.objects.filter(
                            id=room.owner_room_history_id).first()
                        if owner_history:
                            owner = owner_history.owner
                            if UserEarnings.objects.filter(user=owner, game_id=game.id, game_kind='bingo', is_owner=True).first() == None:
                                UserEarnings.objects.create(
                                    user=owner, game_id=game.id, game_kind='bingo', is_owner=True, earning=owner_earning)
                    for winner_bid in winner_bids:
                        winner_bid.earning = winner_earning
                        winner_bid.save()
                        game.winners.add(winner_bid.player)
                        # if UserEarnings.objects.filter(user=winner_bid.player, game_id=game.id, game_kind='bingo', is_owner=False).first() == None:
                        UserEarnings.objects.create(
                            user=winner_bid.player, game_id=game.id, game_kind='bingo', is_owner=False, earning=winner_earning)
                else:
                    game.elapsed_time = elapsed_time
            else:
                if game.status == 'selling':
                    if elapsed_time >= selling_time:
                        if game.total_cards_count >= min_attendee_count:
                            game.status = 'transition'
                            game.elapsed_time = 0
                        else:
                            game.elapsed_time = selling_time-60
                    else:
                        game.elapsed_time = elapsed_time
                elif game.status == 'transition':
                    if elapsed_time >= game_setting_selling_calling_transition_time:
                        game.status = 'calling'
                        game.elapsed_time = 0
                    else:
                        game.elapsed_time = elapsed_time
                elif game.status == 'calling':
                    if elapsed_time >= calling_time:
                        number = random.randint(1, 90)
                        while number in game.called_numbers:
                            number = random.randint(1, 90)
                        game.last_number = number
                        game.called_numbers.append(number)
                        if match_game_number(number, game):
                            game.end_time = now_time
                            game.status = 'ended'
                        else:
                            game.elapsed_time = 0
                    else:
                        game.elapsed_time = elapsed_time
            game.save()
