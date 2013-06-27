# -*- coding: utf-8 -*-
"""
水平分割されたモデルにトランザクションを提供する.

使用方法は下記の通り.

.. code-block:: python

    from horizontalpartitioning.transaction import commit_on_success, savepoint

    with commit_on_success([player_id1, player_id2]):
        p1 = Player.get_for_update(u'11111')
        p2 = Player.get_for_update(u'11112')

        with savepoint([player_id1, player_id2]):
            p1.name = 'spam'
            p2.name = 'spam'
            p1.save()
            p2.save()

            with savepoint([player_id1]):
                p1.name = 'ham'
                p1.save()

            with savepoint([player_id2]):
                p2.name = 'egg'
                p2.save()

        raise Exception, 'rollback'


commit_on_success を with もしくは Decorater
として使用する事で, トランザクションを使用できる.

commit_on_success は, 一つの DB に対しては普通のトランザクションを行うが,
複数の DB に対しては二層コミット(以降, 2PC)を行う.

savepoint を with もしくは Decorator として使用でき,
途中経過の処理を確定して行ける.

savepoint は入れ子にできる.

commit_on_success を入れ子にした場合,
トランザクション中の DB 名が重複すると raise する.

commit_on_success でトランザクション中の DB 名以外を
savepoint で使用すると raise する. 
"""
import uuid
from functools import wraps

from django.db import connections, transaction
from django.conf import settings

from __init__ import get_horizontal_partitioning_database_name
import adhoc
from .monitor import handle_dblock
from .logger import Logger

_logger = Logger('transaction')


class _WithIsDecoratorMixin(object):
    """
    with から使用できる形式に定義したクラスを Decorator にする Mix-in クラス
    """
    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner


class _UserIDtoDBNameMixin(object):
    def _user_ids_to_db_names(self, user_ids=None):
        return [get_horizontal_partitioning_database_name(user_id)
                for user_id in user_ids]

    def _marge_db_names(self, a, b):
        # set を利用すると順序を保証できないため,
        # list(set(a + b)) が使えず, 下記の様なコードとなっている.
        # Transaction Manager が正しく機能しているならば,
        # 下記の処理は取り越し苦労だが, 念のため,
        # 2PC の中途半端な状態も想定し, 下記の様なコードとした.

        marged_db_names = []
        index = {}

        for db_name in a + b:
            if index.get(db_name) is not None:
                continue
            marged_db_names.append(db_name)
            index[db_name] = True

        return marged_db_names

    def get_db_names(self, user_ids=None, db_names=None):
        if user_ids is None:
            user_ids = []

        if db_names is None:
            db_names = []

        if not isinstance(user_ids, list):
            raise ValueError, 'user_ids is not list.'

        if not isinstance(db_names, list):
            raise ValueError, 'db_names is not list.'

        results = self._marge_db_names(db_names,
                                       self._user_ids_to_db_names(user_ids))

        if len(results) == 0:
            raise ValueError, 'user_ids + db_names was zero length.'

        return results


class DuplicateTransactionError(Exception):
    pass


class UnmanagedTransactionError(Exception):
    pass


class _CheckManagedMixin(object):
    def _check_managed(self, db_names, expect, exc_cls):
        for db_name in db_names:
            if transaction.is_managed(db_name) == expect:
                _logger.error('_check_managed: %s is managed', db_name)
                raise exc_cls, db_name

    def _can_start_transaction(self, db_names):
        self._check_managed(db_names, True, DuplicateTransactionError)

    def _can_start_savepoint(self, db_names):
        self._check_managed(db_names, False, UnmanagedTransactionError)


class _HasXidMixin(object):
    def _emit_xid(self, db_name):
        if not hasattr(self, '_xid_for'):
            self._xid_for = {}
        self._xid_for[db_name] = str(uuid.uuid4())

    def _clean_xid(self, db_name):
        if not hasattr(self, '_xid_for'):
            return
        if self._has_xid(db_name):
            del self._xid_for[db_name]

    def _has_xid(self, db_name):
        if not hasattr(self, '_xid_for'):
            return False
        return self._xid_for.has_key(db_name)

    def _xid(self, db_name):
        return self._xid_for[db_name] # 存在しないなら raise で落とす


