#-*- coding:utf-8 -*-

# Developer : Jeong Wooyoung, EGLAB, Hongik University
# Contact   : gunyoung20@naver.com

import pymysql
from enum import Enum
from date import Date

class DBHandler:


    def reformToListFromTuple(self, tuple):
        list = []
        for t in tuple:
            list.append(t)
        return list

    def __init__(self):
        self.host = 'wooyoungsdb.csghu6krp0oh.ap-northeast-2.rds.amazonaws.com'
        self.db_name = 'knowledge_graph'
        self.user = 'word2vec'
        self.pwd = 'knowledge1'
        self.char_set = 'utf8'
        self.ne = Enum()
    def getConnection(self):
        while True:
            try:
                conn = pymysql.Connect(host=self.host, user=self.user, password=self.pwd, db=self.db_name, charset=self.char_set)
            except Exception as e:
                continue
            break
        return conn
