# -*- coding: utf-8 -*-
import re

ENTITY_RE = re.compile(ur'&#((?:x[0-9a-fA-F]+)|\d+);')

def replace_entity(value):
    def repl(matcher):
        v = matcher.group(1).lower()
        if v.startswith('x'):
            code = int(v[1:], 16)
        else:
            code = int(v)

        if code <= 0xff or (code >= 0xe001 and code <=0xf0fc):
            # if ascii, latin-1 and emoji, use original value
            return matcher.group(0)
        else:
            return unichr(code)

    return ENTITY_RE.sub(repl, value)
