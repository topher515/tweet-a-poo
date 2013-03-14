#!/bin/bash

# build virtual environment
virtualenv ve
source ve/bin/activate
pip install -r requirements.pip

# Setup supervisor
mkdir -p ve/etc
printf "[program:monitor_and_tweet]\n\
command=$(pwd)monitor.py\n\
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