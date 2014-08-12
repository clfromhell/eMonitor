from .extensions import signal
from tornado.websocket import WebSocketHandler


class SocketHandler(WebSocketHandler):
    clients = set()

    @staticmethod
    #def send_message(sender='', message='', category='', **extra):
    def send_message(sender, **extra):
        for client in SocketHandler.clients:
            #if category.split('.')[0] in client._config:
            #client.write_message(time.ctime() + '<i class="fa fa-bell-o"></i>')
            client.write_message(sender, extra)

    def open(self):
        SocketHandler.clients.add(self)

    def on_close(self):
        SocketHandler.clients.remove(self)

    def on_message(self, message):
        _op, _cls, _msg = message.split('.')

        if _op == 'add':
            signal.addSignal(_cls, _msg)
        elif _op == 'send':
            signal.signals[_cls + '.' + _msg].send('')