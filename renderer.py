import curses
from curses import wrapper
import curses.textpad as textpad
import time
import math
import threading

class Render():
    def __init__(self):
        self.input = ''
        self.stop = False
        # message_log [{'user':'moku','msg':'hello'}]
        self.message_log = []
        self.msg_count = 0 # Counts the number of messages rendered on screen
        self.curr_y = 0 # Counts the number of lines filled on screen
        wrapper(self.main)

    '''
        Check input from the input box
        @param k: keystroke
    '''
    def input_check(self, k):
        if k == 10: # Enter key pressed
            self.add_message('moku', self.input_tb.gather())
            self.input_win.clear()
            self.input_win.refresh()
            return
        return k

    '''
        render the chatroom
    '''
    def render(self):
        # Get current window size
        h_new, w_new = self.stdscr.getmaxyx()
        # How many lines it'll take for each message
        line = []
        for msg in self.message_log:
            line.append(math.ceil((len(msg['msg']) + 18)/self.w))
        # Delete old messges to fit the new messages in
        lines_occupied = sum(line)
        while lines_occupied > self.h - 2: # Last line is for input prompt
            lines_occupied -= line.pop(0)
            self.message_log.pop(0)
        # If the window has been resized
        if not (self.h == h_new and self.w == w_new):
            self.h, self.w = h_new, w_new # Update window dimensions
            # Clear the current window
            self.stdscr.clear()
            # Restore message count and y so all messages gets rerendered
            self.msg_count = 0
            self.curr_y = 0
        # Render unrendered messages
        # Set cursor at line curr_y
        curses.setsyx(self.curr_y, 0)
        for i, msg in enumerate(self.message_log[self.msg_count:]):
            self.msg_count += 1
            for y in range(line[i]): # Render each line
                self.curr_y += 1
                m = msg['msg'][y*(self.w-18):(y+1)*(self.w-18)]
                u = msg['user'].ljust(18) if y == 0 else ' '*18
                self.stdscr.addstr(u + m + '\n')
        # Move cursor back to where it was
        curses.setsyx(self.h - 1, len(self.input))
        # Refresh window
        self.stdscr.refresh()

    def main(self, stdscr):
        self.stdscr = stdscr
        # Clear screen
        stdscr.clear()
        # Declare terminal window size
        self.h, self.w = stdscr.getmaxyx()
        # Start rendering chatroom
        threading.Thread(target=self.render_worker, daemon=True).start()
        # Make a input box at the bottom of the screen
        self.input_win = curses.newwin(1,self.w, self.h-1, 0)
        self.input_tb = curses.textpad.Textbox(self.input_win,
                                                insert_mode=True)
        self.input = self.input_tb.edit(self.input_check)

    def render_worker(self):
        while not self.stop:
            self.render()
            time.sleep(0.02)

    def add_message(self,username, message):
        self.message_log.append(
            {'user':username,'msg':message}
        )

Render()
