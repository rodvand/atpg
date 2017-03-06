#!/bin/env python
'''
Script to go through the flow tables of 
a number of switches, and predict the flow of a packet.

Takes for input:
	- packet source and destination
	- Optional: specific switches
'''

def get_interfaces(sort=False):
	'''
	Get the interfaces on the host. 
	Parse them and return a dictionary with the switches.
	'''
	import netifaces
	interfaces_old = netifaces.interfaces()
	interfaces = []

	for interface in interfaces_old:
		if 'lo' in interface:
			continue
		elif 'ovs' in interface:
			continue
		
		split_int = interface.split("-")
		switch = split_int[0]
		
		if switch not in interfaces:
			interfaces.append(switch)
	if sort:
		return sorted(interfaces)

	return interfaces	

def dump_flows(switch):
	'''
	Dump the flow entries from one switch
	and return a list with dictionary items.
	
	command run: ovs-ofctl dump-flows <switch>
	'''
	import subprocess

	command = "ovs-ofctl dump-flows " + switch
	proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
	flows = proc.stdout.read()
	flow = flows.split("\n")
	entries = []
	for line in flow:
		if 'NXST' in line:
			continue

		entry = {}
		att = line.split(" ")

		if len(att) > 1:
			att.pop(0) # Remove first element (it's just an empty space)
			el = att[-2].split(",")
			att.pop(len(att) - 2)

			for e in el:
				att.append(e)
			
			for line in att:
				new = line.split("=")
				if len(new) == 2:
					entry[new[0].strip(",")] = new[1].strip(",")
			entries.append(entry)
	if len(entries) == 0:
		return None	

	return entries
		
		
	

def main():
	print(get_interfaces(sort=True))
	dump_flows("s1")

if __name__=="__main__":
	main()
