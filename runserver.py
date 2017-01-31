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

#
def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()


