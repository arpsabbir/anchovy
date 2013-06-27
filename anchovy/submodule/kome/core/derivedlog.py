# coding: utf-8

from datetime import datetime
from kome.core.types import *
from kome.core.types import _isinstance

class DerivedLog(object):
    def __init__(self, parent, parent_record):
        self._parent = parent
        self._parent_record = parent_record

    @property
    def parent(self):
        return self._parent

    @property
    def parent_record(self):
        return self._parent_record

    def log(self, actname, **kwargs):
        u"""
        任意の派生ログを出力する
        """
        # time が指定されている場合はそっちを優先する
        time = kwargs.get('time', datetime.now())

        record = dict(kwargs)
        record.update({
            'uid': self.parent.uid,
            'ver': self.parent.version,
            'time': time,
            'device': self.parent.device,
            'action': actname })

        if self.parent_record is not None:
            record.update({
                'parent': self.parent_record.actname,
                'parentid': self.parent_record.id })

        self.parent.sender.emit(record)

        return self

    #############################
    # 以下自動生成で出力した実装
    #############################

    def inc_money(self, before_value, after_value, value, **opt):
        u"""
        ゲーム内通貨_増加
        
        before_value -- 変化前の値
        after_value -- 変化後の値
        value -- 増減量
        """
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('inc_money',
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)

    def dec_money(self, before_value, after_value, value, **opt):
        u"""
        ゲーム内通貨_減少
        
        before_value -- 変化前の値
        after_value -- 変化後の値
        value -- 増減量
        """
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('dec_money',
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)

    def inc_point(self, point_type, before_value, after_value, value, **opt):
        u"""
        ゲーム内ポイント_増加
        
        point_type -- ポイント種別
        before_value -- 変化前の値
        after_value -- 変化後の値
        value -- 増減量
        
        この派生アクションは、お金以外の、ユーザに直接関連付けられているデータが変動した時に出力して下さい。
        例えば任侠道なら、盃ポイント、レア代紋などです。
        
        ポイント種別には、それらのデータの種類毎に一意な名前を付けて下さい。
        例えば 'SAKAZUKI_PT', 'RARE_DAIMON' などです。
        """
        assert _isinstance(point_type, StringTypes)
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('inc_point',
                        point_type = point_type,
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)

    def dec_point(self, point_type, before_value, after_value, value, **opt):
        u"""
        ゲーム内ポイント_減少
        
        point_type -- ポイント種別
        before_value -- 変化前の値
        after_value -- 変化後の値
        value -- 増減量
        
        この派生アクションは、お金以外の、ユーザに直接関連付けられているデータが変動した時に出力して下さい。
        例えば任侠道なら、盃ポイント、レア代紋などです。
        
        ポイント種別には、それらのデータの種類毎に一意な名前を付けて下さい。
        例えば 'SAKAZUKI_PT', 'RARE_DAIMON' などです。
        """
        assert _isinstance(point_type, StringTypes)
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('dec_point',
                        point_type = point_type,
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)

    def inc_gachaticket(self, ticket_id, before_value, after_value, value, **opt):
        u"""
        ガチャチケット_増加
        
        ticket_id -- チケットID
        before_value -- 変化前の値（個数）
        after_value -- 変化後の値（個数）
        value -- 増減量
        """
        assert _isinstance(ticket_id, StringTypes)
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('inc_gachaticket',
                        ticket_id = ticket_id,
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)

    def dec_gachaticket(self, ticket_id, before_value, after_value, value, **opt):
        u"""
        ガチャチケット_減少
        
        ticket_id -- チケットID
        before_value -- 変化前の値（個数）
        after_value -- 変化後の値（個数）
        value -- 増減量
        """
        assert _isinstance(ticket_id, StringTypes)
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('dec_gachaticket',
                        ticket_id = ticket_id,
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)

    def inc_power(self, power_type, before_value, after_value, value, **opt):
        u"""
        パワー_増加
        
        power_type -- パワー種別
        before_value -- 変化前の値
        after_value -- 変化後の値
        value -- 増減量
        """
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('inc_power',
                        power_type = power_type,
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)

    def dec_power(self, power_type, before_value, after_value, value, **opt):
        u"""
        パワー_減少
        
        power_type -- パワー種別
        before_value -- 変化前の値
        after_value -- 変化後の値
        value -- 増減量
        """
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('dec_power',
                        power_type = power_type,
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)

    def inc_card(self, card_rarity, card_id, value, **opt):
        u"""
        カード_増加
        
        card_rarity -- カードレアリティ
        card_id -- カードID
        value -- 増減量
        """
        assert _isinstance(card_rarity, NumberTypes)
        assert _isinstance(card_id, StringTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('inc_card',
                        card_rarity = card_rarity,
                        card_id = card_id,
                        value = value,
                        **opt)

    def dec_card(self, card_rarity, card_id, value, **opt):
        u"""
        カード_減少
        
        card_rarity -- カードレアリティ
        card_id -- カードID
        value -- 増減量
        """
        assert _isinstance(card_rarity, NumberTypes)
        assert _isinstance(card_id, StringTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('dec_card',
                        card_rarity = card_rarity,
                        card_id = card_id,
                        value = value,
                        **opt)

    def inc_item(self, item_type, item_id, before_value, after_value, value, **opt):
        u"""
        アイテム_増加
        
        item_type -- アイテム種別
        item_id -- アイテムID
        before_value -- 変化前の値（個数）
        after_value -- 変化後の値（個数）
        value -- 増減量
        
        アイテム種別とアイテムIDで、一意にアイテムを識別できるようにして下さい。
        
        アイテムIDだけで一意にアイテムを識別できるアプリもあるが、アプリによっては回復アイテムやガチャチケットでテーブルを分けている場合もある。
        そういった場合はアイテム種別を見れば区別できるようにして下さい。
        """
        assert _isinstance(item_type, StringTypes)
        assert _isinstance(item_id, StringTypes)
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('inc_item',
                        item_type = item_type,
                        item_id = item_id,
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)

    def dec_item(self, item_type, item_id, before_value, after_value, value, **opt):
        u"""
        アイテム_減少
        
        item_type -- アイテム種別
        item_id -- アイテムID
        before_value -- 変化前の値（個数）
        after_value -- 変化後の値（個数）
        value -- 増減量
        
        アイテム種別とアイテムIDで、一意にアイテムを識別できるようにして下さい。
        
        アイテムIDだけで一意にアイテムを識別できるアプリもあるが、アプリによっては回復アイテムやガチャチケットでテーブルを分けている場合もある。
        そういった場合はアイテム種別を見れば区別できるようにして下さい。
        """
        assert _isinstance(item_type, StringTypes)
        assert _isinstance(item_id, StringTypes)
        assert _isinstance(before_value, NumberTypes)
        assert _isinstance(after_value, NumberTypes)
        assert _isinstance(value, NumberTypes)

        return self.log('dec_item',
                        item_type = item_type,
                        item_id = item_id,
                        before_value = before_value,
                        after_value = after_value,
                        value = value,
                        **opt)
