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
from saltwork import *

from db_model import *

cur_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.abspath(os.path.join(cur_dir, 'config.yaml'))
config = yaml.load(open(config_file))

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
        self.write('welcome to the api deployment about cod4server')

class PackHandler(BaseHandler):

    def get(self):
        handler = db_Model('agentInfoTable')
        agentInfo = handler.__getAgentInfo__()
        #print agentInfo
        self.write(json.dumps(agentInfo))

    def post(self):
        post_data = json.loads(self.request.body)
        agent_list = post_data['agent_list']
        file_name = post_data['file_name']

        if agent_list and file_name:
            tgt = agent_list

            gameserver_file = file_name
            source_file_dir = config['source_file_dir']
            source_file = os.path.abspath(os.path.join(source_file_dir, gameserver_file))
            dst_file_dir = config['dst_file_dir']
            dst_file = os.path.abspath(os.path.join(dst_file_dir, gameserver_file))

            saltrun = saltstackwork()
            ret_copy = saltrun.__file_copy_cmd__(tgt, source_file, dst_file)

            md5cmd = 'md5sum %s' % source_file
            md5value = 'md5:%s' % os.popen(md5cmd).readline().split()[0]

            ret_md5 = saltrun.__file_check_hash__(tgt, dst_file, md5value=md5value)

            copy_success_list = []
            copy_fail_list = []
            for i in ret_copy:
                if i['id'] and i['result'] == True:
                    copy_success_list.append(i['id'])
                else:
                    copy_fail_list.append(i['id'])

            md5_success_list = []
            md5_fail_list = []
            for i in ret_md5:
                if i['id'] and i['result'] == True:
                    md5_success_list.append(i['id'])
                else:
                    md5_fail_list.append(i['id'])

            dict_ret = {
                'success': [],
                'failed': {
                    'copy': [],
                    'md5': [],
                }
            }
            for agent in tgt:
                if agent in copy_success_list and md5_success_list:
                    dict_ret['success'].append(agent)
                else:
                    if agent in copy_fail_list:
                        dict_ret['failed']['copy'].append(agent)
                    if agent in md5_fail_list:
                        dict_ret['failed']['md5'].append(agent)

            ret_str = json.dumps(dict_ret, sort_keys=False, indent=4, separators=(',', ': '))

            self.write(ret_str)




































