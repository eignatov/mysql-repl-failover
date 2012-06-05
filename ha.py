#!/opt/bin/python
# -*- coding: utf-8 -*-

import sys
import MySQLdb
import time
from MySQLdb import cursors
import commands
 
def conn_master1():
  host     = '127.0.0.1'
  port     = '3306'
  username = 'root'
  password = ''
  dbname='mysql'
  return MySQLdb.connect(host=host,
                         db=dbname,
                         user=username,
                         passwd=password,
                         port=int(port),
                         charset="utf8",
                         cursorclass = MySQLdb.cursors.SSCursor)

def conn_master2():
  host     = '127.0.0.1'
  port     = '3307'
  username = 'root'
  password = ''
  dbname='mysql'
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

def failover1():
  # when master1 server down
  sys.stderr.write("failover1\n")
  commands.getoutput("supervisorctl stop mysql-proxy-master1")
  commands.getoutput("supervisorctl stop mysql-proxy-master2")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1")
  commands.getoutput("supervisorctl stop mysql-proxy-slave2")
  time.sleep(5)
  stop_slave(master2)
  read_only_off(master2)
  commands.getoutput("supervisorctl start mysql-proxy-master-failover1")
  commands.getoutput("supervisorctl start mysql-proxy-master-failover2")
  commands.getoutput("supervisorctl start mysql-proxy-slave-failover1")
  commands.getoutput("supervisorctl start mysql-proxy-slave-failover2")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished! : master2 is new master\n")
    sys.stderr.write("kill this daemon until master1 failback!\n")
    time.sleep(5)

def failover2():
  # when master2 server down
  sys.stderr.write("failover2\n")
  commands.getoutput("supervisorctl stop mysql-proxy-slave1")
  commands.getoutput("supervisorctl stop mysql-proxy-slave2")
  time.sleep(5)
  commands.getoutput("supervisorctl start mysql-proxy-slave-failover3")
  commands.getoutput("supervisorctl start mysql-proxy-slave-failover4")
  time.sleep(5)
  while 1:
    sys.stderr.write("failover finished! : master2/slave4 has been purged\n")
    sys.stderr.write("kill this daemon until master2 failback!\n")
    time.sleep(5)
  
if __name__ == '__main__':
  master1 = conn_master1()
  master2 = conn_master2()
  commands.getoutput("supervisorctl start mysql-proxy-master1")
  commands.getoutput("supervisorctl start mysql-proxy-master2")
  commands.getoutput("supervisorctl start mysql-proxy-slave1")
  commands.getoutput("supervisorctl start mysql-proxy-slave2")
  read_only_on(master2)
  start_slave(master2)
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
        failover1()
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
        failover2()
        break

    time.sleep(5)
    i += 1


