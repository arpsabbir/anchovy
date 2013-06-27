# -*- coding: utf-8 -*-
"""
templatetags osmobile
"""
import datetime, time
import urllib
from gsocial.log import Log
from django.core.mail import mail_admins

from django import template
from django.conf import settings
from django.template import Node, TemplateSyntaxError, resolve_variable
from django.utils.encoding import smart_str

from gsocial.setting import GREE
from gsocial.set_container import containerdata
from module.maintenance.models import MaintenancePlayer

def url_to_opensocial_url(url, quote=True, url_parameter=True):
    """
    Convert the url to OpensocialUrl and return it.
    argument:
     url:the usual url
     quote: Do quoting(encoding) or not
     url_parameter:Whether there are parameter included in the url
    return value:
     url: URL
      
    URLをOpensocialUrlに変換し、返す

    引数
     url : 通常のURL
     quote : quote（エンコード）するかどうか
     url_parameter : URLに付属するパラメータがあるかどうか

    返り値
     url : URL
    """
    if settings.OPENSOCIAL_DEBUG:
        url = 'http://%s%s' % (settings.SITE_DOMAIN, url)
    else:
        # If given url doesn`t quote(encode)
        # 与えられたurlがquote（エンコード）していない場合
        if quote:
            path = 'http://%s%s'
            url = urllib.quote(path % (settings.SITE_DOMAIN, url), safe='~')
        # If it quote(encode)       
        # quote（エンコード）している場合
        else:
            path = 'http://%s'
            url = urllib.quote(path % (settings.SITE_DOMAIN), safe='~') + url

        url += urllib.quote('?signed=1&t=' + str(time.mktime(datetime.datetime.now().timetuple())))
        if url_parameter:
            url = '?url=%s&guid=ON' % (url)
        else:
            url = '%s&guid=ON' % (url)
    return url

def opensocial_url_convert(url, query=None):
    """
    Create URL and return it
    argument:
     url:URL
     query: dictionary
    return value:
     url: URL
      
    URLを生成し、返す
    引数
     url : URL
     query : 辞書
    返り値
     url : URL
    """
    if settings.OPENSOCIAL_DEBUG:
        if query:
            query_string = ''
            first = True
            for key, value in query.items():
                if first == True:
                    first = False
                else:
                    query_string += '&'
                query_string += '%s=%s' % (key, urllib.quote(value, safe='~'))
            url = 'http://%s%s?%s' % (settings.SITE_DOMAIN, url, query_string)
        else:
            url = 'http://%s%s' % (settings.SITE_DOMAIN, url)
    else:
        if query:
            query_string = ''
            first = True
            for key, value in query.items():
                if first == True:
                    first = False
                else:
                    query_string += '&'
                query_string += '%s=%s' % (key, urllib.quote(value, safe='~'))
            url += urllib.quote('?' + query_string + '&signed=1&t=' + str(time.mktime(datetime.datetime.now().timetuple())))
        else:
            url += urllib.quote('?signed=1&t=' + str(time.mktime(datetime.datetime.now().timetuple())))
        url = '?url=http://%s%s&amp;guid=ON' % (settings.SITE_DOMAIN, url)
    return url

def opensocial_abs_url_convert(url, query=None):
    """
   Create URL and return it
    argument:
     url:URL
     query: not used
    return value:
     url: URL
     
    URLを生成し、返す
   引数
     url : URL
     query : 使ってない 
   返り値
     url : URL
    """
    url = 'http://%s%s?signed=1&guid=ON&t=%s' % (settings.SITE_DOMAIN,
                    url, str(time.mktime(datetime.datetime.now().timetuple())))

    if not settings.OPENSOCIAL_DEBUG:
        app_url = containerdata['app_url'] % {'app_id':settings.APP_ID}
        url = '%s?guid=ON&url=%s' % (app_url, urllib.quote(url))
    return url

