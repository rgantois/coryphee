# Coryphee
Record and replay mouse and keyboard actions

**WARNING: This program can behave unpredictably and cause mayhem if used improperly. Run it at your own risk.**

If you decide to use coryphee, here are a few pieces of advice:

- Only replay a recording if you remember what actions it contains. To help with this, you can use the `-c` option when recording to store a comment. e.g. "This recording opens and configures a bunch of terminal tabs. Terminal emulator is open and fullscreen."
- If you want to stop a replay while it is happening, hit the escape key a bunch of times.
- Do not enter any sensitive information while recording. e.g. **Do not type passwords.** They will be stored in cleartext in the recording!

## Installation

```bash
mkdir ~/.local/share/coryphee
python3 -m pip install build
cd coryphee
python3 -m build
python3 -m pip install dist/coryphee-*.whl
```

## Usage

### Help:

```bash
coryphee -h
```

### Record:

```bash
coryphee rec test -d 10 -c "A test recording, no windows are open"
```

This will record all of your mouse/keyboard actions during 10 seconds.

You can also omit the `-d` argument and just hit the escape key when you want to stop the recording.

### List recordings:

```bash
coryphee list
```

### Replay a recording:

```bash
coryphee replay test
```

This will replay the actions stored in the recording named `test`.

Hit the escape key to stop an ongoing replay.

### Delete a recording:

```bash
coryphee del test
```

## LICENSE

This is licensed under GPLv3. To be honest, I would've prefered GPLv2 but the main imported module is LGPLv3. Oh well.

