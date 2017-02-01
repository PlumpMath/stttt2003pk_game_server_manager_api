#!/usr/bin/env python
# -*- coding: utf8 -*-
import json
dict = {
    'agent_list':
        [
            'gamefile.stttt2003pk.com',
            'devops.stttt2003pk.com',
        ],

    'file_name': 'cod4x18_dedrun.tar.bz2',
}

print json.dumps(dict, sort_keys=False, indent=4, separators=(',', ': '))
