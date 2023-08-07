import time
import pickle
import sys
import os

from coryphee.action import Action, MouseAction, KeyboardAction
from coryphee.pause_menu import PauseMenu

CORYPHEE_DIR = os.path.expanduser("~/.local/share/coryphee")

class Recording():

	def __init__(self):
		self.actions = []
		self.action_types = [
			MouseAction,
			KeyboardAction,
		]
		self.cur_action = 0
		self.signal_pause = False
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
			while not self.signal_pause and not self.signal_stop:
				time.sleep(0.2)
		else:
			time.sleep(duration)

		for action_type in self.action_types:
			action_type.record_stop(self)

	def warn_repeats(self):
		if self.actions != [] and self.actions[-1].repeats:
			print("Warning: recording ends with an unreleased repeating action (e.g. a keypress)")
			print("This means that the last action could loop when replayed")

	def save(self, name: str, comment: str):
		self.warn_repeats()
		with open(f"{CORYPHEE_DIR}/{name}.pickle", "wb") as file:
			pickle.dump({"actions": self.actions, "comment": comment}, file)

	def load(self, name: str):
		self.name = name
		with open(f"{CORYPHEE_DIR}/{self.name}.pickle", "rb") as file:
		   obj = pickle.load(file)
		   self.actions = obj["actions"]
		   self.comment = obj["comment"]
		self.date = self.get_date()

	def cut_recording(self):
		if self.actions == []:
			return
		cropped = self.actions[0:self.cur_action]
		self.actions = cropped
		self.save(self.name, self.comment)

	def handle_commands(self, commands: list) -> str:
		feedback = ""
		for (cmd, args) in commands:
			if cmd == "stop":
				self.signal_stop = True
				break
			elif cmd == "cut":
				self.cut_recording()
				self.signal_stop = True
				feedback += "Recording cut"
		return feedback

	def pause(self):
		for action_type in self.action_types:
			action_type.save_state(self)

		self.pause_menu = PauseMenu()
		#process user commands
		self.handle_commands(self.pause_menu.commands)

		if self.signal_stop:
			return

		for action_type in self.action_types:
			action_type.restore_state(self)

	def replay_all(self, replay_speed: float):
		for action_type in self.action_types:
			action_type.replay_start(self)

		for (index, action) in enumerate(self.actions):
			self.cur_action = index
			if self.signal_pause:
				self.pause()
				self.signal_pause = False
			if self.signal_stop:
				for action_type in self.action_types:
					action_type.replay_stop(self)
				return
			time.sleep(action.relative_time / replay_speed)
			action.replay()

	def push_action(self, action: Action):
		if len(self.actions) == 0:
			action.relative_time = 0
		else:
			action.relative_time = action.timestamp - self.last_timestamp
		self.last_timestamp = action.timestamp
		self.actions.append(action)

