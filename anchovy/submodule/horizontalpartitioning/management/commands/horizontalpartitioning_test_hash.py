# -*- coding: utf-8 -*-

"""

A test for creating hash using python and mysql
get_hash_1, get_hash_2, get_hash_3 and get_hash_4 will return the same value.
PythonとMySQLのハッシュ生成のテスト
get_hash_1, get_hash_2, get_hash_3, get_hash_4 は、全て同じ値を返す
"""
import datetime
import os
import hashlib

from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str
from django.db import connections

PARTITION_NUMBER = 16

def get_hash_1(s):
    hex_hash = hashlib.sha1(s).hexdigest()
    return int(hex_hash[-2:], 16) % PARTITION_NUMBER

def get_hash_2(s):
    hex_hash = hashlib.sha1(s).hexdigest()
    return int(hex_hash, 16) % PARTITION_NUMBER


def get_hash_3(s):
    sql = '''SELECT CAST(CONV(RIGHT(SHA1(%s),1), 16, 10) AS SIGNED)'''
    cursor = connections['read'].cursor()
    cursor.execute(sql, (s,))
    result = cursor.fetchall()
    return result[0][0]

def get_hash_4(s):
    sql = '''SELECT CAST(MOD(CONV(RIGHT(SHA1(%s),2), 16, 10), 16) AS SIGNED)'''
    cursor = connections['read'].cursor()
    cursor.execute(sql, (s,))
    result = cursor.fetchall()
    return result[0][0]

class Command(BaseCommand):
    
    def echo(self, message):
        self.stdout.write(smart_str(message, errors='ignore'))
        self.stdout.write('\n')
        self.stdout.flush()
    
    def logging(self, message):
        self.echo('[%s] %s %s ' % (os.path.basename(__file__),datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))
    
    def handle(self, *args, **options):
        
        for i in xrange(100):
            source = 'source%s' % i
            hash1 = get_hash_1(source)
            hash2 = get_hash_2(source)
            hash3 = get_hash_3(source)
            hash4 = get_hash_4(source)
            
            self.echo('%2s, %2s, %2s, %2s' % (hash1,hash2,hash3,hash4,))

