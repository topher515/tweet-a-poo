#!/usr/bin/env python

import sys
import termios, fcntl, sys, os
from twitter import Twitter, OAuth, oauth_dance, read_token_file
import yaml
import random
from datetime import datetime, timedelta
import threading
import time
import logging
#logging.basicConfig(filename=os.path.expanduser("~/tweet-a-poo.log"), filemode='a', level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

from secrets import CONSUMER_KEY, CONSUMER_SECRET, OAUTH_TOKEN, OAUTH_SECRET


DOOR_CLOSED = 0
DOOR_OPEN = 1


def main(platform="linux", dry_run=False):

    if platform == "linux":
        from keywatcher.devinput import DoorWatcher
    elif platform == "darwin":
        from keywatcher.tk import DoorWatcher
    
    cont = SystemController(DoorWatcherClass=DoorWatcher)
    cont.tweeter.dry_run = dry_run
    cont.watch()


class SystemController(object):
    def __init__(self, DoorWatcherClass):
        self.doorwatcher = DoorWatcherClass()
        self.door_state = None
        self.tweeter = Tweeter()

    def handle_door_closing(self):
        logging.info("Door closing...")
        self.tweeter.tweet_enter()

    def handle_door_opening(self):
        logging.info("Door opening...")
        self.tweeter.tweet_exit()

    def handle_door_is_open(self):
        #logging.info("Door is open.")
        if self.door_state == DOOR_CLOSED:
            self.handle_door_opening()
        self.door_state = DOOR_OPEN

    def handle_door_is_closed(self):
        #logging.info("Door is closed.")
        if self.door_state == DOOR_OPEN:
            self.handle_door_closing()
        self.door_state = DOOR_CLOSED

    def sleep(self):
        time.sleep(0.25)

    def watch(self):
        logging.info("Watching door...")

        def poll():
            while True:
                if self.doorwatcher.stopped:
                    break
                self.sleep()
                if not self.doorwatcher.last_door_signal:
                    continue
                if datetime.now() - self.doorwatcher.last_door_signal > timedelta(seconds=1):
                    self.handle_door_is_open()
                else:
                    self.handle_door_is_closed()

        poller = threading.Thread(target=poll)
        poller.start()

        self.doorwatcher.run(self)




def do_auth():
    MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
    print read_token_file(MY_TWITTER_CREDS)

    # if not os.path.exists(MY_TWITTER_CREDS):
    #     oauth_dance("My App Name", CONSUMER_KEY, CONSUMER_SECRET,
    #                 MY_TWITTER_CREDS)

    # twitter = Twitter(auth=OAuth(
    #     oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET))

    # # Now work with Twitter
    # twitter.statuses.update('Hello, world!')


class Tweeter(object):
    def __init__(self,async=True):
        self.async = async
        self.enter_library = None
        self.exit_library = None
        self.twitter = Twitter(auth=self.get_oauth())
        self.load_tweet_library()

        self.last_enter_tweet_hash = None
        self.last_exit_tweet_hash = None

        self.dry_run = False

    def get_oauth(self):
        MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
        if not os.path.exists(MY_TWITTER_CREDS):
            oauth_dance("WarehouseShower", CONSUMER_KEY, CONSUMER_SECRET,
                        MY_TWITTER_CREDS)

        oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)

        return OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET)

    def load_tweet_library(self):
        logging.debug("Loading tweet files")
        # TODO: Pull from http://raw.github.com/topher515/tweet-a-poo/master/tweets/enter.yml
        with open('tweets/enter.yml','r') as enter_fp:
            self.enter_library = yaml.load(enter_fp.read())
        with open('tweets/exit.yml','r') as exit_fp:
            self.exit_library = yaml.load(exit_fp.read())

    def _tweet(self, msg):

        def do_tweet():
            logging.info("Sending tweet%s: '%s'", " (not really)" if self.dry_run else "", msg)
            if not self.dry_run:
                self.twitter.statuses.update(status=msg)

        if self.async:
            threading.Thread(target=do_tweet).start()
        else:
            return do_tweet()


    def _select_tweet(self, name):
        tweet = random.choice(getattr(self,"%s_library" % name))
        while hash(tweet) == getattr(self,"last_%s_tweet_hash" % name):
            random.choice(getattr(self,"%s_library" % name))
        setattr(self,"last_%s_tweet_hash" % name, hash(tweet))
        return tweet

    def tweet_enter(self):
        return self._tweet(self._select_tweet("enter"))

    def tweet_exit(self):
        return self._tweet(self._select_tweet("exit"))


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0:
        main()
    else:
        if args[0] == "dry_run":
            main(dry_run=True)
        else:
            print "I dont understand %s" % args[0]