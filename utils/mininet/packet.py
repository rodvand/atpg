#! /usr/bin/env python

# Script to craft a packet for testing flow entries
# February 2017 - Martin Roedvand

import sys
import argparse
import logging
import random
import datetime
import os
from scapy.all import *
from subprocess import call

# Commandline arguments
parser = argparse.ArgumentParser(description='Craft a packet to test flow entries.')
parser.add_argument('-d', nargs='?', required=True, help='the destination address of the packet', metavar='DST')
parser.add_argument('-p', nargs=1, choices=['icmp', 'udp', 'tcp'], default=['tcp'], help='the protocol used in the packet')
parser.add_argument('-dp', nargs=1, help='the destination port to be used in the packet', metavar='DPORT')
parser.add_argument('-sp', nargs=1, help='the source port to be used in the packet', metavar='SPORT')
parser.add_argument('-t', action='store_true', help='show packet trace')
parser.add_argument('-v', action='store_true', help='for verbose output. May be helpful under debugging')

args = parser.parse_args()

dest = args.d
prot = args.p[0]
trace = args.t

if args.dp:
	port = int(args.dp[0])
else:
	port = '-1'

if args.sp:
	sourceport = int(args.sp[0])
else:
	sourceport = random.randint(1, 65535)

# Logging
verbose = args.v

if verbose:
	logging.basicConfig(level=logging.DEBUG)
else:
	logging.basicConfig(level=logging.INFO)

# Start crafting a packet with SCAPY
logging.debug("Attempting to craft packet")
logging.debug("CMD arguments: " + str(args))

if prot == 'icmp':
	logging.debug("We're in ICMP")
	packet = IP(dst=dest)/ICMP()/"Hello World"

if prot == 'tcp':
	logging.debug("We're in TCP")
	logging.debug(port)
	if port == '-1':
		logging.warning("Port is not defined. Port is required for TCP.")
		sys.exit(1)
	packet = IP(dst=dest)/TCP(sport=sourceport,dport=port)

if prot == 'udp':
	print

logging.debug("Going for a send")

# Start the trace with ./dump.sh
if trace:
	# Create a time stamp for logging
	timestamp = '{:%Y%m%d%H%M}'.format(datetime.now())	
	outfile = open("logs/" + timestamp, 'w')
	logging.debug("Timestamp: " + timestamp)
	logging.debug("Current directory " + os.getcwd())
	logCode = call(["./dump.sh dst host " + dest + "> logs/" + timestamp + " &"], shell=True)	
	logging.debug("Call Error Code: " + str(logCode))
	
	if logCode != 0:
		logging.info("TCPdump returned with error code " + str(logCode))

sr(packet, timeout=1)
