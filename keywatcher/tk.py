from Tkinter import *

class DoorWatcher(object):
    def __init__(self):
        self.last_door_signal = None
        self.stopped = False

    def run(self, poller):
        root = Tk()
        self.last_door_signal = None

        def handle_die():
            self.stopped = True
            root.destroy()

        def key(event):
            if event.char == ' ':
                root.bell()
                self.last_door_signal = datetime.now()

        def callback(event):
            frame.focus_set()

        frame = Frame(root, width=100, height=100)
        frame.bind("<Key>", key)
        frame.bind("<Button-1>", callback)
        frame.pack()

        root.protocol('WM_DELETE_WINDOW', handle_die)
        root.mainloop()
