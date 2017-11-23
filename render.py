import curses
from curses import wrapper
import curses.textpad as textpad
import time
import math
import threading

class Render():
    def __init__(self, lanchat_api):
        self.stop = False
        self.input = ''
        self.message_log = [] # message_log [{'user':'moku','msg':'hello'}]
        self.msg_count = 0 # Counts the number of messages rendered on screen
        self.curr_y = 0 # Counts the number of lines filled on screen
        self.lanchat_api = lanchat_api


    def run(self):
        wrapper(self.main)

    '''
        render the chatroom
    '''
    def render(self):
        # Get current window size
        h_new, w_new = self.stdscr.getmaxyx()
        # If the window has been resized
        if not (self.h == h_new and self.w == w_new):
            self.h, self.w = h_new, w_new # Update window dimensions
            # Clear the current window
            self.stdscr.clear()
            # Restore message count and y so all messages gets rerendered
            self.msg_count = 0
            self.curr_y = 0
        # How many lines for each message
        line = []
        for msg in self.message_log:
            line.append(math.ceil((len(msg['msg']) + 18)/self.w))
        # Delete old messges to fit the new messages in
        lines_occupied = sum(line)
        while lines_occupied >= self.h - 2: # Last 2 lines are for input prompt
            self.curr_y = 0 # Need to re-render to get rid of old messages
            self.msg_count = 0
            lines_occupied -= line.pop(0)
            self.message_log.pop(0)
        # Render unrendered messages
        # Set cursor at line curr_y
        for i, msg in enumerate(self.message_log[self.msg_count:]):
            self.msg_count += 1
            for y in range(line[i]): # Render each line
                self.curr_y += 1
                m = msg['msg'][y*(self.w-18):(y+1)*(self.w-18)]
                u = msg['user'].ljust(18) if y == 0 else ' '*18
                self.stdscr.addstr(self.curr_y,0,u + m + '\n')
        # Render text input
        self.stdscr.addstr(self.h-2, 0, ' ' * (self.w*2 - 1))
        self.stdscr.addstr(self.h-2, 0, self.input)
        # Refresh window
        self.stdscr.refresh()

    def main(self, stdscr):
        self.stdscr = stdscr
        # Clear screen
        stdscr.clear()
        # Declare terminal window size
        self.h, self.w = stdscr.getmaxyx()
        stdscr.nodelay(True)
        # Start rendering chatroom
        while not self.stop:
            # Get user input
            c = stdscr.getch()
            self.input_change(c)
            # Render chat room
            self.render()
            time.sleep(0.02)

    def input_change(self, c):
        if c not in range(0,255):
            return
        if c == 10: # Enter
            if len(self.input) > 0:
                self.add_message(self.lanchat_api.username, self.input)
                self.lanchat_api.send_message(self.input)
                self.input = ''
        elif c == 127 or c == 263: # Backspace
            if len(self.input) > 0:
                self.input = self.input[:-1]
        else:
            self.input += chr(c)

    def add_message(self,username, message):
        self.message_log.append(
            {'user':username,'msg':message}
        )
