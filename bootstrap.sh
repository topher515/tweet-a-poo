#!/bin/bash

# build virtual environment
virtualenv ve
source ve/bin/activate
pip install -r requirements.pip

sudo touch /var/log/supervisord.log
sudo chmod o+w /var/log/supervisord.log
sudo touch /var/log/monitor_and_tweet.log
sudo chmod o+w /var/log/monitor_and_tweet.log

# Setup supervisor
mkdir -p ve/etc
mkdir -p ve/run
printf "[unix_http_server]\n\
file=$(pwd)/ve/run/supervisor.sock\n\
\n\
[supervisord]\n\
logfile = /var/log/supervisord.log\n\
pidfile=$(pwd)/ve/run/supervisord.pid\n\
user=root\n\
\n\
[rpcinterface:supervisor]\n\
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface\n\
\n\
[supervisorctl]\n\
serverurl=unix://$(pwd)/ve/run/supervisor.sock\n\
\n\
[program:monitor_and_tweet]\n\
command=$(pwd)/monitor.py dry_run\n\
autostart=true\n\
autorestart=true\n\
startsecs=5\n\
startretries=3\n\
exitcodes=0,2\n\
stopsignal=TERM\n\
stopwaitsecs=5\n\
redirect_stderr=true\n\
stdout_logfile=/var/log/monitor_and_tweet.log\n\
environment=PYTHONPATH=$(pwd)" > ve/etc/supervisord.conf