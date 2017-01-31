#!/usr/bin/env python
# -*- coding: utf8 -*-

import os

from tornado.options import define, options

cur_dir = os.path.dirname(os.path.abspath(__file__))

#define domain port
domain_name = 'gamefile.stttt2003pk.com'
port = int(7777)
#server_url = 'http://gamefile.stttt2003pk.com:7777'

define("debug",default=True,help="Debug Mode",type=bool)
define("port", default=port, help="the servers run the default port", type=int)

#cookie
define("cookies_expires", default=1,help="cookies_expires_days")

url_port = 'http://' + domain_name + ':' + str(port) + '/'
define("url_port", default=url_port, help="url_port")

