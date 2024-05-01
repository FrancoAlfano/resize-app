import socket
import os

HOST = os.getenv('HOST', '0.0.0.0')
PORT = 8080
FAMILY = socket.AF_UNSPEC
FLAGS = 0
BUFFER_SIZE = 4096
SERVER_ADDRESS = '::'
SERVER_PORT = 8080
