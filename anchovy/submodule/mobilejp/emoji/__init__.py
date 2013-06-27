# -*- coding: utf-8 -*-
import warnings
import re
import codecs
from binascii import unhexlify
import quotedata, unquotedata

__all__ = ['get_emoji_by_name', 'quote', 'unquote', 'has_emoji', 'strip_emoji',
           'quote_kddi_jis', 'GETA']

ENCODED_EMOJI = u'$%s$'
DECODER_RE = re.compile(r'\$([0-9]{1,4})\$')

EMOJI_UNICODE_RE = re.compile(ur'([\ue001-\uf0fc])')

GETA = u"\u3013"

SOFTBANK_EMOJI_WEBCODE_RE = re.compile(r'\x1b\x24(.+?)\x0f')

def get_emoji_by_name(name, carrier='D'):
    from names import DATA as NAME_MAP
    import compatdata

    if carrier == 'E':
        data = compatdata.KDDI_DATA
    elif carrier == 'S':
        data = compatdata.SOFTBANK_DATA
    else:
        data = compatdata.DOCOMO_DATA

    try:
        code = NAME_MAP[name]
        return data[code]
    except KeyError, e:
        return u'[%s]' % name

def quote(value, carrier, encoding='cp932', errors='strict'):
    """
    quote emoji code and return a unicode.
    """
    warnings.warn("mobilejp.emoji.quote is deprecated. use mobilejpcodecs instead",
                  DeprecationWarning, stacklevel=2)

    if not isinstance(value, unicode):
        value = unicode(value, encoding, errors)

    if carrier == 'S' and SOFTBANK_EMOJI_WEBCODE_RE.search(value):
        return _quote_emoji_softbank(value)

    try:
        table = quotedata.QUOTE_TABLE[carrier]
    except KeyError, e:
        raise ValueError('Invalid short carrier code "%s"' % carrier)

    return u''.join([(u in table and ENCODED_EMOJI % table[u] or u) for u in value])

def _each_two_byte(value):
    for i in xrange(0, len(value), 2):
        part = value[i:i+2]
        if len(part) == 2:
            yield part

def _quote_emoji_softbank(value):
    """
    quote softbank emoji webcode.
    the argument "value" must be a unicode.
    """
    from quotedata.softbank_webcode import DATA as TABLE

    def repl(matcher):
        buf = []
        for v in _each_two_byte(matcher.group(1)):
            try:
                buf.append(ENCODED_EMOJI % TABLE[v])
            except KeyError, e:
                buf.append(GETA)
        return u''.join(buf)

    return SOFTBANK_EMOJI_WEBCODE_RE.sub(repl, value)

def unquote(value, carrier, encoding='cp932', errors='strict'):
    """
    unquote escaped emoji codes and encode value.
    """
    warnings.warn("mobilejp.emoji.unquote is deprecated. use mobilejpcodecs instead",
                  DeprecationWarning, stacklevel=2)

    # normalize the given encoding name
    codec = codecs.lookup(encoding)
    encoding = codec.name

    try:
        if encoding == 'cp932' or encoding == 'shift_jis':
            table = unquotedata.UNQUOTE_TABLE_SJIS[carrier]
        elif encoding == 'utf-8':
            table = unquotedata.UNQUOTE_TABLE_UTF8[carrier]
        else:
            raise ValueError('Only cp932 or utf8 codecs are supported')
    except KeyError, e:
        raise ValueError('Invalid short carrier code "%s"' % carrier)

    if not isinstance(value, basestring):
        value = str(value)
    elif isinstance(value, unicode):
        value = value.encode(encoding, errors)

    return DECODER_RE.sub(lambda m: table[int(m.group(1))], value)

def has_emoji(value):
    if not isinstance(value, unicode):
        raise ValueError('the argument "value" must be a unicode')

    return bool(DECODER_RE.search(value))

def strip_emoji(value, unichar=None):
    """
    strip escaped emoji codes to GETA characters.
    input value must be a unicode.
    """
    if not isinstance(value, unicode):
        raise ValueError('the argument "value" must be a unicode')

    if unichar is None:
        unichar = GETA
    elif not isinstance(unichar, unicode):
        unichar = unicode(unichar)

    value = EMOJI_UNICODE_RE.sub(unichar, value)
    return DECODER_RE.sub(unichar, value)

