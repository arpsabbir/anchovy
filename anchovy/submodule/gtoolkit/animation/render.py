# -*- coding:utf-8 -*-
import StringIO
import os
from django.conf import settings
from django.template import loader, RequestContext
from django.http import HttpResponse
# tomato
from tomato import Swf, create_swf, SwfImage
# submodules
try:
    # gsocial系
    from gsocial.templatetags.osmobile import (
        opensocial_swf_next_url_convert as swf_url_convert,
        opensocial_session_url_convert as session_url_convert
    )
except ImportError:
    # opensocial系
    from opensocial.templatetags.osmobile import (
        opensocial_swf_next_url_convert as swf_url_convert,
        opensocial_session_url_convert as session_url_convert
    )

from mobilejp.middleware.mobile import get_current_device
from gtoolkit import simple_join_url
from gtoolkit.animation.param_map import get_animation_param_name
from gtoolkit.image import Image, get_device_name
from gtoolkit.image2.image import Image as Image2

CACHE_ON = False
_swf_cache = {}

EXTENSION_SWF = 'swf'
ANIMATION_BASE_PATH = os.path.join(settings.MEDIA_ROOT, 'movies')
ANIMATION_HTML_SETTINGS_KEY = 'ANIMATION_HTML_{}_TEMPLATE'
REDBERRY_PARAM_VERSION_KEY = 'redberry-converter-version'


def render_animation(request, animation_name, next_url, params=None,
                     replace_images=None, replace_clips=None,
                     next_is_media=False, using_reel=False):
    """
    アニメーションをレンダリングして返す

    :param request: HttpRequest
    :param string animation_name: レンダリングしたいアニメーション名
    :param string next_url: 次の遷移先へのURL
    :param dict params: 通常のパラメータ {VAR_NAME: VALUE, ...}
    :param dict replace_images: 画像差し替え {PARAM_NAME: Image, ...}
    :param dict replace_clips: ムービークリップ差し替え
        {PARAM_NAME: ('SWF_NAME', 'MOVIE_CLIP_NAME'), ...}
    :param bool next_is_media: 遷移先がSWFかどうか
    :param bool using_reel: SPの場合Reel出力を行うか
    """

    if params is None:
        params = {}

    # 遷移先URLの調整
    if next_is_media:
        params['next_url'] = session_url_convert(next_url)
    else:
        params['next_url'] = swf_url_convert(next_url)

    # テキスト用変数の初期化と適用
    params = _fix_str_params(params)

    return _render(
        request,
        animation_name,
        next_url,
        params=params,
        replace_images=replace_images,
        replace_clips=replace_clips,
        using_reel=using_reel
    )


class NoQuotingString(str):
    """
    animation_tags の _write_args_type_dict_item() で
    ダブルクォーテーションで囲われない文字列。

    RedberryのJSのムービー合成の時、関数を渡す必要があるため
    """
    pass


def _fix_str_params(params):
    """
    メッセージウィンドウのデフォルメッセージを空文字列に設定
    """
    base_params = {}
    for page in range(1, 6):
        for line in range(1, 5):
            base_params['str{page}_{line}'.format(page=page, line=line)] = u''

    base_params.update(params)

    return base_params


def _open_read(path):
    """
    パスからファイルをロードして返す
    """
    if CACHE_ON and path in _swf_cache:
        # キャッシュにヒット
        return _swf_cache[path]

    data = open(path).read()

    if CACHE_ON:
        # キャッシュする
        _swf_cache[path] = data

    return data


def _load_swf(path):
    """
    SWFをロードする
    """
    return Swf(_open_read(path))


class ImageDoesNotExist(Exception):
    pass


def _replace_image_loader(swf_name, replace_images, animation_type,
                          is_redberry=False):
    """
    Flash埋め込み用画像を読み込む
    replace_images = {'key': instance of Image} ==> {'key': raw_data}
    """
    if not replace_images:
        return {}

    result = {}
    for key, image in replace_images.items():
        if isinstance(image, (Image, Image2)):
            object_key = get_animation_param_name(swf_name, animation_type, key)
            if object_key:
                if animation_type in ['swf', 'reel']:
                    result[object_key] = image.media

                if animation_type in ['html']:
                    if is_redberry:
                        if isinstance(image, Image):
                            result[object_key] = \
                                get_device_name() + '/' + image.path
                        elif isinstance(image, Image2):
                            result[object_key] = image.reactive_path
                    else:
                        result[object_key] = image.url

                    if not image.is_exists and not getattr(image,
                                                           'dummy_image', None):
                        raise ImageDoesNotExist(image.url)

    return result


