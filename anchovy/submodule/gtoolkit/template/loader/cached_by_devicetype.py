# -*- coding:utf-8 -*-

import hashlib
from .cached import Loader as _BaseCachedLoader

try:
    from mobilejp.middleware.mobile import get_current_device
except ImportError:
    get_current_device = None


class Loader(_BaseCachedLoader):
    u"""
    デバイスタイプ別にキャッシュするキーを別にするキャッシュテンプレートローダー
    """

    def _get_key(self, template_name, template_dirs):
        """
        キーの生成

        :param template_name:
        :type template_name: str

        :param template_dirs:
        :type: list or None

        :return: キャッシュ用のキー
        :rtype: str
        """
        if not get_current_device:
            return super(Loader, self)._get_key(template_name, template_dirs)

        key = '-'.join([template_name, self._get_device_type_name()])
        if template_dirs:
            key += '-' + hashlib.sha1('|'.join(template_dirs)).hexdigest()

        return key

    def _get_device_type_name(self):
        device = get_current_device()
        if not device:
            return 'no_device'

        deviceattrs = ['is_webview', 'is_featurephone', 'is_smartphone']

        for deviceattr in deviceattrs:
            if getattr(device, deviceattr, False):
                # もし is_xxx が True だったらそれを返す
                return deviceattr
        else:
            return 'default'
