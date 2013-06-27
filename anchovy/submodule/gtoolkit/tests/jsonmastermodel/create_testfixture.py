#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
Jsonmastermodel の テストフィクスチャ作成スクリプト

(テストフィクスチャは 2MB ほどになるので、gitに入れたくなかった)

$ ./create_testfixture.py > jsonmastermodel-testfixture-large.json
$
"""

RECORD_FORMAT = """
    {
        "pk": %(pk)d,
        "model": "jsonmastermodel.Test",
        "fields": {
            "category": "%(category)s",
            "value": %(value)d,
            "detail_text": "%(detail)s"
        }
    }"""

if __name__ == '__main__':

    records = list()
    for i in xrange(1, 10001):

        record = RECORD_FORMAT % {
            'pk': i,
            'category': 'category-{}'.format(i % 100),
            'value': i + 10000000,
            'detail': 'detail for {}'.format(i)
        }
        records.append(record)

    output = '[{}\n]'.format(','.join(records))
    print output