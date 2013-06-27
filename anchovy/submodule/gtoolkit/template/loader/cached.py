# -*- coding:utf-8 -*-
import hashlib
from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.template.loader import get_template_from_string
from django.template.loaders.cached import Loader as CachedLoader


class Loader(CachedLoader):
    u"""
    一度読んだら内部にテンプレート内容をキャッシュするテンプレートローダー

    拡張するために内部メソッドの分割とフックポイントの追加を行った
    """

    def load_template(self, template_name, template_dirs=None):
        key = self._get_key(template_name, template_dirs)

        if settings.DEBUG:
            # デバッグ時はキャッシュしない
            template, origin = self._get_template(template_name, template_dirs)
            return template, None

        if key not in self.template_cache:
            template, origin = self._get_template(template_name, template_dirs)
            self.template_cache[key] = template

        return self.template_cache[key], None

    def _get_template(self, template_name, template_dirs):
        """
        テンプレートの取得

        :param template_name:
        :type template_name: str

        :param template_dirs:
        :type: list or None

        :rtype: Template, origin
        """
        template, origin = self.find_template(template_name, template_dirs)
        if not hasattr(template, 'render'):
            try:
                template = get_template_from_string(template, origin,
                                                    template_name)
            except TemplateDoesNotExist:
                pass

        return template, origin

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
        key = template_name
        if template_dirs:
            key = '-'.join([template_name,
                            hashlib.sha1('|'.join(template_dirs)).hexdigest()])
        return key
