import curses
import threading
import message
from concurrent_queue import ConcurrentQueue
from message_type import MessageType
from curses.textpad import Textbox, rectangle
class UI:
    __keycode = 1234;
    def __init__(self):
        self._output_queue = ConcurrentQueue()
        self.screen = curses.initscr()
        self.scr_height, self.scr_width = self.screen.getmaxyx()
        curses.noecho()
        self.temp_login_done = False
        self.do_login()
        self.start_chat()

    def do_login(self):
        login_win = SubWindowWrapper(self.screen, 1, 8, 2, self.scr_width)
        login_box = ExTextbox(login_win.win)
        self.screen.addstr(1,1, 'alias: ')
        self.refresh_screen()
        login_box.edit()
        username = login_box.gather_and_clear()
        self.screen.clear()
        del login_box
        del login_win
        self.temp_login_done = True
        return username

    def start_chat(self):        
        self.input_win = SubWindowWrapper(self.screen, self.scr_height - 10, 8, self.scr_height - 3, self.scr_width - 8, 1)
        self.output_win = SubWindowWrapper(self.screen, 1, self.input_win.ulx, self.input_win.uly - 3, self.input_win.lrx, 1)
        self.screen.addstr(self.input_win.uly, 1, 'Chat:')
        self.input_box = ExTextbox(self.input_win.win)
        self.output_box = ExTextbox(self.output_win.win)
        self.input_thread = threading.Thread(None, self._input_loop)
        self.input_thread.start()

    def refresh_screen(self):
        if self.screen.is_wintouched():
            self.screen.refresh()
    
    #this is run on its own thread
    def _input_loop(self):
        while True:
            self.refresh_screen()
            self.input_box.edit()
            input = self.input_box.gather_and_clear()
            self._output_queue.push(input)

    def process_message(self, message):
        type = message.get_type()
        if type == MessageType.chat_message:
            m_str = message.get_alias() + ': ' + message.get_payload()
            self._output_queue.push(m_str)
        elif type == MessageType.command:
            pass
        #the following will almost certainly be moved/changed
        while not self._output_queue.isEmpty():
            self.output_box.put_str(self._output_queue.pop())

    def parse(self, string):
        None
    def on_key_down(self, keycode):
        None

class ExTextbox(Textbox):
    def __init__(self, win, insert_mode=False):
        super().__init__(win, insert_mode)

    def gather_and_clear(self):
        result = self.gather()
        self.clear()
        return result
    def edit(self):
        #hack to make textbox return on enter press
        def exit_on_enter(ch):
            if ch == curses.ascii.NL:
                return curses.ascii.BEL
            return ch
        super().edit(exit_on_enter)
    def put_str(self, string):
        for ch in string:
            #newlines are inserted by superclass when line runs out, so ignore nl chars
            if ch == '\n':
                continue
            self._insert_printable_char(ch)
        self._insert_printable_char(curses.ascii.NL)
        self.win.refresh()
    def clear(self):
        self.win.erase()
        self.win.refresh()
    

#wrapper class to allow easier creation and handling of curses subwindows
class SubWindowWrapper:
    #Params:
    #uly, ulx: upper left coords
    #lry, lrx: lower right coords
    def __init__(self, parent_win, uly, ulx, lry, lrx, border_margin = 0):
        self.ulx = ulx
        self.uly = uly
        self.lrx = lrx
        self.lry = lry
        self._parentWin = parent_win
        self.height = lry - uly
        self.width = lrx - ulx
        self.win = parent_win.subwin(self.height, self.width, uly, ulx)
        if  border_margin > 0:
            try:
                curses.textpad.rectangle(parent_win, uly - border_margin, ulx - border_margin, lry + border_margin, lrx + border_margin)
            except curses.error:
                pass

    def clear(self):
        self.win.clear()

if __name__ == '__main__':
    ui = UI()