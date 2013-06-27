#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jsonmastermodel の テストフィクスチャ作成スクリプト

(テストフィクスチャは 2MB ほどになるので、gitに入れたくなかった)

$ ./create_testfixture.py > jsonmastermodel-testfixture-large.json
$
"""
from __future__ import unicode_literals
import json

RECORD_FORMAT = """
    {
        "pk": %(pk)d,
        "model": "jsonmastermodel.Test",
        "fields": {
            "category": "%(category)s",
            "value": %(value)d,
            "detail_text": "%(detail)s",
            "json_params": "%(json_params)s"
        }
    }"""

if __name__ == '__main__':

    records = list()
    for i in xrange(1, 10001):

        json_params = json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
        record = RECORD_FORMAT % {
            'pk': i,
            'category': 'category-{}'.format(i % 100),
            'value': i + 10000000,
            'detail': 'detail for {}'.format(i),
            'json_params': json_params.replace('"', r'\"')
        }
        records.append(record)

    output = '[{}\n]'.format(','.join(records))
    print output
