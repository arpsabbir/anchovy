# -*- coding: utf-8 -*-
import socket
from contextlib import contextmanager

from kombu import BrokerConnection, Queue
from kombu.messaging import Producer, Consumer
from kombu.mixins import ConsumerMixin

from ggacha.utils import RaiseExceptionMixin
from ggacha.conf import settings
import ggacha.amqp_patch

class MessagingMixin(object):
    """
    メッセージキューを使うクラスが Mix-in するクラス
    """

    class _Messaging(object):
        def get_connection(self):
            return BrokerConnection(self._broker_url())

        @contextmanager
        def connect(self):
            with BrokerConnection(self._broker_url()) as connection:
                yield connection

        @contextmanager
        def consume(self, connection, queue_name):
            self._consume_body = None
            self._consume_message = None

            with Consumer(channel=connection.default_channel,
                          queues=[Queue(name=queue_name)],
                          callbacks=[self._consume_callback],
                          no_ack=True,
                          auto_declare=False) as consumer:
                try:
                    connection.drain_events(timeout=3)
                    yield self._consume_body, self._consume_message
                except socket.timeout:
                    yield None, None

        def _consume_callback(self, body, message):
            self._consume_body = body
            self._consume_message = message

        def _broker_url(self):
            return settings.MESSAGE_BROKER

        def declare_queue(self, connection,
                          name='',
                          auto_delete=False, durable=False,
                          **kwargs):
            queue_args = kwargs.pop('queue_arguments', {})
            queue_args['x-ha-policy'] = 'all'

            queue = Queue(name,
                          durable=durable, auto_delete=auto_delete,
                          queue_arguments=queue_args,
                          **kwargs)

            queue.maybe_bind(connection.default_channel)
            queue.queue_declare()
            return queue

        def delete_queue(self, connection, name, *args, **kwargs):
            queue = Queue(name=name)
            queue.maybe_bind(connection.default_channel)
            queue.delete(*args, **kwargs)

        def _build_producer(self, connection):
            if not hasattr(self, '_producer'):
                self._producer = Producer(connection.default_channel,
                                          auto_declare=False)
            return self._producer

        def publish(self, connection, message, routing_key,
                    reply_to='', **properties):
            producer = self._build_producer(connection)
            producer.publish(message,
                             routing_key=routing_key,
                             serializer='msgpack',
                             reply_to=reply_to,
                             **properties)


    @property
    def messaging(self):
        if hasattr(self, '_messaging'):
            return self._messaging

        self._messaging = self._Messaging()
        return self._messaging


class WorkerMixin(RaiseExceptionMixin, ConsumerMixin,
                  MessagingMixin._Messaging):
    """
    Worker が Mix-in するクラス
    """
    def __init__(self, gacha_logic, queue):
        self.connection = self.get_connection()
        self.queue = queue
        self.gacha_logic = gacha_logic

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[self.queue],
                         callbacks=[self.process_task],
                         auto_declare=False)]

    def process_task(self, body, message):
        """
        このメソッドを上書きして, gacha_logic が持つ do_gacha を実行する.
        """
        self.raise_not_impl('process_task')


# 以下, patch
from ggacha.amqp_patch import patch_read_table
patch_read_table()

