# coding: utf-8

import uuid
from datetime import datetime
import kome.core.sender
from kome.core.derivedlog import DerivedLog
from kome.core.types import *
from kome.core.types import _isinstance

class ActionRecord(object):
    def __init__(self, id, actname, time, action):
        self._actname = actname
        self._id = id
        self._time = time
        self._action = action

    @property
    def action(self):
        return self._action

    @property
    def id(self):
        return self._id

    @property
    def time(self):
        return self._time

    @property
    def actname(self):
        return self._actname

    def get_actlog(self):
        return ActionLog(
            self._action.sender,
            self._action.uid,
            self._action.device,
            self)

    def get_derivedlog(self):
        return DerivedLog(self._action, self)

class ActionLog(object):
    def __init__(self, sender, uid, device, parent_record = None):
        u"""
        アクションログの初期化

        sender -- ログの送信先
        uid    -- ユーザID
        device -- デバイス名
        parent_record -- 親アクション
        """
        self._sender = sender
        self._uid = uid
        self._device = device
        self._parent_record = parent_record

    @property
    def sender(self):
        return self._sender

    @property
    def uid(self):
        return self._uid

    @property
    def device(self):
        return self._device

    @property
    def version(self):
        return 2

    @property
    def parent_record(self):
        return self._parent_record

    def log(self, actname, **kwargs):
        u"""
        任意のログを出力する
        """
        # id が指定されている場合はそっちを優先する
        id = kwargs.get('id', str(uuid.uuid4()))
        # time が指定されている場合はそっちを優先する
        time = kwargs.get('time', datetime.now())

        record = dict(kwargs)
        record.update({
            'uid': self.uid,
            'ver': self.version,
            'time': time,
            'device': self.device,
            'action': actname,
            'id': id })
        if self.parent_record != None:
            record.update({
                'parent': self.parent_record.actname,
                'parentid': self.parent_record.id })

        self._sender.emit(record)

        return ActionRecord(id, actname, time, self)

    def _or_none(self, f):
        return lambda xs: xs is None or f(xs)

    def _string_list(self, xs):
        return _isinstance(xs, list) and \
               all([_isinstance(x, StringTypes) for x in xs])

    def _is_trade_items(self, xs):
        return self._string_list(xs)

    #############################
    # 以下自動生成で出力した実装
    #############################

    def register(self, register_type, **opt):
        u"""
        新規登録
        
        register_type -- 登録チャネル(RegisterType.[NORMAL,INVITE,CAMPAIGN])
        """
        assert RegisterType.any_of(register_type)

        return self.log('register',
                        register_type = register_type,
                        **opt)

    def pay(self, payment_category, payment_subcategory, target_id, unit_price, quantity, **opt):
        u"""
        課金
        
        payment_category -- 課金対象カテゴリ(PaymentCategory.[GACHA,ITEM])
        payment_subcategory -- 課金対象サブカテゴリ(PaymentSubcategory.[GACHA,GACHA_SET,GACHA_TICKET,POTION,BATTLE,EQUIPMENT,TRAP,SET,OTHER])
        target_id -- 課金アイテムID
        unit_price -- 単価
        quantity -- 個数
        
        注意:
          課金ガチャの場合、do_gachaアクションも同時に出力して下さい。
          課金ガチャによって増えたカードなどは、do_gachaの派生ログとして出力してください。
        
          アイテム付き課金ガチャの場合 PaymentCategory.GACHA, PaymentSubcategory.GACHA_SET を使用して下さい。
        
          ガチャ以外のアイテムの組み合わせ販売の場合 PaymentCategory.ITEM, PaymentSubcategory.SET を使用して下さい。
        
        例:
          課金ガチャの場合:
            # 幻想郷6連ガチャ、回復アイテム付きの場合
            with log().pay(PaymentCategory.GACHA, PaymentSubcategory.GACHA_SET, target_id, 1500, 1): # GACHA_SET を使う
                with log().do_gacha(GachaType.PAY, 6, 'GENSOKYO_GACHA'):
                    log().derivedlog.inc_card(...) # do_gachaの子として出力
                    log().derivedlog.inc_item(...) # アイテム付きのガチャであってもdo_gachaの子として出力する
        
          行動回復アイテムの場合:
            with log().pay(PaymentCategory.ITEM, PaymentSubcategory.POTION, target_id, 200, 3):
                log().derivedlog.inc_item(...) # payの子として出力
        
          バトル回復アイテムの場合:
            with log().pay(PaymentCategory.ITEM, PaymentSubcategory.BATTLE, target_id, 100, 3):
                log().derivedlog.inc_item(...) # payの子として出力
        
          行動回復アイテム×イベントアイテムのセットを購入した場合:
            with log().pay(PaymentCategory.ITEM, PaymentSubcategory.SET, target_id, 10000, 3): # SET を使う
                log().inc_item(...)
        """
        assert PaymentCategory.any_of(payment_category)
        assert PaymentSubcategory.any_of(payment_subcategory)
        assert _isinstance(target_id, StringTypes)
        assert _isinstance(unit_price, NumberTypes)
        assert _isinstance(quantity, NumberTypes)

        return self.log('pay',
                        payment_category = payment_category,
                        payment_subcategory = payment_subcategory,
                        target_id = target_id,
                        unit_price = unit_price,
                        quantity = quantity,
                        **opt)

    def battle_attack(self, target_uid, battle_result, target_item_category, target_item_id, user_level, target_user_level, show_trap = None, show_damnation = None, player_deck = None, target_deck = None, **opt):
        u"""
        バトル_攻撃
        
        target_uid -- バトル相手
        battle_result -- バトル結果(BattleResult.[WIN,LOSE,NONE])
        target_item_category -- 略奪対象カテゴリ(BattleTargetCategory.[ITEM,NONE])
        target_item_id -- 略奪対象アイテムID
        user_level -- ユーザLv.
        target_user_level -- バトル相手Lv.
        show_trap (opt) -- 罠発動の有無
        show_damnation (opt) -- 天罰発動の有無
        player_deck (opt) -- 攻撃する側のデッキ
        target_deck (opt) -- 攻撃される側のデッキ
        
        PvPバトルを『仕掛けた際』に出力されるログです。
        
        注意:
          仕掛けられた側はアクションを起こしていないため、出力してはいけません。
        
        デッキ情報について:
          デッキは、以下の情報を '/' で繋いだものをリストで渡して下さい。
            - カードID（インスタンスIDではなくマスタID）
            - カードのレアリティ
            - カードのレベル
            - カードのランクや限界突破回数といった、カードの強さに関わる情報（無い場合は0）
            - カードの攻撃力（無い場合は 0）
            - カードの防御力（無い場合は 0）
            * これ以降は任意のデータをいくつでも
        
          例:
            def get_cardinfo(card):
                return [card.master_id, card.rarity, card.level, card.rank, card.attack, card.defense, card.extradata]
        
            def to_str(cardinfo):
                return '/'.join(map(str, cardinfo))
        
            def deck_to_strs(cards):
                return [to_str(get_cardinfo(cardinfo)) for card in cards]
        
            with log().battle_attack(...,
                player_deck=deck_to_strs(player.deck),
                target_deck=deck_to_strs(player.deck))
        """
        assert _isinstance(target_uid, StringTypes)
        assert BattleResult.any_of(battle_result)
        assert BattleTargetCategory.any_of(target_item_category)
        assert _isinstance(target_item_id, StringTypes)
        assert _isinstance(user_level, NumberTypes)
        assert _isinstance(target_user_level, NumberTypes)
        assert _isinstance(show_trap, bool) or show_trap == None
        assert _isinstance(show_damnation, bool) or show_damnation == None
        assert self._or_none(self._string_list)(player_deck)
        assert self._or_none(self._string_list)(target_deck)

        return self.log('battle_attack',
                        target_uid = target_uid,
                        battle_result = battle_result,
                        target_item_category = target_item_category,
                        target_item_id = target_item_id,
                        user_level = user_level,
                        target_user_level = target_user_level,
                        show_trap = show_trap,
                        show_damnation = show_damnation,
                        player_deck = player_deck,
                        target_deck = target_deck,
                        **opt)

    def do_gacha(self, gacha_type, count, gacha_id, **opt):
        u"""
        ガチャ実施
        
        gacha_type -- 実施種別(GachaType.[FREE,TICKET,PAY])
        count -- カードの同時取得枚数
        gacha_id -- ガチャID
        
        注意:
          課金ガチャの場合はこのログと同時に pay アクションログも出力する必要があります。
        """
        assert GachaType.any_of(gacha_type)
        assert _isinstance(count, NumberTypes)
        assert _isinstance(gacha_id, StringTypes)

        return self.log('do_gacha',
                        gacha_type = gacha_type,
                        count = count,
                        gacha_id = gacha_id,
                        **opt)

    def fusion_card(self, fusion_type, base_card_id, base_card_rarity, material_card_ids, material_card_quantity, got_card_exp, before_card_level, before_card_exp, before_card_hitpoint, before_card_attack, before_card_defense, after_card_level, after_card_exp, after_card_hitpoint, after_card_attack, after_card_defense, before_card_ability1_level = None, before_card_ability2_level = None, before_card_ability3_level = None, before_extra_attack = None, before_extra_defense = None, after_card_ability1_level = None, after_card_ability2_level = None, after_card_ability3_level = None, after_extra_attack = None, after_extra_defense = None, **opt):
        u"""
        カード合成
        
        fusion_type -- 合成種別(FusionType.[ENHANCED,EVOLUTION])
        base_card_id -- 素材カードID
        base_card_rarity -- 素材カードレアリティ
        material_card_ids -- 消費カードID(s)
        material_card_quantity -- 消費カード枚数
        got_card_exp -- 取得経験値
        before_card_level -- 合成前Lv.
        before_card_exp -- 合成前カード経験値
        before_card_hitpoint -- 合成前カードHP
        before_card_attack -- 合成前攻撃力
        before_card_defense -- 合成前防御力
        after_card_level -- 合成後Lv.
        after_card_exp -- 合成後カード経験値
        after_card_hitpoint -- 合成後カードHP
        after_card_attack -- 合成後攻撃力
        after_card_defense -- 合成後防御力
        before_card_ability1_level (opt) -- 合成前スキル1Lv.
        before_card_ability2_level (opt) -- 合成前スキル2Lv.
        before_card_ability3_level (opt) -- 合成前スキル3Lv.
        before_extra_attack (opt) -- 合成前追加攻撃力
        before_extra_defense (opt) -- 合成前追加防御力
        after_card_ability1_level (opt) -- 合成後スキル1Lv.
        after_card_ability2_level (opt) -- 合成後スキル2Lv.
        after_card_ability3_level (opt) -- 合成後スキル3Lv.
        after_extra_attack (opt) -- 合成後追加攻撃力
        after_extra_defense (opt) -- 合成後追加防御力
        
        注意:
          base_card_id, material_card_ids にはレコードのインスタンスIDではなくカードマスタのIDを入れて下さい。
          material_card_ids は複数カードの合成を想定し、ID の list を挿入して下さい。
        """
        assert FusionType.any_of(fusion_type)
        assert _isinstance(base_card_id, StringTypes)
        assert _isinstance(base_card_rarity, NumberTypes)
        assert _isinstance(material_card_ids, list)
        assert _isinstance(material_card_quantity, NumberTypes)
        assert _isinstance(got_card_exp, NumberTypes)
        assert _isinstance(before_card_level, NumberTypes)
        assert _isinstance(before_card_exp, NumberTypes)
        assert _isinstance(before_card_hitpoint, NumberTypes)
        assert _isinstance(before_card_attack, NumberTypes)
        assert _isinstance(before_card_defense, NumberTypes)
        assert _isinstance(after_card_level, NumberTypes)
        assert _isinstance(after_card_exp, NumberTypes)
        assert _isinstance(after_card_hitpoint, NumberTypes)
        assert _isinstance(after_card_attack, NumberTypes)
        assert _isinstance(after_card_defense, NumberTypes)
        assert _isinstance(before_card_ability1_level, NumberTypes) or before_card_ability1_level == None
        assert _isinstance(before_card_ability2_level, NumberTypes) or before_card_ability2_level == None
        assert _isinstance(before_card_ability3_level, NumberTypes) or before_card_ability3_level == None
        assert _isinstance(before_extra_attack, NumberTypes) or before_extra_attack == None
        assert _isinstance(before_extra_defense, NumberTypes) or before_extra_defense == None
        assert _isinstance(after_card_ability1_level, NumberTypes) or after_card_ability1_level == None
        assert _isinstance(after_card_ability2_level, NumberTypes) or after_card_ability2_level == None
        assert _isinstance(after_card_ability3_level, NumberTypes) or after_card_ability3_level == None
        assert _isinstance(after_extra_attack, NumberTypes) or after_extra_attack == None
        assert _isinstance(after_extra_defense, NumberTypes) or after_extra_defense == None

        return self.log('fusion_card',
                        fusion_type = fusion_type,
                        base_card_id = base_card_id,
                        base_card_rarity = base_card_rarity,
                        material_card_ids = material_card_ids,
                        material_card_quantity = material_card_quantity,
                        got_card_exp = got_card_exp,
                        before_card_level = before_card_level,
                        before_card_exp = before_card_exp,
                        before_card_hitpoint = before_card_hitpoint,
                        before_card_attack = before_card_attack,
                        before_card_defense = before_card_defense,
                        after_card_level = after_card_level,
                        after_card_exp = after_card_exp,
                        after_card_hitpoint = after_card_hitpoint,
                        after_card_attack = after_card_attack,
                        after_card_defense = after_card_defense,
                        before_card_ability1_level = before_card_ability1_level,
                        before_card_ability2_level = before_card_ability2_level,
                        before_card_ability3_level = before_card_ability3_level,
                        before_extra_attack = before_extra_attack,
                        before_extra_defense = before_extra_defense,
                        after_card_ability1_level = after_card_ability1_level,
                        after_card_ability2_level = after_card_ability2_level,
                        after_card_ability3_level = after_card_ability3_level,
                        after_extra_attack = after_extra_attack,
                        after_extra_defense = after_extra_defense,
                        **opt)

    def invitation_send(self, invitee_oid, **opt):
        u"""
        招待_送信
        
        invitee_oid -- 招待を受けたユーザのOpensocialOwnerID
        
        複数人に送信したときは複数個出力して下さい。
        """
        assert _isinstance(invitee_oid, StringTypes)

        return self.log('invitation_send',
                        invitee_oid = invitee_oid,
                        **opt)

    def invitation_receive(self, invite_from_uid, **opt):
        u"""
        招待_受信
        
        invite_from_uid -- 招待者ユーザID
        
        招待を受けてやってきたことが分かるユーザアクションが発生したときに出力して下さい。
        """
        assert _isinstance(invite_from_uid, StringTypes)

        return self.log('invitation_receive',
                        invite_from_uid = invite_from_uid,
                        **opt)

    def comeback_send(self, receiver_uid, **opt):
        u"""
        カムバックリクエスト送信
        
        receiver_uid -- 受信者UserID
        """
        assert _isinstance(receiver_uid, StringTypes)

        return self.log('comeback_send',
                        receiver_uid = receiver_uid,
                        **opt)

    def comeback_receive(self, sender_uid, **opt):
        u"""
        カムバックリクエスト受信
        
        sender_uid -- 送信者UserID
        """
        assert _isinstance(sender_uid, StringTypes)

        return self.log('comeback_receive',
                        sender_uid = sender_uid,
                        **opt)

    def use_item(self, item_type, item_id, count, event_id = None, user_level = None, boss_instance_id = None, boss_id = None, boss_type = None, boss_level = None, place_id = None, **opt):
        u"""
        アイテム_使用
        
        item_type -- アイテム種別(ItemType.[ITEM,CARD,MONEY,POINT,TREASURE,MEDAL])
        item_id -- アイテムID
        count -- 使用個数
        event_id (opt) -- イベントID
        user_level (opt) -- ユーザLv
        boss_instance_id (opt) -- 現在戦っているボスのID
        boss_id (opt) -- ボスのマスタID
        boss_type (opt) -- ボスの種類
        boss_level (opt) -- ボスのレベル
        place_id (opt) -- ボスと遭遇した時点での場所ID
        
        レイドボス遭遇中は、eraid_boss_encount で定義してあるデータを出力して下さい。
        """
        assert ItemType.any_of(item_type)
        assert _isinstance(item_id, StringTypes)
        assert _isinstance(count, NumberTypes)
        assert _isinstance(event_id, StringTypes) or event_id == None
        assert _isinstance(user_level, NumberTypes) or user_level == None
        assert _isinstance(boss_instance_id, StringTypes) or boss_instance_id == None
        assert _isinstance(boss_id, StringTypes) or boss_id == None
        assert _isinstance(boss_type, StringTypes) or boss_type == None
        assert _isinstance(boss_level, StringTypes) or boss_level == None
        assert _isinstance(place_id, StringTypes) or place_id == None

        return self.log('use_item',
                        item_type = item_type,
                        item_id = item_id,
                        count = count,
                        event_id = event_id,
                        user_level = user_level,
                        boss_instance_id = boss_instance_id,
                        boss_id = boss_id,
                        boss_type = boss_type,
                        boss_level = boss_level,
                        place_id = place_id,
                        **opt)

    def do_quest(self, area_id, step_id, is_cleared, got_progress, after_progress, **opt):
        u"""
        クエスト_実施
        
        area_id -- エリア・都市・章・県etc...
        step_id -- area_id中での区分
        is_cleared -- マップをクリアしたかどうか
        got_progress -- 取得進捗度
        after_progress -- 到達進捗度
        """
        assert _isinstance(area_id, StringTypes)
        assert _isinstance(step_id, StringTypes)
        assert _isinstance(is_cleared, bool)
        assert _isinstance(got_progress, NumberTypes) or _isinstance(got_progress, float)
        assert _isinstance(after_progress, NumberTypes) or _isinstance(after_progress, float)

        return self.log('do_quest',
                        area_id = area_id,
                        step_id = step_id,
                        is_cleared = is_cleared,
                        got_progress = got_progress,
                        after_progress = after_progress,
                        **opt)

    def change_deck(self, deck_type, operation_type, **opt):
        u"""
        デッキ操作
        
        deck_type -- デッキ種別(DeckType.[ATTACK,DEFENSE,NONE])
        operation_type -- 操作種別(DeckOperationType.[MEMBER_ADD,MEMBER_REMOVE,DECK_CREATE,DECK_DESTROY,DECK_COPY])
        
        デッキそのものの操作(作成・複製・削除)およびデッキ内カードの操作(追加・離脱)を対象としたログです。
        """
        assert DeckType.any_of(deck_type)
        assert DeckOperationType.any_of(operation_type)

        return self.log('change_deck',
                        deck_type = deck_type,
                        operation_type = operation_type,
                        **opt)

    def greet(self, target_uid, commented, **opt):
        u"""
        挨拶_実施
        
        target_uid -- 挨拶相手UserID
        commented -- コメント有無
        """
        assert _isinstance(target_uid, StringTypes)
        assert _isinstance(commented, bool)

        return self.log('greet',
                        target_uid = target_uid,
                        commented = commented,
                        **opt)

    def devote(self, target_type, target_id, step_id, **opt):
        u"""
        捧げる
        
        target_type -- 対象種別(DevoteType.[PRINCESS])
        target_id -- 対象ID
        step_id -- 段階
        """
        assert DevoteType.any_of(target_type)
        assert _isinstance(target_id, StringTypes)
        assert _isinstance(step_id, StringTypes)

        return self.log('devote',
                        target_type = target_type,
                        target_id = target_id,
                        step_id = step_id,
                        **opt)

    def allocate_power(self, power_type, added_point, current_point, **opt):
        u"""
        パワー_振り分け
        
        power_type -- 振り分け対象(PowerType.[POWER,ATTACK,DEFENSE,RESET,OTHER])
        added_point -- 増加ポイント
        current_point -- 増加後ポイント
        """
        assert PowerType.any_of(power_type)
        assert _isinstance(added_point, NumberTypes)
        assert _isinstance(current_point, NumberTypes)

        return self.log('allocate_power',
                        power_type = power_type,
                        added_point = added_point,
                        current_point = current_point,
                        **opt)

    def present_send(self, present_type, target_uid, item_type, item_id = None, **opt):
        u"""
        プレゼント_送信
        
        present_type -- プレゼント種別(PresentType.[NORMAL,OFFICIAL,PROMOTION,CAMPAIGN])
        target_uid -- 送信相手のユーザID
        item_type -- アイテム種別(ItemType.[ITEM,CARD,MONEY,POINT,TREASURE,MEDAL])
        item_id (opt) -- アイテムID
        
        注意:
          運営側からのプレゼント(補填など)の場合には uid に0を設定して下さい。
        """
        assert PresentType.any_of(present_type)
        assert _isinstance(target_uid, StringTypes)
        assert ItemType.any_of(item_type)
        assert _isinstance(item_id, StringTypes) or item_id == None

        return self.log('present_send',
                        present_type = present_type,
                        target_uid = target_uid,
                        item_type = item_type,
                        item_id = item_id,
                        **opt)

    def present_receive(self, present_type, from_uid, item_type, item_id = None, **opt):
        u"""
        プレゼント_受信
        
        present_type -- プレゼント種別(PresentType.[NORMAL,OFFICIAL,PROMOTION,CAMPAIGN])
        from_uid -- 送信元
        item_type -- アイテム種別(ItemType.[ITEM,CARD,MONEY,POINT,TREASURE,MEDAL])
        item_id (opt) -- アイテムID
        """
        assert PresentType.any_of(present_type)
        assert _isinstance(from_uid, StringTypes)
        assert ItemType.any_of(item_type)
        assert _isinstance(item_id, StringTypes) or item_id == None

        return self.log('present_receive',
                        present_type = present_type,
                        from_uid = from_uid,
                        item_type = item_type,
                        item_id = item_id,
                        **opt)

    def guild_operation(self, operation_type, guild_id = None, **opt):
        u"""
        ギルド_運営
        
        operation_type -- 操作種別(GuildOperationType.[CREATE,DROP,OTHER])
        guild_id (opt) -- ギルドID
        """
        assert GuildOperationType.any_of(operation_type)
        assert _isinstance(guild_id, StringTypes) or guild_id == None

        return self.log('guild_operation',
                        operation_type = operation_type,
                        guild_id = guild_id,
                        **opt)

    def guild_member_operation(self, operation_type, target_uid = None, guild_id = None, **opt):
        u"""
        ギルドメンバ_運営
        
        operation_type -- 操作種別(GuildMemberOperationType.[JOIN,LEAVE,KICK_OFF,HANDOVER,OTHER])
        target_uid (opt) -- 対象メンバUserID
        guild_id (opt) -- ギルドID
        """
        assert GuildMemberOperationType.any_of(operation_type)
        assert _isinstance(target_uid, StringTypes) or target_uid == None
        assert _isinstance(guild_id, StringTypes) or guild_id == None

        return self.log('guild_member_operation',
                        operation_type = operation_type,
                        target_uid = target_uid,
                        guild_id = guild_id,
                        **opt)

    def boss_battle(self, area_id, step_id, battle_result, player_deck = None, **opt):
        u"""
        ボスと戦闘
        
        area_id -- エリア・都市・章・県etc...
        step_id -- area_id中での区分
        battle_result -- バトル結果(BattleResult.[WIN,LOSE,NONE])
        player_deck (opt) -- 攻撃する側のデッキ
        
        デッキ情報については battle_attack を参照して下さい。
        """
        assert _isinstance(area_id, StringTypes)
        assert _isinstance(step_id, StringTypes)
        assert BattleResult.any_of(battle_result)
        assert self._or_none(self._string_list)(player_deck)

        return self.log('boss_battle',
                        area_id = area_id,
                        step_id = step_id,
                        battle_result = battle_result,
                        player_deck = player_deck,
                        **opt)

    def change_wishlist(self, operation_type, object_type, object_id, **opt):
        u"""
        欲しい物リスト_更新
        
        operation_type -- 操作種別(WishlistOperationType.[APPEND,REMOVE])
        object_type -- 対象種別(ItemType.[ITEM,CARD,MONEY,POINT,TREASURE,MEDAL])
        object_id -- 対象ID
        """
        assert WishlistOperationType.any_of(operation_type)
        assert ItemType.any_of(object_type)
        assert _isinstance(object_id, StringTypes)

        return self.log('change_wishlist',
                        operation_type = operation_type,
                        object_type = object_type,
                        object_id = object_id,
                        **opt)

    def exchange_item(self, exchange_type, **opt):
        u"""
        アイテム交換
        
        exchange_type -- 交換種別(ExchangeType.[CARD_TO_MEDAL,MEDAL_TO_ITEM])
        """
        assert ExchangeType.any_of(exchange_type)

        return self.log('exchange_item',
                        exchange_type = exchange_type,
                        **opt)

    def participate_event(self, event_type, event_id, **opt):
        u"""
        イベント_参加
        
        event_type -- イベント種別(EventType.[QUEST,RAID,USER])
        event_id -- イベントID
        """
        assert EventType.any_of(event_type)
        assert _isinstance(event_id, StringTypes)

        return self.log('participate_event',
                        event_type = event_type,
                        event_id = event_id,
                        **opt)

    def eqst_do_quest(self, event_id, area_id, step_id, is_cleared, got_progress, after_progress, **opt):
        u"""
        イベント_クエスト_クエスト実施
        
        event_id -- イベントID
        area_id -- エリア・都市・章・県etc...
        step_id -- area_id中での区分
        is_cleared -- 達成時のみ記載
        got_progress -- 取得進捗度
        after_progress -- 到達進捗度
        
        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。
        """
        assert _isinstance(event_id, StringTypes)
        assert _isinstance(area_id, StringTypes)
        assert _isinstance(step_id, StringTypes)
        assert _isinstance(is_cleared, bool)
        assert _isinstance(got_progress, NumberTypes) or _isinstance(got_progress, float)
        assert _isinstance(after_progress, NumberTypes) or _isinstance(after_progress, float)

        return self.log('eqst_do_quest',
                        event_id = event_id,
                        area_id = area_id,
                        step_id = step_id,
                        is_cleared = is_cleared,
                        got_progress = got_progress,
                        after_progress = after_progress,
                        **opt)

    def eqst_boss_battle(self, event_id, area_id, step_id, result, player_deck = None, **opt):
        u"""
        イベント_クエスト_ボスバトル実施
        
        event_id -- イベントID
        area_id -- エリア・都市・章・県etc...
        step_id -- area_id中での区分
        result -- バトル結果(BattleResult.[WIN,LOSE,NONE])
        player_deck (opt) -- 攻撃する側のデッキ
        
        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。
        
        デッキ情報については battle_attack を参照して下さい。
        """
        assert _isinstance(event_id, StringTypes)
        assert _isinstance(area_id, StringTypes)
        assert _isinstance(step_id, StringTypes)
        assert BattleResult.any_of(result)
        assert self._or_none(self._string_list)(player_deck)

        return self.log('eqst_boss_battle',
                        event_id = event_id,
                        area_id = area_id,
                        step_id = step_id,
                        result = result,
                        player_deck = player_deck,
                        **opt)

    def eraid_do_quest(self, event_id, area_id, step_id, is_cleared, got_progress, after_progress, **opt):
        u"""
        イベント_レイド_クエスト実施
        
        event_id -- イベントID
        area_id -- エリア・都市・章・県etc...
        step_id -- area_id中での区分
        is_cleared -- 達成時のみ記載
        got_progress -- 取得進捗度
        after_progress -- 到達進捗度
        
        通常クエストのマップを利用するのであれば、このアクションは不要です。
        
        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。
        """
        assert _isinstance(event_id, StringTypes)
        assert _isinstance(area_id, StringTypes)
        assert _isinstance(step_id, StringTypes)
        assert _isinstance(is_cleared, bool)
        assert _isinstance(got_progress, NumberTypes) or _isinstance(got_progress, float)
        assert _isinstance(after_progress, NumberTypes) or _isinstance(after_progress, float)

        return self.log('eraid_do_quest',
                        event_id = event_id,
                        area_id = area_id,
                        step_id = step_id,
                        is_cleared = is_cleared,
                        got_progress = got_progress,
                        after_progress = after_progress,
                        **opt)

    def eraid_boss_encount(self, event_id, user_level, boss_instance_id, boss_id, boss_type, boss_level, place_id, **opt):
        u"""
        イベント_レイド_ボス遭遇
        
        event_id -- イベントID
        user_level -- ユーザLv
        boss_instance_id -- 現在戦っているボスのID
        boss_id -- ボスのマスタID
        boss_type -- ボスの種類
        boss_level -- ボスのレベル
        place_id -- ボスと遭遇した時点での場所ID
        
        event_id には、各イベントで一意になるような文字列を入れて下さい。
        
        user_level には、プレイヤーのレベルを入れて下さい。（プレイヤーのIDはデフォルトで入るようになっているはずなので、パラメータには入れていません。）
                これはプレイヤーのレベル帯別で分析するために利用します。
        
        boss_instance_id には、ユーザが遭遇したボス毎に異なるIDを入れて下さい。
        
        boss_id には、レイドボスのマスタIDを入れて下さい。
        
        boss_type には、レイドボスの種類を入れて下さい。
                １つのイベントでレイドボスが複数キャラ出現することがあるので、それらを分けるために利用します。
        
        boss_level には、ボスのレベルを入れて下さい。
        
        place_id には、『そのボスと遭遇した時点での』場所IDを入れて下さい。これは、ボスと遭遇した後、例えば上級者用マップから初級者用に移動した場合などの、全く違うマップに移動した場合、解析するのが難しくなるからです。
        """
        assert _isinstance(event_id, StringTypes)
        assert _isinstance(user_level, NumberTypes)
        assert _isinstance(boss_instance_id, StringTypes)
        assert _isinstance(boss_id, StringTypes)
        assert _isinstance(boss_type, StringTypes)
        assert _isinstance(boss_level, StringTypes)
        assert _isinstance(place_id, StringTypes)

        return self.log('eraid_boss_encount',
                        event_id = event_id,
                        user_level = user_level,
                        boss_instance_id = boss_instance_id,
                        boss_id = boss_id,
                        boss_type = boss_type,
                        boss_level = boss_level,
                        place_id = place_id,
                        **opt)

    def eraid_boss_battle(self, event_id, user_level, boss_instance_id, boss_id, boss_type, boss_level, place_id, finder_uid, finder_level, damage, use_point, boss_hp, player_deck = None, **opt):
        u"""
        イベント_レイド_ボスバトル実施
        
        event_id -- イベントID
        user_level -- ユーザLv
        boss_instance_id -- 現在戦っているボスのID
        boss_id -- ボスのマスタID
        boss_type -- ボスの種類
        boss_level -- ボスのレベル
        place_id -- ボスと遭遇した時点での場所ID
        finder_uid -- 発見者のユーザID
        finder_level -- 発見者のレベル
        damage -- 与えたダメージ
        use_point -- 何ポイント使ったか
        boss_hp -- 攻撃した後のボスの残り体力
        player_deck (opt) -- 攻撃する側のデッキ
        
        デッキ情報については battle_attack を参照して下さい。
        event_id 〜 place_id までのパラメータについては eraid_boss_encount を参照して下さい。
        
        finder_uid や finder_level には、発見者のユーザIDやレベルを入れて下さい。
                発見者と攻撃したユーザが異なっていた場合、救援攻撃であると判断します。
        damage には、ボスに実際に与えたダメージを入れて下さい。
        
        use_point には、攻撃ポイントなどを、何ポイント使ってボスに攻撃したかを入れて下さい。
                実際に与えたダメージが、何ポイント使った結果なのかを知るために必要です。
        
        boss_hp には、ボスの残り体力を入れて下さい。オーバーキルなどでなければ、通常は boss_hp+damage が攻撃前のボスの体力になるはずです。
        """
        assert _isinstance(event_id, StringTypes)
        assert _isinstance(user_level, NumberTypes)
        assert _isinstance(boss_instance_id, StringTypes)
        assert _isinstance(boss_id, StringTypes)
        assert _isinstance(boss_type, StringTypes)
        assert _isinstance(boss_level, StringTypes)
        assert _isinstance(place_id, StringTypes)
        assert _isinstance(finder_uid, StringTypes)
        assert _isinstance(finder_level, StringTypes)
        assert _isinstance(damage, NumberTypes)
        assert _isinstance(use_point, NumberTypes)
        assert _isinstance(boss_hp, NumberTypes)
        assert self._or_none(self._string_list)(player_deck)

        return self.log('eraid_boss_battle',
                        event_id = event_id,
                        user_level = user_level,
                        boss_instance_id = boss_instance_id,
                        boss_id = boss_id,
                        boss_type = boss_type,
                        boss_level = boss_level,
                        place_id = place_id,
                        finder_uid = finder_uid,
                        finder_level = finder_level,
                        damage = damage,
                        use_point = use_point,
                        boss_hp = boss_hp,
                        player_deck = player_deck,
                        **opt)

    def eraid_send_rescue(self, event_id, user_level, boss_instance_id, boss_id, boss_type, boss_level, place_id, receiver_uid, receiver_level, **opt):
        u"""
        イベント_レイド_救援送信
        
        event_id -- イベントID
        user_level -- ユーザLv
        boss_instance_id -- 現在戦っているボスのID
        boss_id -- ボスのマスタID
        boss_type -- ボスの種類
        boss_level -- ボスのレベル
        place_id -- ボスと遭遇した時点での場所ID
        receiver_uid -- 受信者のユーザID
        receiver_level -- 受信者のレベル
        
        救援要請を出した場合にこのログを出力して下さい。
        複数ユーザに送る場合、複数回に分けてログを出して下さい。
        
        デッキ情報については battle_attack を参照して下さい。
        event_id 〜 place_id までのパラメータについては eraid_boss_encount を参照して下さい。
        """
        assert _isinstance(event_id, StringTypes)
        assert _isinstance(user_level, NumberTypes)
        assert _isinstance(boss_instance_id, StringTypes)
        assert _isinstance(boss_id, StringTypes)
        assert _isinstance(boss_type, StringTypes)
        assert _isinstance(boss_level, StringTypes)
        assert _isinstance(place_id, StringTypes)
        assert _isinstance(receiver_uid, StringTypes)
        assert _isinstance(receiver_level, StringTypes)

        return self.log('eraid_send_rescue',
                        event_id = event_id,
                        user_level = user_level,
                        boss_instance_id = boss_instance_id,
                        boss_id = boss_id,
                        boss_type = boss_type,
                        boss_level = boss_level,
                        place_id = place_id,
                        receiver_uid = receiver_uid,
                        receiver_level = receiver_level,
                        **opt)

    def eraid_receive_rescue(self, event_id, battle_id, boss_id, boss_instance_id, sender_uid, **opt):
        u"""
        イベント_レイド_救援受信
        
        event_id -- イベントID
        battle_id -- バトルID
        boss_id -- ボスID
        boss_instance_id -- ボスインスタンスID
        sender_uid -- 送信者UserID
        
        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。
        
        このログは、救援を受けてやってきたと判断できるユーザアクションがあった場所で出力して下さい。
        例えば救援要請のページを踏んだときなどに出力して下さい。
        """
        assert _isinstance(event_id, StringTypes)
        assert _isinstance(battle_id, StringTypes)
        assert _isinstance(boss_id, StringTypes)
        assert _isinstance(boss_instance_id, StringTypes)
        assert _isinstance(sender_uid, StringTypes)

        return self.log('eraid_receive_rescue',
                        event_id = event_id,
                        battle_id = battle_id,
                        boss_id = boss_id,
                        boss_instance_id = boss_instance_id,
                        sender_uid = sender_uid,
                        **opt)

    def ebtl_user_battle(self, event_id, target_uid, battle_result, show_trap, show_damnation, target_item_category, target_item_id, user_level, target_user_level, player_deck = None, target_deck = None, **opt):
        u"""
        イベント_バトル_ユーザ間バトル
        
        event_id -- イベントID
        target_uid -- バトル相手
        battle_result -- バトル結果(BattleResult.[WIN,LOSE,NONE])
        show_trap -- 罠発動の有無
        show_damnation -- 天罰発動の有無
        target_item_category -- 略奪対象カテゴリ(BattleTargetCategory.[ITEM,NONE])
        target_item_id -- 略奪対象ID
        user_level -- ユーザLv.
        target_user_level -- バトル相手Lv.
        player_deck (opt) -- 攻撃する側のデッキ
        target_deck (opt) -- 攻撃される側のデッキ
        
        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。
        
        デッキ情報については battle_attack を参照して下さい。
        """
        assert _isinstance(event_id, StringTypes)
        assert _isinstance(target_uid, StringTypes)
        assert BattleResult.any_of(battle_result)
        assert _isinstance(show_trap, bool)
        assert _isinstance(show_damnation, bool)
        assert BattleTargetCategory.any_of(target_item_category)
        assert _isinstance(target_item_id, StringTypes)
        assert _isinstance(user_level, NumberTypes)
        assert _isinstance(target_user_level, NumberTypes)
        assert self._or_none(self._string_list)(player_deck)
        assert self._string_list(target_deck)

        return self.log('ebtl_user_battle',
                        event_id = event_id,
                        target_uid = target_uid,
                        battle_result = battle_result,
                        show_trap = show_trap,
                        show_damnation = show_damnation,
                        target_item_category = target_item_category,
                        target_item_id = target_item_id,
                        user_level = user_level,
                        target_user_level = target_user_level,
                        player_deck = player_deck,
                        target_deck = target_deck,
                        **opt)

    def do_tutorial(self, tutorial_step, **opt):
        u"""
        チュートリアル
        
        tutorial_step -- チュートリアルの進捗番号
        
        チュートリアルの進度を計測するためのログです。
        """
        assert _isinstance(tutorial_step, NumberTypes)

        return self.log('do_tutorial',
                        tutorial_step = tutorial_step,
                        **opt)

    def view_page(self, location_type, url, **opt):
        u"""
        ページ表示
        
        location_type -- 表示ページの種類
        url -- 表示ページのURL
        
        ページビューを計測するためのログです。
        """
        assert _isinstance(location_type, StringTypes)
        assert _isinstance(url, StringTypes)

        return self.log('view_page',
                        location_type = location_type,
                        url = url,
                        **opt)

    def do_user_trade(self, status, proposed_time, proposed_uid, proposed_items, wish_items, accepted_time = None, trade_id = None, **opt):
        u"""
        トレード
        
        status -- トレードステータス(TradeStatus.[APPLY,ACCEPT,CANCEL,FINISH])
        proposed_time -- 出品日時
        proposed_uid -- 出品ユーザID
        proposed_items -- 出品アイテム一覧（例: ['ITEM/100/0/3', 'CARD/200/5/1']）
        wish_items -- 希望アイテム一覧（例: ['ITEM/100/0/3', 'CARD/200/5/1']）
        accepted_time (opt) -- トレード成立日時
        trade_id (opt) -- トレードID
        """
        assert TradeStatus.any_of(status)
        assert _isinstance(proposed_time, datetime)
        assert _isinstance(proposed_uid, StringTypes)
        assert _isinstance(accepted_time, datetime) or accepted_time == None
        assert _isinstance(trade_id, str) or trade_id == None
        assert self._is_trade_items(proposed_items)
        assert self._is_trade_items(wish_items)

        return self.log('do_user_trade',
                        status = status,
                        proposed_time = proposed_time,
                        proposed_uid = proposed_uid,
                        proposed_items = proposed_items,
                        wish_items = wish_items,
                        accepted_time = accepted_time,
                        trade_id = trade_id,
                        **opt)

    def ab_test(self, test_id, is_view, action = None, **opt):
        u"""
        ABテスト
        
        test_id -- テストID
        is_view -- ページの表示かどうか
        action (opt) -- ユーザの行動（テスト結果）。is_view == False のときのみ有効。
        
        注意:
          ABテストが実装されたページ(ユーザ選択前)へのアクセス履歴(is_view:True)も出力する必要があります。
        """
        assert _isinstance(test_id, StringTypes)
        assert _isinstance(is_view, bool)
        assert _isinstance(action, StringTypes) or action == None

        return self.log('ab_test',
                        test_id = test_id,
                        is_view = is_view,
                        action = action,
                        **opt)

    def friendship(self, action_type, target_uid, **opt):
        u"""
        友達
        
        action_type -- 行動タイプ(FriendActionType.[REQUEST,ACCEPT,CANCEL,REMOVE])
        target_uid -- 対象ユーザID
        """
        assert FriendActionType.any_of(action_type)
        assert _isinstance(target_uid, StringTypes)

        return self.log('friendship',
                        action_type = action_type,
                        target_uid = target_uid,
                        **opt)

    def platform_comment(self, comment_type, comment_id, **opt):
        u"""
        コメント
        
        comment_type -- コメント種別
        comment_id -- コメントID
        
        ひとことコメントするとアイテムが貰えるとか、そういったコメントを行ったときに出力して下さい。
        
        comment_type には、CommentType.EVENT や CommentType.DIARY といった、大分別を書いて下さい。
        CommentType のどれにも当てはまらない無い場合は、任意の文字列を追加しても構いません。
        
        comment_id には、例えば comment_type が CommentType.EVENT ならイベント名を、comment_type が CommentType.COMPLETE ならコンプリートしたアイテム名などを記述して下さい。
        """
        assert CommentType.any_of(comment_type) or _isinstance(comment_type, StringTypes)
        assert _isinstance(comment_id, StringTypes)

        return self.log('platform_comment',
                        comment_type = comment_type,
                        comment_id = comment_id,
                        **opt)
