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
		elif 'eth' in interface:
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
                entry['switch'] = switch

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
		
def match_rules(flows, match_conditions):
	'''
	Input: a dictionary of flows
	Output: rules matched, first match listed first (list). If no rule matched, return None
	'''
	import ipaddress
	source = ipaddress.IPv4Address(unicode(match_conditions[0][0]))
	dest = ipaddress.IPv4Address(unicode(match_conditions[1][0]))

        if flows is None:
            return None

	matches = []
	
	for flow in flows:
		source_match = True
		dest_match = True
		if 'nw_src' in flow:
			dest_match = ipaddress.ip_address(source) in ipaddress.ip_network(unicode(flow['nw_src']))
		if 'nw_dst' in flow:
			dest_match = ipaddress.ip_address(dest) in ipaddress.ip_network(unicode(flow['nw_dst']))
		
		if source_match and dest_match:
			matches.append(flow)
	
	return matches

def print_flows(flows):
    '''
    Function to prettify the print of a flow.
    Input: flows
    Output: prints the flows in a readable manner
    '''
    for flow in flows:
        if 'nw_dst' in flow and 'nw_src' in flow:
            print("Switch: " + flow['switch']
                    + " Priority: " + flow['priority'] 
                    + " Source: " + flow['nw_src'] 
                    + " Destination: " + flow['nw_dst'] 
                    + " Action: " + flow['actions'])
        elif 'nw_dst' in flow and 'nw_src' not in flow:
            print("Switch: " + flow['switch']
                    + " Priority: " + flow['priority'] 
                    + " Destination: " + flow['nw_dst'] 
                    + " Action: " + flow['actions'])
        elif 'nw_src' in flow and 'nw_dst' not in flow:
            print("Switch: " + flow['switch']
                    + " Priority: " + flow['priority'] 
                    + " Source: " + flow['nw_src'] 
                    + " Action: " + flow['actions'])
        else:
            print("Switch: " + flow['switch']
                    + " Priority: " + flow['priority'] 
                    + " Action: " + flow['actions'])

def main():
	'''
	Script to predict the flow of a packet through the switches.
	Input:
		switches
		source
		destination
		port		
	First start: just show rules matching, don't think about the interconnections
	'''
	import argparse
	
	# Commandline arguments
	parser = argparse.ArgumentParser(description='Predict the packet flow through the network')
	parser.add_argument('-S', nargs='+', help='the switches to check the packet flow through', metavar='SWI,SWI')
	parser.add_argument('-s', nargs=1, help='the source address', metavar='SRC')
	parser.add_argument('-d', nargs=1, help='the destination address', metavar='DST')

	args = parser.parse_args()
	source = args.s
	dest = args.d
        print(args)
	if args.S == None:
		switches = get_interfaces(sort=True)
	else:
		switches = args.S
	
	condition = (source, dest)
	
	for switch in switches:
		flow = dump_flows(switch.strip())	
		matches = match_rules(flow, condition)
                if matches is not None:
                    print_flows(matches)

if __name__=="__main__":
	main()
