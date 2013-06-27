# coding: utf-8
from nose.tools import ok_, eq_, raises
from mock import Mock
from kome.core.actionlog import *
import kome.core.actionlog
from datetime import datetime
import sys

class TestActionLog:
    def test___init__(self):
        sender = Mock()
        uid = '012345678'
        device = 'iPhone'
        actlog = ActionLog(sender, uid, device)
        eq_(actlog.sender, sender)
        eq_(actlog.uid, uid)
        eq_(actlog.device, device)

    def _make_actlog(self):
        sender = Mock()
        uid = '012345678'
        device = 'iPhone'
        return ActionLog(sender, uid, device)

    def test_register(self):
        now = datetime.now()
        actlog = self._make_actlog()
        record = actlog.register(RegisterType.NORMAL, time=now)

        actlog.sender.emit.assert_called_with({
            'uid': actlog.uid,
            'ver': 2,
            'time': now,
            'device': actlog.device,
            'id': record.id,
            'action': 'register',
            'register_type': RegisterType.NORMAL })

    def test_battle_attack(self):
        now = datetime.now()
        actlog = self._make_actlog()
        record = actlog.battle_attack('11112345', BattleResult.WIN, BattleTargetCategory.ITEM, '1234', 51, 40, True, time=now)

        actlog.sender.emit.assert_called_with({
            'uid': actlog.uid,
            'ver': 2,
            'time': now,
            'device': actlog.device,
            'id': record.id,
            'action': 'battle_attack',
            'target_uid': '11112345',
            'battle_result': BattleResult.WIN,
            'target_item_category': BattleTargetCategory.ITEM,
            'target_item_id': '1234',
            'user_level': 51,
            'target_user_level': 40,
            'show_trap': True,
            'show_damnation': None,
            'player_deck': None,
            'target_deck': None })

    def test_battle_attack_other_types(self):
        now = datetime.now()
        actlog = self._make_actlog()
        record = actlog.battle_attack('11112345', BattleResult.WIN, BattleTargetCategory.ITEM, u'1234', 51L, 40L, True, time=now)

        actlog.sender.emit.assert_called_with({
            'uid': actlog.uid,
            'ver': 2,
            'time': now,
            'device': actlog.device,
            'id': record.id,
            'action': 'battle_attack',
            'target_uid': '11112345',
            'battle_result': BattleResult.WIN,
            'target_item_category': BattleTargetCategory.ITEM,
            'target_item_id': u'1234',
            'user_level': 51L,
            'target_user_level': 40L,
            'show_trap': True,
            'show_damnation': None,
            'player_deck': None,
            'target_deck': None })

    def test_do_user_trade(self):
        now = datetime.now()
        actlog = self._make_actlog()
        record = actlog.do_user_trade(
            TradeStatus.ACCEPT,
            datetime(2012, 1, 1),
            '11112345',
            ['CARD/100/3/1', 'ITEM/200/0/3'],
            ['ITEM/10/0/1', 'CARD/20/5/1'], time=now)

        actlog.sender.emit.assert_called_with({
            'uid': actlog.uid,
            'ver': 2,
            'time': now,
            'device': actlog.device,
            'id': record.id,
            'action': 'do_user_trade',
            'status': TradeStatus.ACCEPT,
            'proposed_time': datetime(2012, 1, 1),
            'proposed_uid': '11112345',
            'proposed_items': ['CARD/100/3/1', 'ITEM/200/0/3'],
            'wish_items': ['ITEM/10/0/1', 'CARD/20/5/1'],
            'accepted_time': None,
            'trade_id': None })

    def test_log(self):
        now = datetime.now()
        actlog = self._make_actlog()

        record = actlog.log('test', arg1='hoge', arg2=100, time=now)
        actlog.sender.emit.assert_called_with({
            'uid': actlog.uid,
            'ver': 2,
            'time': now,
            'device': actlog.device,
            'id': record.id,
            'action': 'test',
            'arg1': 'hoge',
            'arg2': 100 })