def _render_swf_replace(swf_name, params, replace_images=None,
                        replace_clips=None, using_reel=False):
    """
    SWFの内部オブジェクトを置き換えて返す
    """

    # 元ファイル
    swf_path = _get_swf_path(swf_name)
    swf = _load_swf(swf_path)

    if replace_clips:
        # ムービークリップを置き換え
        swf = _swf_replace_clips(swf, replace_clips)

    if replace_images:
        # 画像置き換え
        swf = _swf_replace_images(
            swf, _replace_image_loader(swf_name,
                                       replace_images,
                                       animation_type='swf')
        )

    # 最終出力用
    base_swf = StringIO.StringIO()
    swf.write(base_swf)

    # swf からbase_swfを生成
    out_swf = create_swf(base_swf.getvalue(), params)

    return out_swf


def _swf_replace_images(base_swf, replace_images):
    """
    画像の置き換え
    """
    if isinstance(base_swf, Swf):
        # SwfならSwfImageへ変換
        base_swf = SwfImage(base_swf.write())

    base_swf.replace_images(replace_images)

    return base_swf


def _swf_replace_clips(base_swf, replace_clips):
    """
    ムービークリップの置き換え
    """
    if isinstance(base_swf, SwfImage):
        # 元がSwfImageならSwfへ変換
        tmp_base_swf = StringIO.StringIO()
        base_swf.write(tmp_base_swf)
        base_swf = Swf(tmp_base_swf)

    # 差し替え
    for scene_name, clip_data in replace_clips.items():
        clip_name, clip_mc_name = clip_data
        clip_swf = _load_swf(_get_swf_path(clip_name))
        clip_mc = clip_swf.get_movie_clip(clip_mc_name)
        base_swf.replace_movie_clip(scene_name, clip_mc)

    return base_swf


def _render_swf(swf_name, params, replace_images=None, replace_clips=None,
                using_reel=False):
    """
    パラメータのみの置き換え
    :param dict params: {'VAR NAME': VALUE, ...}
    :param dict replace_images:
    :param dict replace_clips:
    """

    if replace_images or replace_clips:
        # SWF内部差し替え
        return _render_swf_replace(
            swf_name, params,
            replace_images=replace_images,
            replace_clips=replace_clips,
            using_reel=using_reel
        )

    swf_path = _get_swf_path(swf_name, using_reel)
    try:
        swf = create_swf(_open_read(swf_path), params)
    except IOError:
        if using_reel:
            swf = create_swf(_open_read(_get_swf_path(swf_name)), params)
        else:
            raise
    return swf


def _get_swf_path(swf_filename, using_reel=False):
    return os.path.join(
        ANIMATION_BASE_PATH,
        'reel' if using_reel else 'swf',
        swf_filename + '.' + EXTENSION_SWF)


class TooLargeSwfError(Exception):
    pass


def _raise_if_swf_size_is_too_large(response):
    """
    SWFサイズをチェックし、規定サイズ以上であれば raise する
    """
    size_threshold = getattr(
        settings, 'GTOOLKIT_ANIMATION_FP_SIZE_THRESHOLD', 98 * 1024)

    dump_file = getattr(
        settings, 'GTOOLKIT_ANIMATION_FP_ERROR_DUMP_FILE', None)

    response_size = len(str(response))

    if response_size > size_threshold:
        if dump_file:
            if isinstance(dump_file, basestring):
                # ダンプファイル名が指定されていればそこに上書きする
                with open(dump_file, 'w') as fp:
                    fp.write(response.content)
            else:
                Exception(u'ダンプ先には有効なパス名を指定してください')

        raise TooLargeSwfError(u'SWFファイル100KBオーバー ({}: {}B)'.format(
            type(response.content), response_size))


def _render(request, animation_name, next_url, params, replace_images=None,
            replace_clips=None, using_reel=False):
    """
    デバイスにあわせてレンダリングする種類を切り替える
    """
    if get_current_device().is_featurephone:
        # FP用SWF
        out_swf = _render_swf(animation_name,
                              params=params,
                              replace_images=replace_images,
                              replace_clips=replace_clips)

        # ヘッダ付与して返す
        response = HttpResponse(mimetype='application/x-shockwave-flash')
        response.write(out_swf)

        if settings.DEBUG:
            _raise_if_swf_size_is_too_large(response)

        return response

    # SP
    return _render_html(
        request,
        animation_name,
        next_url,
        params=params,
        replace_images=replace_images,
        replace_clips=replace_clips,
        using_reel=using_reel
    )


