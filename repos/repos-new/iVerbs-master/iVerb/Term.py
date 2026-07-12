import copy
import curses.ascii as keycode
import os, sys, tty, termios
import select as watcher

from colorclass import Color


class GetKey:
    @classmethod
    def await_tap(cls):
        fd = sys.stdin.fileno()
        cur_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = ""
            block = None
            while True:
                fd_sets = watcher.select([sys.stdin.fileno()], [], [], block)
                if len(fd_sets[0]) > 0:
                    ch_chunk = os.read(sys.stdin.fileno(), 1)
                    ch += ch_chunk.decode("utf-8")
                    block = 0
                else:
                    break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, cur_settings)
        return ch


class GetLine:
    @classmethod
    def await_for_enter(cls, tap_action=None):
        right_position = 0
        term_line = ""
        while True:
            tap_key = GetKey.await_tap()

            if tap_action and tap_action.get(tap_key, None):
                action = tap_action.get(tap_key)
                if action.get("action", None):
                    dargs = {"key": tap_key, "line": term_line}
                    action.get("action")(dargs)
                if action.get("break"):
                    if callable(action.get("break")):
                        dargs = {"key": tap_key, "line": term_line}
                        action.get("break")(dargs)
                        if dargs.get("ret", 0) == 1:
                            break
                    elif action.get("break") == 1: 
                        break
                elif action.get("continue"):
                    if callable(action.get("continue")):
                        dargs = {"key": tap_key, "line": term_line}
                        # use dargs.setdefault("ret", 1)
                        action.get("continue")(dargs)
                        if dargs.get("ret", 0) == 1:
                            continue
                    elif action.get("continue") == 1:
                        continue

            if not tap_key.isprintable():
                if tap_key == "\x1b[D":
                    # left arrow
                    if right_position < len(term_line):
                        right_position += 1
                        print("\b", end="", flush=True)
                        continue
                elif tap_key == "\x1b[C":
                    # right arrow
                    if right_position > 0:
                        print(term_line[(len(term_line) - right_position):(len(term_line) - right_position + 1)], end="", flush=True)
                        right_position -= 1
                        continue
                
                tap_code = ord(tap_key[:1])
                if tap_code in [keycode.BS, keycode.DEL]:
                    if len(term_line) > 0:
                        print("\b" + term_line[len(term_line) - right_position:] + " " + "\b" * (len(term_line[len(term_line) - right_position:]) + 1), end="", flush=True)
                        term_line = term_line[0:len(term_line) - right_position - 1] + term_line[len(term_line) - right_position:]
                elif tap_code == keycode.CR:
                    if right_position > 0:
                        print_key = term_line[(len(term_line) - right_position):len(term_line)]
                        print(print_key, end="", flush=True)
                    term_line += tap_key
                    break
                elif tap_code in [keycode.ETX, keycode.EOT, keycode.SUB]:  # Ctrl+ C,D,Z
                    sys.exit()
                elif tap_code == keycode.ESC and len(tap_key) == 1:  # ESC
                    sys.exit()
            else:
                if right_position == 0:
                    print(tap_key, end="", flush=True)
                    term_line += tap_key 
                else:
                    print_key = tap_key + term_line[(len(term_line) - right_position):len(term_line)]
                    print(print_key + "\b" * right_position, end="", flush=True)
                    term_line = term_line[0:(len(term_line) - right_position)] + tap_key + term_line[(len(term_line) - right_position):len(term_line)]

        return term_line


class HorizontalOptions:
    def __init__(self, options, sep="    "):
        self._options = options
        self._sep = sep

    def choice(self):
        ind = None
        while True:
            if ind is None:
                ind = 0
            else:
                sys.stdout.write("\033[F\n\033[K")
            options = copy.deepcopy(self._options)
            real_ind = ind % len(options)
            options[real_ind] = Color("{autobgwhite}" + options[real_ind] + "{/bgwhite}")
            print(self._sep.join(options), end="", flush=True)

            tap_key = GetKey.await_tap()
            if tap_key == "\x1b[D":
                # left arrow
                ind = len(options) - 1 if ind - 1 < 0 else ind - 1
                continue
            elif tap_key == "\x1b[C":
                # right arrow
                ind = ind + 1 if ind + 1 < len(options) else 0
                continue
            elif ord(tap_key[:1]) in [keycode.CR, ord(" ")]:
                sys.stdout.write("\n")
                return (ind % len(options))
            else:
                continue


if __name__ == "__main__":
    choices = ["foo", "bar", "baz"]
    opt = HorizontalOptions(choices)
    print("Your choice is: " + choices[opt.choice()])
    # GetLine.await_for_enter()
