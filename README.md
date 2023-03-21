# README

* Programming Language: Python 3.9
* IDE: Pycharm
* Environment: ubuntu2004-014.student.cs.uwaterloo.ca

This project is an implementation of Congestion-controlled Pipelined RDT Protocol over UDP.

 

## How to Run:

* Run the emulator at first:

  ```
  ./nEmulator <emulator_port> <receiver_IP_address> <receiver_port> <emulator_port> <sender_IP_address> <sender_port> <maximum_delay> <drop_probability> <verbose>
  ```

* Then run the receiver:

  ```
  ./receiver.sh <hostname> <emulator_port> <receiver_port> <received_file_name>
  ```

* Run the sender at last:

  ```
  ./sender.sh <emulator_address> <emulator_port> <sender_port> <timeout> <file_to_send>

