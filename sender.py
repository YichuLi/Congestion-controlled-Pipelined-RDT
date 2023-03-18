from socket import *
import sys
import threading
from packet import Packet


def checker():
    global emulator_addr
    global emulator_port
    global sender_port
    global timeout_ms
    global filename
    if len(sys.argv) != 6:
        print('Usage: \'python sender.py <emulator address> <emulator port> <sender port> <timeout> <file name>\'')
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


def send_packet(packet):
    global timestamp
    sender_sock.sendto(packet.encode(), (emulator_addr, emulator_port))
    seqnum_log.write("t=" + str(timestamp) + " " + str(packet.seqnum) + "\n")
    timestamp += 1


def timeout_function(index):
    global window_size
    lock.acquire()
    if base_window == len(packets):
        lock.release()
        return

    window_size = 1
    if index == base_window:
        send_packet(packets[index])  # need to reconsider
        reset_timer = threading.Timer(timeout_sec, timeout_function, args=[index])
        reset_timer.start()
    N_log.write("t=" + str(timestamp) + " " + str(window_size) + "\n")
    lock.release()


max_char = 500
recv_size = 1024
emulator_addr = ''
emulator_port = 0
sender_port = 0
timeout_ms = 0
filename = ''
checker()

N_name = 'N.log'
ack_name = 'ack.log'
seqnum_name = 'seqnum.log'
timestamp = 0
timeout_sec = timeout_ms / 1000.0
window_size = 0
max_window_size = 10
base_window = 0
packets = []
seqnum = 0
sender_sock = socket(AF_INET, SOCK_DGRAM)

with open(N_name, "w") as file:
    file.write('')
with open(ack_name, "w") as file:
    file.write('')
with open(seqnum_name, "w") as file:
    file.write('')

N_log = open(N_name, "a")
ack_log = open(ack_name, "a")
seqnum_log = open(seqnum_name, "a")

try:
    open(filename, 'r')
except FileNotFoundError:
    exit(1)

# provide mutual exclusion
lock = threading.Lock()
cv = threading.Condition(lock)

N_log.write("t=" + str(timestamp) + " " + str(window_size) + "\n")
timestamp += 1

# read data from file, max char of a packet is 500
file_data = open(filename, 'r')
packet_data = file_data.read(max_char)
while packet_data:
    packets.append(Packet(1, seqnum % 32, len(packet_data), packet_data))
    packet_data = file_data.read(max_char)
    seqnum += 1
file_data.close()

# timer = threading.Timer(timeout_sec, timeout_function)
# timer.start()
timers = []

timer = threading.Timer(1.0, timeout_function, args=[1])
timers.append(timer)

