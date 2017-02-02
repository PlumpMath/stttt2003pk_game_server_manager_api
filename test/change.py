#!/usr/bin/env python
# -*- coding: utf8 -*-

import re

def changeHandle(date_str):

    content = '%s/%s/20%s\n'
    return content %(date_str.split('.')[2].replace('\n', ''),date_str.split('.')[1],date_str.split('.')[0],)

content_tem = '%s/%s/20%s\n'
ret_file = open('change_final_rent_out.txt', 'wb')
with open('change_rent_out.txt', 'rb') as f:
    lines = f.readlines()
    for line in lines:
        if re.match(r'^(\d{2})\.(\d{2})\.(\d{2}).*$', line):
            template = re.search(r'^(\d{2})\.(\d{2})\.(\d{2}).*$', line)
            ret_file.write(content_tem %(template.group(3), template.group(2), template.group(1)))
            print content_tem %(template.group(3), template.group(2), template.group(1))
        else:
            ret_file.write(line)
            print line

ret_file.close()

print changeHandle('1.1.16\n')


