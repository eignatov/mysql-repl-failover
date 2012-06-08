# MySQL semi-synchronous replication monitoring and failover with Python.

this scripts is for failovering MySQL master db that is running in semi-synchronous replication .

## Configuration 

1. basic configuration You must have at least four units.
 * A single master
 * A semi-synchronous replication slave units 
 * Usually two slave 

2. Case 1 (M1 server down) 
https://docs.google.com/drawings/d/1phSXcws9SfOPgmCkRT1hK5P-HHRpbbvRIxFc8oNWXrI/edit 

3. Case 2 (M2 server is down)
https://docs.google.com/drawings/d/1rzbeWQfx0Jd7y4r28STKnAqdxILy2QdcBNIIhwuGdiI/edit

## Failover monitoring script

Provide a Python script that implements a monitoring and failover server. In order to daemonize the script, the installation of the supervisor required.

<pre>
sudo pip install supervisor
sudo mkdir /var/log/supervisor
echo_supervisord_conf > /etc/supervisord.conf
</pre>

vim /etc/supervisord.conf
<pre>
--- /etc/supervisord.conf.dist  2011-11-24 15:19:15.940609281 +0900
+++ /etc/supervisord.conf       2011-11-24 15:23:12.655620601 +0900
@@ -13,11 +13,11 @@
 ;password=123               ; (default is no password (open server))

 [supervisord]
-logfile=/tmp/supervisord.log ; (main log file;default $CWD/supervisord.log)
+logfile=/var/log/supervisor/supervisord.log ; (main log file;default $CWD/supervisord.log)
 logfile_maxbytes=50MB       ; (max main logfile bytes b4 rotation;default 50MB)
 logfile_backups=10          ; (num of main logfile rotation backups;default 10)
 loglevel=info               ; (log level;default info; others: debug,warn,trace)
-pidfile=/tmp/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
+pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
 nodaemon=false              ; (start in foreground if true;default false)
 minfds=1024                 ; (min. avail startup file descriptors;default 1024)
 minprocs=200                ; (min. avail process descriptors;default 200)
@@ -125,5 +125,5 @@
 ; interpreted as relative to this file.  Included files *cannot*
 ; include files themselves.

[program:mysqlcheck]
command=/home/utada/python_work/ha/ha.py
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=true

</pre>

## configuration of mysql-proxy

to register supervisor, the definition for mysql-proxy connection app.

- Mysql-proxy for connecting to master  
 - mysql-proxy-master1  
 - mysql-proxy-master2  
- Mysql-proxy for connecting to the master (for failover when M1-down)
 - mysql-proxy-master-failover1
 - mysql-proxy-master-failover2
- Mysql-proxy connection for slave
 - mysql-proxy-slave1
 - mysql-proxy-slave2
- Mysql-proxy for slave connection (for failover when M1-down)
 - mysql-proxy-slave-failover1
 - mysql-proxy-slave-failover2
- Mysql-proxy for slave connection (for failover when M2-down)
 - mysql-proxy-slave-failover3
 - mysql-proxy-slave-failover3

vim /etc/supervisord.conf

<pre>
[program:mysql-proxy-master1]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3031 --proxy-backend-addresses 127.0.0.1:3306
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false

[program:mysql-proxy-master2]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3032 --proxy-backend-addresses 127.0.0.1:3306
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false

[program:mysql-proxy-master-failover1]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3031 --proxy-backend-addresses 127.0.0.1:3307
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false

[program:mysql-proxy-master-failover2]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3032 --proxy-backend-addresses 127.0.0.1:3307
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false

[program:mysql-proxy-slave1]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3041 --proxy-backend-addresses 127.0.0.1:3307 --proxy-backend-addresses 127.0.0.1:3308 --proxy-backend-addresses 127.0.0.1:3309
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false