def opensocial_media_url_convert(url, query=None):
    """
    Create URL and return it
    Use this when URL refers to swf or image.
    argument:
     url: URL
     query: not used
    return value:
     url:URL
      
    URLを生成し、返す
    swfやimageを返すURLを返す場合に使用する

    引数
     url : URL
     query : 使ってない

    返り値
     url : URL
    """
    if settings.OPENSOCIAL_DEBUG:
        url = 'http://%s%s' % (settings.SITE_DOMAIN, url)
    else:
        if settings.OPENSOCIAL_CONTAINER == 'mixi.jp' or settings.OPENSOCIAL_CONTAINER.endswith(GREE):
            url = 'http://%s%s?signed=1&guid=ON&t=%s' % (settings.SITE_DOMAIN, url,
                                                         str(time.mktime(datetime.datetime.now().timetuple())))
        else:
            media_url = containerdata['media_url'] % {'app_id':settings.APP_ID}
            url += urllib.quote('?signed=1&guid=ON&t=' + str(time.mktime(datetime.datetime.now().timetuple())))
            url = '%s?guid=ON&url=http://%s%s' % (media_url, settings.SITE_DOMAIN, url)
    return url

def opensocial_swf_next_url_convert(url):
    """
    Create URL and return it
    argument:
     url: URL
    return value:
     url: URL
      
    URLを生成し、返す

    引数
     url : URL

    返り値
     url : URL
    """
    params = 'signed=1&guid=ON&t=%s' % str(time.mktime(datetime.datetime.now().timetuple()))
    if '?' in url:
        url = 'http://%s%s&%s' % (settings.SITE_DOMAIN, url, params)
    else:
        url = 'http://%s%s?%s' % (settings.SITE_DOMAIN, url, params)

    if not settings.OPENSOCIAL_DEBUG:
        app_url = containerdata['app_url'] % {'app_id':settings.APP_ID}
        if not app_url[-1] == '/':
            app_url += '/'
        params = 'guid=ON&url=%s' % urllib.quote(url)
        if '?' in app_url:
            url = app_url + '&' + params
        else:
            url = app_url + '?' + params
    return url

def opensocial_media_swf_next_url_convert(url):
    """
    Create URL and return it.
    argument:
     url:URL
    return value:
     url: URL
      
    URLを生成し、返す

    引数
     url : URL

    返り値
     url : URL
    """
    path = 'signed=1&guid=ON&t=%s'
    params = path % str(time.mktime(datetime.datetime.now().timetuple()))
    if '?' in url:
        url = 'http://%s%s&%s' % (settings.SITE_DOMAIN, url, params)
    else:
        url = 'http://%s%s?%s' % (settings.SITE_DOMAIN, url, params)

    if not settings.OPENSOCIAL_DEBUG:
        media_url = containerdata['media_url'] % {'app_id':settings.APP_ID}
        params = 'guid=ON&url=%s' % urllib.quote(url)
        if '?' in media_url:
            url = '%s&%s' % (media_url, params)
        else:
            url = '%s?%s' % (media_url, params)
    return url

def opensocial_url_convert_separate(url):
    """
    Create URL and return it
    This method will return url and url_suffix separately,so you can put some 
    other parameter between this two,if necessary.
    argument:
     url:URL
    return value:
     url:URL
     url_suffix: The parameter after the URL
       
    URLを生成し、返す
    分割してURLを作るバージョン

    引数
     url : URL

    返り値
     url : URL
     url_suffix : URLの後ろに付けるパラメータ（接尾辞）
    """
    if settings.OPENSOCIAL_DEBUG:
        url = 'http://%s%s' % (settings.SITE_DOMAIN, url)
        url_suffix = ''
    else:
        app_url = containerdata['app_url'] % {'app_id':settings.APP_ID}
        str_time = str(time.mktime(datetime.datetime.now().timetuple()))
        url_suffix = urllib.quote('?signed=1&guid=ON&t=' + str_time)
        path = 'http://%s%s'
        next_url_quoted = urllib.quote(path % (settings.SITE_DOMAIN, url))
        url = '%s?signed=1&guid=ON&url=%s' % (app_url, next_url_quoted)
    return url, url_suffix

