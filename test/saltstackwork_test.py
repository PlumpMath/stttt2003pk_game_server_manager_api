#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os
import yaml

cur_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

if config_dir:
    sys.path.append(config_dir)
    from saltwork import *

config_file = os.path.abspath(os.path.join(config_dir, 'config.yaml'))
config = yaml.load(open(config_file))

tgt = []
if config['agent']:
    for agent in config['agent']:
        if agent['id']:
            tgt.append(agent['id'])

gameserver_file = 'test.html'
source_file_dir = config['source_file_dir']
source_file = os.path.abspath(os.path.join(source_file_dir, gameserver_file))
dst_file_dir = config['dst_file_dir']
dst_file = os.path.abspath(os.path.join(dst_file_dir, gameserver_file))

saltrun = saltstackwork()
print saltrun.test_cmd()

