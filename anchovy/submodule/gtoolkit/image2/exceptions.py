# -*- coding:utf-8 -*-


class ImageValidationError(Exception):
    dummy_color = 'gray'


class AliasTargetNotFoundError(ImageValidationError):
    """
    aliasで存在しない画像名を指定している
    """


class ImageDoesNotExist(ImageValidationError):
    """
    画像が無い
    """
    dummy_color = 'violet'


class InvalidImageSizeError(ImageValidationError):
    """
    画像サイズが違う
    """
    dummy_color = 'aquamarine'


class InvalidImageFormatError(ImageValidationError):
    """
    画像フォーマットが違う
    """
    dummy_color = 'gold'


class InvalidImageProgressiveError(ImageValidationError):
    """
    画像がプログレッシブ
    """
    dummy_color = 'tomato'