def opensocial_media_url_convert_separate(url):
    """
    Create URL and return it
    This method will return url and url_suffix separately,so you can put some 
    other parameter between this two,if necessary.
    This method is used if your URL refers to swf or image.
    argument:
     url:URL
    return value:
     url:URL
     url_suffix: The parameter after the URL
     
    URLを生成し、返す
    swfやimageを返すURLを返す場合に使用する
    分割してURLを作るバージョン

    引数
     url : URL

    返り値
     url : URL
     url_suffix : URLの後ろに付けるパラメータ（接尾辞）
    """
    if settings.OPENSOCIAL_DEBUG:
        url = 'http://%s%s' % (settings.SITE_DOMAIN, url)
        url_suffix = ''
    else:
        app_url = containerdata['media_url'] % {'app_id':settings.APP_ID}
        str_time = str(time.mktime(datetime.datetime.now().timetuple()))
        url_suffix = urllib.quote('?signed=1&guid=ON&t=' + str_time)
        path = 'http://%s%s'
        next_url_quoted = urllib.quote(path % (settings.SITE_DOMAIN, url))
        url = '%s?signed=1&guid=ON&url=%s' % (app_url, next_url_quoted)
    return url, url_suffix

def opensocial_session_url_convert(url, request=None, query=None):
    """
    Create URL and return it
    This method will use SessionID from the request.
    argument:
     request: request
     query:dictionary
    return value:
     url:URL
     
     
    URLを生成し、返す
    requestからセッションIDを取り出したりするバージョン

    引数
     url : URL
     request : request
     query : 辞書

    返り値
     url : URL
    """
    if query is None:
        if request and hasattr(request, 'session_id'):
            query = { settings.SESSION_URL_KEY_NAME : request.session_id, }
        else:
            query = {}
    else:
        if request and hasattr(request, 'session_id'):
            query[settings.SESSION_URL_KEY_NAME] = request.session_id

    query_string = ''
    first = True
    for key, value in query.items():
        if first == True:
            first = False
        else:
            query_string += '&'
        query_string += '%s=%s' % (key, urllib.quote(str(value), safe='~'))

    if query_string:
        url = 'http://%s%s?%s' % (settings.SITE_DOMAIN, url, query_string)
    else:
        url = 'http://%s%s' % (settings.SITE_DOMAIN, url)
    return url


register = template.Library()

@register.inclusion_tag('emoji.html', takes_context=True)
def pager(context, paginator):
    u"""
    使っていない
    """
    return { 'value': u'' }

@register.filter
def new_or_timesince(value):
    u"""
    使っていない
    """
    return value

@register.filter
def firstline(value):
    u"""
    使っていない
    """
    return value

@register.filter
def is_maintenance(value):
    u"""
    ユーザーがメンテナンスユーザーか判定する

    例::

        {% if player|is_maintenance %}
            メンテナンスユーザー専用!
        {% endif %}
    """
    if value:
        return MaintenancePlayer.check(value.id)
    else:
        return False



