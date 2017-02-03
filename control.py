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
import tornado.gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

from tornado import iostream


from jinja2 import Environment, FileSystemLoader, TemplateNotFound

import yaml

import datetime, time
import subprocess
from saltwork import *

from db_model import *

import socket,hashlib
import struct

cur_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.abspath(os.path.join(cur_dir, 'config.yaml'))
config = yaml.load(open(config_file))

#par_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

salt_log_dir = os.path.join(cur_dir, 'log/')
salt_log_file = config['salt_log_file']
tornado_log_file = 'tornado.log'
log_file= os.path.join(salt_log_dir, tornado_log_file)

try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_file,
        filemode='a',
    )
    log = logging.getLogger('salt')
except Exception, err:
    print("Error: %s %s" % (err, log_file))
    sys.exit(2)

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

class SocketHandler(BaseHandler):
    def send_socket(self, type=1, id='1', ipaddr='1', command=''):
        if not type:
            return False
        self.type = type
        self.job_id = id
        self.ipaddr = ipaddr
        self.command = command

        self.key = '1234'

        HOST = ipaddr
        PORT = 9999

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream = iostream.IOStream(s)
        self.stream.set_close_callback(self.auth_close)

        try:
            self.stream.connect((HOST, PORT), self.auth_request)
        except:
            print "auth failed or connection refused"
            return False

    def auth_close(self):
        self.stream.close()
        print 'connection closed'

    def auth_request(self):

        def auth_send(data):
            #print data
            md5_hash = hashlib.md5(self.key + data[0:20]).hexdigest()
            #print md5_hash
            self.stream.write(md5_hash[10:], self.auth_ok)

        self.stream.read_bytes(30, auth_send)

    def auth_ok(self):
        self.stream.write(struct.pack('!H', self.type), self.send_data)

    def send_data(self):
        if self.type == 1:
            command_len = len(self.command)
            str_pack = "!II%ds" %command_len
            self.stream.write(struct.pack(str_pack, self.job_id, command_len, self.command.encode('utf-8')))
            #self.stream.read_bytes(6, self.status_request)


    def status_request(self, data):
        running_state, recive = struct.unpack('!HI', data)
        print '%s\n%s' %(running_state, recive)

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('welcome to the api deployment about cod4server')

class PackHandler(BaseHandler):
    executor = ThreadPoolExecutor(1)
    saltrun = saltstackwork()

    def get(self):
        handler = db_Model('agentInfoTable')
        agentInfo = handler.__getAgentInfo__()
        self.write(json.dumps(agentInfo))

    @tornado.web.asynchronous
    @tornado.gen.coroutine
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

            ret_copy = yield self.__file_copy_cmd(tgt, source_file, dst_file)
            print ret_copy

            md5value = yield self.__md5sum(source_file)
            print md5value

            ret_md5 = yield self.__file_check_hash(tgt, dst_file, md5value)
            print ret_md5

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
            self.finish()

    @run_on_executor
    def __file_copy_cmd(self, tgt, source_file, dst_file):
        ret = self.saltrun.__file_copy_cmd__(tgt, source_file, dst_file)
        return ret

    @run_on_executor
    def __md5sum(self, source_file):
        md5cmd = 'md5sum %s' % source_file
        md5value = 'md5:%s' % os.popen(md5cmd).readline().split()[0]
        return  md5value

    @run_on_executor()
    def __file_check_hash(self, tgt, dst_file, md5value):
        ret = self.saltrun.__file_check_hash__(tgt, dst_file, md5value=md5value)
        return ret

class rsyncHandler(BaseHandler):
    executor = ThreadPoolExecutor(1)
    saltrun = saltstackwork()

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        post_data = json.loads(self.request.body)
        agent_list = post_data['agent_list']
        dir_name = post_data['dir_name']

        if agent_list and dir_name:
            tgt = agent_list

            gameserver_dir = dir_name
            source_file_dir = config['source_file_dir']
            source_file = os.path.abspath(os.path.join(source_file_dir, gameserver_dir))
            dst_file_dir = config['dst_file_dir']
            #dst_file = os.path.abspath(os.path.join(dst_file_dir, gameserver_dir))
            dst_file = dst_file_dir

            # # print source_file
            # print dst_file

            ret_rsync =yield self.__rsyn_cmd(tgt, source_file, dst_file)

            rsync_success_list = []
            rsync_fail_list = []
            for i in ret_rsync:
                if i['id'] and i['result'] == True:
                    rsync_success_list.append(i['id'])
                else:
                    rsync_fail_list.append(i['id'])

            dict_ret = {
                'success': rsync_success_list,
                'failed': rsync_fail_list
            }

            ret_str = json.dumps(dict_ret, sort_keys=False, indent=4, separators=(',', ': '))
            self.write(ret_str)
            self.finish()

    @run_on_executor
    def __rsyn_cmd(self, tgt, source_file, dst_file):
        ret = self.saltrun.__rsync_cmd__(tgt, source_file, dst_file)
        return ret

class autoHandler(SocketHandler):

    def post(self):
        self.send_socket(id=77,
                         ipaddr='192.168.100.77',
                         command='ai')













































