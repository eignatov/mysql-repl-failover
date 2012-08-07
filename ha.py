#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012, UTADA katsuya
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

import sys
import MySQLdb
import time
from MySQLdb import cursors
import commands
 
def conn_master1():
  ### edit environment
  host     = '127.0.0.1'
  port     = '3306'
  username = 'root'
  password = ''
  dbname   = 'mysql'
  ###
  return MySQLdb.connect(host=host,
                         db=dbname,
                         user=username,
                         passwd=password,
                         port=int(port),
                         charset="utf8",
                         cursorclass = MySQLdb.cursors.SSCursor)

def conn_master2():
  ### edit environment
  host     = '127.0.0.1'
  port     = '3307'
  username = 'root'
  password = ''
  dbname   = 'mysql'
  ###
  return MySQLdb.connect(host=host,
                         db=dbname,
                         user=username,
                         passwd=password,
                         port=int(port),
                         charset="utf8",
                         cursorclass = MySQLdb.cursors.SSCursor)

def conn_slave1():
  ### edit environment
  host     = '127.0.0.1'
  port     = '3308'
  username = 'root'
  password = ''
  dbname   = 'mysql'
  ###
  return MySQLdb.connect(host=host,
                         db=dbname,
                         user=username,
                         passwd=password,
                         port=int(port),
                         charset="utf8",
                         cursorclass = MySQLdb.cursors.SSCursor)

def conn_slave2():
  ### edit environment
  host     = '127.0.0.1'
  port     = '3309'
  username = 'root'
  password = ''
  dbname   = 'mysql'
  ###
  return MySQLdb.connect(host=host,
                         db=dbname,
                         user=username,
                         passwd=password,
                         port=int(port),
                         charset="utf8",
                         cursorclass = MySQLdb.cursors.SSCursor)

def master_status(conn):
  cur = conn.cursor()
  sql = "show master status"
  try:
    cur.execute(sql)
  except:
    return False
  return cur.fetchall()

def is_slave_running(conn):
  cur = conn.cursor()
  sql = "show status like 'Slave_running'"
  try:
    cur.execute(sql)
  except:
    return False
  return cur.fetchall()

def read_only_off(conn):
  cur = conn.cursor()
  sql = "set global read_only=0"
  try:
    cur.execute(sql)
  except:
    return False
  return True

def read_only_on(conn):
  cur = conn.cursor()
  sql = "set global read_only=1"
  try:
    cur.execute(sql)
  except:
    return False
  return True

def stop_slave(conn):
  cur = conn.cursor()
  sql = "stop slave"
  try:
    cur.execute(sql)
  except:
    return False
  return True

def start_slave(conn):
  cur = conn.cursor()
  sql = "start slave"
  try:
    cur.execute(sql)
  except:
    return False
  return True

def rpl_semi_sync_master_on(conn):
  cur = conn.cursor()
  sql = "set global rpl_semi_sync_master_enabled = ON"
  try:
    cur.execute(sql)
  except:
    return False
  return True

def rpl_semi_sync_master_off(conn):
  cur = conn.cursor()
  sql = "set global rpl_semi_sync_master_enabled = OFF"
  try:
    cur.execute(sql)
  except:
    return False
  return True

def rpl_semi_sync_slave_on(conn):
  cur = conn.cursor()
  sql = "set global rpl_semi_sync_slave_enabled = ON"
  try:
    cur.execute(sql)
  except:
    return False
  return True

def rpl_semi_sync_slave_off(conn):
  cur = conn.cursor()
  sql = "set global rpl_semi_sync_slave_enabled = OFF"
  try:
    cur.execute(sql)
  except:
    return False
  return True

def failover1():
  # when master1 down
  sys.stderr.write("failover1\n")
  commands.getoutput("supervisorctl stop mysql-proxy-master1_1")
  commands.getoutput("supervisorctl stop mysql-proxy-master1_2")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_1")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_2")
  time.sleep(5)
  stop_slave(master2)
  read_only_off(master2)
  commands.getoutput("supervisorctl start mysql-proxy-master2_1")
  commands.getoutput("supervisorctl start mysql-proxy-master2_2")
  commands.getoutput("supervisorctl start mysql-proxy-slave2_1")
  commands.getoutput("supervisorctl start mysql-proxy-slave2_2")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished : master2 is new master now\n")
    sys.stderr.write("stop this daemon until master1 failback\n")
    time.sleep(5)

def failover2():
  # when master2 down
  sys.stderr.write("failover2\n")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_1")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_2")
  time.sleep(5)
  commands.getoutput("supervisorctl start mysql-proxy-slave3_1")
  commands.getoutput("supervisorctl start mysql-proxy-slave3_2")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished : master2/slave2 has been purged\n")
    sys.stderr.write("stop this daemon until master2 failback!\n")
    time.sleep(5)

