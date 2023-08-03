import signal
import argparse
import os
import sys
import functools
from coryphee.recording import Recording, Action, CORYPHEE_DIR

def cleanup(sig, frame, rec=None):
    if rec is not None:
        rec.cleanup()
    print("Cleaned up action recorders")
    sys.exit(0)

def cli():

    parser = argparse.ArgumentParser(prog="Coryphee",
            description="Record and replay UI mouse and keyboard actions",
            epilog="WARNING:This program can cause serious trouble if you do not use it carefully!!!")

    parser.add_argument("command", choices = ["rec", "replay", "dump", "list", "del"])
    parser.add_argument("name", nargs="?", help="name of the target action sequence, required all commands except 'list'")
    parser.add_argument("-d", "--duration", default=0,
            help="stop recording after [duration] seconds instead of waiting for ESC (float allowed)")
    parser.add_argument("-s", "--speed", default=1.0,
            help="replay speed, strange things could happen if you set this too high")
    parser.add_argument("-c", "--comment", default="",
            help="add a comment to the recording")

    args = parser.parse_args()

    rec = Recording()

    """
    Trap SIGINT so we don't quit without 
    shutting down the event recorders
    """
    signal.signal(signal.SIGINT,
            functools.partial(cleanup, rec=rec))
    signal.signal(signal.SIGTERM,
            functools.partial(cleanup, rec=rec))

    cmd = args.command
    if cmd == "list":
        print(f"Recordings stored in {CORYPHEE_DIR}:\n")
        for path in os.listdir(CORYPHEE_DIR):
            name = os.path.splitext(path)[0]
            rec.load(name)
            print(f"name: {name}\non: {rec.date}\ncomment: {rec.comment}\n")
        sys.exit(0)

    if not args.name:
        print("Missing command line parameter 'name'")
    name = args.name

    if cmd == "rec":
        rec.record(float(args.duration))
        rec.save(args.name, args.comment)
    elif cmd == "replay":
        rec.load(args.name)
        rec.replay_all(float(args.speed))
    elif cmd == "dump":
        rec.load(args.name)
        rec.dump()
    elif cmd == "del":
        path = f"{CORYPHEE_DIR}/{args.name}.pickle"
        if os.path.exists(path):
            os.remove(path)
        else:
            print(f"File {path} not found")
            sys.exit(-1)


