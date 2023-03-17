from socket import *
import sys
import threading

def checker():
    global emulator_addr
    global emulator_port
    global sender_port
    global timeout_ms
    global filename
    if len(sys.argv) != 6:
        print(
            'Usage: \'python sender.py <emulator address> <emulator port> <sender port> <timeout interval> <file name>\'')
        sys.exit(1)
    try:
        emulator_addr = str(sys.argv[1])
    except ValueError:
        print("emulator_addr must be localhost or IP address format.")
    try:
        emulator_port = int(sys.argv[2])
    except ValueError:
        print("emulator_port must be an integer.")
        sys.exit(1)
    if int(emulator_port) < 1024 or int(emulator_port) > 65535:
        print("emulator_port must be between [1024, 65535].")
        sys.exit(1)
    try:
        sender_port = int(sys.argv[3])
    except ValueError:
        print("sender_port must be an integer.")
        sys.exit(1)
    if int(sender_port) < 1024 or int(sender_port) > 65535:
        print("sender_port must be between [1024, 65535].")
        sys.exit(1)
    try:
        timeout_ms = int(sys.argv[4])
    except ValueError:
        print("timeout must be an integer.")
        sys.exit(1)
    try:
        filename = str(sys.argv[5])
    except ValueError:
        print("filename must be a valid name.")


max_char = 500
recv_size = 1024
emulator_addr = ''
emulator_port = 0
sender_port = 0
timeout_ms = 0
filename = ''
checker()
try:
    file_data = open(filename, 'r')
except FileNotFoundError:
    exit(1)
lock = threading.Lock()
cv = threading.Condition(lock)