def failover3():
  # master1 down (M2 is master)
  sys.stderr.write("failover3(M1 down)(M2 is master)\n")
  commands.getoutput("supervisorctl stop mysql-proxy-slave4_1")
  commands.getoutput("supervisorctl stop mysql-proxy-slave4_2")
  time.sleep(5)
  commands.getoutput("supervisorctl start mysql-proxy-slave2_1")
  commands.getoutput("supervisorctl start mysql-proxy-slave2_2")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished : master1/slave1 has been purged\n")
    sys.stderr.write("stop this daemon until master1 failback!\n")
    time.sleep(5)

def failover4():
  # when master2 down (and M2 is master)
  sys.stderr.write("failover4(M2 master down)\n")
  commands.getoutput("supervisorctl stop mysql-proxy-master2_1")
  commands.getoutput("supervisorctl stop mysql-proxy-master2_2")
  commands.getoutput("supervisorctl stop mysql-proxy-slave4_1")
  commands.getoutput("supervisorctl stop mysql-proxy-slave4_2")
  time.sleep(5)
  commands.getoutput("supervisorctl start mysql-proxy-master1_1")
  commands.getoutput("supervisorctl start mysql-proxy-master1_2")
  commands.getoutput("supervisorctl start mysql-proxy-slave3_1")
  commands.getoutput("supervisorctl start mysql-proxy-slave3_2")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished : master2/slave2 has been purged\n")
    sys.stderr.write("stop this daemon until master2 failback!\n")
    time.sleep(5)

def slave0_error():
  # when master2 slave is stopped
  sys.stderr.write("slave0 error\n")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_1")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_2")
  time.sleep(5)
  commands.getoutput("supervisorctl start mysql-proxy-slave3_1")
  commands.getoutput("supervisorctl start mysql-proxy-slave3_2")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished : master2/slave2 has been purged\n")
    sys.stderr.write("stop this daemon until master2 failback!\n")
    time.sleep(5)

def slave0_2_error():
  # master2 is master.
  # when master1 slave is stopped
  sys.stderr.write("slave at master1 error\n")
  #commands.getoutput("supervisorctl stop mysql-proxy-slave2_1")
  #commands.getoutput("supervisorctl stop mysql-proxy-slave2_2")
  time.sleep(5)
  #commands.getoutput("supervisorctl start mysql-proxy-slave3_1")
  #commands.getoutput("supervisorctl start mysql-proxy-slave3_2")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished : master2/slave2 has been purged\n")
    sys.stderr.write("stop this daemon until master2 failback!\n")
    time.sleep(5)

def slave1_error():
  # when slave1 slave is stopped
  sys.stderr.write("slave1 error\n")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_1")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_2")
  time.sleep(5)
  commands.getoutput("supervisorctl start mysql-proxy-slave5_1")
  commands.getoutput("supervisorctl start mysql-proxy-slave5_2")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished : slave1 has been purged\n")
    sys.stderr.write("stop this daemon until slave1 replication back!\n")
    time.sleep(5)

def slave2_error():
  # when slave2 slave is stopped
  sys.stderr.write("slave2 error\n")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_1")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1_2")
  time.sleep(5)
  commands.getoutput("supervisorctl start mysql-proxy-slave6_1")
  commands.getoutput("supervisorctl start mysql-proxy-slave6_2")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished : slave2 has been purged\n")
    sys.stderr.write("stop this daemon until slave2 replication back!\n")
    time.sleep(5)

