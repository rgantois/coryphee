from pynput import mouse
from pynput import keyboard
import time
import yaml
import pickle
import sys
import os

CORYPHEE_DIR = os.path.expanduser("~/.local/share/coryphee")

class Action():

    MOUSEUP = 0
    MOUSEDOWN = 1
    MOUSEMOVE = 2
    MOUSESCROLL = 3
    KEYPRESS = 4
    KEYRELEASE = 5

    def __init__(self, kind: int, data: dict):
        self.timestamp = time.time()
        self.kind = kind
        self.data = data

    def __str__(self):
        return f"Action of kind {self.kind}\n"\
            + f"timestamp: {self.timestamp}\n"\
            + f"data: {yaml.dump(self.data)}"

    def replay(self, mouse, kbd):
        kind = self.kind
        if kind in [Action.MOUSEUP, Action.MOUSEDOWN, 
                Action.MOUSEMOVE, Action.MOUSESCROLL]:
            self.replay_mouse(mouse)
        elif kind in [Action.KEYPRESS, Action.KEYRELEASE]:
            self.replay_keyboard(kbd)

    def replay_mouse(self, mouse):
        x = self.data["x"]
        y = self.data["y"]
        kind = self.kind
        button = self.data.get("button", None)
        dx = self.data.get("dx", None)
        dy = self.data.get("dy", None)
        mouse.position = (x, y)
        if kind == Action.MOUSEDOWN:
            mouse.press(button)
        elif kind == Action.MOUSEUP:
            mouse.release(button)
        elif kind == Action.MOUSESCROLL:
            mouse.scroll(dx, dy)

    def replay_keyboard(self, kbd):
        kind = self.kind
        if kind == Action.KEYPRESS:
            kbd.press(self.data["key"])
        else:
            kbd.release(self.data["key"])



class Recording():

    # mouse events ############################

    def on_click(self, x, y, button, pressed):
        kind = Action.MOUSEDOWN if pressed else Action.MOUSEUP
        self.push_action(Action(kind, {
            "x": x,
            "y": y,
            "button": button,
        }))

    def on_move(self, x, y):
        kind = Action.MOUSEMOVE
        self.push_action(Action(Action.MOUSEMOVE, {
            "x": x,
            "y": y,
        }))

    def on_scroll(self, x, y, dx, dy):
        self.push_action(Action(Action.MOUSESCROLL, {
            "x": x,
            "y": y,
            "dx": dx,
            "dy": dy,
        }))

    # keyboard events ##########################

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.stop()
        self.push_action(Action(Action.KEYPRESS, {
            "key": key,
        }))

    def on_release(self, key):
        self.push_action(Action(Action.KEYRELEASE, {
            "key": key,
        }))

    # recording  ##############################

    def __init__(self):
        self.actions = []
        self.mouse = None
        self.kbd = None
        self.mouse_rec = None
        self.keyboard_rec = None
        self.signal_stop = False
        self.comment = ""
        self.date = ""
        self.last_timestamp = 0

    def get_date(self) -> str:
        if len(self.actions) == 0:
            return "[empty]"

        timestamp = self.actions[0].timestamp
        date = time.strftime("%Y-%m-%d %H:%M:%S",
                time.localtime(timestamp))
        return date

    def dump(self):
        print("Recorded actions:")
        for action in self.actions:
            print(action)

    def stop(self):
        self.signal_stop = True
        if self.keyboard_rec is not None:
            self.keyboard_rec.stop()
        if self.mouse_rec is not None:
            self.mouse_rec.stop()

    def record(self, duration: float):
        self.actions = []

        self.mouse_rec = mouse.Listener(
                on_click=self.on_click,
                on_move=self.on_move,
                on_scroll=self.on_scroll)
        self.keyboard_rec = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release)

        self.mouse_rec.start()
        self.keyboard_rec.start()

        if duration == 0:
            # If no duration is specified, the keyboard
            # listener will stop everything when ESC is detected
            while not self.signal_stop:
                time.sleep(0.2)
        else:
            time.sleep(duration)

        self.stop()

    def save(self, name: str, comment: str):
        with open(f"{CORYPHEE_DIR}/{name}.pickle", "wb") as file:
            pickle.dump({"actions": self.actions, "comment": comment}, file)

    def load(self, name: str):
        with open(f"{CORYPHEE_DIR}/{name}.pickle", "rb") as file:
           obj = pickle.load(file)
           self.actions = obj["actions"]
           self.comment = obj["comment"]
        self.date = self.get_date()

    def replay_all(self, replay_speed: float):
        self.mouse = mouse.Controller()
        self.kbd = keyboard.Controller()

        # Start keyboard listener so that emergency 
        # stop signal can be received
        self.keyboard_rec = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release)
        self.keyboard_rec.start()

        for action in self.actions:
            if self.signal_stop:
                print("Replay stopped")
                break
            time.sleep(action.relative_time / replay_speed)
            action.replay(self.mouse, self.kbd)

    def push_action(self, action: Action):
        if len(self.actions) == 0:
            action.relative_time = 0
        else:
            action.relative_time = action.timestamp - self.last_timestamp
        self.last_timestamp = action.timestamp
        self.actions.append(action)


