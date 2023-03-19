#!/bin/bash

#Run script for client distributed as part of 
#Assignment 2
#Computer Networks (CS 456)
#Number of parameters: 5
#Parameter:
#    $1: <emulator_address>
#    $2: <emulator_port>
#    $3: <sender_port>
#    $4: <timeout>
#    $5: <file_name>

#For Python implementation
python sender.py $1 $2 $3 $4 "$5"
