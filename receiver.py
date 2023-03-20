from socket import *
import sys
from packet import Packet


def checker():
    global hostname_emulator
    global emulator_port
    global receiver_port
    global filename
    if len(sys.argv) != 5:
        print('Usage: \'./receiver.sh <hostname> <emulator_port> <receiver_port> <file_name>\'')
        sys.exit(1)
    try:
        hostname_emulator = str(sys.argv[1])
    except ValueError:
        print("hostname_emulator must be a string format.")
    try:
        emulator_port = int(sys.argv[2])
    except ValueError:
        print("emulator_port must be an integer.")
        sys.exit(1)
    if int(emulator_port) < 1024 or int(emulator_port) > 65535:
        print("emulator_port must be between [1024, 65535].")
        sys.exit(1)
    try:
        receiver_port = int(sys.argv[3])
    except ValueError:
        print("emulator_port must be an integer.")
        sys.exit(1)
    if int(receiver_port) < 1024 or int(receiver_port) > 65535:
        print("emulator_port must be between [1024, 65535].")
        sys.exit(1)
    try:
        filename = str(sys.argv[4])
    except ValueError:
        print("filename must be a valid name.")


def send_packet(packet):
    receiver_sock.sendto(packet.encode(), (hostname_emulator, emulator_port))


def seq_is_within_window():
    margin = (expected_seq + 10) % 32
    if margin > expected_seq:
        if expected_seq <= curr_seq < margin:
            return True
        else:
            return False
    else:
        if expected_seq <= curr_seq or margin > curr_seq:
            return True
        else:
            return False


def seq_is_within_last_10_seq():
    margin = (expected_seq - 10) % 32
    if margin < expected_seq:
        if margin < curr_seq <= expected_seq:
            return True
        else:
            return False
    else:
        if curr_seq <= expected_seq or curr_seq > margin:
            return True
        else:
            return False


hostname_emulator = ''
emulator_port = 0
receiver_port = 0
filename = ''
checker()
arrival_name = 'arrival.log'
recv_size = 1024
buffer = [None] * 32
expected_seq = 0
curr_seq = 0
receiver_sock = socket(AF_INET, SOCK_DGRAM)
receiver_sock.bind(('', receiver_port))
with open(arrival_name, "w") as file:
    file.write('')
with open(filename, "w") as file:
    file.write('')
arrival_log = open(arrival_name, "a")
received_file = open(filename, "a")

while True:
    packet_receive, addr = receiver_sock.recvfrom(recv_size)
    packet_receive = Packet(packet_receive)
    curr_seq = int(packet_receive.seqnum)
    # print((str(curr_seq) + "\n"))

    # the packet is an EOT packet
    if packet_receive.typ == 2:
        EOT_packet = Packet(2, curr_seq, 0, '')
        send_packet(EOT_packet)
        arrival_log.write("EOT\n")
        print("EOT\n")
        arrival_log.close()
        receiver_sock.close()
        exit()
    elif seq_is_within_window():
        SACK_packet = Packet(0, curr_seq, 0, '')
        send_packet(SACK_packet)
        arrival_log.write(str(curr_seq) + "\n")
        print((str(curr_seq) + "\n"))
        if buffer[curr_seq] is None:
            buffer[curr_seq] = packet_receive
        # the received packet is at the base of the window
        if expected_seq == curr_seq:
            while buffer[curr_seq] is not None:
                curr_packet = buffer[curr_seq]
                buffer[curr_seq] = None
                received_file.write(str(curr_packet.data))
                curr_seq += 1
                curr_seq = curr_seq % 32
                expected_seq += 1
                expected_seq = expected_seq % 32
    elif seq_is_within_last_10_seq():
        SACK_packet = Packet(0, curr_seq, 0, '')
        send_packet(SACK_packet)
