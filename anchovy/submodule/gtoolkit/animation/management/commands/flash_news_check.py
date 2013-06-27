# -*- coding:utf-8 -*-
#import inspect
import datetime
import filecmp
import re
from django.core.management.base import BaseCommand
#from django.conf import settings
from django.utils.encoding import smart_unicode, smart_str
from django.utils.functional import cached_property
#from gtoolkit.image import ImageMixin, ImageManager, DEVICE_NAME_FEATUREPHONE, DEVICE_NAME_SMARTPHONE
#from gtoolkit.image.image import BaseImageValidationError

import glob
import os
from gtoolkit.animation.render import ANIMATION_BASE_PATH

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        画像の権限確認をするバッチ
        """
        print args
#        ANIMATIONS = Paths(Path(u'/Users/yugo/Desktop/004_現行Flash')).tree
        ANIMATIONS = Paths(Path(smart_unicode(args[0]))).tree
        USED_ANIMATIONS = Paths(Path(smart_unicode(
            args[1] if len(args) >= 2 else os.path.join(ANIMATION_BASE_PATH, 'html')
        ))).tree


        for name, paths in ANIMATIONS.items():
            print '-'*200
            first = True
            for path in paths:
                print u"%80s | %20s | %s" % (
                    name if first else '',
                    path.mdatetime,
                    path.absolute_path
                    )
                first = False


        LATEST_ANIMATIONS = {}
        for animation_name, animation_paths in ANIMATIONS.items():

            latest_path = None

            for path in animation_paths:
                if (not latest_path) or cmp_version(
                    path.absolute_path,
                    latest_path.absolute_path
                ):
                    latest_path = path

            LATEST_ANIMATIONS[animation_name] = latest_path


        for name, paths in USED_ANIMATIONS.items():
            print '-'*200

            if name in LATEST_ANIMATIONS:
                latest_index_path = None
                for child_path in LATEST_ANIMATIONS[name].children:
                    if child_path.ext == '.html':
                        latest_index_path = child_path
                print u"%80s | %20s | %s" % (
                    name,
                    LATEST_ANIMATIONS[name].mdatetime,
                    LATEST_ANIMATIONS[name].absolute_path
                    )
                if latest_index_path:
                    print u"%80s | %10s | %s" % (
                        '',
                        get_redberry_version(latest_index_path.absolute_path),
                        latest_index_path.absolute_path
                        )

                for use_path in paths:
                    use_index_path = Path(os.path.join(use_path.absolute_path, 'index.html'))
                    if latest_index_path and not cmp_redberry_version(
                        use_index_path.absolute_path,
                        latest_index_path.absolute_path):
                        print red(u"%80s | %10s | %s" % (
                            '',
                            get_redberry_version(use_index_path.absolute_path),
                            use_index_path.absolute_path
                        ))
                    else:
                        print green(u"%80s | %10s | %s" % (
                            '',
                            get_redberry_version(use_index_path.absolute_path),
                            use_index_path.absolute_path
                        ))
            else:
                print u"%80s | skip" % (
                    name,
                    )

RB_CACHES = {}

def cmp_redberry_version(from_path, to_path):
    return cmp_version(get_redberry_version(from_path),
                       get_redberry_version(to_path))

def get_redberry_version(path):
    if path in RB_CACHES:
        return RB_CACHES.get(path)

    fh = open(path)
    line = fh.readline()
    while line:
        result = re.match('.*redberry-(?P<version>[0-9.]+).*', line)
        if result:
            version = result.group('version')
            if re.match('^[0-9.]+$', result):
                RB_CACHES[path] = version
                return version
        line = fh.readline()

    return "0"

def cmp_version(from_ver, to_ver):
    """
    fromが大きいとTrue
    :param from_ver:
    :type from_ver: string
    :param to_ver:
    :type to_ver: string
    :return:
    """
    from_ver = from_ver.split(".")
    to_ver = to_ver.split(".")
    max_len = len(from_ver) if len(from_ver) >= len(to_ver) else len(to_ver)
    while max_len-len(from_ver):
        from_ver.append('0')
    while max_len-len(to_ver):
        to_ver.append('0')
    for i in range(max_len):
        if re.match('^[0-9]?$', smart_str(from_ver[i])) and re.match('^[0-9]?$', smart_str(to_ver[i])):
            if int(from_ver[i]) == int(to_ver[i]):
                continue
            return int(from_ver[i]) > int(to_ver[i])


def green(message):
    return u"\x1b[42m\x1b[37m{MESSAGE}\x1b[0m".format(MESSAGE=message)

def red(message):
    return u"\x1b[41m\x1b[37m{MESSAGE}\x1b[0m".format(MESSAGE=message)


class Paths(object):
    def __init__(self, master_path):
        self.tree = {}
        self.master_path = master_path
        self.prt(master_path)

    def prt(self, path):

        if path.is_dir and path.parent and path.parent.is_img_dir:
            for child_path in path.parent.parent.children:
                if child_path.ext == '.html' and get_redberry_version(
                    child_path.absolute_path
                ):
                    if path.name not in self.tree:
                        self.tree[path.name] = []
                    self.tree[path.name].append(path.parent.parent)
                    break

        if path.is_dir:
            for dir_child_path in path.children:
                self.prt(dir_child_path)

        return self.tree



class Path(object):
    def __init__(self, path, parent=None):
        self._path = path

        self.is_dir = os.path.isdir(path)
        self.parent = parent

    @cached_property
    def is_img_dir(self):
        return self.is_dir and self.name == 'img'

    @cached_property
    def children(self):
        root_path = os.path.join(self._path, '*')

        return [Path(path, parent=self) for path in glob.glob(root_path)]

    @cached_property
    def sub_dirs(self):
        return [path for path in self.children if path.is_dir]

    @cached_property
    def name(self):
        if self.parent:
            return os.path.relpath(self._path, self.parent.absolute_path)

        return self._path

    @cached_property
    def path(self):
        if self.parent:
            return os.path.relpath(self._path, self.root_path)

        return self._path

    @cached_property
    def absolute_path(self):
        return self._path

    @cached_property
    def root_path(self):
        if self.parent:
            return self.parent.root_path

        return self.absolute_path

    @cached_property
    def mtime(self):
        return os.path.getmtime(self.absolute_path)

    @cached_property
    def mdatetime(self):
        return datetime.datetime.fromtimestamp(self.mtime)

    @cached_property
    def ext(self):
        root, ext = os.path.splitext(self.absolute_path)
        return smart_str(ext)