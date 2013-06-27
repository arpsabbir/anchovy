# -*- coding: utf-8 -*-
import docomo_sjis, ezweb_sjis, softbank_sjis
import docomo_utf8, ezweb_utf8, softbank_utf8

__all__ = ['UNQUOTE_TABLE_SJIS', 'UNQUOTE_TABLE_UTF8']

UNQUOTE_TABLE_SJIS = {'D': docomo_sjis.DATA,
                      'E': ezweb_sjis.DATA,
                      'S': softbank_sjis.DATA,
                      'W': docomo_sjis.DATA,
                      'N': docomo_sjis.DATA,
                      }


UNQUOTE_TABLE_UTF8 = {'D': docomo_utf8.DATA,
                      'E': ezweb_utf8.DATA,
                      'S': softbank_utf8.DATA,
                      'W': docomo_utf8.DATA,
                      'N': docomo_utf8.DATA,
                      }

