import curses
from curses import wrapper
import time
import math
import os


class Render():
    """ Linux/MacOS Terminal renderer """
    def __init__(self, lanchat):
        """ Constructor

        Keyword arguments:
        lanchat -- a LANChat object
        """
        self.stop = False
        self.lanchat = lanchat
        self.input = ''
        self.message_log = []  # message_log [{'user':'moku','msg':'hello'}...]
        self.msg_count = 0  # Counts the number of messages rendered on screen
        self.curr_y = 0  # Counts the number of lines filled on screen
        self.max_input = 900 # Maximum input size

    def run(self):
        """ Start rendering """
        # Clear screen avoid glitchy display to do with scrolls
        # Warning: Not sustainable, will use pads in future
        for _ in range(3):
            os.system('clear')
        wrapper(self.main)

    def stahp(self):
        """ Stop the renderer """
        self.stop = True

    ''' Sub functions '''
    def calc_lines(self):
        """ Calculate how many lines for each message """
        line = []
        for msg in self.message_log:
            msg = msg['msg']
            if '\n' not in msg:
                line.append(math.ceil((len(msg) + 18) / self.w))
            else:
                msg = msg.split('\n')
                total = 0
                for i in msg:
                    total += math.ceil((len(i) + 18) / self.w)
                line.append(total)
        return line

    def del_old_msg(self, line):
        """ Delete old messages to fit new messages in

        Keyword arguments:
        line -- a list of numbers representing the number of lines needed
                for each message
        """
        if not isinstance(line, list):
            raise ValueError
        lines_occupied = sum(line)
        while lines_occupied >= self.h - 2:  # Last 2 lines are for input
            self.curr_y = 0  # Need to re-render to get rid of old messages
            self.msg_count = 0
            lines_occupied -= line.pop(0)
            self.message_log.pop(0)

    def render_message(self, username, message, mode=None):
        """ Render one message on screen

        Keyword arguments:
        username -- who sent the message
        message -- the message
        """
        lines = message.split('\n')
        for ln in lines:
            bp = 0
            m = ln[bp * (self.w - 18):(bp + 1) * (self.w - 18)]
            while m:
                m = m.ljust(self.w - 18)
                u = ' ' * 18
                if bp == 0 and ln == lines[0]:
                    u = username.ljust(18)
                if mode:
                    self.stdscr.addstr(self.curr_y, 0, u + m + '\n',
                                       mode)
                else:
                    self.stdscr.addstr(self.curr_y, 0, u + m + '\n')
                self.curr_y += 1
                bp += 1
                m = ln[bp * (self.w - 18):(bp + 1) * (self.w - 18)]

    def render_input(self):
        """ Render the input field """
        prompt = "Chat >>> "
        message = self.input
        if len(message) + len(prompt) > self.w:
            message = message[len(message) + len(prompt) + 4 - self.w:]
            message = '...' + message
        self.stdscr.hline(self.h - 1, 0, ord(' '), self.w)
        self.stdscr.addstr(self.h - 1, 0, prompt + message)
        # Move cursor to the end of input

    def render(self):
        """ Renders the entire screen """
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
        # Calculate how many lines for each message
        line = self.calc_lines()
        # Delete old messges to fit the new messages in
        self.del_old_msg(line)
        # Render unrendered messages
        for i, msg in enumerate(self.message_log[self.msg_count:]):
            self.msg_count += 1
            try:
                self.render_message(msg['user'], msg['msg'], mode=msg['mode'])
            except curses.error:
                return
        # Clear screen after the last message
        for offset in range(self.h - self.curr_y - 1):
            try:
                self.stdscr.hline(self.curr_y + offset, 0, ord(' '), self.w)
            except curses.error:
                return
        # Render text input
        try:
            self.render_input()
        except curses.error:
            return
        # Refresh window
        self.stdscr.refresh()

    def main(self, stdscr):
        """ The main program

        Keyword arguments:
        stdscr -- main screen
        """
        # Initialize window properties
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

        # Start rendering chatroom
        while not self.stop:
            # Get user input
            c = stdscr.getch()
            self.input_change(c)
            # Render chat room
            self.render()
            time.sleep(0.02)

    def input_change(self, c):
        """ Handler for change of input

        Keyword arguments:
        c -- a single character
        """
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
            if c not in range(0, 127):  # Non-printable characters
                return
            if len(self.input) >= self.max_input:
                return
            self.input += chr(c)

    def add_message(self, username, message, mode=None):
        """ Add a message into the message queue to get rendered

        Keyword arguments:
        username -- username of whom the message is sent from
        message -- the message
        mode -- mode of the message, could be 'REVERSE'. (optional)
        """
        if mode == 'REVERSE':
            mode = curses.A_REVERSE
        self.message_log.append(
            {'user': username, 'msg': message, 'mode': mode}
        )
