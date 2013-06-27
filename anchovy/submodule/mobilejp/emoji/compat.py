# -*- coding: utf-8 -*-
import re
import compatdata

EMOJI_RE = re.compile(r'\$(\d+)\$')

GETA = u"\u3013"

def to_str(value, encoding):
    assert isinstance(value, str)

    def repl(matcher):
        code = int(matcher.group(1))
        res = compatdata.DATA.get(code, GETA)
        return res.encode(encoding)

    return EMOJI_RE.sub(repl, value)

def to_unicode(value):
    assert isinstance(value, unicode)

    def repl(matcher):
        code = int(matcher.group(1))
        res = compatdata.DATA.get(code, GETA)
        return res

    return EMOJI_RE.sub(repl, value)
