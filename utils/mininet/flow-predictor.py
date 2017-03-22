#!/bin/env python
'''
Script to go through the flow tables of 
a number of switches, and predict the flow of a packet.

Takes for input:
	- packet source and destination
	- Optional: specific switches
'''

class Device(object):
    '''
    A class to represent a Device (host/switch) in the network
    '''
    
    def __init__(self, name):
        self.connections = {}
        self.name = name

    def add_connection(self, port, device):
        connections = self.connections
        connections[port] = device
    
    def list_connections(self):
        connections = self.connections
        if len(connections) > 0:
            for p in connections:
                print(self.name + " is connected to " + p + " on port " + connections[p])

    def __eq__(self, other):
        return self.name == other.name

    def get_connection(self):
        '''
        If device only have one connection, return it 
        '''
        conn = self.connections

        if len(conn) == 1:
            return conn 

        return False

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
        if match_conditions[0]:
	    source = ipaddress.IPv4Address(unicode(match_conditions[0][0]))
        if match_conditions[1]:
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

def get_port(string):
    local = string[0].split('-')
    external = string[1].split('-')
    device = external[0]
    port = local[1]

    return (device, port)

def get_device(dev, search):
    '''
    Return Device object after searching for device
    '''

    for device in dev:
        if search in device.name:
            return device 
    return None

def create_topology(conn, f='topology.txt'):
    '''
    Definition to create a topology of the network.
    '''
    o = open(f, 'r')
    topology = []

    for line in o:
        new_line = line.split()

        # Loop through the list 
        count = 0
        for entry in new_line:
            if count == 0:
                device = Device(entry)

            count = count + 1
            sp = entry.split(':')

            if len(sp) == 1:
                continue
            elif not sp[1]:
                continue
            port, ext = get_port(sp)

            device.add_connection(port, ext)
            topology.append(device)

    return topology

def predict_path(topo, start, props):
    '''
    Predict the path between start and end by analysing the 
    flow tables on the switches and create a path.

    Returns list with path
    '''

    start_device = get_device(topo, start) 
    first_hop = start_device.get_connection()

    if first_hop:
        for s in first_hop:
            dev = get_device(topo, s)
            flow = dump_flows(dev.name)
            matches = match_rules(flow, props)

    print(matches)




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
        topology_database = {}
        topo = create_topology(topology_database)
	
	condition = (source, dest)
        predict_path(topo, 'h197', condition)
	
	for switch in switches:
		flow = dump_flows(switch.strip())	
		matches = match_rules(flow, condition)
                if matches is not None:
                    print_flows(matches)

if __name__=="__main__":
	main()

