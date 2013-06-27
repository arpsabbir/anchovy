# -*- coding: utf-8 -*-
from base import MessageBase
from django.conf import settings
from django.utils import simplejson
from gsocial.log import Log

class MessageGree(MessageBase):
    """
    Message APIを使う（GREE用）
    """
    class Meta:
        proxy = True
        verbose_name = u'Message API(GREE用)'
        verbose_name_plural = verbose_name

    RECIPIENTS_MAX = 20

    def __unicode__(self):
        return self.title

    def platform(self):
        """
        return platform
        """
        return 'gree'

    def _api_request(self, sender_osuser_id, data):
        """
        OAuth リクエスト
        """
        headers={'Content-Type': 'application/json; charset=utf8'}
        path = '/messages/@me/@outbox'
        res = self.container.oauth_request('POST', sender_osuser_id, path,
                                            data, headers, body_hash=True)


    def _send_list(self, send_ids):
        """
        sendlist生成メソッド
        idsを20県ごとにまとめて返す
        返り値: list
        ((1,2,3....),(100,200.....))
        """
        tmp_ids = []
        send_ids_list = []
        Log.debug(u'id listing.')
        for user_id in send_ids:
            tmp_ids.append(user_id)
            if len(tmp_ids) == self.RECIPIENTS_MAX:
                send_ids_list.append(tmp_ids)
                tmp_ids = []
        # 端数
        if len(tmp_ids) > 0:
            send_ids_list.append(tmp_ids)
        total = len(send_ids)
        Log.debug(u'ids: %d.' % total)
        Log.debug(u'ids: %s.' % send_ids_list)
        print send_ids_list
        return send_ids_list

    def sends(self, sender_osuser_id, osuser_ids, title, body,
              relative_mobile_url):
        """
        複数送信（ただし、２０件まで）
        """
        if len(osuser_ids) > self.RECIPIENTS_MAX:
            raise
        mobile_url = relative_mobile_url
        mobile_url = 'http://%s%s' % (settings.SITE_DOMAIN, mobile_url)
        data_format = {
            "title": title, 
            "body": body, 
            "recipients": osuser_ids,
             "urls": [{"value": mobile_url}]
        }
        data = simplejson.dumps(data_format)
        self._api_request(sender_osuser_id, data)

    def send(self, sender_osuser_id, osuser_id, title, body,
             relative_mobile_url):
        """
        単発送信
        """
        self.sends(sender_osuser_id, [osuser_id], title, body,
                   relative_mobile_url)

