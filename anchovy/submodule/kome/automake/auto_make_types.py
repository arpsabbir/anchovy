# coding: utf-8

from auto_make import *

enums = [{
    'name': 'DeviceType',
    'values': ['FP', 'SP_iPhone', 'SP_Android', 'Unknown']
},{
    'name': 'RegisterType',
    'values': ['NORMAL', 'INVITE', 'CAMPAIGN']
},{
    'name': 'PaymentCategory',
    'values': ['GACHA', 'ITEM']
},{
    'name': 'PaymentSubcategory',
    'values': ['GACHA', 'GACHA_SET', 'GACHA_TICKET', 'POTION', 'BATTLE', 'EQUIPMENT', 'TRAP', 'SET', 'OTHER']
},{
    'name': 'GachaType',
    'values': ['FREE', 'TICKET', 'PAY']
},{
    'name': 'BattleTargetCategory',
    'values': ['ITEM', 'NONE']
},{
    'name': 'FusionType',
    'values': ['ENHANCED', 'EVOLUTION']
},{
    'name': 'DeckType',
    'values': ['ATTACK', 'DEFENSE', 'NONE']
},{
    'name': 'DeckOperationType',
    'values': ['MEMBER_ADD', 'MEMBER_REMOVE', 'DECK_CREATE', 'DECK_DESTROY', 'DECK_COPY']
},{
    'name': 'PowerType',
    'values': ['POWER', 'ATTACK', 'DEFENSE', 'RESET', 'OTHER']
},{
    'name': 'PresentType',
    'values': ['NORMAL', 'OFFICIAL', 'PROMOTION', 'CAMPAIGN']
},{
    'name': 'ItemType',
    'values': ['ITEM', 'CARD', 'MONEY', 'POINT', 'TREASURE', 'MEDAL']
},{
    'name': 'GuildOperationType',
    'values': ['CREATE', 'DROP', 'OTHER']
},{
    'name': 'GuildMemberOperationType',
    'values': ['JOIN', 'LEAVE', 'KICK_OFF', 'HANDOVER', 'OTHER']
},{
    'name': 'BattleResult',
    'values': ['WIN', 'LOSE', 'NONE']
},{
    'name': 'DevoteType',
    'values': ['PRINCESS']
},{
    'name': 'WishlistOperationType',
    'values': ['APPEND', 'REMOVE']
},{
    'name': 'WishlistObjectType',
    'values': ['ITEM', 'CARD']
},{
    'name': 'ExchangeType',
    'values': ['CARD_TO_MEDAL', 'MEDAL_TO_ITEM']
},{
    'name': 'EventType',
    'values': ['QUEST', 'RAID', 'USER']
},{
    'name': 'TradeStatus',
    'values': ['APPLY', 'ACCEPT', 'CANCEL', 'FINISH']
},{
    'name': 'LocationType',
    'values': ['MYPAGE', 'QUEST_TOP']
},{
    'name': 'FriendActionType',
    'values': ['REQUEST', 'ACCEPT', 'CANCEL', 'REMOVE']
},{
    'name': 'CommentType',
    'values': ['COMPLETE', 'EVENT', 'DIARY']
}]

if __name__ == '__main__':
    print '\n'.join([generate_enum(enum) for enum in enums])
