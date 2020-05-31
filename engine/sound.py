import os
import subprocess
import tempfile 
import socket
import time


class Sound:
    def __init__(self):
        self.socket_name = tempfile.mktemp()
        self.process = subprocess.Popen(['mpv', '--idle', f"--input-ipc-server={self.socket_name}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while not os.path.exists(self.socket_name):
            time.sleep(0.1)
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(self.socket_name)

    def play(self, path, loop=False, mode='replace'):
        loop = 'yes' if loop else 'no'
        cmd = f"loadfile \"{path}\" {mode} loop={loop}\n"
        self.socket.send(cmd.encode('utf-8'))

    # def push_sound(self, path):
    #     cmd = f"loadfile \"{path}\" replace\n"
    #     self.socket.send(cmd.encode('utf-8'))

    def close(self):
        self.socket.close()
        self.process.terminate()
