from evdev import InputDevice, list_devices, categorize, ecodes
import logging

class DoorWatcher(object):
    def __init__(self):
        self.device = None
        self.setup_device()
        self.last_door_signal = None
        self.stopped = False


    def setup_device(self):
        for dev_str in list_devices():
            dev = InputDevice(dev_str)
            if "arduino" in dev.name.lower():
                self.device = dev
                break
        else:
            raise IOError("Unable to find Arduino input device")


    def _run(self, poller):
        for event in self.device.read_loop():
            if self.stopped:
                print "Exiting key read loop..."
                break

            if event.type == ecodes.EV_KEY:
                logging.debug(categorize(event))
                if event.code == ecodes.KEY_SPACE and event.value == 0: # value == 0 is up
                    self.last_door_signal = datetime.now()
                    

    def run(self, poller):
        try:
            return self._run(poller)
        finally:
            self.stopped = True