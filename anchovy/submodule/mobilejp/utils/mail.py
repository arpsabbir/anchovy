# -*- coding: utf-8 -*-
import unicodedata
from urllib import quote
from mobilejp.emoji import unquote_emoji, replace_emoji
from mobilejp.middleware import get_current_device

class BaseMailtoScheme(object):
    def __init__(self, carrier, to=None, subject=None, body=None):
        self.carrier = carrier
        self.to = to or ''
        self.subject = subject
        self.body = body

    def __unicode__(self):
        carrier = self.carrier
        if carrier == 'D':
            body = self.body and unquote_emoji(self.body) or None
            subject = self.subject and unquote_emoji(self.subject) or None
        elif carrier == 'E':
            # TODO
            #unicodedata.normalize('NFKC')
            body = self.body and unquote_emoji(self.body) or None
            subject = self.subject and unquote_emoji(self.subject) or None
        elif carrier == 'S':
            body = None
            subject = None
        else:
            body = self.body and replace_emoji(self.body).encode('utf-8') or None
            subject = self.subject and replace_emoji(self.subject).encode('utf-8') or None

        mailto_params = []
        if subject:
            mailto_params.append((u'subject', subject))
        if body:
            mailto_params.append((u'body', body))
        mailto = u'%s%s%s' % (self.to,
                              mailto_params and u'?' or '',
                              u'&'.join([u'%s=%s' % (k, quote(v)) for k, v in mailto_params])
                              )
        return mailto

class MailtoScheme(BaseMailtoScheme):
    def __init__(self, to=None, subject=None, body=None, accesskey=None, style=None):
        super(MailtoScheme, self).__init__(get_current_device(),
                                           to, subject, body, accesskey, style)
