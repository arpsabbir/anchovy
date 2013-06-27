# -*- coding: utf-8 -*-
"""
Logic から使用するバックグラウンドのワーカー
"""
import sys
import traceback
import datetime

from ggacha.messaging import WorkerMixin
from ggacha.kvs import KVSMixin
from ggacha.logger import WritableLogMixin


class GachaWorkerMixin(object):
    def run_worker(self, queue):
        self._gacha_worker = _GachaWorker(self, queue)
        self._gacha_worker.run()

    def stop_worker(self):
        if hasattr(self, '_gacha_worker'):
            self._gacha_worker.should_stop = True


class DeadLetterGachaWorkerMixin(GachaWorkerMixin):
    def run_worker(self, queue):
        self._gacha_worker = _DeadLetterGachaWorker(self, queue)
        self._gacha_worker.run()


class _BaseGachaWorker(WorkerMixin, KVSMixin, WritableLogMixin):
    def _write_header_log(self, body, message):
        self.write_log_info(u'process_task: in')
        self.write_log_info(u'process_task: body = %s', body)
        self.write_log_info(u'process_task: properties = %s', message.properties)

    def _dump_exc_info(self, exc_info, body, message):
        self.write_log_error(''.join(traceback.format_exception(*exc_info)))
        # Supervisor 経由で起動されたなら, 標準出力はログに残る.
        print
        print '<error_log>'
        print datetime.datetime.now()
        traceback.print_exception(file=sys.stdout, *exc_info)
        print 'body:', body
        print 'properties:', message.properties
        print '</error_log>'
        print


class _GachaWorker(_BaseGachaWorker):
    """
    キューを監視して, メッセージがあればガチャの処理を実行するワーカー
    """
    def process_task(self, body, message):
        self._write_header_log(body, message)

        try:
            player = self.gacha_logic.get_player(body['player_id'])
            gacha_kwargs = body['gacha_kwargs']
            logging_kwargs = body['logging_kwargs']
            reply_to = message.properties['reply_to']

            try:
                with self.gacha_logic.transaction_context(player, **gacha_kwargs):
                    self.write_log_info(u'process_task: start log')
                    with self.gacha_logic.logging.get_logger(logging_kwargs):
                        self.write_log_info(u'process_task: start do_gacha')
                        gacha_result = self.gacha_logic.do_gacha(player,
                                                                 **gacha_kwargs)
                        self.write_log_info(u'process_task: gacha_result = %s',
                                            gacha_result)
                    self.write_log_info(u'process_task: end log')
                    result = {'status': 'success',
                              'result': gacha_result}
            except:
                self._dump_exc_info(sys.exc_info(), body, message)
                self.write_log_info(u'process_task: message requeue')
                message.requeue()
            else:
                self.write_log_info(u'process_task: message ack')
                message.ack()

                self.write_log_info(u'process_task: write kvs')
                self.init_kvs(self.gacha_logic.gacha_id, player.pk)
                self.kvs.set_result(result)

                self.write_log_info(u'process_task: publish to %s', reply_to)
                self.publish(self.connection,
                             result,
                             routing_key=reply_to)
        except:
            self._dump_exc_info(sys.exc_info(), body, message)
            # 通信で落ちている可能性があるので, Supervisor に再起動させる.
            raise
        self.write_log_info(u'process_task: out')


class _DeadLetterGachaWorker(_BaseGachaWorker):
    """
    DeadLetter 専用ワーカー
    """
    def process_task(self, body, message):
        self._write_header_log(body, message)

        try:
            self.write_log_info(u'process_task: start drain')
            self.gacha_logic.drain(body, message.properties)

            self.write_log_info(u'process_task: message ack')
            message.ack()
        except:
            # requeue しない. reject するか要検討.
            self._dump_exc_info(sys.exc_info(), body, message)
        self.write_log_info(u'process_task: out')
