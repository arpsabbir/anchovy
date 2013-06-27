# -*- coding:utf-8 -*-
import os
import re
from django.conf import settings
from django.http import HttpResponse
from django.template import loader, RequestContext
from django.utils.encoding import smart_unicode
from django.views.generic.base import View
from gtoolkit.image import get_device_name


MOCK_BASE_PATH = os.path.join(settings.EXTENSION_PATH, 'templates', 'mock')


class ObjectMock(object):
    def __init__(self, key=None, pk=None):
        if not pk:
            import random

            pk = random.randint(0, 1000)
        self.id = self.pk = pk
        self.key = smart_unicode(key.capitalize()) if key else key

    def __repr__(self):
        return smart_unicode(
            u'<{}:{}>'.format(self.key, self.pk)
            if self.key else u'<{}>'.format(self.pk))

    def __getitem__(self, item):
        return getattr(self, item)

    def __getattr__(self, item):
        return self.get(item)

    def get(self, item):
        if item in ['card', 'category']:
            return ObjectMock(key=item)

        return u'111'


class MockView(View):
    def get(self, request, *args, **kwargs):
        path = kwargs.get('path').split('/')
        filename = path.pop(-1)
        path = os.path.join(MOCK_BASE_PATH,
                            get_device_name(request.device.is_featurephone),
                            *path)
        t, origin = loader.find_template(filename, [path])

        context = {'card': ObjectMock(pk=33),
                   'player_card': ObjectMock(pk=33),
                   'player': ObjectMock(pk=str(33))}
        context.update(get_template_article_keys(os.path.join(path, filename)))
        return HttpResponse(t.render(RequestContext(request, context)))

    post = get


def get_template_article_keys(template_names):
    """
    テンプレートIDを作成して渡す

    :param template_names:
    :return:
    """
    template_article_id = re.sub(
        '/[^/]*\.html$', '',
        smart_unicode(template_names[0])
    ).replace('/', '-')
    template_article_class = re.sub(
        '\.html$', '',
        smart_unicode(template_names[0])
    )
    template_article_class = re.sub(
        '^(.*/)?', '', template_article_class)

    return {
        'template_article_id': template_article_id,
        'template_article_class': template_article_class,
    }
