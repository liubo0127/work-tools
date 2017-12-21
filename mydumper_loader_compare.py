#!/bin/env python
#coding=utf-8

from __future__ import division
import threadpool
import MySQLdb
import os
import sys
import logging
import argparse

def Usage():
    parser = argparse.ArgumentParser(description="TiDB loader result check")
    parser.add_argument("-d", "--dir", dest="dir", default='None', help="(default: None)")
    parser.add_argument("-H", "--host", dest="host", default='127.0.0.1', help="(default: 127.0.0.1)")
    parser.add_argument("-u", "--username", dest="username", default='root', help="(default: root)")
    parser.add_argument("-p", "--password", dest="password", default='', help="(default: null)")
    parser.add_argument("-P", "--port", dest="port", default='3306', help="(default: 3306)")
    parser.add_argument("-l", "--log", dest="log", default='result.log', help="(default: result.log)")
    parser.add_argument("-t", "--thread", dest="thread", default='30', help="(default: 30)")
    args = parser.parse_args()
    return args

def getlogger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler(log)
    fmt = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger

def cmp_cnt(db_table):

    file_data_cnt = 0

    for i in data_file:
        if db_table + '.' in i:
            f = open(Dir.rstrip('/') + '/' + i)
            for line in f.readlines():
                if '(' in line:
                    file_data_cnt += 1
    db = MySQLdb.connect(host=host,user=username,passwd=password,port=port,db=db_table.split('.')[0])
    cursor = db.cursor()
    cursor.execute("select count(*) from " + db_table)
    data_cnt = cursor.fetchall()[0][0]
    db.close()
    if int(file_data_cnt) != int(data_cnt):
        logger.info(db_table + ' load not complete: mydumper data count is ' + str(file_data_cnt) + '; tidb data count is ' + str(data_cnt) + '.')
    else:
        logger.info(db_table + ' load complete: mydumper data count is ' + str(file_data_cnt) + '; tidb data count is ' + str(data_cnt) + '.')

    global num
    num += 1
    percent = int((num + 1) / table_num) * 100
    sys.stdout.write('[' + '#'*percent + ' '*(100 - percent) + '] ' + str(percent) + '%\r')
    sys.stdout.flush()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "usage: " + __file__ + " -h"
        exit(2)
    args = Usage()

    Dir = args.dir
    host = args.host
    username = args.username
    password = str(args.password)
    port = int(args.port)
    log = args.log
    Threads = int(args.thread)

    logger = getlogger()
    file_list = os.listdir(Dir)
    data_file = [i for i in file_list if "schema" not in i and "metadata" not in i]
    table_list = []
    for i in data_file:
        database = i.split('.')[0]
        table = i.split('.')[1]
        if database + '.' + table not in table_list:
            table_list.append(database + '.' + table)
    table_num = len(table_list)
    num = 0
    pool = threadpool.ThreadPool(Threads)
    requests = threadpool.makeRequests(cmp_cnt,table_list)
    [pool.putRequest(req) for req in requests]
    pool.wait()
    print ''