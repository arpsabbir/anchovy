# -*- coding: utf-8 -*-
from django.conf import settings

def device(request):
    is_vga = request.device.display.is_vga()
    width = is_vga and 480 or 240
    return { 'device'       : request.device,
             'request'      : request,
             'DISPLAY_WIDTH': width,
             'VGA'          : is_vga,
             'domain':settings.SITE_DOMAIN,
             }
