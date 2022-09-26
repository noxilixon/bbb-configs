#!/usr/bin/env python

import argparse
import yaml
import ipaddress as ip

parser = argparse.ArgumentParser(description='convert a networks.yml into a nice wiki table')
parser.add_argument('yml', help='the networks.yml file to be converted')
parser.add_argument('wiki', help='output file with wiki syntax')

args = parser.parse_args()

with open(args.yml, 'r') as file:
    networks = yaml.safe_load(file)

subnets = {}
ipv6_prefix = ip.ip_network(networks['ipv6_prefix'])

class Vlan:
    def __init__(self, n, v4, v6, v, m):
        self.name = n
        self.ipv4 = v4
        self.ipv6 = v6
        self.vlan = v
        self.mgmt = m

def __str__(self):
    return self.name

def find_mesh_data(name, v):
    s = name.split('-')[1]
    for section in networks['networks']:
        sec = section.get('name')
        if sec and len(sec.split('_')) >1 and sec.split('_')[1] == s:
            return Vlan(name, 
                        ip.ip_network(section.get('prefix')), 
                        list(ipv6_prefix.subnets(new_prefix=64))[section.get('ipv6_subprefix')],
                        section.get('vid'),
                        v)
    return Vlan('','','','',v)
 
class Node:
    def __init__(self, n, v4, v6, v):
        self.name = n
        self.ipv4 = v4
        self.ipv6 = v6
        self.vlan = v

    def __str__(self):
        return self.name

for section in networks['networks']:
    if section.get('name'):
        k = section['name']
    else:
        k = section['role']
    subnets[k] = []
    if section.get('prefix'):
        vsub4 = ip.ip_network(section.get('prefix'))
    else:
        vsub4 = None
    vsub6 = section.get('ipv6_subprefix')
    if section.get('assignments'):
        s = section['assignments']
        for n in s:
            if vsub4 and vsub6:
                subnets[k].append(Node(n,
                                       vsub4[s[n]],
                                       list(ipv6_prefix.subnets(new_prefix=64))[vsub6][s[n]],
                                       find_mesh_data(n, section['vid'])))
            else:
                subnets[k].append(Node(n, '', '', find_mesh_data(n, section['vid'])))
        
def print_table():
    print('{| class="wikitable"')
    print('! Name || Mesh VLAN || Mesh IPv6 @ core || Mesh IPv4 @ core || Management IPv4 || Management IPv4 || Management VLAN ')
    for k in subnets.keys():
        v = subnets.get(k)
        if v:
            for i in v:
                print('|- ')
                print('| http://'+i.name+'.olsr')
                print('|| '+str(i.vlan.vlan))
                print('|| '+str(i.vlan.ipv6))
                print('|| '+str(i.vlan.ipv4))
                print('|| '+str(i.ipv6))
                print('|| '+str(i.ipv4))
                print('|| '+str(i.vlan.mgmt))
    print('|}')
    
print_table()                
