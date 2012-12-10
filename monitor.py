import sys
import select
import termios, fcntl, sys, os
from twitter import Twitter, OAuth
import yaml
import random
import requests
from datetime import datetime, timedelta
import threading
import time

from secrets import CONSUMER_KEY, CONSUMER_SECRET

# see "Authentication" section below for tokens and keys


DOOR_CLOSED = 0
DOOR_OPEN = 1


def main():
    SystemController().watch()


class SystemController(object):
    def __init__(self):
        self.doorwatcher = DoorWatcher()
        self.door_state = None
        #self.tweeter = Tweeter()

    def handle_door_closing(self):
        print "Door closing..."
        #self.tweeter.tweet_enter()

    def handle_door_opening(self):
        print "Door opening..."
        #self.tweeter.tweet_exit()

    def handle_door_is_open(self):
        print "Door is open."
        if self.door_state == DOOR_CLOSED:
            self.handle_door_opening()
        self.door_state = DOOR_OPEN

    def handle_door_is_closed(self):
        print "Door is closed."
        if self.door_state == DOOR_OPEN:
            self.handle_door_closing()
        self.door_state = DOOR_CLOSED

    def sleep(self):
        time.sleep(0.25)

    def watch(self):
        self.doorwatcher.start() # Start watching
        while True:
            self.sleep()
            if not self.doorwatcher.last_door_signal:
                continue
            if datetime.now() - self.doorwatcher.last_door_signal > timedelta(seconds=1):
                self.handle_door_is_open()
            else:
                self.handle_door_is_closed()



class DoorWatcher(threading.Thread):
    def __init__(self,*args,**kwargs):
        self.keywatcher = KeyPressReader()
        self.last_door_signal = None
        super(DoorWatcher,self).__init__(*args,**kwargs)

    def run(self):
        while True:
            key = self.keywatcher.read_single_keypress()
            if key == 'q':
                break
            elif key == ' ':
                self.last_door_signal = datetime.now()


class Tweeter(object):
    def __init__(self):
        self.enter_library = None
        self.exit_library = None
        self.twitter = Twitter(auth=OAuth(OAUTH_TOKEN, 
                        OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
        self.load_tweet_library()

    def load_tweet_library(self):
        # TODO: Pull from http://raw.github.com/topher515/tweet-a-poo/master/tweets/enter.yml
        with open('tweets/enter.yml','r') as enter_fp:
            self.enter_library = yaml.load(enter_fp.read())
        with open('tweets/exit.yml','r') as exit_fp:
            self.exit_library = yaml.load(exit_fp.read())

    def _tweet(self, msg):
        self.twitter.statuses.update(status=msg)


    def tweet_enter(self):
        return self._tweet(random.choice(self.enter_library))

    def tweet_exit(self):
        return self._tweet(random.choice(self.exit_library))



class KeyPressReader(object):

    def __init__(self):
        self.attrs_save = None
        self.flags_save = None
        self.fd = None

    def __enter__(self):
        self.fd = sys.stdin.fileno()
        # save old state
        self.flags_save = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        self.attrs_save = termios.tcgetattr(self.fd)
        # make raw - the way to do this comes from the termios(3) man page.
        attrs = list(self.attrs_save) # copy the stored version to update
        # iflag
        attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK 
                      | termios.ISTRIP | termios.INLCR | termios. IGNCR 
                      | termios.ICRNL | termios.IXON )
        # oflag
        attrs[1] &= ~termios.OPOST
        # cflag
        attrs[2] &= ~(termios.CSIZE | termios. PARENB)
        attrs[2] |= termios.CS8
        # lflag
        attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                      | termios.ISIG | termios.IEXTEN)
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
        # turn off non-blocking
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.flags_save & ~os.O_NONBLOCK)
        return self

    def __exit__(self, type, value, tb):
        # restore old state
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.attrs_save)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.flags_save)

    def read_single_keypress(self):
        try:
            ret = sys.stdin.read(1) # returns a single character
        except KeyboardInterrupt: 
            ret = 0
            raise
        return ret



if __name__ == '__main__':
    main()