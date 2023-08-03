import time
import yaml
import pickle
import sys
import os

from coryphee.action import Action, MouseAction, KeyboardAction

CORYPHEE_DIR = os.path.expanduser("~/.local/share/coryphee")

class Recording():

    def __init__(self):
        self.actions = []
        self.action_types = [
            MouseAction,
            KeyboardAction,
        ]
        self.cur_action = 0
        self.signal_stop = False
        self.comment = ""
        self.date = ""
        self.last_timestamp = 0
        self.name = ""

    def cleanup(self):
        for action_type in self.action_types:
            action_type.record_stop(self)

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

    def record(self, duration: float):
        self.actions = []

        for action_type in self.action_types:
            action_type.record_start(self)

        if duration == 0:
            # If no duration is specified, the keyboard
            # listener will stop everything when ESC is detected
            while not self.signal_stop:
                time.sleep(0.2)
        else:
            time.sleep(duration)

        for action_type in self.action_types:
            action_type.record_stop(self)

    def save(self, name: str, comment: str):
        with open(f"{CORYPHEE_DIR}/{name}.pickle", "wb") as file:
            pickle.dump({"actions": self.actions, "comment": comment}, file)

    def load(self, name: str):
        self.name = name
        with open(f"{CORYPHEE_DIR}/{self.name}.pickle", "rb") as file:
           obj = pickle.load(file)
           self.actions = obj["actions"]
           self.comment = obj["comment"]
        self.date = self.get_date()

    def replay_all(self, replay_speed: float):
        for action_type in self.action_types:
            action_type.replay_start(self)

        for (index, action) in enumerate(self.actions):
            self.cur_action = index
            if self.signal_stop:
                for action_type in self.action_types:
                    action_type.replay_stop(self)
            time.sleep(action.relative_time / replay_speed)
            action.replay()

    def push_action(self, action: Action):
        if len(self.actions) == 0:
            action.relative_time = 0
        else:
            action.relative_time = action.timestamp - self.last_timestamp
        self.last_timestamp = action.timestamp
        self.actions.append(action)

