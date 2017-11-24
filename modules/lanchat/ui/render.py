import curses
from curses import wrapper
import time
import math


class Render():
    def __init__(self, lanchat):
        self.stop = False
        self.lanchat = lanchat
        self.input = ''
        self.message_log = []  # message_log [{'user':'moku','msg':'hello'}]
        self.msg_count = 0  # Counts the number of messages rendered on screen
        self.curr_y = 0  # Counts the number of lines filled on screen

    def run(self):
        wrapper(self.main)

    def setup(self, stdscr):
        self.stdscr = stdscr
        # Clear screen
        stdscr.clear()
        # Declare terminal window size
        self.h, self.w = stdscr.getmaxyx()
        stdscr.nodelay(True)
        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)

    def stahp(self):
        self.stop = True

    ''' render the chatroom '''
    def render(self):
        # Get current window size
        h_new, w_new = self.stdscr.getmaxyx()
        # If the window has been resized
        if not (self.h == h_new and self.w == w_new):
            self.h, self.w = h_new, w_new  # Update window dimensions
            # Clear the current window
            self.stdscr.clear()
            # Restore message count and y so all messages gets rerendered
            self.msg_count = 0
            self.curr_y = 0
        # How many lines for each message
        line = []
        for msg in self.message_log:
            msg = msg['msg']
            if '\n' not in msg:
                line.append(math.ceil((len(msg) + 18) / self.w))
            else:
                msg = msg.split('\n')
                for i in msg:
                    line.append(math.ceil((len(i) + 18) / self.w))
        # Delete old messges to fit the new messages in
        lines_occupied = sum(line)
        while lines_occupied >= self.h - 2:  # Last 2 lines are for input
            self.curr_y = 0  # Need to re-render to get rid of old messages
            self.msg_count = 0
            lines_occupied -= line.pop(0)
            self.message_log.pop(0)
        # Render unrendered messages
        for i, msg in enumerate(self.message_log[self.msg_count:]):
            self.msg_count += 1
            for y in range(line[i]):  # Render each line
                ms = msg['msg'].split('\n')
                for i in ms:
                    self.curr_y += 1
                    m = i[y * (self.w - 18):(y + 1) * (self.w - 18)]
                    m = m.ljust(self.w - 18)
                    u = msg['user'].ljust(18) if i == ms[0] else ' ' * 18
                    if msg['mode']:
                        self.stdscr.addstr(self.curr_y, 0, u + m + '\n',
                                           msg['mode'])
                    else:
                        self.stdscr.addstr(self.curr_y, 0, u + m + '\n')
        # Render text input
        self.stdscr.addstr(self.h - 2, 0, ' ' * (self.w * 2 - 1))
        self.stdscr.addstr(self.h - 1, 0,
                           "Chat >>> {}".format(self.input))
        # Refresh window
        self.stdscr.refresh()

    def main(self, stdscr):
        self.setup(stdscr)
        # Start rendering chatroom
        while not self.stop:
            # Get user input
            c = stdscr.getch()
            self.input_change(c)
            # Render chat room
            self.render()
            time.sleep(0.02)

    def input_change(self, c):
        if c == 10:  # Enter
            if len(self.input) > 0:
                if self.input.startswith('/'):  # It's a command
                    self.lanchat.do_command(self.input)
                else:  # It's a message
                    self.add_message(self.lanchat.get_host().get_username(),
                                     self.input)
                    self.lanchat.send_message(self.input)
                self.input = ''
        elif c == 127 or c == 263:  # Backspace
            if len(self.input) > 0:
                self.input = self.input[:-1]
        else:
            if c not in range(0, 255):  # Non-printable characters
                return
            if len(self.input) >= self.w - 10:
                return
            self.input += chr(c)

    def add_message(self, username, message, mode=None):
        if mode == 'REVERSE':
            mode = curses.A_REVERSE
        self.message_log.append(
            {'user': username, 'msg': message, 'mode': mode}
        )
