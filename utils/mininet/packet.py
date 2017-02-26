#! /usr/bin/env python

# Script to craft a packet for testing flow entries
# February 2017 - Martin Roedvand

import sys
import argparse
from scapy.all import *

parser = argparse.ArgumentParser(description='Craft a packet to test flow entries.')
parser.add_argument('-s', nargs='?', required=True, help='the source address of the packet', metavar='SRC')
parser.add_argument('-d', nargs='?', required=True, help='the destination address of the packet', metavar='DST')
parser.add_argument('-p', nargs=1, choices=['icmp', 'udp', 'tcp'], default='tcp', help='the protocol used in the packet')
parser.add_argument('-P', nargs=1, required=True, help='the port to be used in the packet', metavar='PORT')

args = parser.parse_args()

src = args.s
dst = args.d
prot = args.p
port = args.P

# Start crafting a packet with SCAPY
