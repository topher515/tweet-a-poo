from evdev import InputDevice, list_devices, categorize, ecodes


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



    def run(self, poller):
        for event in self.dev.read_loop():
            if self.stopped:
                print "Exiting key read loop..."
                break

            if event.type == ecodes.EV_KEY:
                logging.debug(categorize(event))
                logging.debug(dir(event))