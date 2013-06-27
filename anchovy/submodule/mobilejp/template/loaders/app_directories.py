# -*- coding: utf-8 -*-
from django.conf import settings
from django.template.loaders.app_directories import load_template_source as _load

from mobilejp.template.wrapper import replace_entity

def load_template_source(template_name, template_dirs=None):
    content, filepath = _load(template_name, template_dirs)
    content = replace_entity(content)
    return content, filepath
load_template_source.is_usable = True

