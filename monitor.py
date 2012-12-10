import sys
import select
import termios, fcntl, sys, os
from twitter import Twitter, OAuth
import yaml
import random

from secrets import CONSUMER_KEY, CONSUMER_SECRET

# see "Authentication" section below for tokens and keys



def main():
    with KeyPressReader() as k:
        while True:
            key = k.read_single_keypress()
            if key == 'q':
                break
            else:
                print key


class Tweeter(object):
    def __init__(self):
        self.enter_library = None
        self.exit_library = None
        self.twitter = Twitter(auth=OAuth(OAUTH_TOKEN, 
                        OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
        self.load_tweet_library()

    def load_tweet_library(self):
        with open('enter.yml','r') as enter_fp:
            self.enter_library = yaml.load(enter_fp.read())
        with open('exit.yml','r') as exit_fp:
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


def read_single_keypress():
    """Waits for a single keypress on stdin.

    This is a silly function to call if you need to do it a lot because it has
    to store stdin's current setup, setup stdin for reading single keystrokes
    then read the single keystroke then revert stdin back after reading the
    keystroke.

    Returns the character of the key that was pressed (zero on
    KeyboardInterrupt which can happen when a signal gets handled)

    """
    import termios, fcntl, sys, os
    fd = sys.stdin.fileno()
    # save old state
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)
    # make raw - the way to do this comes from the termios(3) man page.
    attrs = list(attrs_save) # copy the stored version to update
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
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    # turn off non-blocking
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
    # read a single keystroke
    try:
        ret = sys.stdin.read(1) # returns a single character
    except KeyboardInterrupt: 
        ret = 0
    finally:
        # restore old state
        termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
    return ret

if __name__ == '__main__':
    main()