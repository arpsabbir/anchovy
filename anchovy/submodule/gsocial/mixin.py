# -*- coding: utf-8 -*-
"""
GreeSocialMixin(PlayerMixinClass)
=====================

概要
-----------------

・サムネイルURLを取得できるpropertyメソッドが使えるようになる


注意点
-----------
・APIリクエスト負荷軽減のため、ThumnailUrlは1日キャッシュします。
・キャッシュキーにはPlayer.id(opensocial_owner_id)が利用されることを想定しています。
・ローカル開発時は下記サムネイルを利用します。

> IMG_NORMAL: 'http://sb.gree.jp/img/profile/avatar48.gif',
> IMG_SMALL: 'http://sb.gree.jp/img/profile/avatar25.gif',
> IMG_LARGE: 'http://sb.gree.jp/img/profile/avatar4876.gif',
> IMG_HUGE:  'http://sb.gree.jp/img/profile/avatar190.gif',


HowTo
--------
1.PlayerクラスでGreeSocialMixinを継承させる
2.メソッドの利用方法

> player = Player.get(1)
> player.gree_thumbnail_normal_url #48x48 URL
> player.gree_thumbnail_small_url #25x25 URL
> player.gree_thumbnail_large_url #76x48
> player.gree_thumbnail_huge_url #190x120
"""

import msgpack
from gsocial.log import Log


from django.core.cache import cache
from django.conf import settings

from gsocial.utils.people import People
from mobilejp.middleware.mobile import get_current_request

class GreeSocialMixin(object):
    IMG_SMALL  = 1
    IMG_NORMAL = 2
    IMG_LARGE  = 3
    IMG_HUGE   = 4

    THUMBNAIL_MAPS = {
        IMG_NORMAL: 'thumbnailUrl',
        IMG_SMALL: 'thumbnailUrlSmall',
        IMG_LARGE: 'thumbnailUrlLarge',
        IMG_HUGE: 'thumbnailUrlHuge',
    }

    LOCAL_THMBNAIL_MAPS = {
        IMG_NORMAL: 'http://sb.gree.jp/img/profile/avatar48.gif',
        IMG_SMALL: 'http://sb.gree.jp/img/profile/avatar25.gif',
        IMG_LARGE: 'http://sb.gree.jp/img/profile/avatar4876.gif',
        IMG_HUGE:  'http://sb.gree.jp/img/profile/avatar190.gif',
    }

    CACHE_TIME = 60 * 60 * 24

    @property
    def gree_thumbnail_normal_url(self):
        """
        通常URL
        """
        return self.get_gree_thumbnail_url(size_type=self.IMG_NORMAL)

    @property
    def gree_thumbnail_small_url(self):
        """
        SmallURL
        """
        return self.get_gree_thumbnail_url(size_type=self.IMG_SMALL)

    @property
    def gree_thumbnail_large_url(self):
        """
        LargeUrl
        """
        return self.get_gree_thumbnail_url(size_type=self.IMG_LARGE)

    @property
    def gree_thumbnail_huge_url(self):
        """
        HugeUrl
        """
        return self.get_gree_thumbnail_url(size_type=self.IMG_HUGE)


    def thumbnail_path_key(self):
        """
        cache用 thumbnail_path_key
        """
        return "thumbnail_url_cache:%s" % self.id


    def get_or_cache_thumbnail_list(self):
        """
        cacheがなければAPIgetする
        """
        url_list = {}
        path = self.thumbnail_path_key()
        try:
            data = cache.get(path, None)
            if data:
                Log.debug("data %s" % data)
                url_list = msgpack.unpackb(data)
                Log.debug("data url_list %s" % url_list)
            else:
                request = get_current_request()
                request_params = [value for key,value in self.THUMBNAIL_MAPS.items()]
                request_params = (',').join(request_params)
                profile = People(request).get_myself(self.id, request_params, caching=False)
                for key, value in self.THUMBNAIL_MAPS.items():
                    url_list[value] = profile[value]
                Log.debug("new data url_list %s" % url_list)

                pack_data = msgpack.packb(url_list)
                Log.debug("pack_data url_list %s" % pack_data)
                cache.set(path, pack_data, timeout=self.CACHE_TIME)
        except:
            url_list = {}
        Log.debug("return url_list %s" % url_list)

        return url_list

    def delete_cache_thumbnail_list(self):
        cache.delete(self.thumbnail_path_key())


    def get_gree_thumbnail_url(self, size_type=IMG_NORMAL):
        """
        指定したSIZE TYPEのイメージURLを返す
        """
        #self.delete_cache_thumbnail_list()
        if settings.OPENSOCIAL_DEBUG:
            url = self.LOCAL_THMBNAIL_MAPS[size_type]
        else:
            size = self.THUMBNAIL_MAPS[size_type]
            url_list = self.get_or_cache_thumbnail_list()

            try:
                url = url_list[size]
            except:
                url = None
            Log.debug("thumbnail_url(%s): %s" % (size, url))
        return url
