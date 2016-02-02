#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gi import require_version
import threading
import os
from dummy_smtpd import DummySmtp

require_version('Gtk', '3.0')
require_version('WebKit', '3.0')
require_version('Notify', '0.7')

from gi.repository import Gtk, WebKit, Notify


class FSMTPd(object):
    def __init__(self, builder):

        # Windows
        self.window = builder.get_object("window")
        self.window_about = builder.get_object("about_dialog")
        self.window_about.connect('delete-event', lambda w, e: w.hide() or True)

        self.window.show()

        # Notify APP
        Notify.init('Dummy SMTP Viewer')

        # Main Widgets
        self.scrolledwindow = builder.get_object("scrolledwindow")

        self.status_label = builder.get_object('status_label')

        self.email_subject = builder.get_object('email_subject')
        self.email_from = builder.get_object('email_from')
        self.email_to = builder.get_object('email_to')

        self.menu_about = builder.get_object('about_menu')

        # Webkit for previewing
        self.view = WebKit.WebView()
        self.scrolledwindow.add(self.view)

        # Connecting Signals
        builder.connect_signals({
            "gtk_main_quit": shutdown,
            "about_menu_activate": self.about_open
        })

        self.status_label.set_text('Listening 127.0.0.1:1025')

    def about_open(self, event):
        self.window_about.show()

    def about_close(self, event):
        return self.window_about.hide() or True

    def message_received(self, data):

        self.email_from.set_text('From: %s' % data['mailfrom'])
        self.email_to.set_text('To: %s' % data['rcpttos'])
        self.email_subject.set_text('Subject: %s' % data['data']['subject'])

        n = Notify.Notification.new(
                'Email From %s' % data['mailfrom'],
                'New Message Received',
                "mail-mark-read")
        n.show()


        with open('/tmp/fsmtp_preview.html', 'w') as email_temp:
            email_temp.write(data['data']['message'])

        self.view.open("file:///tmp/fsmtp_preview.html")
        self.view.show()


stop_event = threading.Event()


def shutdown(*args, **kwargs):
    print 'Finishing app...'

    try:
        os.remove('/tmp/fsmtp_preview.html')
    except OSError:
        print "Temp file not found. Moving..."

    Notify.uninit()

    stop_event.set()
    Gtk.main_quit()


if __name__ == "__main__":
    dummy_smtp = DummySmtp(localaddr=('127.0.0.1', 1025), remoteaddr=None)

    builder = Gtk.Builder()
    builder.add_from_file("app.glade")

    browser = FSMTPd(builder)

    smtp_thread = threading.Thread(target=dummy_smtp.serve, args=(browser.message_received, stop_event))
    smtp_thread.start()

    Gtk.main()
