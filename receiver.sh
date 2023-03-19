#!/bin/bash

#Run script for the server distributed as a part of 
#Assignment 2
#Computer Networks (CS 456)
#Number of parameters: 2
#Parameter:
#    $1: <hostname>
#    $2: <emulator_port>
#    $3: <receiver_port>
#    $4: <file_name>

#For Python implementation
python receiver.py $1 $2 $3 "$4"

