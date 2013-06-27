# -*- coding: utf-8 -*-


class DoesNotExist(Exception):
    pass


class MultipleObjectsReturned(Exception):
    pass


class JsonMasterModelError(Exception):
    pass


class ValidationError(Exception):
    pass