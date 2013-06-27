# coding: utf-8

def _isinstance(instance, cls):
    if hasattr(cls, '_instancecheck'):
        return cls._instancecheck(instance)
    else:
        return isinstance(instance, cls)

class NumberTypes:
    _classes = []
    @classmethod
    def _instancecheck(cls, instance):
        return any([_isinstance(instance, c) for c in cls._classes])
    @classmethod
    def register(cls, subclass):
        cls._classes.append(subclass)
NumberTypes.register(int)
NumberTypes.register(long)

class StringTypes:
    _classes = []
    @classmethod
    def _instancecheck(cls, instance):
        return any([_isinstance(instance, c) for c in cls._classes])
    @classmethod
    def register(cls, subclass):
        cls._classes.append(subclass)
StringTypes.register(str)
StringTypes.register(unicode)

#############################
# 以下自動生成で出力した実装
#############################

class DeviceType:
    FP = 'FP'
    SP_iPhone = 'SP_iPhone'
    SP_Android = 'SP_Android'
    Unknown = 'Unknown'

    @classmethod
    def any_of(cls, value):
        vs = [cls.FP,cls.SP_iPhone,cls.SP_Android,cls.Unknown]
        return any([value == v for v in vs])


class RegisterType:
    NORMAL = 'NORMAL'
    INVITE = 'INVITE'
    CAMPAIGN = 'CAMPAIGN'

    @classmethod
    def any_of(cls, value):
        vs = [cls.NORMAL,cls.INVITE,cls.CAMPAIGN]
        return any([value == v for v in vs])


class PaymentCategory:
    GACHA = 'GACHA'
    ITEM = 'ITEM'

    @classmethod
    def any_of(cls, value):
        vs = [cls.GACHA,cls.ITEM]
        return any([value == v for v in vs])


class PaymentSubcategory:
    GACHA = 'GACHA'
    GACHA_SET = 'GACHA_SET'
    GACHA_TICKET = 'GACHA_TICKET'
    POTION = 'POTION'
    BATTLE = 'BATTLE'
    EQUIPMENT = 'EQUIPMENT'
    TRAP = 'TRAP'
    SET = 'SET'
    OTHER = 'OTHER'

    @classmethod
    def any_of(cls, value):
        vs = [cls.GACHA,cls.GACHA_SET,cls.GACHA_TICKET,cls.POTION,cls.BATTLE,cls.EQUIPMENT,cls.TRAP,cls.SET,cls.OTHER]
        return any([value == v for v in vs])


class GachaType:
    FREE = 'FREE'
    TICKET = 'TICKET'
    PAY = 'PAY'

    @classmethod
    def any_of(cls, value):
        vs = [cls.FREE,cls.TICKET,cls.PAY]
        return any([value == v for v in vs])


class BattleTargetCategory:
    ITEM = 'ITEM'
    NONE = 'NONE'

    @classmethod
    def any_of(cls, value):
        vs = [cls.ITEM,cls.NONE]
        return any([value == v for v in vs])


class FusionType:
    ENHANCED = 'ENHANCED'
    EVOLUTION = 'EVOLUTION'

    @classmethod
    def any_of(cls, value):
        vs = [cls.ENHANCED,cls.EVOLUTION]
        return any([value == v for v in vs])


class DeckType:
    ATTACK = 'ATTACK'
    DEFENSE = 'DEFENSE'
    NONE = 'NONE'

    @classmethod
    def any_of(cls, value):
        vs = [cls.ATTACK,cls.DEFENSE,cls.NONE]
        return any([value == v for v in vs])


class DeckOperationType:
    MEMBER_ADD = 'MEMBER_ADD'
    MEMBER_REMOVE = 'MEMBER_REMOVE'
    DECK_CREATE = 'DECK_CREATE'
    DECK_DESTROY = 'DECK_DESTROY'
    DECK_COPY = 'DECK_COPY'

    @classmethod
    def any_of(cls, value):
        vs = [cls.MEMBER_ADD,cls.MEMBER_REMOVE,cls.DECK_CREATE,cls.DECK_DESTROY,cls.DECK_COPY]
        return any([value == v for v in vs])


class PowerType:
    POWER = 'POWER'
    ATTACK = 'ATTACK'
    DEFENSE = 'DEFENSE'
    RESET = 'RESET'
    OTHER = 'OTHER'

    @classmethod
    def any_of(cls, value):
        vs = [cls.POWER,cls.ATTACK,cls.DEFENSE,cls.RESET,cls.OTHER]
        return any([value == v for v in vs])