[program:mysql-proxy-slave2]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3042 --proxy-backend-addresses 127.0.0.1:3307 --proxy-backend-addresses 127.0.0.1:3308 --proxy-backend-addresses 127.0.0.1:3309
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false

[program:mysql-proxy-slave-failover1]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3041 --proxy-backend-addresses 127.0.0.1:3309
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false

[program:mysql-proxy-slave-failover2]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3042 --proxy-backend-addresses 127.0.0.1:3309
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false

[program:mysql-proxy-slave-failover3]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3041 --proxy-backend-addresses 127.0.0.1:3308
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false

[program:mysql-proxy-slave-failover4]
command=/usr/local/mysql-proxy/bin/mysql-proxy --proxy-address 127.0.0.1:3042 --proxy-backend-addresses 127.0.0.1:3308
stdout_logfile_maxbytes=1MB
stderr_logfile_maxbytes=1MB
stdout_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile=/var/log/supervisor/%(program_name)s.log
autorestart=false
</pre>


Configured to boot via init the Supervisor.

sudo / etc / rc.d / init.d / supervisord

<pre>
#! / bin / sh
#
# Supervisord - this script starts and stops the supervisord daemon
#
# Chkconfig: - 90 10
# Description: Supervisor is a client / server system that allows \
# Its users to monitor and control a number of \
# Processes on UNIX-like operating systems.
# Processname: supervisord
# Config: / etc / supervisord.conf
# Pidfile: / tmp / supervisord.pid

# Source function library.
. / Etc / init.d / functions

# Source networking configuration.
. / Etc / sysconfig / network

# Check that networking is up.
["$ NETWORKING" = "no"] && exit 0

RETVAL = 0
supervisord = "/ usr / bin / supervisord"
prog = $ (basename $ supervisord)
pidfile = / tmp / supervisord.pid
lockfile = / var / lock / subsys / supervisord

start () {
     echo-n $ "Starting $ prog:"
     daemon $ supervisord - pidfile $ pidfile
     RETVAL = $?
     echo
     [$ RETVAL-eq 0] && touch $ lockfile
     return $ RETVAL
}
stop () {
     echo-n $ "Stopping $ prog:"
     killproc-p $ pidfile $ supervisord-QUIT
     RETVAL = $?
     echo
     [$ RETVAL-eq 0] && rm-f $ lockfile
     return $ RETVAL
}
restart () {
     stop
     sleep 1
     start
}
reload () {
     echo-n $ "Reloading $ prog:"
     killproc-p $ pidfile $ supervisord-HUP
     RETVAL = $?
     echo
}

case "$ 1" in
     start)
start
;;
     stop)
stop
;;
     reload)
reload
;;
     restart)
restart
;;
     status)
status-p $ {pidfile} supervisord
RETVAL = $?
;;
     *)
echo $ "Usage: $ 0 {start | stop | status | restart | reload}"
         RETVAL = 2
;;
esac

exit $ RETVAL
</pre>

## Flow details

Configuration DB 

- M1 (192.168.0.1 port: 3306)
- M2 (192.168.0.1 port: 3307)
- S1 (192.168.0.1 port: 3308)
- S2 (192.168.0.1 port: 3309)

To set up as.

DB was configured as a master M1 is ON the plug-in semi-synchronous replication.

M2 refers to the M1 as a slave to the ON DB plug-in semi-synchronous replication, which is set to ON log_slave_update. read_only = on

S1 refers to the M1 in the normal replication. read_only = 1

S2 refers to the M2 in the normal replication. read_only = 1

## Supervisor

mysql-proxy on the supervisor and all Python scripts, and manage to daemonize.

* write to /etc/supervisord.conf the start command.

* startup python script and mysql-proxy.

in the state of online DB4,

<pre>
sudo supervisor start mysqlcheck
</pre>

starting python scripts and 4 mysql-proxy process.daemon on. 

confirmation of supervisor running

<pre>
sudo supervisorctl status

$ sudo supervisorctl status

