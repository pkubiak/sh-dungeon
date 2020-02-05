import tty
import os
import sys
import termios
import select
import time
from typing import Optional
from collections import deque


class Keys:
    """Keyboard keys mapping constants."""

    PAGE_UP = 'KEY_PAGE_UP'
    PAGE_DOWN = 'KEY_PAGE_DOWN'
    UP = 'KEY_UP'
    DOWN = 'KEY_DOWN'
    RIGHT = 'KEY_RIGHT'
    LEFT = 'KEY_LEFT'
    ESC = 'KEY_ESC'
    ENTER = 'KEY_ENTER'
    SPACE = 'KEY_SPACE'
    BACKSPACE = 'KEY_BACKSPACE'
    TAB = 'KEY_TAB'
    INSERT = 'KEY_INSERT'
    DELETE = 'KEY_DELETE'

    KEYS_TABLE = {
        9: TAB,
        10: ENTER,
        27: ESC,
        32: SPACE,
        127: BACKSPACE,
    }

    SPECIAL_KEYS_TABLE = {
        50: INSERT,
        51: DELETE,
        53: PAGE_UP,
        54: PAGE_DOWN,
        65: UP,
        66: DOWN,
        67: RIGHT,
        68: LEFT,
    }


class Keyboard:
    """
    Get user pressed keys in terminal in non-buffered way.

    @see: https://stackoverflow.com/a/2409034/5822988
    """

    ANSI_SEQ = '\033['
    EXTENDED_ANSI_SEQ = '\033[1;'

    _initialized = False
    _buffer = deque()

    @classmethod 
    def _has_data(cls, wait: bool = False) -> bool:
        """Check if there is some data in sys.stdin and wait for it if needed."""
        return select.select([sys.stdin], [], [], None if wait else 0) == ([sys.stdin], [], [])

    @classmethod
    def is_initialized(cls) -> bool:
        return bool(getattr(cls, '_original_settings', None))

    @classmethod
    def init(cls): 
        cls._original_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    @classmethod
    def close(cls):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, cls._original_settings)
        delattr(cls, '_original_settings')


    @classmethod
    def _read_into_buffer(cls):
        """Read keyboard input in non-blocking way and parse it."""
        data = b''
        while True:
            data += os.read(sys.stdin.fileno(), 1024)
            if not cls._has_data(False):
                break

        data = data.decode('utf-8')  # WARNING: to support unicode keys

        while data:
            if data.startswith(cls.EXTENDED_ANSI_SEQ): 
                assert len(data) >= 6
                # TODO: data[4] is modifier keys and is not supported at that moment
                key = Keys.SPECIAL_KEYS_TABLE[ord(data[5])]
                data = data[6:]
            elif data.startswith(cls.ANSI_SEQ): 
                assert len(data) >= 3
                key = Keys.SPECIAL_KEYS_TABLE[ord(data[2])]
                data = data[3:]
            else: # Normal key
                key = Keys.KEYS_TABLE.get(ord(data[0]), data[0])
                # print('>>', ord(data[0]))
                data = data[1:]

            cls._buffer.append(key)

    @classmethod
    def getch(cls, block: bool = True) -> Optional[str]:
        """

        @param block:
        """
        if not cls.is_initialized():
            raise RuntimeError('You must initialize Keyboard first!')
        
        if len(cls._buffer) > 0:
            return cls._buffer.popleft()

        if not cls._has_data(block):
            return None

        cls._read_into_buffer()  # put new keys into buffer
        
        return cls._buffer.popleft()

    @classmethod
    def clear(cls):
        """Clear keyboard input buffer."""
        if cls._has_data(False):
            cls._read_into_buffer()
        cls._buffer.clear()


if __name__ == '__main__':
    Keyboard.init()

    while True:
        key = Keyboard.getch(True)
        print(f"Pressed: {key}")
        if key == Keys.ESC:
            break

    Keyboard.close() 