def watch_m1():
  stop_slave(master1)
  read_only_off(master1)
  read_only_on(master2)
  start_slave(master2)
  commands.getoutput("supervisorctl start mysql-proxy-master1_1")
  commands.getoutput("supervisorctl start mysql-proxy-master1_2")
  commands.getoutput("supervisorctl start mysql-proxy-slave1_1")
  commands.getoutput("supervisorctl start mysql-proxy-slave1_2")
  i = 0
  while 1:
    # check master1
    sys.stderr.write("%d: check master1 status at %s\n" % (i, time.ctime()))
    r = master_status(master1)
    if r and len(r) > 0:
      master1_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("master1 fail detected!\n")
      master1_err_cnt += 1
      if master1_err_cnt > 5:
        sys.stderr.write("master1 failing: failover starting\n")
        failover1()
        break

    # check master2
    sys.stderr.write("%d: check master2 status at %s\n" % (i, time.ctime()))
    r = master_status(master2)
    if r and len(r) > 0:
      master2_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("master2 fail detected!\n")
      master2_err_cnt += 1
      if master2_err_cnt > 5:
        sys.stderr.write("master2 failing: failover starting\n")
        failover2()
        break

    # check replication slave at master2
    sys.stderr.write("%d: check replication slave on master2 at %s\n" % (i, time.ctime()))
    r = is_slave_running(master2)
    for row in r:
      slave_running = row[1]
    if slave_running == "ON":
      slave0_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("replication slave stop detected on master2!\n")
      slave0_err_cnt += 1
      if slave0_err_cnt > 5:
        sys.stderr.write("replication error on master2: purging master2 from slave\n")
        slave0_error()
        break

    # check replication slave at slave1
    sys.stderr.write("%d: check replication slave on slave1 at %s\n" % (i, time.ctime()))
    r = is_slave_running(slave1)
    for row in r:
      slave_running = row[1]
    if slave_running == "ON":
      slave1_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("replication slave stop detected on slave1! \n")
      slave1_err_cnt += 1
      if slave1_err_cnt > 5:
        sys.stderr.write("replication error on slave1: purging slave1 from slave\n")
        slave1_error()
        break

    # check replication slave at slave2
    sys.stderr.write("%d: check replication slave on slave2 at %s\n" % (i, time.ctime()))
    r = is_slave_running(slave2)
    for row in r:
      slave_running = row[1]
    if slave_running == "ON":
      slave2_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("replication slave stop detected on slave2! \n")
      slave2_err_cnt += 1
      if slave2_err_cnt > 5:
        sys.stderr.write("replication error on slave2: purging slave2 from slave\n")
        slave2_error()
        break

    time.sleep(5)
    i += 1

def watch_m2():
  stop_slave(master2)
  read_only_off(master2)
  read_only_on(master1)
  start_slave(master1)
  commands.getoutput("supervisorctl start mysql-proxy-master2_1")
  commands.getoutput("supervisorctl start mysql-proxy-master2_2")
  commands.getoutput("supervisorctl start mysql-proxy-slave4_1")
  commands.getoutput("supervisorctl start mysql-proxy-slave4_2")
  i = 0
  while 1:
    # check master1
    sys.stderr.write("%d: master1 status check at %s\n" % (i, time.ctime()))
    r = master_status(master1)
    if r and len(r) > 0:
      master1_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("master1 fail detected!\n")
      master1_err_cnt += 1
      if master1_err_cnt > 5:
        sys.stderr.write("master1 failing: failover starting\n")
        failover3()
        break

    # check master2
    sys.stderr.write("%d: master2 status check at %s\n" % (i, time.ctime()))
    r = master_status(master2)
    if r and len(r) > 0:
      master2_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("master2 fail detected!\n")
      master2_err_cnt += 1
      if master2_err_cnt > 5:
        sys.stderr.write("master2 failing: failover starting\n")
        failover4()
        break

    # check replication slave at master1
    sys.stderr.write("%d: check replication slave on master1 at %s\n" % (i, time.ctime()))
    r = is_slave_running(master1)
    for row in r:
      slave_running = row[1]
    if slave_running == "ON":
      slave0_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("replication slave stop detected on master1!\n")
      slave0_err_cnt += 1
      if slave0_err_cnt > 5:
        sys.stderr.write("replication error on master1: purging master1 from slave\n")
        slave0_2_error()
        break

    # check replication slave at slave1
    sys.stderr.write("%d: check replication slave on slave1 at %s\n" % (i, time.ctime()))
    r = is_slave_running(slave1)
    for row in r:
      slave_running = row[1]
    if slave_running == "ON":
      slave1_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("replication slave stop detected on slave1! \n")
      slave1_err_cnt += 1
      if slave1_err_cnt > 5:
        sys.stderr.write("replication error on slave1: purging slave1 from slave\n")
        slave1_error()
        break

    # check replication slave at slave2
    sys.stderr.write("%d: check replication slave on slave2 at %s\n" % (i, time.ctime()))
    r = is_slave_running(slave2)
    for row in r:
      slave_running = row[1]
    if slave_running == "ON":
      slave2_err_cnt = 0
      sys.stderr.write("ok\n")
    else:
      sys.stderr.write("replication slave stop detected on slave2! \n")
      slave2_err_cnt += 1
      if slave2_err_cnt > 5:
        sys.stderr.write("replication error on slave2: purging slave2 from slave\n")
        slave2_error()
        break

    time.sleep(5)
    i += 1

  
if __name__ == '__main__':
  argvs = sys.argv
  argc = len(argvs)
  if (argc < 2):
    print 'Usage: ha.py <m1|m2>'
    quit()

  master1 = conn_master1()
  master2 = conn_master2()
  slave1 = conn_slave1()
  slave2 = conn_slave2()
  if (argvs[1] == 'm1'):
    ## when m1 is master
    watch_m1()
  if (argvs[1] == 'm2'):
    ## when m2 is master
    watch_m2()