mysql-proxy-master-failover1     STOPPED    Jun 05 10:47 AM
mysql-proxy-master-failover2     STOPPED    Jun 05 10:47 AM
mysql-proxy-master1              RUNNING    pid 2510, uptime 0:00:04
mysql-proxy-master2              RUNNING    pid 2519, uptime 0:00:03
mysql-proxy-slave-failover1      STOPPED    Jun 05 10:47 AM
mysql-proxy-slave-failover2      STOPPED    Jun 05 10:47 AM
mysql-proxy-slave-failover3      STOPPED    Jun 05 11:08 AM
mysql-proxy-slave-failover4      STOPPED    Jun 05 11:08 AM
mysql-proxy-slave1               RUNNING    pid 2528, uptime 0:00:02
mysql-proxy-slave2               STARTING
mysqlcheck                       RUNNING    pid 2504, uptime 0:00:05
</pre>

monitoring is performed by the script mysqlcheck = Python.

<pre>
mysql-proxy-master1              RUNNING    pid 2510, uptime 0:00:04
mysql-proxy-master2              RUNNING    pid 2519, uptime 0:00:03
</pre>
is usual Proxy for the master connection.

As a precaution, proxy will launch two lines. 

Reviewing the Log Monitoring

<pre>
tail /var/log/supervisord/mysqlcheck.log
20: master2 status check at Tue Jun  5 15:20:00 2012
ok
21: master1 status check at Tue Jun  5 15:20:05 2012
ok
21: master2 status check at Tue Jun  5 15:20:05 2012
ok
22: master1 status check at Tue Jun  5 15:20:10 2012
ok
22: master2 status check at Tue Jun  5 15:20:10 2012
ok
23: master1 status check at Tue Jun  5 15:20:15 2012
ok
23: master2 status check at Tue Jun  5 15:20:15 2012
ok
24: master1 status check at Tue Jun  5 15:20:20 2012
ok
24: master2 status check at Tue Jun  5 15:20:20 2012
ok
25: master1 status check at Tue Jun  5 15:20:25 2012
ok
25: master2 status check at Tue Jun  5 15:20:25 2012
ok
26: master1 status check at Tue Jun  5 15:20:30 2012
ok
26: master2 status check at Tue Jun  5 15:20:30 2012
ok
27: master1 status check at Tue Jun  5 15:20:35 2012
ok
27: master2 status check at Tue Jun  5 15:20:35 2012
ok
28: master1 status check at Tue Jun  5 15:20:40 2012
ok
28: master2 status check at Tue Jun  5 15:20:40 2012
</pre>

Check every 5 seconds of life and death is running.

## Failure Case of M1
M1 shut down intentionally.
<pre>
mysql1.server stop
</pre>
mysqlcheck.log
<pre>
63: master1 status check at Tue Jun  5 15:23:35 2012
master1 fail detected!
63: master2 status check at Tue Jun  5 15:23:35 2012
ok
64: master1 status check at Tue Jun  5 15:23:40 2012
master1 fail detected!
64: master2 status check at Tue Jun  5 15:23:40 2012
ok
65: master1 status check at Tue Jun  5 15:23:45 2012
master1 fail detected!
65: master2 status check at Tue Jun  5 15:23:45 2012
ok
66: master1 status check at Tue Jun  5 15:23:50 2012
master1 fail detected!
66: master2 status check at Tue Jun  5 15:23:50 2012
ok
67: master1 status check at Tue Jun  5 15:23:55 2012
master1 fail detected!
67: master2 status check at Tue Jun  5 15:23:55 2012
ok
68: master1 status check at Tue Jun  5 15:24:00 2012
master1 fail detected!
master1 failing: failover starting
failover1
</pre>
If you fail a check for five consecutive times life and death of M1, start the failover process.
<pre>
==> supervisord.log <==
2012-06-05 15:24:00,664 INFO stopped: mysql-proxy-master1 (exit status 0)
2012-06-05 15:24:01,897 INFO stopped: mysql-proxy-master2 (exit status 0)
2012-06-05 15:24:03,140 INFO stopped: mysql-proxy-slave1 (exit status 0)
2012-06-05 15:24:04,379 INFO stopped: mysql-proxy-slave2 (exit status 0)
2012-06-05 15:24:10,628 INFO spawned: 'mysql-proxy-master-failover1' with pid 2585
2012-06-05 15:24:11,633 INFO success: mysql-proxy-master-failover1 entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
2012-06-05 15:24:11,865 INFO spawned: 'mysql-proxy-master-failover2' with pid 2594
2012-06-05 15:24:12,870 INFO success: mysql-proxy-master-failover2 entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
2012-06-05 15:24:13,102 INFO spawned: 'mysql-proxy-slave-failover1' with pid 2603
2012-06-05 15:24:14,108 INFO success: mysql-proxy-slave-failover1 entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
2012-06-05 15:24:14,340 INFO spawned: 'mysql-proxy-slave-failover2' with pid 2612
2012-06-05 15:24:15,345 INFO success: mysql-proxy-slave-failover2 entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
</pre>
Mysql-proxy process four stops, mysql-proxy for the definition of when a failover starts, M2 and S2 only the DB request, skip. To read_only = off of M2.