class PresentType:
    NORMAL = 'NORMAL'
    OFFICIAL = 'OFFICIAL'
    PROMOTION = 'PROMOTION'
    CAMPAIGN = 'CAMPAIGN'

    @classmethod
    def any_of(cls, value):
        vs = [cls.NORMAL,cls.OFFICIAL,cls.PROMOTION,cls.CAMPAIGN]
        return any([value == v for v in vs])


class ItemType:
    ITEM = 'ITEM'
    CARD = 'CARD'
    MONEY = 'MONEY'
    POINT = 'POINT'
    TREASURE = 'TREASURE'
    MEDAL = 'MEDAL'

    @classmethod
    def any_of(cls, value):
        vs = [cls.ITEM,cls.CARD,cls.MONEY,cls.POINT,cls.TREASURE,cls.MEDAL]
        return any([value == v for v in vs])


class GuildOperationType:
    CREATE = 'CREATE'
    DROP = 'DROP'
    OTHER = 'OTHER'

    @classmethod
    def any_of(cls, value):
        vs = [cls.CREATE,cls.DROP,cls.OTHER]
        return any([value == v for v in vs])


class GuildMemberOperationType:
    JOIN = 'JOIN'
    LEAVE = 'LEAVE'
    KICK_OFF = 'KICK_OFF'
    HANDOVER = 'HANDOVER'
    OTHER = 'OTHER'

    @classmethod
    def any_of(cls, value):
        vs = [cls.JOIN,cls.LEAVE,cls.KICK_OFF,cls.HANDOVER,cls.OTHER]
        return any([value == v for v in vs])


class BattleResult:
    WIN = 'WIN'
    LOSE = 'LOSE'
    NONE = 'NONE'

    @classmethod
    def any_of(cls, value):
        vs = [cls.WIN,cls.LOSE,cls.NONE]
        return any([value == v for v in vs])


class DevoteType:
    PRINCESS = 'PRINCESS'

    @classmethod
    def any_of(cls, value):
        vs = [cls.PRINCESS]
        return any([value == v for v in vs])


class WishlistOperationType:
    APPEND = 'APPEND'
    REMOVE = 'REMOVE'

    @classmethod
    def any_of(cls, value):
        vs = [cls.APPEND,cls.REMOVE]
        return any([value == v for v in vs])


class WishlistObjectType:
    ITEM = 'ITEM'
    CARD = 'CARD'

    @classmethod
    def any_of(cls, value):
        vs = [cls.ITEM,cls.CARD]
        return any([value == v for v in vs])


class ExchangeType:
    CARD_TO_MEDAL = 'CARD_TO_MEDAL'
    MEDAL_TO_ITEM = 'MEDAL_TO_ITEM'

    @classmethod
    def any_of(cls, value):
        vs = [cls.CARD_TO_MEDAL,cls.MEDAL_TO_ITEM]
        return any([value == v for v in vs])


class EventType:
    QUEST = 'QUEST'
    RAID = 'RAID'
    USER = 'USER'

    @classmethod
    def any_of(cls, value):
        vs = [cls.QUEST,cls.RAID,cls.USER]
        return any([value == v for v in vs])


class TradeStatus:
    APPLY = 'APPLY'
    ACCEPT = 'ACCEPT'
    CANCEL = 'CANCEL'
    FINISH = 'FINISH'

    @classmethod
    def any_of(cls, value):
        vs = [cls.APPLY,cls.ACCEPT,cls.CANCEL,cls.FINISH]
        return any([value == v for v in vs])


class LocationType:
    MYPAGE = 'MYPAGE'
    QUEST_TOP = 'QUEST_TOP'

    @classmethod
    def any_of(cls, value):
        vs = [cls.MYPAGE,cls.QUEST_TOP]
        return any([value == v for v in vs])


class FriendActionType:
    REQUEST = 'REQUEST'
    ACCEPT = 'ACCEPT'
    CANCEL = 'CANCEL'
    REMOVE = 'REMOVE'

    @classmethod
    def any_of(cls, value):
        vs = [cls.REQUEST,cls.ACCEPT,cls.CANCEL,cls.REMOVE]
        return any([value == v for v in vs])


class CommentType:
    COMPLETE = 'COMPLETE'
    EVENT = 'EVENT'
    DIARY = 'DIARY'

    @classmethod
    def any_of(cls, value):
        vs = [cls.COMPLETE,cls.EVENT,cls.DIARY]
        return any([value == v for v in vs])

