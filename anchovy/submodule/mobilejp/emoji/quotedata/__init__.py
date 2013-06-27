# -*- coding: utf-8 -*-
import docomo, ezweb, softbank_sjis, softbank_webcode

__all__ = ['QUOTE_TABLE']

QUOTE_TABLE = {'D': docomo.DATA,
               'E': ezweb.DATA,
               'S': softbank_sjis.DATA,
               'W': docomo.DATA,
               'N': docomo.DATA,
               }