def _render_html(request, animation_name, next_url, params,
                 replace_images=None, replace_clips=None, using_reel=False):

    """
    HTMLベースの非Flashアニメーションレンダリング
    """

    params['next_url'] = session_url_convert(next_url, request)

    if using_reel or int(request.GET.get('reel', 0)):
        # REEL出力
        if 'swf' in request.GET and int(request.GET['swf']):
            # 元になるSWF出力
            out_swf = _render_swf(
                animation_name,
                params=params,
                replace_images=replace_images,
                replace_clips=replace_clips,
                using_reel=using_reel
            )
            response = HttpResponse(mimetype='application/x-shockwave-flash')
            response.write(out_swf)
            return response

        # HTML出力
        params['flash_url'] = request.path + '?swf=1&reel=1'
        t, origin = loader.find_template(
            'reel_base.html',
            [os.path.join(settings.ROOT_PATH,
                          'templates', 'website', 'common')])

        return HttpResponse(t.render(RequestContext(request, params)))

    # 専用素材へのベースURL
    params['materials_base_path'] = simple_join_url(
        settings.STATIC_URL, 'movies/html/' + animation_name)
    params['material_base_path'] = params['materials_base_path']

    # 画像をParamsに統合
    params.update(_replace_image_loader(animation_name, replace_images, 'html'))

    # 自動変数置き換え対象をリストアップ
    params['param_keys'] = params.keys()

    # redberry用
    params['base_path'] = settings.STATIC_URL
    params['redberry_orig_path'] = 'movies/html/' + animation_name
    params['redberry_common_path'] = 'images'
    params['redberry_replace_images'] = _replace_image_loader(
        animation_name, replace_images, 'html', is_redberry=True)
    params['image_base_path'] = params['materials_base_path']

    # redberry ムービークリップ置き換え
    # <script>タグで外部HTMLを読み込む用
    # (テンプレートローダー animation_redberry.Loader で置換)
    child_movie_clip_links = []
    # write_redberry_configuration_modifier で child_movieclips を置き換える用
    # (animation_tags.write_redberry_configuration_modifier で置換)
    redberry_replace_clips = {}
    if replace_clips:
        for place_holder, (child_movie_clip_file_name,
                           function_name) in replace_clips.items():
            child_movie_clip_links.append(
                '<script type="text/javascript" src="{}"></script>'.format(
                    child_movie_clip_file_name))
            redberry_replace_clips[place_holder] = NoQuotingString(function_name)

    params['child_movie_clip_links'] = '\n'.join(child_movie_clip_links)
    params['redberry_replace_clips'] = redberry_replace_clips

    t, origin = loader.find_template('index.html',
                                     [os.path.join(ANIMATION_BASE_PATH,
                                                   'html', animation_name)])

    version = get_redberry_version_from_template(t)

    params['animation_html_header'] = get_redberry_animation_html(
        'HEADER', version)
    params['animation_html_footer'] = get_redberry_animation_html(
        'FOOTER', version)
    params['animation_html_extension'] = get_redberry_animation_html(
        'EXTENSION', version)

    params['animation_name'] = animation_name
    params['redberry_version'] = version

    return HttpResponse(t.render(RequestContext(request, params)))


def get_redberry_version_from_template(t):
    from django.template import TextNode

    version = None
    for n in t.nodelist:
        if isinstance(n, TextNode):
            s = n.s
            if s[:3] == '{--' and s[-3:] == '--}':
                key, val = s[3:-3].split(':')
                if key == REDBERRY_PARAM_VERSION_KEY:
                    return _version_tuple(val, (0, 0, 0))

    return 0, 0, 0


def get_redberry_animation_html(html_type, version):

    key = ANIMATION_HTML_SETTINGS_KEY.format(html_type)
    template_list = getattr(settings, key, None)

    if template_list:

        if isinstance(template_list, basestring):
            return template_list

        elif isinstance(template_list, (tuple, list)):
            for min_ver, max_ver, name in template_list:
                min_ver = _version_tuple(min_ver, (0, 0, 0))
                max_ver = _version_tuple(max_ver, (255, 255, 255))
                if min_ver <= version <= max_ver:
                    return name
            return None
        else:
            raise Exception(u'invalid settings.{}'.format(key))

    return None


def _version_tuple(ver, default=(0, 0, 0)):
    if isinstance(ver, basestring):
        return tuple(int(s) for s in ver.split('.'))
    elif isinstance(ver, list):
        return tuple(ver)
    elif isinstance(ver, tuple):
        return ver
    return default
