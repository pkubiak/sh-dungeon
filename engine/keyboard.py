import tty
import os
import sys
import termios
import select
import time
from typing import Optional
from collections import deque

# TODO: Handle key modifiers (shift, alt, ctrl)

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
    END = 'KEY_END'
    HOME = 'KEY_HOME'
    F1 = 'KEY_F1'
    F2 = 'KEY_F2'
    F3 = 'KEY_F3'
    F4 = 'KEY_F4'
    F5 = 'KEY_F5'
    F6 = 'KEY_F6'
    F7 = 'KEY_F7'
    F8 = 'KEY_F8'
    F9 = 'KEY_F9'
    F10 = 'KEY_F10'
    F11 = 'KEY_F11'
    F12 = 'KEY_F12'


    KEYS_TABLE = {
        8: BACKSPACE,
        9: TAB,
        10: ENTER,
        27: ESC,
        32: SPACE,
        127: BACKSPACE,
    }

    SS3_MAPPING = {
        80: F1,
        81: F2,
        82: F3,
        83: F4,
    }

    CSI_TABLE = {
        '1': HOME,
        '2': INSERT,
        '3': DELETE,
        '4': END,
        '5': PAGE_UP,
        '6': PAGE_DOWN,
        '15': F5,
        '17': F6,
        '18': F7,
        '19': F8,
        '20': F9,
        '21': F10,
        '23': F11,
        '24': F12,
        'A': UP,
        'B': DOWN,
        'C': RIGHT,
        'D': LEFT,
        'F': END,
        'H': HOME,
        'Z': TAB  # WARNING: with SHIFT
    }


class Keyboard:
    """
    Get user pressed keys in terminal in non-buffered way.

    @see: https://stackoverflow.com/a/2409034/5822988
    """

    CSI = '\033['  # Control Sequence Introducer
    SS3 = '\033O'  # Single Shift Select of G3 Character Set
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
            if data.startswith(cls.SS3):
                key = Keys.SS3_MAPPING[ord(data[2])]
                data = data[3:]
            elif data.startswith(cls.EXTENDED_ANSI_SEQ):
                assert len(data) >= 6
                # TODO: data[4] is modifier keys and is not supported at that moment
                key = Keys.CSI_TABLE[data[5]]

                data = data[6:]
            elif data.startswith(cls.CSI):
                assert len(data) >= 3
                if '0' <= data[2] <= '9':
                    assert '~' in data
                    pos = data.index('~')
                    code = data[2:pos]
                    if ';' in code:
                        code = code.split(';')[0]
                    data = data[pos+1:]
                else:
                    code = data[2]
                    data = data[3:]

                key = Keys.CSI_TABLE[code]
            else: # Normal key
                key = Keys.KEYS_TABLE.get(ord(data[0]), data[0])
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
