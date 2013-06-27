# -*- coding: utf-8 -*-
import re
import urllib
import unicodedata

from django import template
from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode, smart_str

import mobilejpcodecs

from mobilejp import emoji as mobilejp_emoji
from mobilejp.emoji import compat
from mobilejp.middleware.mobile import get_current_device, get_current_request
from mobilejp.utils.session import embed_session_id

register = template.Library()

def spam(domain, color=None):
    device = get_current_device()
    request = get_current_request()
    return { 'color' : color or 'red',
             'device': device,
             'domain': domain,
             }
spam = register.inclusion_tag('common/spam.html')(spam)

class InvalidEmojiError(Exception):
    pass

class EmojiNode(template.Node):
    def __init__(self, name, **opts):
        self.name = name
        self.opts = opts

    def __repr__(self):
        return "<EmojiNode>"

    def render(self, context):
        name = self.name.resolve(context)
        try:
            device = None
            if context.has_key('device'):
                device = context['device']
            #カスタムタグから使えるように修正
            elif context.has_key('context'):
                device = context['context']['device']
            if not device:
                device = get_current_device()

            if device.is_au and name in EZWEB_FALLBACK:
                return mark_safe(EZWEB_FALLBACK[name])
            elif device.is_softbank and name in SOFTBANK_FALLBACK:
                return mark_safe(SOFTBANK_FALLBACK[name])
            elif device.is_smartphone:
                if device.is_android:
                    return ''
                else:
                    return mark_safe(mobilejp_emoji.get_emoji_by_name(name, 'S'))
            
#            print "render------0"
#            print name
#            print "------"
#            print  mark_safe(EMOJI_NAME_TO_UNICODE[name])
#            print "render------1"


            if name in BANNED_EMOJI:
                raise InvalidEmojiError

            return mark_safe(EMOJI_NAME_TO_UNICODE[name])
        except KeyError:
            return u'[%s]' % name

