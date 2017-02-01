#!/usr/bin/env python
# -*- coding: utf8 -*-

import logging
import sys, os
import yaml

cur_dir = os.path.dirname(os.path.abspath(__file__))
par_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
config_file = os.path.abspath(os.path.join(cur_dir, 'config.yaml'))
config = yaml.load(open(config_file))

salt_log_dir = os.path.join(cur_dir, 'log/')
salt_log_file = config['salt_log_file']
log_file= os.path.join(salt_log_dir, salt_log_file)

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

class saltstackwork():
    def __init__(self):
        import salt.client
        self.local = salt.client.LocalClient()

    def __run_cmd__(self, tgt, cmd):
        _cmd = [cmd]
        result = self.local.cmd(tgt, 'cmd.run', _cmd, expr_form='list', timeout=10)
        result_list = []
        for i in tgt:
            if result.has_key(i):
                result_list.append({"id": i, "ret": result[i], "result": True})
            else:
                result_list.append({"id": i, "result": False})
        return result_list

    def rsync_cmd(self, tgt, source_file, dst_file):
        pass

    def test_cmd(self):
        result = self.local.cmd('*', 'test.ping')
        log.info('test salt log')
        return result

    # def __file_manage_cmd__(self, tgt, source_file, dst_file, **kwargs):
    #     md5value = kwargs.get('md5value', None)
    #
    #     dict = {
    #         'name': dst_file,
    #         'source': source_file,
    #         'makedirs': True,
    #         'user': 'nginx',
    #         'group': 'nginx',
    #         'mode': 0755,
    #         'replace': True,
    #     }
    #
    #     if md5value != None:
    #         # dict.update({
    #         #     'source_hash': 'md5=%s' % md5value,
    #         # })
    #         dict_md5 = {
    #             'hash_type': 'md5',
    #             'hsum': md5value,
    #         }
    #
    #     user = 'nginx'
    #     group = 'nginx'
    #
    #     result = self.local.cmd(tgt, 'file.check_managed', [dst_file, source_file, dict_md5, user,
    #                                                         group, '755', 'jinja',
    #                                                         True, None, None, 'base'],
    #                             expr_form='list', timeout=10)
    #
    #     result_list = []
    #     for i in tgt:
    #         if result.has_key(i):
    #             result_list.append({"id": i, "ret": result[i], "result": True})
    #         else:
    #             result_list.append({"id": i, "result": False})
    #
    #     return  result_list

    def __file_copy_cmd__(self, tgt, source_file, dst_file, **kwargs):

        dict = {
            'recurse': True,
            'remove_existing': True,
        }

        result = self.local.cmd(tgt, 'file.copy', [source_file, dst_file],
                                kwargs=dict,
                                expr_form='list', timeout=10)

        result_list = []
        for i in tgt:
            if result.has_key(i):
                result_list.append({"id": i, "ret": result[i], "result": True})
                log.info('%s copy %s to %s success' %(i, source_file, dst_file))
            else:
                result_list.append({"id": i, "result": False})
                log.error('%s copy %s to %s No Connect' %(i, source_file, dst_file))

        return result_list

    def __file_check_hash__(self, tgt, check_file, md5value):

        result = self.local.cmd(tgt, 'file.check_hash', [check_file, md5value],
                                expr_form='list', timeout=10)

        result_list = []
        for i in tgt:
            if result.has_key(i):
                result_list.append({"id": i, "ret": result[i], "result": result[i]})
                if result[i] == True:
                    log.info('%s md5_check %s result %s' % (i, check_file, result[i]))
                else:
                    log.error('%s md5_check %s result %s' % (i, check_file, result[i]))
            else:
                result_list.append({"id": i, "result": False})
                log.error('%s md5_check result %s' % (i, 'No Connect'))

        return result_list






