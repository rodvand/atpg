#!/bin/bash
# Add default route on all hosts

for i in {17..256}
	do
		echo "h$i route add default dev h$i-eth0"
	done
