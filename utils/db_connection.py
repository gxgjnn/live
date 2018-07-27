# -*- coding: utf-8 -*-

import pymysql as sql
# import redis
import os
import ConfigParser
import sys
sys.path.append("..")


class Connection:

    def __init__(self):
        self.conf_dir = os.path.split(os.path.realpath(__file__))[0].replace('utils', 'conf')

    def __mysql_read(self):

        config = ConfigParser.ConfigParser()
        file_path = os.path.join(self.conf_dir, 'default.ini')
        try:
            config.read(file_path)
        except Exception, e:
            print e
        return config

    def mysql_param_read(self, section_name, param):

        config = self.__mysql_read()
        return config.get(section_name, param)

    def conn_source(self):
        db = 'db_source'
        conn = sql.connect(host=self.mysql_param_read(db, 'host'),
                           user=self.mysql_param_read(db, 'user'),
                           passwd=self.mysql_param_read(db, 'password'),
                           db=self.mysql_param_read(db, 'database'),
                           charset="utf8")
        return conn

    def conn_destination(self):
        db = 'db_destination'
        conn = sql.connect(host=self.mysql_param_read(db, 'host'),
                           user=self.mysql_param_read(db, 'user'),
                           passwd=self.mysql_param_read(db, 'password'),
                           db=self.mysql_param_read(db, 'database'),
                           charset="utf8")
        return conn

    def conn_back(self):
        db = 'db_back'
        conn = sql.connect(host=self.mysql_param_read(db, 'host'),
                           user=self.mysql_param_read(db, 'user'),
                           passwd=self.mysql_param_read(db, 'password'),
                           db=self.mysql_param_read(db, 'database'),
                           charset="utf8")
        return conn

    # def conn_redis(self):
    #     db = 'redis'
    #     pool = redis.ConnectionPool(host=self.mysql_param_read(db, 'host'),
    #                                 port=self.mysql_param_read(db, 'port'),
    #                                 db=self.mysql_param_read(db, 'database'))
    #                                 #password=obj.mysql_param_read(db, 'password'))
    #     r = redis.StrictRedis(connection_pool=pool)
    #     return r