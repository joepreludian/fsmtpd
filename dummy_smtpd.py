from smtpd import SMTPServer
import asyncore
from threading import Event
from email.parser import Parser

def parse_message(data):

    email_parser = Parser()
    parsed_message = email_parser.parsestr(data)

    return {
        'headers': parsed_message._headers,
        'subject': parsed_message._headers[3][1],
        'message': parsed_message._payload
    }



class DummySmtp(SMTPServer):

    def process_message(self, peer, mailfrom, rcpttos, data):

        data_parsed = parse_message(data)

        self._on_get_message_callback({'peer': peer,
                                       'mailfrom': mailfrom,
                                       'rcpttos': rcpttos,
                                       'data': data_parsed})

    def only_print(self, data):
        print "Received Data"
        print data

    def serve(self, on_get_message_callback=None, stop_event=None):

        if not stop_event:
            stop_event = Event()

        if on_get_message_callback:
            self._on_get_message_callback = on_get_message_callback
        else:
            self._on_get_message_callback = self.only_print

        while True:
            asyncore.poll(3, asyncore.socket_map)

            if stop_event.is_set():
                print "Shutdown SMTP service..."
                break

if __name__ == '__main__':
    print 'Turning on DummySMTP Standalone'

    smtp_dummy = DummySmtp(localaddr=('127.0.0.1', 1025), remoteaddr=None)
    smtp_dummy.serve()



