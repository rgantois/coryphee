from pynput import mouse
from pynput import keyboard
import time
import functools
import enum
import yaml

# Base action kinds
BaseAction = enum.Enum("BaseAction", [
"MOUSEUP",
"MOUSEDOWN",
"MOUSEMOVE",
"MOUSESCROLL",
"KEYPRESS",
"KEYRELEASE",
])

class Action():

	def __init__(self, kind: int, data: dict):
		self.timestamp = time.time()
		self.relative_time = None
		self.kind = kind
		self.data = data
		"""
		Actions that repeat if not released
		e.g. key down, mouse down
		"""
		self.repeats = False

	def __str__(self):
		return f"Action of kind {self.kind}\n"\
			+ f"timestamp: {self.timestamp}\n"\
			+ f"data: {yaml.dump(self.data)}"

	def record_start(rec):
		return

	def record_stop(rec):
		return

	def replay_start(rec):
		return

	def replay_stop(rec):
		return

	def save_state(rec):
		return

	def restore_state(rec):
		return

	def replay(self):
		# Replay a single action
		return

class KeyboardAction(Action):

	keyboard_rec = None
	keyboard_ctrl = None

	# Class methods

	def on_press(key, rec=None):
		# Keypress handler for recordings
		if key == keyboard.Key.esc:
			rec.signal_stop = True
		rec.push_action(KeyboardAction(BaseAction.KEYPRESS, {
			"key": key,
		}))

	def on_press_replay(key, rec=None):
		# Keypress handler for replays
		if key == keyboard.Key.esc:
			rec.signal_pause = True

	def on_release(key, rec=None):
		rec.push_action(KeyboardAction(BaseAction.KEYRELEASE, {
			"key": key,
		}))

	def record_start(rec):
		KeyboardAction.keyboard_rec = keyboard.Listener(
			on_press  =functools.partial(KeyboardAction.on_press,
				rec=rec),
			on_release=functools.partial(KeyboardAction.on_release,
				rec=rec)
		)
		KeyboardAction.keyboard_rec.start()
		return

	def record_stop(rec):
		if KeyboardAction.keyboard_rec is not None:
			KeyboardAction.keyboard_rec.stop()

	def replay_start(rec):
		KeyboardAction.keyboard_ctrl = keyboard.Controller()

		# Start keyboard listener so that emergency
		# stop signal can be received
		KeyboardAction.keyboard_rec = keyboard.Listener(
			on_press=functools.partial(KeyboardAction.on_press_replay,
				rec=rec),
			)

		KeyboardAction.keyboard_rec.start()

	# Instance methods

	def __init__(self, kind: int, data: dict):
		super(KeyboardAction, self).__init__(kind, data)
		self.repeats = kind == BaseAction.KEYPRESS

	def replay(self):
		kind = self.kind
		if kind == BaseAction.KEYPRESS:
			KeyboardAction.keyboard_ctrl.press(self.data["key"])
		else:
			KeyboardAction.keyboard_ctrl.release(self.data["key"])

class MouseAction(Action):

	mouse_ctrl = None
	mouse_rec = None
	position = None

	# Class methods

	def on_click(x, y, button, pressed, rec=None):
		kind = BaseAction.MOUSEDOWN if pressed else BaseAction.MOUSEUP
		rec.push_action(MouseAction(kind, {
			"x": x,
			"y": y,
			"button": button,
		}))

	def on_move(x, y, rec=None):
		kind = BaseAction.MOUSEMOVE
		rec.push_action(MouseAction(BaseAction.MOUSEMOVE, {
			"x": x,
			"y": y,
		}))

	def on_scroll(x, y, dx, dy, rec=None):
		self.push_action(MouseAction(BaseAction.MOUSESCROLL, {
			"x": x,
			"y": y,
			"dx": dx,
			"dy": dy,
		}))

	def record_start(rec):
		MouseAction.mouse_rec = mouse.Listener(
			on_click =functools.partial(MouseAction.on_click, rec=rec),
			on_move  =functools.partial(MouseAction.on_move, rec=rec),
			on_scroll=functools.partial(MouseAction.on_scroll, rec=rec)
		)
		MouseAction.mouse_rec.start()

	def record_stop(rec):
		if MouseAction.mouse_rec is not None:
			MouseAction.mouse_rec.stop()

	def replay_start(rec):
		MouseAction.mouse_ctrl = mouse.Controller()

	def save_state(rec):
		MouseAction.position = MouseAction.mouse_ctrl.position

	def restore_state(rec):
		MouseAction.mouse_ctrl.position = MouseAction.position

	# Instance methods

	def __init__(self, kind: int, data: dict):
		super(MouseAction, self).__init__(kind, data)
		self.repeats = kind == BaseAction.MOUSEDOWN

	def replay(self):
		x = self.data["x"]
		y = self.data["y"]
		kind = self.kind
		button = self.data.get("button", None)
		dx = self.data.get("dx", None)
		dy = self.data.get("dy", None)
		MouseAction.mouse_ctrl.position = (x, y)
		if kind == BaseAction.MOUSEDOWN:
			MouseAction.mouse_ctrl.press(button)
		elif kind == BaseAction.MOUSEUP:
			MouseAction.mouse_ctrl.release(button)
		elif kind == BaseAction.MOUSESCROLL:
			MouseAction.mouse_ctrl.scroll(dx, dy)

