# -*- coding: utf-8 -*-

import uuid

def generate_uuid(separator=':', *args):
    """
    引数から UUID を生成する.
    """
    return separator.join([str(x) for x in args + (uuid.uuid4(),)])


def simple_join_url(head, tail):
    """
    urlparse.urljoin ほど複雑でない、シンプルなURL結像
    >>> simple_join_url('http://spam/', 'eggs')
    'http://spam/eggs'
    >>> simple_join_url('http://spam', '/eggs')
    'http://spam/eggs'
    >>> simple_join_url('http://spam', 'eggs')
    'http://spam/eggs'
    >>> simple_join_url('http://spam/', '/eggs')
    'http://spam/eggs'
    """
    if head.endswith('/'):
        if tail.startswith('/'):
            return head[:-1] + tail
        return head + tail
    elif tail.startswith('/'):
        return head + tail
    return head + '/' + tail