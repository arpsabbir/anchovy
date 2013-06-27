# -*- coding: utf-8 -*-
# Use this module for e-mailing.

# This module is almost a copy-and-paste from django.core.mail,
# but is able to send ISO-2022-JP or Shift_JIS encoded mails
# depending on which domain you are sending a e-mail to.

from django.conf import settings
from django.core.mail import SMTPConnection, SafeMIMEText, SafeMIMEMultipart, EmailMessage, make_msgid
from django.utils.encoding import smart_unicode

import re
import unicodedata
from email import charset
from email.MIMEText import MIMEText
from email.header import Header
from email.utils import formatdate, parseaddr

import mobilejpcodecs

CHARSET_DOCOMO = charset.Charset('Shift_JIS')
CHARSET_DOCOMO.header_encoding = charset.BASE64
CHARSET_DOCOMO.body_encoding   = None
CHARSET_DOCOMO.output_charset  = 'Shift_JIS'
CHARSET_DOCOMO.input_codec     = 'x_sjis_docomo'
CHARSET_DOCOMO.output_codec    = 'x_sjis_docomo'

CHARSET_KDDI = charset.Charset('Shift_JIS')
CHARSET_KDDI.header_encoding = charset.BASE64
CHARSET_KDDI.body_encoding   = None
CHARSET_KDDI.output_charset  = 'Shift_JIS'
CHARSET_KDDI.input_codec     = 'x_sjis_kddi'
CHARSET_KDDI.output_codec    = 'x_sjis_kddi'

CHARSET_SOFTBANK = charset.Charset('utf-8')
CHARSET_SOFTBANK.header_encoding = charset.BASE64
CHARSET_SOFTBANK.body_encoding   = None
CHARSET_SOFTBANK.output_charset  = 'utf-8'
CHARSET_SOFTBANK.input_codec     = 'x_utf8_softbank'
CHARSET_SOFTBANK.output_codec    = 'x_utf8_softbank'

CHARSET_NONMOBILE = charset.Charset('iso-2022-jp')
CHARSET_NONMOBILE.header_encoding = charset.BASE64
CHARSET_NONMOBILE.body_encoding   = None
CHARSET_NONMOBILE.output_charset  = 'iso-2022-jp'
CHARSET_NONMOBILE.input_codec     = 'iso-2022-jp'
CHARSET_NONMOBILE.output_codec    = 'iso-2022-jp'


_MAIL_DOMAIN = ((r'docomo\.ne\.jp$', 'D'),
                (r'ezweb\.ne\.jp$', 'E'),
                (r'softbank\.ne\.jp$', 'S'),
                (r'[dhtckrnsq]\.vodafone\.ne\.jp$', 'S'),
                (r'disney\.ne\.jp$', 'S'),
                (r'willcom\.com$', 'W'),
                (r'pdx\.ne\.jp$', 'W'),
                (r'ido\.ne\.jp$', 'E'),
                (r'sky\.(?:tk[ck]|tu\-ka)\.ne\.jp$', 'E'),
                )

MAIL_DOMAIN_RE = [(re.compile(x[0]), x[1]) for x in _MAIL_DOMAIN]

def get_carrier_by_email_address(addr):
    """
    get a carrier from the given email address.
    """
    for r, carrier in MAIL_DOMAIN_RE:
        if r.search(addr):
            return carrier

    # TODO
    # should return None?
    return False

def make_message(short_carrier, subject, body, errors='strict'):
    cst = { 'D' : CHARSET_DOCOMO,
            'E' : CHARSET_KDDI,
            'S' : CHARSET_SOFTBANK,
            'W' : CHARSET_DOCOMO,
            'N' : CHARSET_DOCOMO, # TODO
            }[short_carrier]

    m = MIMEText(body.encode(cst.output_codec, errors),
                 'plain',
                 cst.output_codec)
    m.set_charset(cst)
    m['Subject'] = Header(subject, cst)

    return m

def normalize(value):
    return unicodedata.normalize('NFKC', value)

class PostfixESMTPConnection(SMTPConnection):
    def _send(self, email_message):
        """
        A helper method that does the actual sending.
        Override the default method to use VERP.
        """
        if not email_message.to:
            return False
        try:
            self.connection.sendmail(email_message.from_email,
                                     email_message.recipients(),
                                     email_message.message().as_string(),
                                     mail_options=['XVERP=+=']
                                     )
        except:
            if not self.fail_silently:
                raise
            return False
        return True

class IterableHeader(Header):
    def __iter__(self):
        return iter(self.encode())

class MobileJpEmailMessage(EmailMessage):
    """
    A container for email information.
    """
    def __init__(self, subject='', body='', from_email=None, to=None, bcc=None,
            connection=None, attachments=None, headers=None, force_encoding=None, errors='replace'):
        connection = connection or PostfixESMTPConnection()
        super(MobileJpEmailMessage, self).__init__(subject, body, from_email, to, bcc,
                                                   connection, attachments, headers)
        self.force_encoding = force_encoding
        self.errors = errors

    def message(self):
        if len(self.to) == 1:
            carrier = get_carrier_by_email_address(self.to[0]) or 'N'
        else:
            # TODO
            carrier = 'N'

        msg = make_message(carrier,
                           smart_unicode(self.subject),
                           smart_unicode(self.body),
                           errors=self.errors)

        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.to)
        msg['Date'] = formatdate()
        msg['Message-ID'] = make_msgid()
        if self.bcc:
            msg['Bcc'] = ', '.join(self.bcc)
        for name, value in self.extra_headers.items():
            msg[name] = value
        return msg

def send_mail(subject='', body='', from_email=None, to=None, bcc=None,
              connection=None, attachments=None, headers=None, force_encoding=None):
    MobileJpEmailMessage(subject, body, from_email, to, bcc, connection, attachments,
                         headers, force_encoding).send()
