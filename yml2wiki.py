#!/usr/bin/env python

import argparse
import yaml

parser = argparse.ArgumentParser(description='convert a networaks.yml into a nice wiki table')
parser.add_argument('yml', help='the networks.yml file to be converted')
parser.add_argument('wiki', help='output file with wiki syntax')

args = parser.parse_args()

with open(args.yml, 'r') as file:
    networks = yaml.safe_load(file)

class Node:
    def __init__(self, n, v, mg4):
        self.name = n
        self.mgmt_vlan = v
        #self.mgmt_ipv6
        self.mgmt_ipv4 = mg4
        #self.mesh_vlan #matching mesh sections will be quite hard without naming convention
        #self.mesh_ipv6
        #self.mesh_ipv4

    def __str__(self):
        return "|-\n"+"| "+self.name+"\n"+"|VLAN "+str(self.mgmt_vlan)+"||  \n"+"| "+str(self.mgmt_ipv4)

def add2ip(ip, i):
    ip = ip.split('/')[0]
    ipl = ip.split('.')
    last = int(ipl[3]) + i
    return '.'.join(ipl[:-1]+[str(last)])

nodes = []
for section in networks['networks']:
    if section['role'] == 'mgmt':
        prefix = section['prefix']
        s = section['assignments']
        for a in s:
            nodes.append(Node(a, 
                              section['vid'], 
                              add2ip(prefix,s[a])))

for n in nodes:
    print(n)
