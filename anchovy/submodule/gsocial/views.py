# coding: utf-8
from gsocial.exceptions import SessionError

from gsocial.log import Log

from django.views.generic.base import View
from django.utils.functional import cached_property

from gsocial.models import get_osuser


class OpenSocialUserViewMixin(object):

    def _get_opensocial_viewer(self, request):
        """
        requestから「opensocial_viewer_id」を取得する
        """
        if hasattr(request, 'opensocial_viewer_id'):
            opensocial_viewer_id = request.opensocial_viewer_id
        else:
            opensocial_viewer_id = request.REQUEST.get(
                'opensocial_viewer_id', None)
            if not opensocial_viewer_id:
                if 'opensocial_userid' in request.session:
                    opensocial_viewer_id = request.session['opensocial_userid']
                else:
                    raise SessionError('opensocial_userid is not in session.')
        Log.debug("_get_opensocial_viewer id: %s" % opensocial_viewer_id)
        Log.debug("_get_opensocial_viewer session: %s" % request.session)
        return opensocial_viewer_id

    def set_request(self, request):
        if not hasattr(self, '_request'):
            self._request = request

    @cached_property
    def opensocial_viewer_id(self):
        return self._get_opensocial_viewer(self._request)

    @cached_property
    def os_user(self):
        return get_osuser(self.opensocial_viewer_id, self._request)

    @cached_property
    def is_webview(self):
        return 'is_webview' in self._request.session


class OpenSocialUserView(OpenSocialUserViewMixin, View):
    """
    View.dispatch を上書きして self に os_user アトリビュートを追加する

    このビューを継承したビューでは、

    * self.opensocial_viewer_id
    * self.os_user
    * self.is_webview

    が使えるようになる

    .. code-block:: python

        from gsocial.views import OpenSocialUserView

        class FooView(OpenSocialUserView):
            def get(self, request, *args, **kwargs):
                print self.os_user

    :self.os_user:  gsocial.models.OpenSocialUserオブジェクト
    """
    def dispatch(self, request, *args, **kwargs):
        self.set_request(request)
        return super(OpenSocialUserView, self) \
            .dispatch(request, *args, **kwargs)
