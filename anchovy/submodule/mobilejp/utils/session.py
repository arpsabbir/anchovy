# -*- coding: utf-8 -*-
import re
from urlparse import urlsplit, urlunsplit, urljoin

__all__ = ['embed_session_id', 'parse_session_id', 'session_uri']

def embed_session_id(url, session_id=None, domain=None, base=None):
    """
    returns a new url that a given session id is embedded in.
    If the session id is None, return the original url.

    >>> embed_session_id('', 'egg')
    ''
    >>> embed_session_id('/', 'egg')
    '/.egg/'
    >>> embed_session_id('/spam', 'egg')
    '/.egg/spam'
    >>> embed_session_id('/spam/', 'egg')
    '/.egg/spam/'
    >>> embed_session_id('#id', 'egg', base='/')
    '#id'
    >>> embed_session_id('/spam/#id', 'egg', base='/spam/')
    '/.egg/spam/#id'
    >>> embed_session_id('?url=spam#id', 'egg')
    '/.egg?url=spam#id'
    >>> embed_session_id('http://example.com#id', 'egg', 'example.com')
    'http://example.com/.egg#id'

    >>> embed_session_id('.', 'egg')
    '.'
    >>> embed_session_id('.', 'egg', base='/top/')
    '/.egg/top/'
    >>> embed_session_id('..', 'egg', base='/top/')
    '/.egg/'
    >>> embed_session_id('..?a=1', 'egg', base='/top/')
    '/.egg/?a=1'
    >>> embed_session_id('../..', 'egg', base='/top/')
    '/.egg/'

    >>> embed_session_id('my', 'egg', base='/')
    '/.egg/my'
    >>> embed_session_id('my?a=1', 'egg', base='/')
    '/.egg/my?a=1'

    >>> embed_session_id('http://localhost/spam/', 'egg', 'localhost')
    'http://localhost/.egg/spam/'

    >>> embed_session_id('https://localhost/spam/', 'egg', 'localhost')
    'https://localhost/.egg/spam/'

    >>> embed_session_id('http://example.org/spam/', 'egg', 'example.com')
    'http://example.org/spam/'

    >>> embed_session_id('http://localhost/spam/', 'egg')
    'http://localhost/spam/'

    >> embed_session_id('https://localhost/spam/', 'egg', 'localhost')
    'https://localhost/.egg/spam/'

    >> embed_session_id('/spam/?spam=1&ham=2', 'abcd')
    '/.abcd/spam/?spam=1&ham=2'

    >> embed_session_id('/spam/#header', 'abcd')
    '/.abcd/spam/#header'

    >> embed_session_id('mailto:info@example.com', 'abcd')
    'mailto:info@example.com'
    >> embed_session_id('ftp://example.com/', 'abcd')
    'ftp://example.com/'
    """
    if session_id is None:
        return url

    if not url:
        return url

    scheme, netloc, path, query, fragment = urlsplit(url)
    if scheme and not scheme.startswith('http'):
        # scheme must be HTTP or HTTPS
        return url

    if netloc and netloc != domain:
        # don't embed a session id in a link to external site
        return url

    if not netloc and not path and not query:
        # like '#id'
        return url

    if base is not None:
        path = urljoin(base, path)
    else:
        if path and not path.startswith('/'):
            # path is relative but 'base' parameter isn't given.
            # we can't determine absolute path
            return url

    path = '/.%s%s' % (session_id, path)
    return urlunsplit((scheme, netloc, path, query, fragment))

URL_SESSION_ID_RE = re.compile(r'^/\.([0-9a-z]+)(.*)$')

def parse_session_id(url):
    """
    parse the given url and return a tuple of the original url
    and the session id.
    If no session is part is found, session id will be None.

    >>> parse_session_id('/spam')
    ('/spam', None)
    >>> parse_session_id('/.egg/spam/')
    ('/spam/', 'egg')
    >>> parse_session_id('/.egg/')
    ('/', 'egg')
    >>> parse_session_id('/.egg')
    ('/', 'egg')
    >>> parse_session_id('/.spam/?egg=ham')
    ('/?egg=ham', 'spam')
    >>> parse_session_id('/.spam?egg=ham')
    ('?egg=ham', 'spam')
    >>> parse_session_id('/.spam/#ham')
    ('/#ham', 'spam')
    >>> parse_session_id('/.spam#ham')
    ('#ham', 'spam')
    >>> parse_session_id('')
    ('', None)
    """
    matcher = URL_SESSION_ID_RE.match(url)
    if matcher:
        session_id, real_path = matcher.groups()
        return (real_path or '/', session_id)
    else:
        return (url, None)

TAG_RE = re.compile(r'<(?:a|form).+?>', re.I|re.S)
HREF_RE = re.compile(r'''(href)=((?:"[^"]+")|(?:'[^']+'))''', re.I)
ACTION_RE = re.compile(r'''(action)=((?:"[^"]+")|(?:'[^']+'))''', re.I)

def session_uri(html, session_id, domain, base):
    def func(matcher):
        key, value = matcher.groups()
        quot = value[0]
        # strip single/double quote
        value = value[1:-1]
        new_value = embed_session_id(value, session_id, domain, base)
        res = '%s=%s%s%s' % (key, quot, new_value, quot)
        return res

    def rewrite_tag(matcher):
        value = matcher.group(0)
        value_lower = value.lower()
        if value_lower.startswith('<a'):
            return HREF_RE.sub(func, value)
        elif value_lower.startswith('<form'):
            return ACTION_RE.sub(func, value)
        else:
            # never reach here
            return matcher.group(0)

    return TAG_RE.sub(rewrite_tag, html)