class URLNode(Node):
    """
    URLNode
    """
    def __init__(self, view_name, args, kwargs, asvar, converter, query=None):
        """
        argument
         view_name: Letters
         args: list
         kwargs: dictionary
         asvar:
         converter:
         query:dictionary
         
        引数
         view_name : 文字列
         args : リスト
         kwargs : 辞書
         asvar :
         converter :
         query : 辞書
        """
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar
        self.converter = converter
        self.query = query

    def render(self, context):
        """
        Create URL and return it.
        argument:
         context
        return value:
         url or ''
          
        URLを生成し、返す

        引数
         context

        返り値
         url or ''
        """
        #Log.debug("UrlNode 1")
        from django.core.urlresolvers import reverse, NoReverseMatch
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        try:
            #if view_name is included in context,use it.
            # view_nameがコンテキストに含まれる変数名ならば展開して使う
            view_name = resolve_variable(self.view_name, context)
        except template.VariableDoesNotExist:
            view_name = self.view_name

        if 'request' in context:
            request = context['request']
        else:
            request = None

        url = ''
        try:
            url = reverse(view_name, args=args, kwargs=kwargs, current_app=context.current_app)
        except NoReverseMatch, e:
            if getattr(settings, 'ERROR_PAGE_MAIL', False):
                try:
                    try:
                        request_repr = repr(request)
                    except:
                        request_repr = "Request repr() unavailable"
                    subject = 'opensocial_url_error'
                    message = str(e) + '\r\n\r\n' + request_repr
                    mail_admins(subject, message)
                except:
                    pass

            if settings.SETTINGS_MODULE:
                project_name = settings.SETTINGS_MODULE.split('.')[0]
                try:
                    url = reverse(project_name + '.' + view_name,
                              args=args, kwargs=kwargs, current_app=context.current_app)
                except NoReverseMatch:
                    if self.asvar is None:
                        raise e
            else:
                if self.asvar is None:
                    raise e


        from mobilejp.middleware.mobile import get_current_request, get_current_device
        request= get_current_request()
        device = get_current_device()


        if request and not device.is_featurephone:
            if self.query:
                url = opensocial_session_url_convert(url, request, resolve_variable(self.query, context))
            else:
                url = opensocial_session_url_convert(url, request)

#            from mobilejp.middleware.mobile import get_is_webview
#            if get_is_webview():
#                url += '&is_webview=True'

        else:
            if self.query:
                url = self.converter(url, resolve_variable(self.query, context))
            else:
                url = self.converter(url)

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url

