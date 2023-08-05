import PySimpleGUI as sg

class PauseMenu():

	def __init__(self):

		self.stop = False
		self.commands = []

		# Must not reuse layout
		self.feedback = sg.Text('', visible=False, size=100)
		self.layout = [
		[sg.Text("Coryphee replay paused")],
		[sg.Radio("Stop replay", "RADIO_COMMAND", key="action_stop",
			default=True)],
		[sg.Radio("Cut recording here", "RADIO_COMMAND", key="action_cut")],
		[sg.Button("Apply"), sg.Button("Done")],
		[self.feedback],
		]

		self.window = sg.Window("Coryphee", self.layout)

		#event loop
		while True:
			event, values = self.window.read()
			if event == sg.WIN_CLOSED or event == "Done":
				self.window.close()
				break
			elif event == "Apply":
				self.push_command(values)
				if self.stop:
					self.window.close()
					break
				self.feedback.update({"visible": True})
				self.feedback.update("feedback")

	def push_command(self, values: dict):
		args = []
		if values["action_stop"]:
			cmd = "stop"
			self.stop = True
		if values["action_cut"]:
			cmd = "cut"
		self.commands.append((cmd, args))


