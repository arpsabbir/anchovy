# coding: utf-8

from auto_make import *
import auto_make_types

funcs = [{
    'summary': '新規登録',
    'name': 'register',
    'params': [{
        'name': 'register_type',
        'summary': '登録チャネル',
        'type': 'RegisterType'
    }]
},{
    'summary': '課金',
    'name': 'pay',
    'description': """
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
    """,
    'params': [{
        'name': 'payment_category',
        'summary': '課金対象カテゴリ',
        'type': 'PaymentCategory'
    },{
        'name': 'payment_subcategory',
        'summary': '課金対象サブカテゴリ',
        'type': 'PaymentSubcategory'
    },{
        'name': 'target_id',
        'summary': '課金アイテムID',
        'type': 'StringTypes'
    },{
        'name': 'unit_price',
        'summary': '単価',
        'type': 'NumberTypes'
    },{
        'name': 'quantity',
        'summary': '個数',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'バトル_攻撃',
    'name': 'battle_attack',
    'description': """
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
    """,
    'params': [{
        'name': 'target_uid',
        'summary': 'バトル相手',
        'type': 'StringTypes'
    },{
        'name': 'battle_result',
        'summary': 'バトル結果',
        'type': 'BattleResult'
    },{
        'name': 'target_item_category',
        'summary': '略奪対象カテゴリ',
        'type': 'BattleTargetCategory'
    },{
        'name': 'target_item_id',
        'summary': '略奪対象アイテムID',
        'type': 'StringTypes'
    },{
        'name': 'user_level',
        'summary': 'ユーザLv.',
        'type': 'NumberTypes'
    },{
        'name': 'target_user_level',
        'summary': 'バトル相手Lv.',
        'type': 'NumberTypes'
    },{
        'name': 'show_trap',
        'summary': '罠発動の有無',
        'type': 'bool',
        'default': None
    },{
        'name': 'show_damnation',
        'summary': '天罰発動の有無',
        'type': 'bool',
        'default': None
    },{
        'name': 'player_deck',
        'summary': '攻撃する側のデッキ',
        'assert': 'self._or_none(self._string_list)',
        'default': None
    },{
        'name': 'target_deck',
        'summary': '攻撃される側のデッキ',
        'assert': 'self._or_none(self._string_list)',
        'default': None
    }]
},{
    'summary': 'ガチャ実施',
    'name': 'do_gacha',
    'description': """
      注意:
        課金ガチャの場合はこのログと同時に pay アクションログも出力する必要があります。
    """,
    'params': [{
        'name': 'gacha_type',
        'summary': '実施種別',
        'type': 'GachaType'
    },{
        'name': 'count',
        'summary': 'カードの同時取得枚数',
        'type': 'NumberTypes'
    },{
        'name': 'gacha_id',
        'summary': 'ガチャID',
        'type': 'StringTypes'
    }]
},{
    'summary': 'カード合成',
    'name': 'fusion_card',
    'description': """
      注意:
        base_card_id, material_card_ids にはレコードのインスタンスIDではなくカードマスタのIDを入れて下さい。
        material_card_ids は複数カードの合成を想定し、ID の list を挿入して下さい。
    """,
    'params': [{
        'name': 'fusion_type',
        'summary': '合成種別',
        'type': 'FusionType'
    },{
        'name': 'base_card_id',
        'summary': '素材カードID',
        'type': 'StringTypes'
    },{
        'name': 'base_card_rarity',
        'summary': '素材カードレアリティ',
        'type': 'NumberTypes'
    },{
        'name': 'material_card_ids',
        'summary': '消費カードID(s)',
        'type': 'list'
    },{
        'name': 'material_card_quantity',
        'summary': '消費カード枚数',
        'type': 'NumberTypes'
    },{
        'name': 'got_card_exp',
        'summary': '取得経験値',
        'type': 'NumberTypes'
    },{
        'name': 'before_card_level',
        'summary': '合成前Lv.',
        'type': 'NumberTypes'
    },{
        'name': 'before_card_exp',
        'summary': '合成前カード経験値',
        'type': 'NumberTypes'
    },{
        'name': 'before_card_hitpoint',
        'summary': '合成前カードHP',
        'type': 'NumberTypes'
    },{
        'name': 'before_card_attack',
        'summary': '合成前攻撃力',
        'type': 'NumberTypes'
    },{
        'name': 'before_card_defense',
        'summary': '合成前防御力',
        'type': 'NumberTypes'
    },{
        'name': 'after_card_level',
        'summary': '合成後Lv.',
        'type': 'NumberTypes'
    },{
        'name': 'after_card_exp',
        'summary': '合成後カード経験値',
        'type': 'NumberTypes'
    },{
        'name': 'after_card_hitpoint',
        'summary': '合成後カードHP',
        'type': 'NumberTypes'
    },{
        'name': 'after_card_attack',
        'summary': '合成後攻撃力',
        'type': 'NumberTypes'
    },{
        'name': 'after_card_defense',
        'summary': '合成後防御力',
        'type': 'NumberTypes'
    },{
        'name': 'before_card_ability1_level',
        'summary': '合成前スキル1Lv.',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'before_card_ability2_level',
        'summary': '合成前スキル2Lv.',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'before_card_ability3_level',
        'summary': '合成前スキル3Lv.',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'before_extra_attack',
        'summary': '合成前追加攻撃力',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'before_extra_defense',
        'summary': '合成前追加防御力',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'after_card_ability1_level',
        'summary': '合成後スキル1Lv.',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'after_card_ability2_level',
        'summary': '合成後スキル2Lv.',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'after_card_ability3_level',
        'summary': '合成後スキル3Lv.',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'after_extra_attack',
        'summary': '合成後追加攻撃力',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'after_extra_defense',
        'summary': '合成後追加防御力',
        'type': 'NumberTypes',
        'default': None
    }]
},{
    'summary': '招待_送信',
    'name': 'invitation_send',
    'description': """
        複数人に送信したときは複数個出力して下さい。
    """,
    'params': [{
        'name': 'invitee_oid',
        'summary': '招待を受けたユーザのOpensocialOwnerID',
        'type': 'StringTypes'
    }]
},{
    'summary': '招待_受信',
    'name': 'invitation_receive',
    'description': """
        招待を受けてやってきたことが分かるユーザアクションが発生したときに出力して下さい。
    """,
    'params': [{
        'name': 'invite_from_uid',
        'summary': '招待者ユーザID',
        'type': 'StringTypes'
    }]
},{
    'summary': 'カムバックリクエスト送信',
    'name': 'comeback_send',
    'params': [{
        'name': 'receiver_uid',
        'summary': '受信者UserID',
        'type': 'StringTypes'
    }]
},{
    'summary': 'カムバックリクエスト受信',
    'name': 'comeback_receive',
    'params': [{
        'name': 'sender_uid',
        'summary': '送信者UserID',
        'type': 'StringTypes'
    }]
},{
    'summary': 'アイテム_使用',
    'name': 'use_item',
    'description': """
        レイドボス遭遇中は、eraid_boss_encount で定義してあるデータを出力して下さい。
    """,
    'params': [{
        'name': 'item_type',
        'summary': 'アイテム種別',
        'type': 'ItemType'
    },{
        'name': 'item_id',
        'summary': 'アイテムID',
        'type': 'StringTypes'
    },{
        'name': 'count',
        'summary': '使用個数',
        'type': 'NumberTypes'
    },{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes',
        'default': None
    },{
        'name': 'user_level',
        'summary': 'ユーザLv',
        'type': 'NumberTypes',
        'default': None
    },{
        'name': 'boss_instance_id',
        'summary': '現在戦っているボスのID',
        'type': 'StringTypes',
        'default': None
    },{
        'name': 'boss_id',
        'summary': 'ボスのマスタID',
        'type': 'StringTypes',
        'default': None
    },{
        'name': 'boss_type',
        'summary': 'ボスの種類',
        'type': 'StringTypes',
        'default': None
    },{
        'name': 'boss_level',
        'summary': 'ボスのレベル',
        'type': 'StringTypes',
        'default': None
    },{
        'name': 'place_id',
        'summary': 'ボスと遭遇した時点での場所ID',
        'type': 'StringTypes',
        'default': None
    }]
},{
    'summary': 'クエスト_実施',
    'name': 'do_quest',
    'params': [{
        'name': 'area_id',
        'summary': 'エリア・都市・章・県etc...',
        'type': 'StringTypes'
    },{
        'name': 'step_id',
        'summary': 'area_id中での区分',
        'type': 'StringTypes'
    },{
        'name': 'is_cleared',
        'summary': 'マップをクリアしたかどうか',
        'type': 'bool'
    },{
        'name': 'got_progress',
        'summary': '取得進捗度',
        'type': ['NumberTypes', 'float']
    },{
        'name': 'after_progress',
        'summary': '到達進捗度',
        'type': ['NumberTypes', 'float']
    }]
},{
    'summary': 'デッキ操作',
    'name': 'change_deck',
    'description': """
      デッキそのものの操作(作成・複製・削除)およびデッキ内カードの操作(追加・離脱)を対象としたログです。
    """,
    'params': [{
        'name': 'deck_type',
        'summary': 'デッキ種別',
        'type': 'DeckType'
    },{
        'name': 'operation_type',
        'summary': '操作種別',
        'type': 'DeckOperationType'
    }]
},{
    'summary': '挨拶_実施',
    'name': 'greet',
    'params': [{
        'name': 'target_uid',
        'summary': '挨拶相手UserID',
        'type': 'StringTypes'
    },{
        'name': 'commented',
        'summary': 'コメント有無',
        'type': 'bool'
    }]
},{
    'summary': '捧げる',
    'name': 'devote',
    'params': [{
        'name': 'target_type',
        'summary': '対象種別',
        'type': 'DevoteType'
    },{
        'name': 'target_id',
        'summary': '対象ID',
        'type': 'StringTypes'
    },{
        'name': 'step_id',
        'summary': '段階',
        'type': 'StringTypes'
    }]
},{
    'summary': 'パワー_振り分け',
    'name': 'allocate_power',
    'params': [{
        'name': 'power_type',
        'summary': '振り分け対象',
        'type': 'PowerType'
    },{
        'name': 'added_point',
        'summary': '増加ポイント',
        'type': 'NumberTypes'
    },{
        'name': 'current_point',
        'summary': '増加後ポイント',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'プレゼント_送信',
    'name': 'present_send',
    'description': """
      注意:
        運営側からのプレゼント(補填など)の場合には uid に0を設定して下さい。
    """,
    'params': [{
        'name': 'present_type',
        'summary': 'プレゼント種別',
        'type': 'PresentType'
    },{
        'name': 'target_uid',
        'summary': '送信相手のユーザID',
        'type': 'StringTypes'
    },{
        'name': 'item_type',
        'summary': 'アイテム種別',
        'type': 'ItemType'
    },{
        'name': 'item_id',
        'summary': 'アイテムID',
        'type': 'StringTypes',
        'default': None
    }]
},{
    'summary': 'プレゼント_受信',
    'name': 'present_receive',
    'params': [{
        'name': 'present_type',
        'summary': 'プレゼント種別',
        'type': 'PresentType'
    },{
        'name': 'from_uid',
        'summary': '送信元',
        'type': 'StringTypes'
    },{
        'name': 'item_type',
        'summary': 'アイテム種別',
        'type': 'ItemType'
    },{
        'name': 'item_id',
        'summary': 'アイテムID',
        'type': 'StringTypes',
        'default': None
    }]
},{
    'summary': 'ギルド_運営',
    'name': 'guild_operation',
    'params': [{
        'name': 'operation_type',
        'summary': '操作種別',
        'type': 'GuildOperationType'
    },{
        'name': 'guild_id',
        'summary': 'ギルドID',
        'type': 'StringTypes',
        'default': None
    }]
},{
    'summary': 'ギルドメンバ_運営',
    'name': 'guild_member_operation',
    'params': [{
        'name': 'operation_type',
        'summary': '操作種別',
        'type': 'GuildMemberOperationType'
    },{
        'name': 'target_uid',
        'summary': '対象メンバUserID',
        'type': 'StringTypes',
        'default': None
    },{
        'name': 'guild_id',
        'summary': 'ギルドID',
        'type': 'StringTypes',
        'default': None
    }]
},{
    'summary': 'ボスと戦闘',
    'name': 'boss_battle',
    'description': """
        デッキ情報については battle_attack を参照して下さい。
    """,
    'params': [{
        'name': 'area_id',
        'summary': 'エリア・都市・章・県etc...',
        'type': 'StringTypes'
    },{
        'name': 'step_id',
        'summary': 'area_id中での区分',
        'type': 'StringTypes'
    },{
        'name': 'battle_result',
        'summary': 'バトル結果',
        'type': 'BattleResult'
    },{
        'name': 'player_deck',
        'summary': '攻撃する側のデッキ',
        'assert': 'self._or_none(self._string_list)',
        'default': None
    }]
},{
    'summary': '欲しい物リスト_更新',
    'name': 'change_wishlist',
    'params': [{
        'name': 'operation_type',
        'summary': '操作種別',
        'type': 'WishlistOperationType'
    },{
        'name': 'object_type',
        'summary': '対象種別',
        'type': 'ItemType'
    },{
        'name': 'object_id',
        'summary': '対象ID',
        'type': 'StringTypes'
    }]
},{
    'summary': 'アイテム交換',
    'name': 'exchange_item',
    'params': [{
        'name': 'exchange_type',
        'summary': '交換種別',
        'type': 'ExchangeType'
    }]
},{
    'summary': 'イベント_参加',
    'name': 'participate_event',
    'params': [{
        'name': 'event_type',
        'summary': 'イベント種別',
        'type': 'EventType'
    },{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes'
    }]
},{
    'summary': 'イベント_クエスト_クエスト実施',
    'name': 'eqst_do_quest',
    'description': """
        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。
    """,
    'params': [{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes'
    },{
        'name': 'area_id',
        'summary': 'エリア・都市・章・県etc...',
        'type': 'StringTypes'
    },{
        'name': 'step_id',
        'summary': 'area_id中での区分',
        'type': 'StringTypes'
    },{
        'name': 'is_cleared',
        'summary': '達成時のみ記載',
        'type': 'bool'
    },{
        'name': 'got_progress',
        'summary': '取得進捗度',
        'type': ['NumberTypes', 'float']
    },{
        'name': 'after_progress',
        'summary': '到達進捗度',
        'type': ['NumberTypes', 'float']
    }]
},{
    'summary': 'イベント_クエスト_ボスバトル実施',
    'name': 'eqst_boss_battle',
    'description': """
        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。

        デッキ情報については battle_attack を参照して下さい。
    """,
    'params': [{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes'
    },{
        'name': 'area_id',
        'summary': 'エリア・都市・章・県etc...',
        'type': 'StringTypes'
    },{
        'name': 'step_id',
        'summary': 'area_id中での区分',
        'type': 'StringTypes'
    },{
        'name': 'result',
        'summary': 'バトル結果',
        'type': 'BattleResult'
    },{
        'name': 'player_deck',
        'summary': '攻撃する側のデッキ',
        'assert': 'self._or_none(self._string_list)',
        'default': None
    }]
},{
    'summary': 'イベント_レイド_クエスト実施',
    'name': 'eraid_do_quest',
    'description': """
        通常クエストのマップを利用するのであれば、このアクションは不要です。

        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。
    """,
    'params': [{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes'
    },{
        'name': 'area_id',
        'summary': 'エリア・都市・章・県etc...',
        'type': 'StringTypes'
    },{
        'name': 'step_id',
        'summary': 'area_id中での区分',
        'type': 'StringTypes'
    },{
        'name': 'is_cleared',
        'summary': '達成時のみ記載',
        'type': 'bool'
    },{
        'name': 'got_progress',
        'summary': '取得進捗度',
        'type': ['NumberTypes', 'float']
    },{
        'name': 'after_progress',
        'summary': '到達進捗度',
        'type': ['NumberTypes', 'float']
    }]
},{
    'summary': 'イベント_レイド_ボス遭遇',
    'name': 'eraid_boss_encount',
    'description': """
        event_id には、各イベントで一意になるような文字列を入れて下さい。

        user_level には、プレイヤーのレベルを入れて下さい。（プレイヤーのIDはデフォルトで入るようになっているはずなので、パラメータには入れていません。）
                これはプレイヤーのレベル帯別で分析するために利用します。

        boss_instance_id には、ユーザが遭遇したボス毎に異なるIDを入れて下さい。

        boss_id には、レイドボスのマスタIDを入れて下さい。

        boss_type には、レイドボスの種類を入れて下さい。
                １つのイベントでレイドボスが複数キャラ出現することがあるので、それらを分けるために利用します。

        boss_level には、ボスのレベルを入れて下さい。

        place_id には、『そのボスと遭遇した時点での』場所IDを入れて下さい。これは、ボスと遭遇した後、例えば上級者用マップから初級者用に移動した場合などの、全く違うマップに移動した場合、解析するのが難しくなるからです。
    """,
    'params': [{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes'
    },{
        'name': 'user_level',
        'summary': 'ユーザLv',
        'type': 'NumberTypes'
    },{
        'name': 'boss_instance_id',
        'summary': '現在戦っているボスのID',
        'type': 'StringTypes'
    },{
        'name': 'boss_id',
        'summary': 'ボスのマスタID',
        'type': 'StringTypes'
    },{
        'name': 'boss_type',
        'summary': 'ボスの種類',
        'type': 'StringTypes'
    },{
        'name': 'boss_level',
        'summary': 'ボスのレベル',
        'type': 'StringTypes'
    },{
        'name': 'place_id',
        'summary': 'ボスと遭遇した時点での場所ID',
        'type': 'StringTypes'
    }]
},{
    'summary': 'イベント_レイド_ボスバトル実施',
    'name': 'eraid_boss_battle',
    'description': """
        デッキ情報については battle_attack を参照して下さい。
        event_id 〜 place_id までのパラメータについては eraid_boss_encount を参照して下さい。

        finder_uid や finder_level には、発見者のユーザIDやレベルを入れて下さい。
                発見者と攻撃したユーザが異なっていた場合、救援攻撃であると判断します。
        damage には、ボスに実際に与えたダメージを入れて下さい。

        use_point には、攻撃ポイントなどを、何ポイント使ってボスに攻撃したかを入れて下さい。
                実際に与えたダメージが、何ポイント使った結果なのかを知るために必要です。

        boss_hp には、ボスの残り体力を入れて下さい。オーバーキルなどでなければ、通常は boss_hp+damage が攻撃前のボスの体力になるはずです。
    """,
    'params': [{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes'
    },{
        'name': 'user_level',
        'summary': 'ユーザLv',
        'type': 'NumberTypes'
    },{
        'name': 'boss_instance_id',
        'summary': '現在戦っているボスのID',
        'type': 'StringTypes'
    },{
        'name': 'boss_id',
        'summary': 'ボスのマスタID',
        'type': 'StringTypes'
    },{
        'name': 'boss_type',
        'summary': 'ボスの種類',
        'type': 'StringTypes'
    },{
        'name': 'boss_level',
        'summary': 'ボスのレベル',
        'type': 'StringTypes'
    },{
        'name': 'place_id',
        'summary': 'ボスと遭遇した時点での場所ID',
        'type': 'StringTypes'
    },{
        'name': 'finder_uid',
        'summary': '発見者のユーザID',
        'type': 'StringTypes'
    },{
        'name': 'finder_level',
        'summary': '発見者のレベル',
        'type': 'StringTypes'
    },{
        'name': 'damage',
        'summary': '与えたダメージ',
        'type': 'NumberTypes'
    },{
        'name': 'use_point',
        'summary': '何ポイント使ったか',
        'type': 'NumberTypes'
    },{
        'name': 'boss_hp',
        'summary': '攻撃した後のボスの残り体力',
        'type': 'NumberTypes'
    },{
        'name': 'player_deck',
        'summary': '攻撃する側のデッキ',
        'assert': 'self._or_none(self._string_list)',
        'default': None
    }]
},{
    'summary': 'イベント_レイド_救援送信',
    'name': 'eraid_send_rescue',
    'description': """
        救援要請を出した場合にこのログを出力して下さい。
        複数ユーザに送る場合、複数回に分けてログを出して下さい。

        デッキ情報については battle_attack を参照して下さい。
        event_id 〜 place_id までのパラメータについては eraid_boss_encount を参照して下さい。
    """,
    'params': [{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes'
    },{
        'name': 'user_level',
        'summary': 'ユーザLv',
        'type': 'NumberTypes'
    },{
        'name': 'boss_instance_id',
        'summary': '現在戦っているボスのID',
        'type': 'StringTypes'
    },{
        'name': 'boss_id',
        'summary': 'ボスのマスタID',
        'type': 'StringTypes'
    },{
        'name': 'boss_type',
        'summary': 'ボスの種類',
        'type': 'StringTypes'
    },{
        'name': 'boss_level',
        'summary': 'ボスのレベル',
        'type': 'StringTypes'
    },{
        'name': 'place_id',
        'summary': 'ボスと遭遇した時点での場所ID',
        'type': 'StringTypes'
    },{
        'name': 'receiver_uid',
        'summary': '受信者のユーザID',
        'type': 'StringTypes'
    },{
        'name': 'receiver_level',
        'summary': '受信者のレベル',
        'type': 'StringTypes'
    }]
},{
    'summary': 'イベント_レイド_救援受信',
    'name': 'eraid_receive_rescue',
    'description': """
        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。

        このログは、救援を受けてやってきたと判断できるユーザアクションがあった場所で出力して下さい。
        例えば救援要請のページを踏んだときなどに出力して下さい。
    """,
    'params': [{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes'
    },{
        'name': 'battle_id',
        'summary': 'バトルID',
        'type': 'StringTypes'
    },{
        'name': 'boss_id',
        'summary': 'ボスID',
        'type': 'StringTypes'
    },{
        'name': 'boss_instance_id',
        'summary': 'ボスインスタンスID',
        'type': 'StringTypes'
    },{
        'name': 'sender_uid',
        'summary': '送信者UserID',
        'type': 'StringTypes'
    }]
},{
    'summary': 'イベント_バトル_ユーザ間バトル',
    'name': 'ebtl_user_battle',
    'description': """
        イベントIDには、どのイベントであるか区別できる、任意の文字列を指定して下さい。

        デッキ情報については battle_attack を参照して下さい。
    """,
    'params': [{
        'name': 'event_id',
        'summary': 'イベントID',
        'type': 'StringTypes'
    },{
        'name': 'target_uid',
        'summary': 'バトル相手',
        'type': 'StringTypes'
    },{
        'name': 'battle_result',
        'summary': 'バトル結果',
        'type': 'BattleResult'
    },{
        'name': 'show_trap',
        'summary': '罠発動の有無',
        'type': 'bool'
    },{
        'name': 'show_damnation',
        'summary': '天罰発動の有無',
        'type': 'bool'
    },{
        'name': 'target_item_category',
        'summary': '略奪対象カテゴリ',
        'type': 'BattleTargetCategory'
    },{
        'name': 'target_item_id',
        'summary': '略奪対象ID',
        'type': 'StringTypes'
    },{
        'name': 'user_level',
        'summary': 'ユーザLv.',
        'type': 'NumberTypes'
    },{
        'name': 'target_user_level',
        'summary': 'バトル相手Lv.',
        'type': 'NumberTypes'
    },{
        'name': 'player_deck',
        'summary': '攻撃する側のデッキ',
        'assert': 'self._or_none(self._string_list)',
        'default': None
    },{
        'name': 'target_deck',
        'summary': '攻撃される側のデッキ',
        'assert': 'self._string_list',
        'default': None
    }]
},{
    'summary': 'チュートリアル',
    'name': 'do_tutorial',
    'description': """
      チュートリアルの進度を計測するためのログです。
    """,
    'params': [{
        'name': 'tutorial_step',
        'summary': 'チュートリアルの進捗番号',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'ページ表示',
    'name': 'view_page',
    'description': """
      ページビューを計測するためのログです。
    """,
    'params': [{
        'name': 'location_type',
        'summary': '表示ページの種類',
        'type': 'StringTypes'
    },{
        'name': 'url',
        'summary': '表示ページのURL',
        'type': 'StringTypes'
    }]
},{
    'summary': 'トレード',
    'name': 'do_user_trade',
    'params': [{
        'name': 'status',
        'summary': 'トレードステータス',
        'type': 'TradeStatus'
    },{
        'name': 'proposed_time',
        'summary': '出品日時',
        'type': 'datetime'
    },{
        'name': 'proposed_uid',
        'summary': '出品ユーザID',
        'type': 'StringTypes'
    },{
        'name': 'proposed_items',
        'summary': "出品アイテム一覧（例: ['ITEM/100/0/3', 'CARD/200/5/1']）",
        'assert': 'self._is_trade_items'
    },{
        'name': 'wish_items',
        'summary': "希望アイテム一覧（例: ['ITEM/100/0/3', 'CARD/200/5/1']）",
        'assert': 'self._is_trade_items'
    },{
        'name': 'accepted_time',
        'summary': 'トレード成立日時',
        'type': 'datetime',
        'default': None
    },{
        'name': 'trade_id',
        'summary': 'トレードID',
        'type': 'str',
        'default': None
    }]
},{
    'summary': 'ABテスト',
    'name': 'ab_test',
    'description': """
      注意:
        ABテストが実装されたページ(ユーザ選択前)へのアクセス履歴(is_view:True)も出力する必要があります。
    """,
    'params': [{
        'name': 'test_id',
        'summary': 'テストID',
        'type': 'StringTypes'
    },{
        'name': 'is_view',
        'summary': 'ページの表示かどうか',
        'type': 'bool'
    },{
        'name': 'action',
        'summary': 'ユーザの行動（テスト結果）。is_view == False のときのみ有効。',
        'type': 'StringTypes',
        'default': None
    }]
},{
    'summary': '友達',
    'name': 'friendship',
    'params': [{
        'name': 'action_type',
        'summary': '行動タイプ',
        'type': 'FriendActionType'
    },{
        'name': 'target_uid',
        'summary': '対象ユーザID',
        'type': 'StringTypes'
    }]
},{
    'summary': 'コメント',
    'name': 'platform_comment',
    'description': """
        ひとことコメントするとアイテムが貰えるとか、そういったコメントを行ったときに出力して下さい。

        comment_type には、CommentType.EVENT や CommentType.DIARY といった、大分別を書いて下さい。
        CommentType のどれにも当てはまらない無い場合は、任意の文字列を追加しても構いません。

        comment_id には、例えば comment_type が CommentType.EVENT ならイベント名を、comment_type が CommentType.COMPLETE ならコンプリートしたアイテム名などを記述して下さい。
    """,
    'params': [{
        'name': 'comment_type',
        'summary': 'コメント種別',
        'type': ['CommentType', 'StringTypes']
    },{
        'name': 'comment_id',
        'summary': 'コメントID',
        'type': 'StringTypes'
    }]
}]

if __name__ == '__main__':
    print '\n'.join([generate_func(func, auto_make_types.enums) for func in funcs])