def _opensocial_url_tokenizer(parser, token):
    """
    Analysis parser token and return "viewname args kwargs asvar".
    argument:
     parser
     token
    return value:
     viewname : Letters
     args : list
     kwargs : dictionary
     asvar
      
    parser tokenを解析し、viewname args kwargs asvar を返す

    引数
     parser
     token

    返り値
     viewname : 文字列
     args : リスト
     kwargs : 辞書
     asvar
    """
    #Log.debug("_opensocial_url_tokenizer")
    bits = token.split_contents()
    #Log.debug("_opensocial_url_tokenizer bits: %s" % bits)

    if len(bits) < 2:
        raise TemplateSyntaxError('"%s" takes at least one argument'
                                  ' (path to a view)' % bits[0])
    viewname = bits[1]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 2:
        bits = iter(bits[2:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(','):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return viewname, args, kwargs, asvar

def _opensocial_url_tokenizer_with_query(parser, token):
    """
    Analysis parser token and return "viewname args kwargs asvar".
    argument:
     parser
     token
    return value:
     viewname : Letters
     args : list
     kwargs : dictionary
     asvar
     
    parser tokenを解析し、viewname query args kwargs asvar を返す

    引数
     parser
     token

    返り値
     viewname : 文字列
     query
     args : リスト
     kwargs : 辞書
     asvar
    """
    bits = token.split_contents()

    if len(bits) < 2:
        raise TemplateSyntaxError('"%s" takes at least one argument'
                                  ' (path to a view)' % bits[0])
    query = bits[1]
    viewname = bits[2]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 3:
        bits = iter(bits[3:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(','):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return viewname, query, args, kwargs, asvar

def _opensocial_url_tokenizer_with_body(parser, token):
    """
    Analysis parser token and return "viewname args kwargs asvar".
    This it a tokensizer for inviting to send "body" with GET.
    argument:
     parser
     token
    return value:
     viewname : Letters
     args : list
     kwargs : dictionary
     asvar
    parser tokenを解析し、viewname body args kwargs asvar を返す
    invite用にGETでbodyを渡すためのトークナイザ

    引数
     parser
     token

    返り値
     viewname : 文字列
     body
     args : リスト
     kwargs : 辞書
     asvar
    """
    bits = token.split_contents()

    if len(bits) < 2:
        raise TemplateSyntaxError('"%s" takes at least one argument'
                                  ' (path to a view)' % bits[0])
    body = bits[1]
    viewname = bits[2]
    args = []
    kwargs = {}
    asvar = None

    if len(bits) > 3:
        bits = iter(bits[3:])
        for bit in bits:
            if bit == 'as':
                asvar = bits.next()
                break
            else:
                for arg in bit.split(','):
                    if '=' in arg:
                        k, v = arg.split('=', 1)
                        k = k.strip()
                        kwargs[k] = parser.compile_filter(v)
                    elif arg:
                        args.append(parser.compile_filter(arg))
    return viewname, body, args, kwargs, asvar

def opensocial_url(parser, token):
    u"""
    プラットフォーム提供会社 (例:GREE) の、ガジェットサーバ経由のリンク URL を作成する

    ゲーム内のリンク (aタグ、formタグ等) は、すべてこのテンプレートタグ経由で作ること

    アプリケーションが、http://example.com/game/ というURLで提供されているとしたら、
    ガジェットサーバ経由のURL…つまり、このテンプレートタグで作られる URL はこのようになる

        http://mgadget.gree.jp/00000/?url=http%3A%2F%2Fexample.com%2Fgame%2F

    使い方::

        {% opensocial_url <ビューURL名> [URL引数1] [URL引数2] ... %}

    例::

        {% opensocial_url profile_index player.player.id %}

    """
    viewname, args, kwargs, asvar = _opensocial_url_tokenizer(parser, token)
    return URLNode(viewname, args, kwargs, asvar, converter=opensocial_url_convert)

opensocial_url = register.tag(opensocial_url)

def opensocial_query_url(parser, token):
    u"""
    GETパラメータ付きの opensocial_url を生成する

    GETパラメータは辞書にして第一引数に渡す。

    使い方::

        {% opensocial_query_url <パラメータ辞書> <ビューURL名> [URL引数1] [URL引数2] ... %}
    """
    viewname, query, args, kwargs, asvar = _opensocial_url_tokenizer_with_query(parser, token)
    return URLNode(viewname, args, kwargs, asvar, converter=opensocial_url_convert, query=query)

opensocial_query_url = register.tag(opensocial_query_url)

def opensocial_abs_url(parser, token):
    u"""
    相対URLではなく絶対URLを出す opensocial_url

    使い方は opensocial_url と同じ
    """
    viewname, args, kwargs, asvar = _opensocial_url_tokenizer(parser, token)
    return URLNode(viewname, args, kwargs, asvar, converter=opensocial_abs_url_convert)

opensocial_abs_url = register.tag(opensocial_abs_url)

def opensocial_media_url(parser, token):
    u"""
    画像やswfに使う opensocial_url

    …だったと思う。通常は使わない
    """
    viewname, args, kwargs, asvar = _opensocial_url_tokenizer(parser, token)
    return URLNode(viewname, args, kwargs, asvar, converter=opensocial_media_url_convert)

opensocial_media_url = register.tag(opensocial_media_url)


class OpensocialSpacerNode(template.Node):
    """
    Spacer(images) provided by container.
    Containerが提供するspacer（画像）
    """
    def __init__(self, height):
        self.height = height

    def render(self, context):
        return '<img src="%s" height="%s" width="1" />' % (containerdata['spacer_url'], self.height)

def spacer(parser, token):
    u"""
    スペーサー画像を出す

    ただし、通常はアプリケーション独自の spacer タグが用意されていると思うので、
    これが使われることは基本的に無い。

    使い方::

        {% spacer <高さ> %}
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError('"%s" takes one argument "height"' % bits[0])
    return OpensocialSpacerNode(bits[1])

spacer = register.tag(spacer)


class OpensocialCellUrlNode(template.Node):
    """
    URLNode of Cell
    CellのURLNode
    """
    def __init__(self, view_name, args, kwargs, asvar):
        """
        argument:
         view_name : Letters
         args : List
         kwargs : dictionary
         asvar
         
        引数
         view_name : 文字列
         args : リスト
         kwargs : 辞書
         asvar
        """
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        """
        Create Opensocial Cell URL and return it
        argument:
         context
        return value: 
         opensocial_cell_url
        
        Opensocial Cell URLを生成し、返す

        引数
         context

        返り値
         opensocial_cell_url
        """
        from django.core.urlresolvers import reverse
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        callback_url = reverse(self.view_name, args=args, kwargs=kwargs, current_app=context.current_app)
        if not settings.OPENSOCIAL_DEBUG:
            if settings.OPENSOCIAL_CONTAINER == 'mixi.jp':
                opensocial_cell_url = 'location:cell' + opensocial_url_convert(urllib.quote(callback_url))
            elif settings.OPENSOCIAL_CONTAINER[-7:] == 'mbga.jp':
                opensocial_cell_url = 'location:self' + opensocial_url_convert(urllib.quote(callback_url)) + '&amp;type=cell'
            elif settings.OPENSOCIAL_CONTAINER == GREE:
                opensocial_cell_url = 'location:cell?callbackurl=' + urllib.quote(
                    'http://' + settings.SITE_DOMAIN + callback_url)
            else:
                opensocial_cell_url = callback_url
        else:
            opensocial_cell_url = callback_url
        return opensocial_cell_url

def opensocial_cell_url(parser, token):
    u"""
    地域情報を取得するURLを出す (…だったと思う)

    使い方::

        {% opensocial_cell_url <コールバックビューURL名> [URL引数1] [URL引数2] ... %}
    """
    viewname, args, kwargs, asvar = _opensocial_url_tokenizer(parser, token)
    return OpensocialCellUrlNode(viewname, args, kwargs, asvar)

opensocial_cell_url = register.tag(opensocial_cell_url)


class OpensocialGpsUrlNode(template.Node):
    """
    URLNode of GPS
    GPSのURLNode
    """
    def __init__(self, view_name, args, kwargs, asvar):
        """
        argument
         view_name: letters
         args: list
         kwargs:dictionary
         asvar
        引数
         view_name : 文字列
         args : リスト
         kwargs : 辞書
         asvar
        """
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        """
        Create Opensocial Gps Url and return it.
        argument:
         context
        return value:
          opensocial_gps_url
          
        Opensocial GPS URLを生成し、返す

        引数
         context

        返り値
         opensocial_gps_url
        """
        from django.core.urlresolvers import reverse
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        callback_url = reverse(self.view_name, args=args, kwargs=kwargs, current_app=context.current_app)
        if not settings.OPENSOCIAL_DEBUG:
            if settings.OPENSOCIAL_CONTAINER == 'mixi.jp':
                opensocial_gps_url = 'location:gps' + opensocial_url_convert(urllib.quote(callback_url))
            elif settings.OPENSOCIAL_CONTAINER[-7:] == 'mbga.jp':
                opensocial_gps_url = 'location:self' + opensocial_url_convert(urllib.quote(callback_url)) + '&amp;type=gps'
            elif settings.OPENSOCIAL_CONTAINER.endswith(GREE):
                opensocial_gps_url = 'location:gps?callbackurl=' + urllib.quote(
                    'http://' + settings.SITE_DOMAIN + callback_url)
            else:
                opensocial_gps_url = callback_url
        else:
            opensocial_gps_url = callback_url
        return opensocial_gps_url

def opensocial_gps_url(parser, token):
    u"""
    GPS座標情報を取得するURLを出す

    使い方::

        {% opensocial_gps_url <コールバックビューURL名> [URL引数1] [URL引数2] ... %}
    """
    viewname, args, kwargs, asvar = _opensocial_url_tokenizer(parser, token)
    return OpensocialGpsUrlNode(viewname, args, kwargs, asvar)

opensocial_gps_url = register.tag(opensocial_gps_url)


class OpensocialInviteUrlNode(template.Node):
    """
    Invite URLNode
    招待のURLNode
    """
    def __init__(self, view_name, args, kwargs, asvar, body=None):
        """
        argument:
         view_name:letters
         args: list
         kwargs :dictionary
         asvar
         body
         
        引数
         view_name : 文字列
         args : リスト
         kwargs : 辞書
         asvar
         body
        """
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar
        self.body = body

    def render(self, context):
        """
        Create OpensocialInviteUrl and return it
        argument:
           parser
        return value:
          opensocial_invite_url
       
        Opensocial Invite URLを生成し、返す

        引数
         context

        返り値
         opensocial_invite_url
        """
        from django.core.urlresolvers import reverse
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k,'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        callback_url = reverse(self.view_name, args=args, kwargs=kwargs, current_app=context.current_app)
        if not settings.OPENSOCIAL_DEBUG:
            # mixi
            if settings.OPENSOCIAL_CONTAINER == 'mixi.jp':
                opensocial_invite_url = 'invite:friends?callback=' + urllib.quote(
                    'http://' + settings.SITE_DOMAIN + callback_url)
            # mobage
            elif settings.OPENSOCIAL_CONTAINER[-7:] == 'mbga.jp':
                opensocial_invite_url = 'invite:friends?guid=ON&url=' + urllib.quote(
                    'http://' + settings.SITE_DOMAIN + callback_url)
            # gree
            elif settings.OPENSOCIAL_CONTAINER.endswith(GREE):
                opensocial_invite_url = 'invite:friends?callbackurl=' + urllib.quote(
                    'http://' + settings.SITE_DOMAIN + callback_url)
                if self.body:
                    body = resolve_variable(self.body, context)
                    from mobilejp.middleware.mobile import get_current_request, get_current_device
                    device = get_current_device()
                    if device.is_softbank: # and request.encoding == 'x_utf8_softbank':
                        body = body.encode('utf-8')
                    else:
                        body = body.encode('shift_jis')
                    opensocial_invite_url += '&body=' + urllib.quote_plus(body)
            else:
                opensocial_invite_url = callback_url
        else:
            opensocial_invite_url = callback_url
        return opensocial_invite_url

def opensocial_invite_url(parser, token):
    u"""
    招待サービスを呼び出すURLを出す

    使い方::

        {% opensocial_invite_url <コールバックビューURL名> [URL引数1] [URL引数2] ... %}
    """
    viewname, args, kwargs, asvar = _opensocial_url_tokenizer(parser, token)
    return OpensocialInviteUrlNode(viewname, args, kwargs, asvar)

opensocial_invite_url = register.tag(opensocial_invite_url)

def opensocial_invite_url_with_body(parser, token):
    u"""
    招待サービスを呼び出すURLを出す (招待文言を指定できる)

    使い方::

        {% opensocial_invite_url_with_body <招待文言> <コールバックビューURL名> [URL引数1] [URL引数2] ... %}
    """
    viewname, body, args, kwargs, asvar = _opensocial_url_tokenizer_with_body(parser, token)
    return OpensocialInviteUrlNode(viewname, args, kwargs, asvar, body)

opensocial_invite_url_with_body = register.tag(opensocial_invite_url_with_body)

@register.simple_tag
def opensocial_url_with_domain(reversed_url):
    u"""
    SPの場合、リクエストからセッションIDを取得してURLを出す。
    FPの場合は opensocial_url のように動作する。

    だだし、引数は reverse された URLを取る。

    例::

        {% opensocial_url_with_domain <reverseされたURL> %}
    """
    from mobilejp.middleware.mobile import get_current_request, get_current_device
    request = get_current_request()
    device = get_current_device()

    if request and not device.is_featurephone:
        url = opensocial_session_url_convert(reversed_url, request)
    else:
        url = opensocial_url_convert(reversed_url)

    return url