ISO2022JP_SPLIT_RE = re.compile(r'(\x1b\x24\x42.+?\x1b\x28\x42)')

def quote_kddi_jis(value, error='strict'):
    from quotedata.ezweb_jis import DATA as TABLE
    from codecs import lookup
    codec = lookup('iso2022_jp_2')

    buf = []
    for x in ISO2022JP_SPLIT_RE.split(value):
        if x.startswith('\x1b\x24\x42') and x.endswith('\x1b\x28\x42'):
            for bytes in _each_two_byte(x[3:-3]):
                code = TABLE.get(bytes)
                if code is not None:
                    buf.append(u'$%d$' % code)
                    continue

                uni = JISX0213_MAP.get(bytes)
                if uni is not None:
                    buf.append(uni)
                else:
                    buf.append(codec.decode('\x1b\x24\x42%s\x1b\x28\x42' % bytes, error)[0])
        else:
            buf.append(x.decode('iso2022_jp_2', error))
    return u''.join(buf)

JISX0213_CHARS = [
 ('2d21', u'\u2460'),
 ('2d22', u'\u2461'),
 ('2d23', u'\u2462'),
 ('2d24', u'\u2463'),
 ('2d25', u'\u2464'),
 ('2d26', u'\u2465'),
 ('2d27', u'\u2466'),
 ('2d28', u'\u2467'),
 ('2d29', u'\u2468'),
 ('2d2a', u'\u2469'),
 ('2d2b', u'\u246a'),
 ('2d2c', u'\u246b'),
 ('2d2d', u'\u246c'),
 ('2d2e', u'\u246d'),
 ('2d2f', u'\u246e'),

 #
 ('2d30', u'\u246f'),
 ('2d31', u'\u2470'),
 ('2d32', u'\u2471'),
 ('2d33', u'\u2472'),
 ('2d34', u'\u2473'),
 ('2d35', u'\u2160'),
 ('2d36', u'\u2161'),
 ('2d37', u'\u2162'),
 ('2d38', u'\u2163'),
 ('2d39', u'\u2164'),
 ('2d3a', u'\u2165'),
 ('2d3b', u'\u2166'),
 ('2d3c', u'\u2167'),
 ('2d3d', u'\u2168'),
 ('2d3e', u'\u2169'),

 #
 ('2d40', u'\u3349'),
 ('2d41', u'\u3314'),
 ('2d42', u'\u3322'),
 ('2d43', u'\u334d'),
 ('2d44', u'\u3318'),
 ('2d45', u'\u3327'),
 ('2d46', u'\u3303'),
 ('2d47', u'\u3336'),
 ('2d48', u'\u3351'),
 ('2d49', u'\u3357'),
 ('2d4a', u'\u330d'),
 ('2d4b', u'\u3326'),
 ('2d4c', u'\u3323'),
 ('2d4d', u'\u332b'),
 ('2d4e', u'\u334a'),
 ('2d4f', u'\u333b'),

 #
 ('2d50', u'\u339c'),
 ('2d51', u'\u339d'),
 ('2d52', u'\u339e'),
 ('2d53', u'\u338e'),
 ('2d54', u'\u338f'),
 ('2d55', u'\u33c4'),
 ('2d56', u'\u33a1'),
 ('2d5f', u'\u337b'),

 #
 ('2d60', u'\u301d'),
 ('2d61', u'\u301f'),
 ('2d62', u'\u2116'),
 ('2d63', u'\u33cd'),
 ('2d64', u'\u2121'),
 ('2d65', u'\u32a4'),
 ('2d66', u'\u32a5'),
 ('2d67', u'\u32a6'),
 ('2d68', u'\u32a7'),
 ('2d69', u'\u32a8'),
 ('2d6a', u'\u3231'),
 ('2d6b', u'\u3232'),
 ('2d6c', u'\u3239'),
 ('2d6d', u'\u337e'),
 ('2d6e', u'\u337d'),
 ('2d6f', u'\u337c'),]

JISX0213_MAP = dict((unhexlify(x[0]), x[1]) for x in JISX0213_CHARS)
