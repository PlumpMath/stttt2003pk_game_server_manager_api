#!/usr/bin/env python
# -*- coding: utf8 -*-

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
        return result

    def __file_manage_cmd__(self, tgt, source_file, dst_file, **kwargs):
        md5value = kwargs.get('md5value', None)

        dict = {
            'name': dst_file,
            'source': source_file,
            'makedirs': True,
            'user': 'nginx',
            'group': 'nginx',
            'mode': 0755,
            'replace': True,
        }

        if md5value != None:
            dict.update({
                'source_hash': 'md5=%s' % md5value,
            })

        result = self.local.cmd(tgt, 'file.managed', [], kwagr=dict,
                                expr_form='list', timeout=10)

        result_list = []
        for i in tgt:
            if result.has_key(i):
                result_list.append({"id": i, "ret": result[i], "result": True})
            else:
                result_list.append({"id": i, "result": False})

        return  result_list




