#!/usr/bin/env python
# -*- coding: utf8 -*-

import salt

class saltstackwork():
    def __init__(self):
        import salt
        self.local = salt.client.LocalClient()

    def run_cmd(self, tgt, cmd):
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

