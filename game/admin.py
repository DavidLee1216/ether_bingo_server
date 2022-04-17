from django.contrib import admin

from game.bingo.bingoGame.models import BingoGame, BingoBids, BingoGameStatus
from game.bingo.bingoRoom.models import BingoRoom, BingoRoomAuction, BingoRoomAuctionBidHistory, BingoRoomHistory, BingoRoomSetting
from game.models import UserProfile, UserCoin, UserCoinBuyHistory, GameSettings

admin.site.register(BingoGame)
admin.site.register(BingoBids)
admin.site.register(BingoGameStatus)
admin.site.register(BingoRoom)
admin.site.register(BingoRoomSetting)
admin.site.register(BingoRoomAuction)
admin.site.register(BingoRoomAuctionBidHistory)
admin.site.register(BingoRoomHistory)
admin.site.register(UserProfile)
admin.site.register(UserCoin)
admin.site.register(UserCoinBuyHistory)
admin.site.register(GameSettings)
