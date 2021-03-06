from evdev import InputDevice, list_devices, categorize, ecodes
import logging
from datetime import datetime
import time

class DoorWatcher(object):
    def __init__(self):
        self.device = None
        self.wait_for_device = True
        self.setup_device()
        self.last_door_signal = None
        self.stopped = False

    def setup_device(self):
        while not self.device:
            for dev_str in list_devices():
                dev = InputDevice(dev_str)
                if "arduino" in dev.name.lower():
                    self.device = dev
                    break
            else:
                if self.wait_for_device:
                    logging.warning("Waiting for arduino device...")
                    time.sleep(1)
                else:
                    raise IOError("Unable to find Arduino input device")


    def _run(self, poller):
        for event in self.device.read_loop():
            if self.stopped:
                print "Exiting key read loop..."
                break

            if event.type == ecodes.EV_KEY:
                logging.debug(categorize(event))
                if event.code == ecodes.KEY_SPACE:
                    if event.value in (0, 2): # 0 is up 2 is hold
                        self.last_door_signal = datetime.now()


    def run(self, poller):
        try:
            return self._run(poller)
        finally:
            self.stopped = True