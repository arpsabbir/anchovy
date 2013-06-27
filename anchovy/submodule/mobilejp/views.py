# -*- coding: utf-8 -*-
import time
from PIL import Image
from cStringIO import StringIO

from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.utils.cache import patch_cache_control
from django.utils.hashcompat import md5_constructor as md5
from django.utils.http import http_date
from django.utils.cache import patch_cache_control

CACHE_TIMEOUT = 86400

def qrcode(req, width):
    import qr

    url = req.GET.get('url')
    if url is None:
        raise Http404

    try:
        data = url.encode('ascii')
    except UnicodeError:
        # only supports URLs properly urlencoded
        raise Http404

    if width == "480":
        magnify = 8
    else:
        magnify = 4

    buf = StringIO()
    try:
        qr.qrcode(data, buf, format=qr.GIF, magnify=magnify)
    except ValueError:
        # qr module wasn't be compiled with GD library
        raise Http404

    content = buf.getvalue()

    CACHE_TIMEOUT = 86400
    res = HttpResponse(content, content_type='image/gif')
    res['Content-Length'] = str(len(content))
    res['ETag']           = '"%s"' % md5(content).hexdigest()
    res['Last-Modified']  = http_date()
    res['Expires'] = http_date(time.time() + CACHE_TIMEOUT)
    patch_cache_control(res, max_age=CACHE_TIMEOUT)
    return res


def border(req, style, rgb):
    import gd
    rgb = tuple(map(lambda x: int(x, 16), (rgb[0:2], rgb[2:4], rgb[4:6])))

    try:
        width = int(req.GET.get('w', 228))
    except (ValueError, TypeError):
        width = 228

    try:
        height = int(req.GET.get('h', 1))
    except (ValueError, TypeError):
        height = 1

    if width < 1 or height < 1:
        raise Http404

    if rgb != (0, 0, 0):
        # if line is black, then use white(#FFFFF) as background color
        backcolor = (255, 255, 255)
    else:
        backcolor = (0, 0, 0)

    # TODO
    # check display width
    img = gd.image((width, height))

    back = img.colorAllocate(backcolor)
    img.colorTransparent(back)

    color = img.colorAllocate(rgb)

    if style == 'dotted':
        pattern = (color, color, back, back)
    elif style == 'dashed':
        pattern = (color, color, color, back, back, back)
    else:
        # solid
        pattern = (color,)

    img.setStyle(pattern)
    for y in xrange(height):
        img.line((0, y), (width, y), gd.gdStyled)

    fp = StringIO()
    img.writeGif(fp)
    content = fp.getvalue()
    fp.close()

    content_type = 'image/gif'
    res = HttpResponse(content, content_type=content_type)
    res['Content-Type']   = content_type
    res['Content-Length'] = str(len(content))
    res['ETag']           = '"%s"' % md5(content).hexdigest()
    res['Last-Modified']  = http_date()
    res['Expires'] = http_date(time.time() + CACHE_TIMEOUT)
    patch_cache_control(res, max_age=CACHE_TIMEOUT)

    return res


###
from django import forms

class ImageProxyForm(forms.Form):
    url = forms.URLField()
    r   = forms.URLField(required=False)
    w   = forms.IntegerField(min_value=0, required=False)
    h   = forms.IntegerField(min_value=0, required=False)
    f   = forms.CharField(required=False)
    t   = forms.IntegerField(min_value=0, required=False)

def image_proxy(req, headers=None, cache=None, timeout=None, proxy_info=None):
    import httplib2
    import gd

    form = ImageProxyForm(req.GET)
    if not form.is_valid():
        return HttpResponseBadRequest()

    url = form.cleaned_data['url']
    width = form.cleaned_data.get('w')
    height = form.cleaned_data.get('h')
    format = form.cleaned_data.get('f')
    timeout = form.cleaned_data.get('t') or timeout
    referrer = form.cleaned_data.get('r')

    headers = headers or {}
    if referrer:
        headers['Referer'] = referrer

    conn = httplib2.Http(cache, timeout, proxy_info)
    result, content = conn.request(url, headers=headers)

    status = int(result['status'])
    if status not in [200, 304]:
        return HttpResponse(status=status)

    try:
        img = Image.open(StringIO(content))
    except IOError:
        raise Http404

    w, h = img.size
    if width and height:
        if (w <= width and h <= height):
            need_resize = False
        else:
            need_resize = True

            w_ratio = width / float(w)
            h_ratio = height / float(h)
            # use smaller ratio
            ratio = min(w_ratio, h_ratio)
            size = (int(w * ratio), int(h * ratio))
    else:
        # either width or height is undefined
        if height is not None and h > height:
            need_resize = True
            ratio = height / float(h)
            size = (int(w * ratio), int(h * ratio))
        elif width is not None and w > width:
            need_resize = True
            ratio = width / float(w)
            size = (int(w * ratio), int(h * ratio))
        else:
            need_resize = False

    format = img.format.lower()
    if format == 'gif':
        content_type = 'image/gif'

        if need_resize:
            newimage = gd.image(size)

            tmp = StringIO()
            img.save(tmp, 'PNG')
            tmp.seek(0)

            gdimage = gd.image(tmp, 'png')

            # resize
            gdimage.copyResizedTo(newimage, (0, 0), (0, 0), size, img.size)

            # get result
            output = StringIO()
            newimage.writeGif(output)
            # override image binary content
            content = output.getvalue()

    else:
        # force output to be JPEG
        content_type = 'image/jpeg'

        if need_resize or format != 'image/jpeg':
            # resize
            if need_resize:
                img = img.resize(size)

            # change color mode to RGB if not
            if img.mode != 'RGB':
                img = img.convert("RGB")

            output = StringIO()
            img.save(output, 'JPEG')
            # override image binary content
            content = output.getvalue()


    CACHE_TIMEOUT = 86400
    res = HttpResponse(content, content_type=content_type)
    res['Content-Length'] = str(len(content))
    res['ETag']           = '"%s"' % md5(content).hexdigest()
    res['Last-Modified']  = http_date()
    res['Expires'] = http_date(time.time() + CACHE_TIMEOUT)
    patch_cache_control(res, max_age=CACHE_TIMEOUT)
    return res
