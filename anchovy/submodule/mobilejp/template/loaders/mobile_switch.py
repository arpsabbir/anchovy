# -*- encoding: utf-8 -*-
"""
FP/SPの切り替えTemplateLoader
"""

import os
import sys

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader

from django.utils._os import safe_join
from django.utils.importlib import import_module

from mobilejp.log import logger
from mobilejp.middleware.mobile import get_current_device
from mobilejp.template.wrapper import replace_entity

class Loader(BaseLoader):
    """
    FP/SPの切り替えTemplateLoader機能
    """
    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):
        """
        Returns the absolute paths to "template_name", when appended to each
        directory in "template_dirs". Any paths that don't lie inside one of the
        template dirs are excluded from the result set, for security reasons.
        """
        device = get_current_device()

        if device.is_smartphone:
            template_dirs = settings.SMARTPHONE_TEMPLATE_DIRS
        else:
            template_dirs = settings.PC_TEMPLATE_DIRS

        # if not template_dirs:
        #     if device.is_featurephone:
        #         template_dirs = settings.TEMPLATE_DIRS
        #     else if device.is_smartphone:
        #         template_dirs = settings.SMARTPHONE_TEMPLATE_DIRS

        for template_dir in template_dirs:
            try:
                yield safe_join(template_dir, template_name)
            except UnicodeDecodeError:
                # The template dir name was a bytestring that wasn't valid UTF-8.
                raise
            except ValueError:
                # The joined path was located outside of this particular
                # template_dir (it might be inside another one, so this isn't
                # fatal).
                pass

    def load_template_source(self, template_name, template_dirs=None):
        tried = []
        if not template_dirs:
            device = get_current_device()
            if device and device.is_featurephone:
                template_dirs = settings.TEMPLATE_DIRS
            else:
                template_dirs = settings.SMARTPHONE_TEMPLATE_DIRS

        for filepath in self.get_template_sources(template_name, template_dirs):
            try:
                file = open(filepath)
                try:
                    return (replace_entity(file.read().decode(settings.FILE_CHARSET)), filepath)
                finally:
                    file.close()
            except IOError:
                tried.append(filepath)
        if tried:
            error_msg = "Tried %s" % tried
        else:
            error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
        raise TemplateDoesNotExist(error_msg)
    load_template_source.is_usable = True

_loader = Loader()

