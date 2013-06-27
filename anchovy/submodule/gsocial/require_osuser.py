# -*- coding: utf-8 -*-
from django.conf import settings
from gsocial.models import get_osuser

def require_osuser2(view_func):
    def decorate(request, *args, **kwds):
        if hasattr(request, 'opensocial_viewer_id'):
            opensocial_viewer_id = request.opensocial_viewer_id
        else:
            opensocial_viewer_id = request.REQUEST.get('opensocial_viewer_id')
            if not opensocial_viewer_id:
                opensocial_viewer_id = request.session['opensocial_userid']
        
        # Get OpenSocialUser
        # OpenSocialUserを取得する
        osuser = get_osuser(opensocial_viewer_id, request)
        request.osuser = osuser
            
        return view_func(request, *args, **kwds)
    return decorate
