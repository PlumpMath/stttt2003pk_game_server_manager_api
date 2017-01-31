#!/usr/bin/env python
# -*- coding: utf8 -*-

import os, signal

import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options
import tornado.web
from tornado.escape import json_decode, json_encode
import torndb
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

import yaml

import datetime, time
import subprocess

cur_dir = os.path.dirname(os.path.abspath(__file__))


class TemplateRendering():
    def __init__(self):
        #	self.settings = dict(
        #        template_path = os.path.join(cur_dir,'templates/'),
        #        static_path = os.path.join(cur_dir,'lib/'),
        #        cookie_secret = "SunRunVas38288446TestStttt2003pk",
        #        login_url = "/",
        #    )
        pass

    def render_template(self, template_name, **kwargs):
        template_dirs = []

        if self.settings.get('template_path', ''):
            template_dirs.append(self.settings["template_path"])

        ####jinja2 env setting,set test and filters
        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)

        content = template.render(kwargs)

        return content

####basehendler rendering overwrite
class BaseHandler(tornado.web.RequestHandler, TemplateRendering):
    ####render2 method
    def render2(self, template_name, **kwargs):
        kwargs.update({
            'settings': self.settings,
            'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),
            'request': self.request,

            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
            # {{ current_user }}
            'current_user': self.get_current_user(),

        })

        content = self.render_template(template_name, **kwargs)
        self.write(content)

    def template(self, template_name, **kwargs):
        kwargs.update({
            'settings': self.settings,
            'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),

            'request': self.request,

            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
        })

        content = self.render_template(template_name, **kwargs)
        return content

        ####overwrite tornado.web.RequestHandler get user method

    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id:
            return None

        return user_id

    def get_context(self):
        self.context = {'current_user': self.get_current_user()}
        return self.context

    #time out cmd
    def TIMEOUT_COMMAND(self, command, timeout):

        '''call shell-command and either return its output or kill it
        if it doesn't normally exit within timeout seconds and return None'''

        time_start = datetime.datetime.now()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, close_fds=True)
        while process.poll() is None:
            time.sleep(0.2)
            time_now = datetime.datetime.now()
            if (time_now - time_start).seconds > timeout:
                os.kill(process.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
                return "False error timeout"
        return process.stdout.read()











class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('test')