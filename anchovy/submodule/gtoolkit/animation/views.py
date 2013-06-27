# -*- coding: utf-8 -*-
import importlib
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.generic.base import View
from gtoolkit.animation.param_map import load_animation_id_map
from gtoolkit.animation.render import render_animation


class AnimationResponseMixin(object):
    """
    swfファイルをレンダリングする
    """
    animation_name = None
    use_id_map = False

    def render_animation(self, request, next_url, params=None, replace_images=None,
                         replace_clips=None, using_reel=False, **kwargs):
        """
        Returns a response with a template rendered with the given context.

        :param use_id_map:
            .idmap.json ファイルを読み込むかどうか。
            True の場合は、swf, html で .idmap.json を使う。
            'swf', 'html', 'reel' からなるシーケンスを渡すと、
            指定されたフォーマットでのみ使う。

        """
        if self.use_id_map:
            # id_mapのロードを試みる。ロード済みなら何もせず早期returnされる。
            if self.use_id_map is True:
                load_animation_id_map(self.get_animation_names())
            else:
                load_animation_id_map(self.get_animation_names(),
                                      animation_types=self.use_id_map)

        if params and hasattr(self, 'os_user'):
            # プレイヤーが生えてればいれる
            params.update({'os_user': getattr(self, 'os_user')})

        # settingsに、GTOOLKIT_RENDER_ANIMATION_HOOKS が定義してある場合、
        # そこで引数を処理する
        hook_functions = self._get_hook_functions()
        if hook_functions:
            for hook_function in hook_functions:
                request, next_url, params, replace_images, \
                    replace_clips, using_reel, kwargs = \
                    hook_function(self, request, next_url, params,
                                  replace_images, replace_clips,
                                  using_reel, kwargs)

        return render_animation(
            request,
            self.get_animation_names(),
            next_url,
            params=params,
            replace_images=replace_images,
            replace_clips=replace_clips,
            using_reel=using_reel,
            **kwargs
        )

    def get_animation_names(self):
        if self.animation_name is None:
            raise ImproperlyConfigured(
                "AnimationResponseMixin requires either a definition of "
                "'animation_name' or an implementation of "
                "'get_animation_names()'")
        else:
            return self.animation_name

    def _get_hook_functions(self):
        """
        :return: settings から取得したフック関数のリスト
        :rtype: list or None

        settingsの例::

            GTOOLKIT_RENDER_ANIMATION_HOOKS = (
                'module.configuration.hooks.quality_configuration_hook',
            )

        GTOOLKIT_RENDER_ANIMATION_HOOKS には、関数のインポートパスを列挙する。
        この関数は、引数
        view, request, next_url, params, replace_images, replace_clips,
        using_reel, kwargs
        をとり、
        request, next_url, params, replace_images, \
        replace_clips, using_reel, kwargs
        を返す関数でなければならない。
        """
        hook_settings = getattr(
            settings, 'GTOOLKIT_RENDER_ANIMATION_HOOKS', None)
        if not hook_settings:
            return None
        hook_functions = []
        for hook_function_paths in hook_settings:
            module_name, func_name = hook_function_paths.rsplit('.', 1)
            m = importlib.import_module(module_name)
            hook_functions.append(getattr(m, func_name))
        return hook_functions


class AnimationView(AnimationResponseMixin, View):
    """
    アニメーションをレンダリングする

    必要な部分のみ上書きして使える
    """

    next_url_name = None
    next_url_args = []
    reel = False


    def get(self, request, *args, **kwargs):
        return self.render_animation(
            request,
            self.get_next_url(request, *args, **kwargs),
            params=self.get_params(request, *args, **kwargs),
            replace_images=self.get_replace_images(request, *args, **kwargs),
            replace_clips=self.get_replace_clips(request, *args, **kwargs),
            using_reel=self.reel
        )


    def get_next_url(self, request, *args, **kwargs):
        """
        アニメーションの次のURLを返す
        """
        return reverse(self.next_url_name, args=self.next_url_args)


    def get_params(self, request, *args, **kwargs):
        """
        アニメーション生成に使用するパラメータのdictを返す
        """
        return {}


    def get_replace_images(self, request, *args, **kwargs):
        """
        アニメーション生成に使用する画像のdictを返す

        :example:
            {
                'card1': cards[0].image.large,
                'card2': cards[1].image.large
            }
        """
        return {}


    def get_replace_clips(self, request, *args, **kwargs):
        """
        アニメーション生成時に差し替えるムービクリッップを返す

        :example:
            {
                'clip_name': ('swf_filename', 'movie_clip_name'),
            }
        """
        return {}
