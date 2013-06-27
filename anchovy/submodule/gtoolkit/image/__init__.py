# -*- coding: utf-8 -*-

from gtoolkit.image.image import Image, ImageFormat, ImageMixin, ImageManager, load_image_format_map
from gtoolkit.image.static_switcher import (
    get_device_name, get_image_path, get_image_url,
    get_static_url, get_current_device,
    DEVICE_NAME_FEATUREPHONE, DEVICE_NAME_SMARTPHONE
)