def emoji(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError("emoji tag requires at leaset one parameter")

    name = parser.compile_filter(bits[1])
    

    opts = {}
    for arg in bits[2:]:
        try:
            k, v = arg.split(u"=", 1)
            key = smart_str(k).upper()
            if key not in ("DOCOMO", "EZWEB", "SOFTBANK", "WILLCOM", "NONMOBILE"):
                raise template.TemplateSyntaxError("Invalid keyword argument for emoji tag. key must be either"
                                                   "dococmo, ezweb, softbank, willcom, or nonmobile")
            # Use capital letter as a key
            opts[key[0]] = parser.compile_filter(v)
        except ValueError:
            raise template.TemplateSyntaxError("Invalid argument '%s' for emoji tag."
                                               "argumetn must be a key=value pair" % arg)
    
    return EmojiNode(name, **opts)
emoji = register.tag(emoji)

class MailToNode(template.Node):
    def __init__(self, args, kwds):
        self.args = args
        self.kwds = kwds

    def _quote(self, value, device):
        if device.is_docomo():
            charset = 'x_sjis_docomo'
        elif device.is_ezweb():
            value = unicodedata.normalize('NFKC', value)
            charset = 'x_sjis_kddi'
        elif device.is_softbank():
            charset = 'x_utf8_softbank'
        else:
            value = unicodedata.normalize('NFKC', value)
            value = mobilejp_emoji.strip_emoji(value)
            charset = 'utf8'
        return urllib.quote(value.encode(charset, 'replace'))

    def render(self, context):
        try:
            device = context['device']
        except KeyError:
            raise template.TemplateSyntaxError('You need to enable the context_processor device')

        kwds = {}
        if self.args is not None:
            args = self.args.resolve(context)
            if isinstance(args, dict):
                kwds.update(args)

        for k, v in self.kwds.items():
            kwds[k] = v.resolve(context)

        params = []
        subject = kwds.get('subject')
        if subject:
            subject = compat.to_unicode(force_unicode(subject))
            params.append('subject=%s' % self._quote(subject, device))

        body = kwds.get('body')
        if body:
            body = compat.to_unicode(force_unicode(body))
            params.append('body=%s' % self._quote(body, device))

        to = kwds.get('to', '')
        querystring = '&amp;'.join(params)
        return mark_safe('mailto:%s?%s' % (to, querystring))

def mailto(parser, token):
    bits = token.split_contents()
    args = None
    kwds = {}
    if len(bits) > 1:
        for arg in bits[1].split(','):
            if '=' in arg:
                k, v = arg.split('=', 1)
                k = k.strip()
                kwds[str(k)] = parser.compile_filter(v)
            else:
                args = parser.compile_filter(arg)

    return MailToNode(args, kwds)
mailto = register.tag(mailto)


class IconNode(template.Node):
    def __init__(self, name, color):
        self.name  = name
        self.color = color

    def render(self, context):
        char = { 'next'       : u'\u21d2',
                 'kuromaru'   : u'\u25cb',
                 'shiromaru'  : u'\u25cf',
                 'arrow_up'   : u'\u2191',
                 'arrow_down' : u'\u2193',
                 'star'       : u'\u2605',
                 'white_star' : u'\u2606',
                 'sen_middle' : u'\u251c',
                 'sen_bottom' : u'\u2514',
                 'triangle_down': u'\u25bc',
                 'square' : u'\u25a0',
                 'LEFTWARDS ARROW': u'\u2190',
                 'RIGHTWARDS ARROW': u'\u2192',
             }.get(self.name.resolve(context), u'')
        if self.color:
            color = self.color.resolve(context)
            if color:
                return mark_safe(u'<span style="color:%s">%s</span>' % (color, char))

        # no color is defined
        return mark_safe(char)

def do_icon(parser, token):
    bits = token.split_contents()
    try:
        name = parser.compile_filter(bits[1])
    except KeyError:
        raise template.TemplateSyntaxError('icon block requries at leaset one argument')

    if len(bits) > 2:
        color = parser.compile_filter(bits[2])
    else:
        color = None

    return IconNode(name, color)
do_icon = register.tag('icon', do_icon)

# class SpacerNode(template.Node):
#     def __init__(self, height):
#         self.height = height

#     def __repr__(self):
#         return "<SpacerNode>"

#     def render(self, context):
#         device = get_current_device()
#         if device and device.is_docomo():
#             return mark_safe(u'<div><img src="/img/space.gif" alt="" width="1" height="%s" /></div>' % self.height)
#         else:
#             return mark_safe(u'')
# def do_spacer(parser, token):
#     bits = token.split_contents()
#     try:
#         height = len(bits) > 1 and int(bits[1]) or 4
#     except TypeError:
#         raise template.TemplateSyntaxError('spacer height must be an integer')
#     return SpacerNode(height)
# do_spacer = register.tag('spacer', do_spacer)

class DashNode(template.Node):
    def __init__(self, margin=0):
        self.margin = margin

    def __repr__(self):
        return "<DashNode>"

    def render(self, context):
        try:
            device = context['device']
        except KeyError:
            raise template.TemplateSyntaxError('You need to enable the context_processor device')
        return mark_safe(u'<div><img src="/img/top/240/line.gif" alt="" width="240" height="3" /></div>')

def do_dash(parser, token):
    bits = token.split_contents()
    try:
        margin = len(bits) > 1 and int(bits[1]) or 0
    except TypeError:
        raise template.TemplateSyntaxError('dash margin must be an integer')
    return DashNode(margin)
do_dash = register.tag('dash', do_dash)

################

## E6E2 => emoji "one", E6E3 => emoji "two" ...
TRANSLATE_MAP = dict((ord(unicode(x)), 0xe6e1 + x) for x in xrange(1, 10))
TRANSLATE_MAP[ord(u"0")] = ord(u"\ue6eb")

@register.filter
def number2emoji(value):
    if not isinstance(value, (int, long)):
        return value
    return unicode(value).translate(TRANSLATE_MAP)


################

EZWEB_FALLBACK = { 'shadow': u'\uefd4',
                   'sports': u'\uef43',
                   }

SOFTBANK_FALLBACK = { 'shadow': u'\ue001',
                      'sports': u'\ue006',
                      'wrench': u'\ue116',
                      'pen'   : u'\ue148',
                      'game'  : u'\ue12b',
                      'event' : u'\ue037',
                      'clip'  : u'\ue313',
                      'enter' : u'\ue230',
                      'flag'  : u'\ue14b',
                      'eyeglass': u'\ue211',
                      }

EMOJI_NAME_TO_UNICODE = dict([
  ('sun', u'\ue63e'),
  ('cloud', u'\ue63f'),
  ('rain', u'\ue640'),
  ('snow', u'\ue641'),
  ('thunder', u'\ue642'),
  ('typhoon', u'\ue643'),
  ('mist', u'\ue644'),
  ('sprinkle', u'\ue645'),
  ('aries', u'\ue646'),
  ('taurus', u'\ue647'),
  ('gemini', u'\ue648'),
  ('cancer', u'\ue649'),
  ('leo', u'\ue64a'),
  ('virgo', u'\ue64b'),
  ('libra', u'\ue64c'),
  ('scorpius', u'\ue64d'),
  ('sagittarius', u'\ue64e'),
  ('capricornus', u'\ue64f'),
  ('aquarius', u'\ue650'),
  ('pisces', u'\ue651'),
  ('sports', u'\ue652'),
  ('baseball', u'\ue653'),
  ('golf', u'\ue654'),
  ('tennis', u'\ue655'),
  ('soccer', u'\ue656'),
  ('ski', u'\ue657'),
  ('basketball', u'\ue658'),
  ('motorsports', u'\ue659'),
  ('pocketbell', u'\ue65a'),
  ('train', u'\ue65b'),
  ('subway', u'\ue65c'),
  ('bullettrain', u'\ue65d'),
  ('car', u'\ue65e'),
  ('rvcar', u'\ue65f'),
  ('bus', u'\ue660'),
  ('ship', u'\ue661'),
  ('airplane', u'\ue662'),
  ('house', u'\ue663'),
  ('building', u'\ue664'),
  ('postoffice', u'\ue665'),
  ('hospital', u'\ue666'),
  ('bank', u'\ue667'),
  ('atm', u'\ue668'),
  ('hotel', u'\ue669'),
  ('24hours', u'\ue66a'),
  ('gasstation', u'\ue66b'),
  ('parking', u'\ue66c'),
  ('signaler', u'\ue66d'),
  ('toilet', u'\ue66e'),
  ('restaurant', u'\ue66f'),
  ('cafe', u'\ue670'),
  ('bar', u'\ue671'),
  ('beer', u'\ue672'),
  ('fastfood', u'\ue673'),
  ('boutique', u'\ue674'),
  ('hairsalon', u'\ue675'),
  ('karaoke', u'\ue676'),
  ('movie', u'\ue677'),
  ('upwardright', u'\ue678'),
  ('carouselpony', u'\ue679'),
  ('music', u'\ue67a'),
  ('art', u'\ue67b'),
  ('drama', u'\ue67c'),
  ('event', u'\ue67d'),
  ('ticket', u'\ue67e'),
  ('smoking', u'\ue67f'),
  ('nosmoking', u'\ue680'),
  ('camera', u'\ue681'),
  ('bag', u'\ue682'),
  ('book', u'\ue683'),
  ('ribbon', u'\ue684'),
  ('present', u'\ue685'),
  ('birthday', u'\ue686'),
  ('telephone', u'\ue687'),
  ('mobilephone', u'\ue688'),
  ('memo', u'\ue689'),
  ('tv', u'\ue68a'),
  ('game', u'\ue68b'),
  ('cd', u'\ue68c'),
  ('heart', u'\ue68d'),
  ('spade', u'\ue68e'),
  ('diamond', u'\ue68f'),
  ('club', u'\ue690'),
  ('eye', u'\ue691'),
  ('ear', u'\ue692'),
  ('rock', u'\ue693'),
  ('scissors', u'\ue694'),
  ('paper', u'\ue695'),
  ('downwardright', u'\ue696'),
  ('upwardleft', u'\ue697'),
  ('foot', u'\ue698'),
  ('shoe', u'\ue699'),
  ('eyeglass', u'\ue69a'),
  ('wheelchair', u'\ue69b'),
  ('newmoon', u'\ue69c'),
  ('moon1', u'\ue69d'),
  ('moon2', u'\ue69e'),
  ('moon3', u'\ue69f'),
  ('fullmoon', u'\ue6a0'),
  ('dog', u'\ue6a1'),
  ('cat', u'\ue6a2'),
  ('yacht', u'\ue6a3'),
  ('xmas', u'\ue6a4'),
  ('downwardleft', u'\ue6a5'),
  ('slate', u'\ue6ac'),
  ('pouch', u'\ue6ad'),
  ('pen', u'\ue6ae'),
  ('shadow', u'\ue6b1'),
  ('chair', u'\ue6b2'),
  ('night', u'\ue6b3'),
  ('soon', u'\ue6b7'),
  ('true', u'\ue6b8'),
  ('end', u'\ue6b9'),
  ('clock', u'\ue6ba'),
  ('phoneto', u'\ue6ce'),
  ('mailto', u'\ue6cf'),
  ('faxto', u'\ue6d0'),
  ('info01', u'\ue6d1'),
  ('info02', u'\ue6d2'),
  ('mail', u'\ue6d3'),
  ('by-d', u'\ue6d4'),
  ('d-point', u'\ue6d5'),
  ('yen', u'\ue6d6'),
  ('free', u'\ue6d7'),
  ('id', u'\ue6d8'),
  ('key', u'\ue6d9'),
  ('enter', u'\ue6da'),
  ('clear', u'\ue6db'),
  ('search', u'\ue6dc'),
  ('new', u'\ue6dd'),
  ('flag', u'\ue6de'),
  ('freedial', u'\ue6df'),
  ('sharp', u'\ue6e0'),
  ('mobaq', u'\ue6e1'),
  ('one', u'\ue6e2'),
  ('two', u'\ue6e3'),
  ('three', u'\ue6e4'),
  ('four', u'\ue6e5'),
  ('five', u'\ue6e6'),
  ('six', u'\ue6e7'),
  ('seven', u'\ue6e8'),
  ('eight', u'\ue6e9'),
  ('nine', u'\ue6ea'),
  ('zero', u'\ue6eb'),
  ('heart01', u'\ue6ec'),
  ('heart02', u'\ue6ed'),
  ('heart03', u'\ue6ee'),
  ('heart04', u'\ue6ef'),
  ('happy01', u'\ue6f0'),
  ('angry', u'\ue6f1'),
  ('despair', u'\ue6f2'),
  ('sad', u'\ue6f3'),
  ('wobbly', u'\ue6f4'),
  ('up', u'\ue6f5'),
  ('note', u'\ue6f6'),
  ('spa', u'\ue6f7'),
  ('cute', u'\ue6f8'),
  ('kissmark', u'\ue6f9'),
  ('shine', u'\ue6fa'),
  ('flair', u'\ue6fb'),
  ('annoy', u'\ue6fc'),
  ('punch', u'\ue6fd'),
  ('bomb', u'\ue6fe'),
  ('notes', u'\ue6ff'),
  ('down', u'\ue700'),
  ('sleepy', u'\ue701'),
  ('sign01', u'\ue702'),
  ('sign02', u'\ue703'),
  ('sign03', u'\ue704'),
  ('impact', u'\ue705'),
  ('sweat01', u'\ue706'),
  ('sweat02', u'\ue707'),
  ('dash', u'\ue708'),
  ('sign04', u'\ue709'),
  ('sign05', u'\ue70a'),
  ('ok', u'\ue70b'),
  ('appli01', u'\ue70c'),
  ('appli02', u'\ue70d'),
  ('t-shirt', u'\ue70e'),
  ('moneybag', u'\ue70f'),
  ('rouge', u'\ue710'),
  ('denim', u'\ue711'),
  ('snowboard', u'\ue712'),
  ('bell', u'\ue713'),
  ('door', u'\ue714'),
  ('dollar', u'\ue715'),
  ('pc', u'\ue716'),
  ('loveletter', u'\ue717'),
  ('wrench', u'\ue718'),
  ('pencil', u'\ue719'),
  ('crown', u'\ue71a'),
  ('ring', u'\ue71b'),
  ('sandclock', u'\ue71c'),
  ('bicycle', u'\ue71d'),
  ('japanesetea', u'\ue71e'),
  ('watch', u'\ue71f'),
  ('think', u'\ue720'),
  ('confident', u'\ue721'),
  ('coldsweats01', u'\ue722'),
  ('coldsweats02', u'\ue723'),
  ('pout', u'\ue724'),
  ('gawk', u'\ue725'),
  ('lovely', u'\ue726'),
  ('good', u'\ue727'),
  ('bleah', u'\ue728'),
  ('wink', u'\ue729'),
  ('happy02', u'\ue72a'),
  ('bearing', u'\ue72b'),
  ('catface', u'\ue72c'),
  ('crying', u'\ue72d'),
  ('weep', u'\ue72e'),
  ('ng', u'\ue72f'),
  ('clip', u'\ue730'),
  ('copyright', u'\ue731'),
  ('tm', u'\ue732'),
  ('run', u'\ue733'),
  ('secret', u'\ue734'),
  ('recycle', u'\ue735'),
  ('r-mark', u'\ue736'),
  ('danger', u'\ue737'),
  ('ban', u'\ue738'),
  ('empty', u'\ue739'),
  ('pass', u'\ue73a'),
  ('full', u'\ue73b'),
  ('leftright', u'\ue73c'),
  ('updown', u'\ue73d'),
  ('school', u'\ue73e'),
  ('wave', u'\ue73f'),
  ('fuji', u'\ue740'),
  ('clover', u'\ue741'),
  ('cherry', u'\ue742'),
  ('tulip', u'\ue743'),
  ('banana', u'\ue744'),
  ('apple', u'\ue745'),
  ('bud', u'\ue746'),
  ('maple', u'\ue747'),
  ('cherryblossom', u'\ue748'),
  ('riceball', u'\ue749'),
  ('cake', u'\ue74a'),
  ('bottle', u'\ue74b'),
  ('noodle', u'\ue74c'),
  ('bread', u'\ue74d'),
  ('snail', u'\ue74e'),
  ('chick', u'\ue74f'),
  ('penguin', u'\ue750'),
  ('fish', u'\ue751'),
  ('delicious', u'\ue752'),
  ('smile', u'\ue753'),
  ('horse', u'\ue754'),
  ('pig', u'\ue755'),
  ('wine', u'\ue756'),
  ('shock', u'\ue757')
])

BANNED_EMOJI = dict([
  ('mist', u'\ue644'),
  ('snail', u'\ue74e'),
  ('banana', u'\ue744'),
  ('carouselpony', u'\ue679'),
  ('cherry', u'\ue742'),
  ('pass', u'\ue73a'),
  ('ban', u'\ue738'),
  ('recycle', u'\ue735'),
  ('ng', u'\ue72f'),
  ('watch', u'\ue71f'),
  ('sandclock', u'\ue71c'),
  ('door', u'\ue714'),
  ('snowboard', u'\ue712'),
  ('denim', u'\ue711'),
  ('moneybag', u'\ue70f'),
  ('appli02', u'\ue70d'),
  ('appli01', u'\ue70c'),
  ('sign05', u'\ue70a'),
  ('sign04', u'\ue709'),
  ('impact', u'\ue705'),
  ('cute', u'\ue6f8'),
  ('mobaq', u'\ue6e1'),
  ('freedial', u'\ue6df'),
  ('clear', u'\ue6db'),
  ('free', u'\ue6d7'),
  ('d-point', u'\ue6d5'),
  ('by-d', u'\ue6d4'),
  ('info02', u'\ue6d2'),
  ('info01', u'\ue6d1'),
  ('end', u'\ue6b9'),
  ('true', u'\ue6b8'),
  ('soon', u'\ue6b7'),
  ('chair', u'\ue6b2'),
  ('pouch', u'\ue6ad'),
  ('pocketbell', u'\ue65a'),
])