<pre>
==> mysqlcheck.log 
failover finished! : master2 is new master
kill this daemon until master1 failback!
failover finished! : master2 is new master
stop this daemon until master1 failback!
</pre>

Completion of the failover process.
## Failure case of M2
M2 is shut down intentionally.
<pre>
mysql2.server stop
</pre>
mysqlcheck.log
<pre>
280: master2 status check at Tue Jun 5 15:54:33 2012
master2 fail detected!
281: master1 status check at Tue Jun 5 15:54:38 2012
ok
281: master2 status check at Tue Jun 5 15:54:38 2012
master2 fail detected!
282: master1 status check at Tue Jun 5 15:54:43 2012
ok
282: master2 status check at Tue Jun 5 15:54:43 2012
master2 fail detected!
283: master1 status check at Tue Jun 5 15:54:48 2012
ok
283: master2 status check at Tue Jun 5 15:54:48 2012
master2 fail detected!
284: master1 status check at Tue Jun 5 15:54:53 2012
ok
284: master2 status check at Tue Jun 5 15:54:53 2012
master2 fail detected!
285: master1 status check at Tue Jun 5 15:54:58 2012
ok
285: master2 status check at Tue Jun 5 15:54:58 2012
master2 fail detected!
master2 failing: failover starting
failover2
</pre>
If you fail a check for five consecutive times life and death of M2, start the failover process.
<pre>
==> Supervisord.log <==
2012-06-05 15:54:59,185 INFO stopped: mysql-proxy-slave1 (exit status 0)
2012-06-05 15:54:59,447 INFO stopped: mysql-proxy-slave2 (exit status 0)
2012-06-05 15:55:05,683 INFO spawned: 'mysql-proxy-slave-failover3' with pid 3016
2012-06-05 15:55:06,688 INFO success: mysql-proxy-slave-failover3 entered RUNNING state, process has stayed up for> than 1 seconds (startsecs)
2012-06-05 15:55:06,921 INFO spawned: 'mysql-proxy-slave-failover4' with pid 3025
2012-06-05 15:55:07,925 INFO success: mysql-proxy-slave-failover4 entered RUNNING state, process has stayed up for> than 1 seconds (startsecs)
</pre>
mysql-proxy process for the two slave is stopped, mysql-proxy for the definition of when a failover starts,
M1 and S1 only the DB request, skip.
<pre>
==> Mysqlcheck.log <==
failover finished:! master2/slave4 has been purged
kill this daemon until master2 failback!
failover finished:! master2/slave4 has been purged
kill this daemon until master2 failback!
</pre>
Completion of the failover process.



