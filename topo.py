#!/usr/bin/python3
# copyright 2017 Peter Dordal 
# licensed under the Apache 2.0 license
from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch, Controller, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from algorithms.algorithms import Algorithms

import multiprocessing
import sys


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        info ('enabling forwarding on ', self)
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class RTopo(Topo):
    #def init(self, **kwargs):
    #global r
    def build(self, **_opts):     # special names?
        # switch = self.addSwitch('s1')
        r  = self.addNode( 'r', cls=LinuxRouter) # , ip=defaultIP )
        h1 = self.addHost( 'h1', ip='10.0.1.10/24', defaultRoute='via 10.0.1.1' ) # Smartphone
        h2 = self.addHost( 'h2', ip='10.0.2.11/24', defaultRoute='via 10.0.2.1' ) # Door alarm
        h3 = self.addHost( 'h3', ip='10.0.3.12/24', defaultRoute='via 10.0.3.1' ) # Health monitoring device
        h4 = self.addHost( 'h4', ip='10.0.4.13/24', defaultRoute='via 10.0.4.1' ) # Smart coffee maker
        h5 = self.addHost( 'h5', ip='10.0.5.10/24', defaultRoute='via 10.0.5.1' ) # Smart Tv
        h6 = self.addHost( 'h6', ip='10.0.6.10/24', defaultRoute='via 10.0.6.1' ) # Internet

 # connecting each host to a link to router
 # Each link is bidirectional
 # Can test upload and download
        access_list = [h1,h2,h3,h4,h5]
        for i in range(len(access_list)+1):
            if i == 0:
                continue    
            self.addLink(access_list[i-1], r, intfName1 = f'h{i}-eth', intfName2 = f'r-eth{i}', 
                 params2 = {'ip' : '10.0.{i}.1/24'}, bw=10)

 # connect bottleneck link to router
 # Bottleneck link to internet
        self.addLink( h6, r, intfName1 = 'h6-eth', intfName2 = 'r-eth6', 
                 params2 = {'ip' : '10.0.6.1/24'}, 
                 bw=0.01, delay='110ms', max_queue_size=int(10))  
 

# Running Evaluation commands using iperf
# iPerf will run between 2 hosts, 

def udpConnect(h, port):
    port_no = port - 1
    h.cmd(f'iperf3 -c 10.0.6.10 -u -b 1000g -p 520{port_no} -J > h{port}_udp_result.json')

def tcpConnect(h, port):
    port_no = port - 1
    h.cmd(f'iperf3 -c 10.0.6.10 -b 1g -p 520{port_no} -J > h{port}_tcp_result.json')

def main():
    # Creating topology
    rtopo = RTopo()
    net = Mininet(topo = rtopo,
                  link=TCLink,
                  #switch = OVSKernelSwitch, 
                  #controller = RemoteController,
           autoSetMacs = True   # --mac
                )  
    net.start()
    r = net['r']
    r.cmd('ip route list')
    # r's IPv4 addresses are set here, not above.
    # ifconfig command is used to produce links
    # Can check bandwidth,delay,etc.
    r.cmd('ifconfig r-eth1 10.0.1.1/24')
    r.cmd('ifconfig r-eth2 10.0.2.1/24')
    r.cmd('ifconfig r-eth3 10.0.3.1/24')
    r.cmd('ifconfig r-eth4 10.0.4.1/24')
    r.cmd('ifconfig r-eth5 10.0.5.1/24')
    r.cmd('ifconfig r-eth6 10.0.6.1/24')
    r.cmd('sysctl net.ipv4.ip_forward=1')

    # Declare host in topology
    h1 = net['h1']
    h2 = net['h2']
    h3 = net['h3']
    h4 = net['h4']
    h5 = net['h5']
    h6 = net['h6']
    access_list = [h1,h2,h3,h4,h5]
    
    # Standardize Q discipline from hosts to routers
    for h in range(1,6):
        access_list[h-1].cmd(f'tc qdisc del dev h{h}-eth root')
        access_list[h-1].cmd(f'tc qdisc add dev h{h}-eth root fq')
    for h in [r, h1, h2, h3, h4, h5, h6]: h.cmd('/usr/sbin/sshd')

    # Bottleneck open up iperf to act as server
    h6.popen('iperf3 -s -p 5200')
    h6.popen('iperf3 -s -p 5201')
    h6.popen('iperf3 -s -p 5202')
    h6.popen('iperf3 -s -p 5203')
    h6.popen('iperf3 -s -p 5204')

    ##==============================================================================
    ## Classless AQM
    # Queue_disc = 'pfifo'
    # r.cmd('tc qdisc del dev r-eth5 root')
    # r.cmd(f'tc qdisc add dev r-eth5 root {Queue_disc}')
    ##==============================================================================
    ## Classful AQM
    # Define Q discipline from linux tc (traffic control).
    # Experiment between whatever we send in the chat
    algorithm = Algorithms(sys.argv[1])
    algorithm.router_command(r, "r-eth6")
    ##==============================================================================
    ## Ensure the hosts run iperf run on the same time
    threads = []
    for h in range(1,6):
        port = f'520{h-1}'
        #threads.append(multiprocessing.Process(target=algorithm.udpConnect, args=(access_list[h-1], port, "10.0.6.10", "1000g")))
        threads.append(multiprocessing.Process(target=algorithm.tcpConnect, args=(access_list[h-1], port, "10.0.6.10", "1g")))

    for i in threads:
        i.start()
        
    for i in threads:
        i.join()
    CLI( net)
    net.stop()

setLogLevel('info')
main()
