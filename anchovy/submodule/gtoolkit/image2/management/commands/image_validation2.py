# -*- coding:utf-8 -*-
from optparse import make_option
from django.core.management.base import BaseCommand
from ...device import FEATUREPHONE_DEVICE, SMARTPHONE_DEVICE
from ...exceptions import ImageValidationError
from ...mixins import ImageMixin

# 検査オブジェクトを取得するのに使うクラスメソッドを優先順に
GET_OBJECTS_METHODS = ['get_image_validation_objects', 'get_all']


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-s', '--success', dest='view_success',
                    default=False, action='store_true',
                    help=u'バリデーションに成功した情報も表示します'),
        make_option('-d', '--detail', dest='detail',
                    default=False, action='store_true',
                    help=u'結果表示時にインスタンスの情報を表示します'),
        make_option('-t', '--target', action='store',
                    dest='target', type='string',
                    help=u'指定したクラスのみ実行します'),
    )

    def handle(self, *args, **options):
        """
        画像の状態確認をするバッチ
        """
        for cls in search_last_classes(ImageMixin):

            if hasattr(cls, '_meta') and getattr(cls._meta, 'abstract', False):
                # 抽象クラスはスルー
                continue

            if options['target'] and cls.__name__ != options['target']:
                # 指定がある場合は指定クラスのみ行う
                continue

            print "{} ({} {})".format(cls.__name__, cls.__module__, cls)

            # 使用するオブジェクト取得メソッドを探す
            using_method = None
            for method_name in GET_OBJECTS_METHODS:
                if hasattr(cls, method_name):
                    using_method = method_name
                    break

            if not using_method:
                # インスタンス取得メソッドが生えてない
                warn('{} has not class method {}'.format(
                    cls.__name__, ', '.join(GET_OBJECTS_METHODS)), 'NO CHECK')
                continue

            for obj in getattr(cls, using_method)():
                check_images(obj, FEATUREPHONE_DEVICE, **options)
                check_images(obj, SMARTPHONE_DEVICE, **options)


def search_last_classes(base_cls):
    """
    特定クラスの親でないクラスを全て探してくる
    :param base_cls:
    :return:
    """
    result = []
    for cls in base_cls.__subclasses__():
        if cls.__subclasses__():
            # さらにサブクラスがある場合は再帰
            result.extend(search_last_classes(cls))
            continue

        result.append(cls)

    return result


def check_images(obj, device_name, view_success=False, detail=False, **kwargs):
    image_manager = obj._image_manager(device_name=device_name)
    for label in image_manager.labels:

        try:
            if image_manager.validate(label, dummy_off=True) and view_success:
                if detail:
                    echo('validate {} {} {}'.format(obj, label, device_name),
                         indent=1)
                success(image_manager[label], '  PASS   ', indent=2)
        except ImageValidationError as e:
            if detail:
                echo('validate {} {} {}'.format(obj, label, device_name),
                     indent=1)
            error('{}{}'.format(e.__class__.__name__, e.message), '**ERROR**',
                  indent=2)


def error(message, code, indent=0):
    code = _red(code) if code else ''
    echo(message, code, indent)


def warn(message, code, indent=0):
    code = _yellow(code) if code else ''
    echo(message, code, indent)


def success(message, code, indent=0):
    code = _green(code) if code else ''
    echo(message, code, indent)


def echo(message='', code='', indent=0):
    indent = ' ' * (1 + indent * 4)
    print '{}{} {}'.format(indent, code, message)


def _green(message):
    return "\x1b[42m\x1b[37m {MESSAGE} \x1b[0m".format(MESSAGE=message)


def _red(message):
    return "\x1b[41m\x1b[37m {MESSAGE} \x1b[0m".format(MESSAGE=message)


def _yellow(message):
    return "\x1b[43m\x1b[37m {MESSAGE} \x1b[0m".format(MESSAGE=message)
