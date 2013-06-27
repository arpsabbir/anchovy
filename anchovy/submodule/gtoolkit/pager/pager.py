# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import math
from mobilejp.middleware.mobile import get_current_device


DEFAULT_PER_PAGE = 5
PER_PAGE_ARG_INDEX = 2

SETTINGS_NAV_LENGTH_DEFAULT = 'SETTINGS_NAV_LENGTH_DEFAULT'


def get_pager(object_list, page=1, per_page=DEFAULT_PER_PAGE, nav_length=None):
    """
    pagerを生成して返す。テンプレートタグとセットで使う

    引数の順番に変更がある場合はPER_PAGE_ARG_INDEXも考慮すること

    :param object_list: ページングするオブジェクト全て
    :type object_list: QuerySet or list or tuple

    :param page: 何ページ目か
    :type page: int

    :param per_page: 一ページ当りの表示数
    :type per_page: int

    :param nav_length: 前後ページへのリンクを最大合計いくつ表示するか
    :type nav_length: int
    """
    if nav_length is None:
        nav_length = getattr(settings, SETTINGS_NAV_LENGTH_DEFAULT, 6)

    paginator = Paginator(object_list, per_page)
    try:
        current = paginator.page(page)
    except PageNotAnInteger:
        current = paginator.page(1)
    except EmptyPage:
        current = paginator.page(1)

    nav_length_prev = int(math.floor((nav_length - 1) / 2.0))
    nav_length_next = int(math.ceil((nav_length - 1) / 2.0))
    if current.number - nav_length_prev < 1:
        nav_first = 1
        if nav_first + nav_length - 1 > paginator.num_pages:
            nav_last = paginator.num_pages
        else:
            nav_last = nav_first + nav_length - 1
    else:
        if current.number + nav_length_next > paginator.num_pages:
            nav_last = paginator.num_pages
            if nav_last - nav_length < 0:
                nav_first = 1
            else:
                nav_first = nav_last - nav_length + 1
        else:
            nav_first = current.number - nav_length_prev
            nav_last = current.number + nav_length_next

    pager = {
        'paginator': paginator,
        'current': current,
        'navigator': xrange(nav_first, nav_last + 1)
    }

    return pager


def _force_limited_pager(force_limit, condition_func):
    """
    特定条件で強制的にper_pageに制限をかける事ができるget_pagerを作成する

    :param force_limit: 制限値この値以上にならない
    :param condition_func: 制限をかけるかどうか判別するロジック
    :return:
    """
    def _get_pager(*args, **kwargs):
        if not callable(condition_func) or condition_func(*args, **kwargs):
            if len(args) > PER_PAGE_ARG_INDEX:
                per_page = args[PER_PAGE_ARG_INDEX]
                is_arg = True
            else:
                per_page = kwargs.get('per_page', DEFAULT_PER_PAGE)
                is_arg = False

            if int(per_page) > force_limit:
                if is_arg:
                    # tupleで変更が出来ないのでリストに変更する
                    args = list(args)
                    args[PER_PAGE_ARG_INDEX] = force_limit
                else:
                    kwargs['per_page'] = force_limit

        return get_pager(*args, **kwargs)

    return _get_pager


def _is_softbank_fp(*args, **kwargs):
    device = get_current_device()
    if not device.is_featurephone:
        # FPじゃない
        return False

    return device.is_softbank


get_pager_with_softbank_fp_limited = _force_limited_pager(
    force_limit=5, condition_func=_is_softbank_fp)
