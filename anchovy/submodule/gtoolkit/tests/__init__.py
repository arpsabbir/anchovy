# -*- coding: utf-8 -*-

import uuid

def generate_uuid(separator=':', *args):
    """
    引数から UUID を生成する.
    """
    return separator.join([str(x) for x in args + (uuid.uuid4(),)])
