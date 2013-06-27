# -*- coding: utf-8 -*-
"""
python の libamqp は, consume するメッセージに
x-death ヘッダが付加されていると, raise で落ちるため,
下記のように Patch をあてる必要がある.

このコードは, kombu 2.4.X に対応する為のパッチであり,
kombu 2.5.X では, pyamqp を使用するため, 問題が発生しない.
"""
from struct import unpack
from decimal import Decimal

def _patched_read_table(self):
    """
    Read an AMQP table, and return as a Python dictionary.
    """
    self.bitcount = self.bits = 0
    tlen = unpack('>I', self.input.read(4))[0]
    table_data = AMQPReader(self.input.read(tlen))
    result = {}
    while table_data.input.tell() < tlen:
        name = table_data.read_shortstr()
        ftype = ord(table_data.input.read(1))

        if ftype == 65: # 'A' これが新しく加わった!!
            len = unpack('>I', table_data.input.read(4))[0] # len は読み捨てる
            ftype = ord(table_data.input.read(1))

        if ftype == 83: # 'S'
            val = table_data.read_longstr()
        elif ftype == 73: # 'I'
            val = unpack('>i', table_data.input.read(4))[0]
        elif ftype == 68: # 'D'
            d = table_data.read_octet()
            n = unpack('>i', table_data.input.read(4))[0]
            val = Decimal(n) / Decimal(10 ** d)
        elif ftype == 84: # 'T'
            val = table_data.read_timestamp()
        elif ftype == 70: # 'F'
            val = table_data.read_table() # recurse
        else:
            raise ValueError('Unknown table item type: %s' % repr(ftype))
        result[name] = val
    return result

try:
    from amqplib.client_0_8.serialization import AMQPReader

    def patch_read_table():
        AMQPReader.read_table = _patched_read_table
except ImportError:
    # kombu 2.5.X では amqplib 使用しないため, import error は無視してよい
    def patch_read_table():
        pass
