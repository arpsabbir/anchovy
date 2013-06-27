# coding: utf-8

from auto_make import *
import auto_make_types

funcs = [{
    'summary': 'ゲーム内通貨_増加',
    'name': 'inc_money',
    'params': [{
        'name': 'before_value',
        'summary': '変化前の値',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'ゲーム内通貨_減少',
    'name': 'dec_money',
    'params': [{
        'name': 'before_value',
        'summary': '変化前の値',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'ゲーム内ポイント_増加',
    'name': 'inc_point',
    'description': """
        この派生アクションは、お金以外の、ユーザに直接関連付けられているデータが変動した時に出力して下さい。
        例えば任侠道なら、盃ポイント、レア代紋などです。

        ポイント種別には、それらのデータの種類毎に一意な名前を付けて下さい。
        例えば 'SAKAZUKI_PT', 'RARE_DAIMON' などです。
    """,
    'params': [{
        'name': 'point_type',
        'summary': 'ポイント種別',
        'type': 'StringTypes'
    },{
        'name': 'before_value',
        'summary': '変化前の値',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'ゲーム内ポイント_減少',
    'name': 'dec_point',
    'description': """
        この派生アクションは、お金以外の、ユーザに直接関連付けられているデータが変動した時に出力して下さい。
        例えば任侠道なら、盃ポイント、レア代紋などです。

        ポイント種別には、それらのデータの種類毎に一意な名前を付けて下さい。
        例えば 'SAKAZUKI_PT', 'RARE_DAIMON' などです。
    """,
    'params': [{
        'name': 'point_type',
        'summary': 'ポイント種別',
        'type': 'StringTypes'
    },{
        'name': 'before_value',
        'summary': '変化前の値',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'ガチャチケット_増加',
    'name': 'inc_gachaticket',
    'params': [{
        'name': 'ticket_id',
        'summary': 'チケットID',
        'type': 'StringTypes'
    },{
        'name': 'before_value',
        'summary': '変化前の値（個数）',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値（個数）',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'ガチャチケット_減少',
    'name': 'dec_gachaticket',
    'params': [{
        'name': 'ticket_id',
        'summary': 'チケットID',
        'type': 'StringTypes'
    },{
        'name': 'before_value',
        'summary': '変化前の値（個数）',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値（個数）',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'パワー_増加',
    'name': 'inc_power',
    'params': [{
        'name': 'power_type',
        'summary': 'パワー種別',
        'enum': 'PowerType'
    },{
        'name': 'before_value',
        'summary': '変化前の値',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'パワー_減少',
    'name': 'dec_power',
    'params': [{
        'name': 'power_type',
        'summary': 'パワー種別',
        'enum': 'PowerType'
    },{
        'name': 'before_value',
        'summary': '変化前の値',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'カード_増加',
    'name': 'inc_card',
    'params': [{
        'name': 'card_rarity',
        'summary': 'カードレアリティ',
        'type': 'NumberTypes'
    },{
        'name': 'card_id',
        'summary': 'カードID',
        'type': 'StringTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'カード_減少',
    'name': 'dec_card',
    'params': [{
        'name': 'card_rarity',
        'summary': 'カードレアリティ',
        'type': 'NumberTypes'
    },{
        'name': 'card_id',
        'summary': 'カードID',
        'type': 'StringTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'アイテム_増加',
    'name': 'inc_item',
    'description': """
        アイテム種別とアイテムIDで、一意にアイテムを識別できるようにして下さい。

        アイテムIDだけで一意にアイテムを識別できるアプリもあるが、アプリによっては回復アイテムやガチャチケットでテーブルを分けている場合もある。
        そういった場合はアイテム種別を見れば区別できるようにして下さい。
    """,
    'params': [{
        'name': 'item_type',
        'summary': 'アイテム種別',
        'type': 'StringTypes'
    },{
        'name': 'item_id',
        'summary': 'アイテムID',
        'type': 'StringTypes'
    },{
        'name': 'before_value',
        'summary': '変化前の値（個数）',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値（個数）',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
},{
    'summary': 'アイテム_減少',
    'name': 'dec_item',
    'description': """
        アイテム種別とアイテムIDで、一意にアイテムを識別できるようにして下さい。

        アイテムIDだけで一意にアイテムを識別できるアプリもあるが、アプリによっては回復アイテムやガチャチケットでテーブルを分けている場合もある。
        そういった場合はアイテム種別を見れば区別できるようにして下さい。
    """,
    'params': [{
        'name': 'item_type',
        'summary': 'アイテム種別',
        'type': 'StringTypes'
    },{
        'name': 'item_id',
        'summary': 'アイテムID',
        'type': 'StringTypes'
    },{
        'name': 'before_value',
        'summary': '変化前の値（個数）',
        'type': 'NumberTypes'
    },{
        'name': 'after_value',
        'summary': '変化後の値（個数）',
        'type': 'NumberTypes'
    },{
        'name': 'value',
        'summary': '増減量',
        'type': 'NumberTypes'
    }]
}]

if __name__ == '__main__':
    print '\n'.join([generate_func(func, auto_make_types.enums) for func in funcs])
