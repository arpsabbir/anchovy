# -*- coding:utf-8 -*-
import inspect
from django.core.management.base import BaseCommand
from django.conf import settings
from gtoolkit.image import ImageMixin, ImageManager, DEVICE_NAME_FEATUREPHONE, DEVICE_NAME_SMARTPHONE
from gtoolkit.image.image import BaseImageValidationError

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        画像の権限確認をするバッチ
        """

        for app_name in settings.INSTALLED_APPS:
            if app_name.split('.')[0] not in ('apps', 'module'):
                continue
            app_name += '.models'
            # import
            module = include(app_name)

            # check
            for name, cls in inspect.getmembers(module, inspect.isclass):
                if hasattr(cls, '_meta') and getattr(cls._meta, 'abstract', False):
                    continue
                if issubclass(cls, ImageMixin):
                    # インポートしたファイルで定義されてているImageMixinを継承しているクラス
                    print "{} ({} {})".format(name, app_name, cls)

                    if not hasattr(cls, 'get_all'):
                        continue

                    for obj in cls.get_all():

                        check_images(obj, DEVICE_NAME_FEATUREPHONE)
                        check_images(obj, DEVICE_NAME_SMARTPHONE)

def check_images(obj, device_name):
    for label in obj.image_format_map[device_name].keys():
        image_manager = ImageManager(
            obj.image_path_format,
            obj.get_image_path_base_params(),
            obj.image_format_map,
            device_name=device_name
        )
        try:
            if image_manager[label].is_valid():
                print '', green('  PASS   '), image_manager[label]
        except BaseImageValidationError as e:
            print '', red('**ERROR**'), e.__class__.__name__, e.message

def green(message):
    return "\x1b[42m\x1b[37m {MESSAGE} \x1b[0m".format(MESSAGE=message)

def red(message):
    return "\x1b[41m\x1b[37m {MESSAGE} \x1b[0m".format(MESSAGE=message)

def include(module_path):
    """
    パスからインポートしたオブジェクトを返す

    __import__だけだとパスの最初のオブジェクトが帰ってくるので最後のを返す
    :param module_path:
    :return:
    """
    try:
        module = __import__(module_path) # models
    except ImportError as e:
        return None
    else:
        for path in module_path.split('.')[1:]:
            module = getattr(module, path)
        return module
