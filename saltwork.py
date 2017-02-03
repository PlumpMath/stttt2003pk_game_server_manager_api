#!/usr/bin/env python
# -*- coding: utf8 -*-

import logging
import sys, os
import yaml

from tornado.log import access_log, app_log, gen_log

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

    def __rsync_cmd__(self, tgt, source_file, dst_file):
        dict = {
            'delete': True,
            'update': True,
        }
        result = self.local.cmd(tgt, 'rsync.rsync', [source_file, dst_file],
                                kwarg=dict,
                                expr_form='list', timeout=10)

        result_list = []
        for i in tgt:
            if result.has_key(i):
                result_list.append({"id": i, "ret": result[i], "result": True})
                access_log.info('%s rsync %s to %s success' % (i, source_file, dst_file))
            else:
                result_list.append({"id": i, "result": False})
                access_log.error('%s rsync %s to %s No Connect' % (i, source_file, dst_file))

        return result_list

    def test_cmd(self):
        result = self.local.cmd('*', 'test.ping')
        access_log.info('test salt log')
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
                access_log.info('%s copy %s to %s success' %(i, source_file, dst_file))
            else:
                result_list.append({"id": i, "result": False})
                access_log.error('%s copy %s to %s No Connect' %(i, source_file, dst_file))

        return result_list

    def __file_check_hash__(self, tgt, check_file, md5value):

        result = self.local.cmd(tgt, 'file.check_hash', [check_file, md5value],
                                expr_form='list', timeout=10)

        result_list = []
        for i in tgt:
            if result.has_key(i):
                result_list.append({"id": i, "ret": result[i], "result": result[i]})
                if result[i] == True:
                    access_log.info('%s md5_check %s result %s' % (i, check_file, result[i]))
                else:
                    access_log.error('%s md5_check %s result %s' % (i, check_file, result[i]))
            else:
                result_list.append({"id": i, "result": False})
                access_log.error('%s md5_check result %s' % (i, 'No Connect'))

        return result_list






