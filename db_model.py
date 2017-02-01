#!/usr/bin/env python
# -*- coding: utf8 -*-

from tornado.options import define, options
import torndb

import os , time

from settings import *

import json

class mysql_conn():
    def __init__(self):
        self._db = torndb.Connection('127.0.0.1', 'devops', user='root', password='')

    @property
    def db(self):
        return self._db

class db_Model():
    def __init__(self, method):
        self.method = method
        self.mysql = mysql_conn()
        self.db = self.mysql.db

    def __getAgentInfo__(self):
        result = self.db.query("select * from agentInfoTable")
        return  result


