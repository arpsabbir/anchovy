# -*- coding: utf-8 -*-

from factory import create_kvs_class, get_kvs_class_name

# エラークラス
class KVSError(Exception):
    pass

class KVS(object):
    """
    汎用KVSクラス。
    KVS_TYPEにINT,STR,OBJなどを指定するとsettings.DEFAULT_KVS_ENGINEで自動切り替え
    KVS_CLASSに指定があればKVS_CLASSを優先する。
    """
    KVS_TYPE = None
    KVS_CLASS = None
    KEY_NAME = None
    KEY_FORMAT = '%s'
    SET_NAME = None
    def __init__(self, *args, **argv):

        # argv['kvsclass'] > self.KVS_CLASS > self.KVS_TYPE の優先度で使用するクラスを決める
        default_class_name = self.KVS_CLASS if self.KVS_CLASS else get_kvs_class_name(type=self.KVS_TYPE)
        self._kvsclass = create_kvs_class(argv.get('kvsclass', default_class_name))

        if 'keyname' not in argv:
            argv['keyname'] = self.KEY_NAME if self.KEY_NAME else self.__class__.__name__
        if 'keyformat' not in argv:
            argv['keyformat'] = self.KEY_FORMAT
        if 'set_name' not in argv:
            argv['set_name'] = self.SET_NAME
        self._kvs = self._kvsclass(*args, **argv)

    @property
    def kvs(self):
        """
        KVSクラスインスタンスを返す
        """
        return self._kvs

    @property
    def key(self):
        """
        キー名取得
        """
        return self.kvs.key

    def setkey(self, keyvalue):
        """
        キー名設定
        """
        self.kvs.setkey(keyvalue)

    def get(self, default=None, keyvalue=None):
        """
        値取得
        """
        return self.kvs.get(default=default, keyvalue=keyvalue)

    def set(self, value, keyvalue=None):
        """
        値設定
        """
        self.kvs.set(value, keyvalue=keyvalue)

    def add(self, value, keyvalue=None):
        """
        値追加
        """
        if callable(getattr(self, 'add')):
            return self.kvs.add(value, keyvalue=keyvalue)
        else:
            raise KVSError('Not defined method (%s)' % str('add'))

    def delete(self, keyvalue=None):
        """
        値削除
        """
        self.kvs.delete(keyvalue=keyvalue)

    def close(self):
        """
        接続クローズ
        """
        self.kvs.close()

class ListKVS(object):
    """
    汎用リストKVSクラス
    使用は非推奨
    """
    MAX = None
    KVS_CLASS = None
    KEY_NAME = None
    KEY_FORMAT = '%s'
    def __init__(self, *args, **argv):
        self._max = argv.get('max', self.MAX)
        self._kvsclass = create_kvs_class(argv.get('kvsclass', self.KVS_CLASS))
        if 'keyname' not in argv:
            argv['keyname'] = self.KEY_NAME if self.KEY_NAME else self.__class__.__name__
        if 'keyformat' not in argv:
            argv['keyformat'] = self.KEY_FORMAT
        self._kvs = self._kvsclass(*args, **argv)

    @property
    def kvs(self):
        return self._kvs

    @property
    def key(self):
        """
        キー名取得
        """
        return self.kvs.key

    def setkey(self, keyvalue):
        """
        キー名設定
        """
        self.kvs.setkey(keyvalue)

    def get(self, keyvalue=None):
        """
        リスト取得
        """
        value = self.kvs.get(default=[], keyvalue=keyvalue)

        if not isinstance(value, (list, tuple)):
            raise TypeError('Require list object')
        if value is None:
            return []
        else:
            return value if isinstance(value, list) else list(value)

    def set(self, value, keyvalue=None):
        """
        リスト設定
        """
        if not isinstance(value, list):
            raise TypeError('Require list object')
        self.kvs.set(value[-self._max:], keyvalue=keyvalue)

    def append(self, value, keyvalue=None):
        """
        リスト要素追加
        """
        lst = self.get(keyvalue=keyvalue)
        lst.append(value)
        # maxを超えたら、古いデータを消す
        if self._max is not None:
            lst = lst[-self._max:]
        self.set(lst, keyvalue=keyvalue)

    def remove(self, value, keyvalue=None):
        """
        リスト要素削除
        """
        lst = self.get(keyvalue=keyvalue)
        lst.remove(value)
        self.set(lst, keyvalue=keyvalue)

    def delete(self, keyvalue=None):
        self.kvs.delete(keyvalue=keyvalue)