class _XATransaction(_WithIsDecoratorMixin, _CheckManagedMixin, _HasXidMixin):
    """
    複数の DB に対して XA トランザクションで 2PC を行う.
    このクラスは, 2PC の TM を担う.
    利用者は, このクラスを直接利用しない事.
    """
    class _open_cursor(object):
        def __init__(self, con): 
            self._con = con

        def __enter__(self):
            self._cur = self._con.cursor() 
            return self._cur

        def __exit__(self, exc_type, exc_value, traceback):
            self._cur.close()
            return exc_type is None

    def __init__(self, db_names, on_serializable, verbose):
        self._db_names = db_names
        self._on_serializable = on_serializable
        self._verbose = verbose

        self._can_start_transaction(self._db_names)
        for db_name in self._db_names:
            self._enter_transaction_management(db_name)

    def _enter_transaction_management(self, db_name):
        # enter_transaction_management しないと
        # objects.create 等のタイミングで commit される.
        # 処理後, leave_transaction_management 必ず呼ぶ事.
        _logger.info('enter_transaction_management: %s', db_name,
                     verbose=self._verbose)
        transaction.enter_transaction_management(using=db_name)
        transaction.managed(True, using=db_name)

        cur = self._ensure_get_cursor(db_name)
        self._emit_xid(db_name)

        # 分離レベルを SERIALIZABLE にした方が安全
        self._set_transaction_isolation_level(cur, 'SERIALIZABLE')

        self._xa_command(db_name, cur, 'start')
        cur.close()

    def _ensure_get_cursor(self, db_name):
        con = connections[db_name].connection
        if not con:
            return connections[db_name].cursor()

        # mysql 接続済みなら, xa session を開始するため,
        # セッションを一度終わらせる
        try:
            con.rollback()
            return con.cursor()
        except:
            # 既に終了している Connection であればエラーが出る.
            _logger.except_error()
            return connections[db_name].cursor()

    def _set_transaction_isolation_level(self, cur, level):
        if self._on_serializable:
            _logger.info('_set_transaction_isolation_level: %s', level,
                         verbose=self._verbose)
            cur.execute('set session transaction isolation level {}'.format(level))

    def _xa_command(self, db_name, cur, command):
        _logger.info('_xa_command: %s %s %s',
                     db_name, command, self._xid(db_name),
                     verbose=self._verbose)
        cur.execute('xa {} "{}"'.format(command, self._xid(db_name)))

    def _get_connections(self, has_xid=True):
        cons = [(db_name, connections[db_name].connection)
                for db_name in reversed(self._db_names)]
        if not has_xid:
            return cons
        return filter(lambda (db_name, con): self._has_xid(db_name), cons)

    def _exec_on_connections(self, f, with_con=True, has_xid=True):
        for db_name, con in self._get_connections(has_xid):
            if with_con:
                f(db_name, con)
            else:
                f(db_name)

    def rollback(self):
        self._exec_on_connections(self._ensure_rollback)

    def _ensure_rollback(self, db_name, con):
        with self._open_cursor(con) as cur:
            # TODO: Connection 単位で進捗管理しないと, 無駄なエラーが出る.
            for command in ['end', 'prepare', 'rollback']:
                try:
                    self._xa_command(db_name, cur, command)
                except:
                    # DeadLock 時, xa end で 1614 が発生するが, xa end は必須.
                    _logger.except_error()
        self._clean_xid(db_name)
 
    def commit(self):
        try:
            self._exec_on_connections(self._end)
            self._exec_on_connections(self._prepare)
            self._exec_on_connections(self._commit)
        except:
            _logger.except_error()
            self.rollback()
            raise
        finally:
            self._exec_on_connections(self._clean_xid, with_con=False)

    def _end(self, db_name, con):
        with self._open_cursor(con) as cur:
            self._xa_command(db_name, cur, 'end')

    def _prepare(self, db_name, con):
        with self._open_cursor(con) as cur:
            self._xa_command(db_name, cur, 'prepare')

    def _commit(self, db_name, con):
        try:
            with self._open_cursor(con) as cur:
                self._xa_command(db_name, cur, 'commit')
        except:
            _logger.except_error()

    def leave(self):
        self._exec_on_connections(self._leave, has_xid=False)

    def _leave(self, db_name, con):
        if self._has_xid(db_name):
            # xa commit / xa rollback 共にされていない場合は接続を切る
            # con.close() を呼ぶと, 下記が発生し try で捕捉できない.
            # ProgrammingError: closing a closed connection
            connections[db_name].connection = None
            _logger.error('_leave: con has not xid')
        else:
            with self._open_cursor(con) as cur:
                self._set_transaction_isolation_level(cur, 'REPEATABLE READ')
            _logger.info('leave_transaction_management: %s', db_name,
                         verbose=self._verbose)
            transaction.set_clean(using=db_name)
            transaction.leave_transaction_management(using=db_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if exc_type is None:
                self.commit()
                return True
            else:
                self.rollback()
                return False
        finally:
            self.leave()


class MockTransaction(_WithIsDecoratorMixin):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return exc_type is None


def commit_on_success(user_ids=None, db_names=None,
                      ensure_start=None,
                      lock_timeout=None,
                      wait_timeout=None,
                      on_serializable=None,
                      notify_lock=None,
                      verbose=False):
    """
    水平分割用の commit_on_success

    対象が一つの DB である場合, 通常のトランザクションを行うが,
    複数の DB を使用する場合, XA トランザクションで 2PC を行う.

    .. attention::
        XA の場合, ブロックに入る際に既存の接続を全て rollback し,
        isolation level を SERIALIZABLE へ変更する.


    commit_on_success を入れ子にする場合,
    トランザクション中のデータベース名が重複すると
    DuplicateTransactionError 例外を raise する.

    基本的に, commit_on_success を入れ子にしない事.

    使用方法は, 下記の通り.

    .. code-block:: python

        # Decorator の例
        @commit_on_success([player_id1, player_id2]):
        def spam():
            for player_id in [player_id1, player_id2]
                p = Player(player_id)
                p.name = 'ham'
                p.save()

        # with の例
        with commit_on_success([player_id1, player_id2]):
            for player_id in [player_id1, player_id2]
                p = Player(player_id)
                p.name = 'ham'
                p.save()
    """
    if adhoc.ON_TEST:
        _logger.debug('commit_on_success: ON_TEST')
        return MockTransaction()

    if on_serializable is None:
        on_serializable = getattr(settings, 'XA_ON_SERIALIZABLE', True)
    _logger.debug('commit_on_success: XA_ON_SERIALIZABLE = %s',
                  on_serializable)

    if notify_lock is None:
        notify_lock = getattr(settings, 'USE_NOTIFY_LOCK', True)
    _logger.debug('commit_on_success: USE_NOTIFY_LOCK = %s',
                  notify_lock)

    db_names = _UserIDtoDBNameMixin().get_db_names(user_ids, db_names)
    _logger.info('commit_on_success: user_ids = %s, db_names = %s',
                 user_ids, db_names, verbose=verbose)

    _set_wait_timeout(db_names, wait_timeout, verbose)
    _set_lock_timeout(db_names, lock_timeout, verbose)

    if ensure_start:
        _force_clean_transaction(db_names, verbose)

    commit_context = _commit_on_success(db_names, on_serializable, verbose)
    return handle_dblock(db_names, commit_context) \
        if notify_lock else commit_context

def _set_wait_timeout(db_names, timeout, verbose):
    if timeout is None:
        return

    for db_name in db_names:
        con = connections[db_name].connection
        if con:
            cur = con.cursor()
        else:
            cur = connections[db_name].cursor()
        cur.execute('set session wait_timeout = {}'.format(timeout))
        _logger.info('_set_wait_timeout: set wait_timeout %s %s',
                     db_name, timeout, verbose=verbose)

def _set_lock_timeout(db_names, timeout, verbose):
    """
    MySQL 5.5 以上かつ innodb でなければ動作しない
    """
    if timeout is None:
        return

    if not hasattr(settings, 'USE_INNODB_LOCK_WAIT_TIMEOUT'):
        return

    if not settings.USE_INNODB_LOCK_WAIT_TIMEOUT:
        return

    for db_name in db_names:
        con = connections[db_name].connection
        if con:
            cur = con.cursor()
        else:
            cur = connections[db_name].cursor()
        cur.execute('set session innodb_lock_wait_timeout = {}'.format(timeout))
        _logger.info('_set_lock_timeout: set lock_wait_timeout %s %s',
                     db_name, timeout, verbose=verbose)

def _force_clean_transaction(db_names, verbose):
    """
    接続数が増えると, is_managed フラグがクリアされない事が増える.
    それを, この関数で強制的にクリアする.
    """
    for db_name in db_names:
        if not transaction.is_managed(db_name):
            continue

        _logger.info('_force_clean_transaction: %s', db_name, verbose=verbose)
        _force_rollback(db_name)
        _force_leave(db_name)

def _force_rollback(db_name):
    try:
        connections[db_name].connection.rollback()
    except:
        _logger.error('force rollback error: %s', db_name)
        _logger.except_error()

def _force_leave(db_name):
    try:
        transaction.set_clean(using=db_name)
        transaction.leave_transaction_management(using=db_name)
    except:
        _logger.error('force leave error: %s', db_name)
        _logger.except_error()

def _commit_on_success(db_names, on_serializable, verbose):
    if 2 <= len(db_names):
        _logger.info('_commit_on_success: start xa transaction', verbose=verbose)
        return _XATransaction(db_names, on_serializable, verbose)

    _logger.info('_commit_on_success: start transaction', verbose=verbose)
    return _single_commit_on_success(db_names[0])

def _single_commit_on_success(db_name):
    if transaction.is_managed(db_name):
        _logger.error('_single_commit_on_success: raise DuplicateTransactionError')
        raise DuplicateTransactionError, db_name

    return transaction.commit_on_success(using=db_name)

class _Savepoint(_WithIsDecoratorMixin,
                 _UserIDtoDBNameMixin,
                 _CheckManagedMixin):
    def __init__(self, user_ids=None, db_names=None):
        db_names = self.get_db_names(user_ids, db_names)
        self._can_start_savepoint(db_names)
        self._sids = [(transaction.savepoint(using=db_name), db_name)
                      for db_name in db_names]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self._apply_on_sids(transaction.savepoint_commit)
            return True
        else:
            self._apply_on_sids(transaction.savepoint_rollback)
            return False

    def _apply_on_sids(self, f):
        for sid, db_name in self._sids:
            f(sid, using=db_name)

 
def savepoint(user_ids=None, db_names=None):
    """
    savepoint を提供する.

    savepoint が commit_on_success に入っていない場合,
    UnmanagedTransactionError を raise する.

    使用方法は, 下記の通り.

    .. code-block:: python

        # Decorator の例
        @savepoint([player_id]):
        def spam():
            p = Player(player_id)
            p.name = 'ham'
            p.save()

        # with の例
        with savepoint([player_id]):
            p = Player(player_id)
            p.name = 'ham'
            p.save()
    """
    if adhoc.ON_TEST:
        return MockTransaction()

    return _Savepoint(user_ids, db_names)

def require_transaction(user_ids=None, db_names=None):
    """
    commit_on_success の中か確認する.
    commit_on_success の外であれば raise する.
    """
    if adhoc.ON_TEST:
        return

    db_names = _UserIDtoDBNameMixin().get_db_names(user_ids, db_names)
    _CheckManagedMixin()._can_start_savepoint(db_names)

#DEBUG
#DuplicateTransactionError を探す為に下記を駆使する.
#import inspect
#_org_enter_fun = transaction.enter_transaction_management
#def _debug_enter_fun(*args, **kwargs):
#    curframe = inspect.currentframe()
#    calframe = inspect.getouterframes(curframe, 2)
#    _logger.info('enter_transaction_management!! %s %s %s',
#        calframe[3][3], calframe[2][3], calframe[1][3])
#    return _org_enter_fun(*args, **kwargs)
#transaction.enter_transaction_management = _debug_enter_fun
#
#_org_leave_fun = transaction.leave_transaction_management
#def _debug_leave_fun(*args, **kwargs):
#    curframe = inspect.currentframe()
#    calframe = inspect.getouterframes(curframe, 2)
#    _logger.info('leave_transaction_management!! %s %s %s',
#        calframe[3][3], calframe[2][3], calframe[1][3])
#    return _org_leave_fun(*args, **kwargs)
#transaction.leave_transaction_management = _debug_leave_fun
