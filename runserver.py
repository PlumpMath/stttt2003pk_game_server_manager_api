#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import tornado.autoreload
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado import gen
from tornado.options import define, options
from tornado.log import access_log, app_log, gen_log

from settings import *

import yaml
import json

import unicodedata

import control

import logging.config

cur_dir = os.path.dirname(os.path.abspath(__file__))

class Application(tornado.web.Application):
    def __init__(self):
        web_path = [
            (r"/", control.HomeHandler),
            (r"/packhandler/", control.PackHandler),
            (r"/autoinstall/", control.autoHandler),
            (r"/rsyncpack/", control.rsyncHandler)
        ]

        handlers = web_path

        settings = dict(
            template_path=os.path.join(cur_dir, 'templates/'),
            static_path=os.path.join(cur_dir, 'lib/'),
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/",

            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

    def log_request(self, handler):
        if "log_function" in self.settings:
            self.settings["log_function"](handler)
            return
        if handler.get_status() < 400:
            log_method = access_log.info
        elif handler.get_status() < 500:
            log_method = access_log.warning
        else:
            log_method = access_log.error
        request_time = 1000.0 * handler.request.request_time()
        log_method("%d %s %.2fms", handler.get_status(),
                   handler._request_summary(), request_time)
        log_method("request is %s", handler.request.body)

#
def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()