def get_kvs(kvsclass, keygroup, name, keyvalue, keyformat, argv):
    keyname = '%s.%s' % (keygroup, name)
    kvs = kvsclass(keyvalue, keyname=keyname, keyformat=keyformat, **argv)
    return kvs

class AttributeKVS(object):
    """
    属性KVSクラス
    各キーを属性アクセスできる
    """
    KVS_CLASS = None # 使用KVSクラス
    KEY_GROUP = None # キーグループ名
    KEY_FORMAT = '%s' # キーフォーマット
    ATTRIBUTES = None # 属性名、初期値

    class Error(KVSError):
        pass

    def __init__(self, keyvalue, keygroup=None, keyformat=None, attributes=None, **argv):
        """
        コンストラクタ
        """
        self._keygroup = keygroup if keygroup else self.KEY_GROUP
        if self._keygroup is None:
            self._keygroup = self.__class__.__name__

        self._keyvalue = keyvalue
        self._keyformat = keyformat if keyformat else self.KEY_FORMAT
        self._kvsclass = create_kvs_class(argv.get('kvsclass', self.KVS_CLASS))
        self._argv = argv
        self._initvalues = {}

        if not attributes:
            attributes = self.ATTRIBUTES
        if attributes:
            # 属性名設定
            if isinstance(attributes, (list, tuple)):
                self._attributes = set(attributes)
            elif isinstance(attributes, dict):
                self._initvalues = attributes
                self._attributes = set(attributes.keys())

    def __getattr__(self, name):
        """
        属性値取得
        """
        if name.startswith('_'):
            # _から始まる属性名は従来通りの動作
            return super(AttributeKVS, self).__getattr__(name)

        if self._attributes and name not in self._attributes:
            raise self.Error('Not defined attribute (%s)' % str(name))

        kvs = get_kvs(self._kvsclass, self._keygroup, name, self._keyvalue, self._keyformat, self._argv)
        return kvs.get()

    def __setattr__(self, name, value):
        """
        属性値設定
        """
        if name.startswith('_'):
            # _から始まる属性名は従来通りの動作
            super(AttributeKVS, self).__setattr__(name, value)
        else:
            kvs = get_kvs(self._kvsclass, self._keygroup, name, self._keyvalue, self._keyformat, self._argv)
            kvs.set(value)
            ##print kvs.key

    def __delattr__(self, name):
        """
        属性値削除
        """
        if name.startswith('_'):
            # _から始まる属性名は従来通りの動作
            super(AttributeKVS, self).__delattr__(name)
        else:
            kvs = get_kvs(self._kvsclass, self._keygroup, name, self._keyvalue, self._keyformat, self._argv)
            kvs.delete()

    def init_values(self):
        """
        値の初期化
        """
        for k,v in self._initvalues.iteritems():
            kvs = get_kvs(self._kvsclass, self._keygroup, k, self._keyvalue, self._keyformat, self._argv)
            kvs.set(v)

    def setkey(self, keyvalue):
        """
        キー名設定
        """
        self._keyvalue = keyvalue

    def deleteall(self):
        """
        全ての属性項目を削除
        """
        if self._attributes is None:
            raise self.Error('Not defined attributes')

        for k in list(self._attributes):
            self.__delattr__(k)

    def attributes(self):
        """
        属性一覧を返す
        """
        if self._attributes is None:
            raise self.Error('Not defined attributes')

        return tuple(self._attributes)

    def kvsdict(self):
        """
        属性に対応したKVSオブジェクトを辞書形式で返す
        """
        if self._attributes is None:
            raise self.Error('Not defined attributes')

        ret = {}
        for k in list(self._attributes):
            kvs = get_kvs(self._kvsclass, self._keygroup, k, self._keyvalue, self._keyformat, self._argv)
            ret[k] = kvs

        return ret
