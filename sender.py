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
        print('Usage: \'./sender.sh <emulator_address> <emulator_port> <sender_port> <timeout> <file_name>\'')
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
    global timestamp
    lock.acquire()
    if base_window >= len(packets):
        lock.release()
        return

    window_size = 1
    if index == base_window % 32:
        send_packet(packets[base_window])  # need to resend
        reset_timer = threading.Timer(timeout_sec, timeout_function, args=[index])
        reset_timer.start()
    N_log.write("t=" + str(timestamp) + " " + str(window_size) + "\n")
    timestamp += 1
    lock.release()


def receive_ack():
    global timestamp
    global window_size
    global ack_log
    global base_window
    receiver_sock = socket(AF_INET, SOCK_DGRAM)
    receiver_sock.bind(('', sender_port))
    while True:
        packet_ack, addr = receiver_sock.recvfrom(recv_size)
        packet_ack = Packet(packet_ack)
        lock.acquire()
        # When the packet is EOT
        if packet_ack.typ == 2 and packet_ack.length == 0:
            print("ack.log: t=" + str(timestamp) + " EOT\n")
            ack_log.write("t=" + str(timestamp) + " EOT\n")
            timestamp += 1
            lock.release()
            break
        # Otherwise, it is a SACK
        seq_ack = packet_ack.seqnum
        ack_log.write("t=" + str(timestamp) + " " + str(seq_ack) + "\n")
        print("ack.log: t=" + str(timestamp) + " " + str(seq_ack) + "\n")
        if seq_ack in not_acked_packets:
            timers[seq_ack].cancel()
            not_acked_packets.remove(seq_ack)
            # resend the packet
            if seq_ack == base_window % 32:
                base_window += 1
            elif len(not_acked_packets) == 0:
                base_window += window_size
            if window_size < max_window_size:
                window_size += 1
                N_log.write("t=" + str(timestamp) + " " + str(window_size) + "\n")
            cv.notify()
        timestamp += 1
        lock.release()

    receiver_sock.close()


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
window_size = 1
max_window_size = 10
base_window = 0
packets = []
not_acked_packets = []
sent_packets = []
seqnum = 0
counter = 0
sender_sock = socket(AF_INET, SOCK_DGRAM)

with open(seqnum_name, "w") as file:
    file.write('')
with open(ack_name, "w") as file:
    file.write('')
with open(N_name, "w") as file:
    file.write('')

seqnum_log = open(seqnum_name, "a")
ack_log = open(ack_name, "a")
N_log = open(N_name, "a")

try:
    open(filename, 'r')
except FileNotFoundError:
    exit(1)

# provide mutual exclusion
lock = threading.Lock()
cv = threading.Condition(lock)

# print("t=" + str(timestamp) + " " + str(window_size) + "\n")
N_log.write("t=" + str(timestamp) + " " + str(window_size) + "\n")
timestamp += 1

# read data from file, max char of a packet is 500
file_data = open(filename, 'r')
packet_data = file_data.read(max_char)
while packet_data:
    print(packet_data)
    print("--------------------")
    packets.append(Packet(1, seqnum % 32, len(packet_data), packet_data))
    packet_data = file_data.read(max_char)
    seqnum += 1
file_data.close()

timers = {}

receive_ack_thread = threading.Thread(target=receive_ack)
receive_ack_thread.start()

while base_window < len(packets):
    target = base_window + window_size
    lock.acquire()
    counter = base_window
    # check if the window is full
    while counter < target and counter < len(packets):
        if counter not in sent_packets:
            send_packet(packets[counter])
            i = counter % 32
            timers[i] = threading.Timer(timeout_sec, timeout_function, args=[i])
            timers[i].start()
            sent_packets.append(counter)
            not_acked_packets.append(i)
        counter += 1
    cv.wait()
    lock.release()

send_packet(Packet(2, seqnum % 32, 0, ''))
receive_ack_thread.join()
sender_sock.close()

seqnum_log.close()
ack_log.close()
N_log.close()
