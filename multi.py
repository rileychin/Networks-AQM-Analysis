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
        r1 = self.addNode( 'r1', cls=LinuxRouter) # , ip=defaultIP )
        r2 = self.addNode( 'r2', cls=LinuxRouter) 
        r3 = self.addNode( 'r3', cls=LinuxRouter) 
        h1 = self.addHost( 'h1', ip='10.0.1.10/24', defaultRoute='via 10.0.1.1' ) # Smartphone
        h2 = self.addHost( 'h2', ip='10.0.2.11/24', defaultRoute='via 10.0.2.1' ) # Door alarm
        h3 = self.addHost( 'h3', ip='10.0.3.12/24', defaultRoute='via 10.0.3.1' ) # Health monitoring device
        h4 = self.addHost( 'h4', ip='10.0.4.13/24', defaultRoute='via 10.0.4.1' ) # Smart coffee maker
        h5 = self.addHost( 'h5', ip='10.0.5.10/24', defaultRoute='via 10.0.5.1' ) # Smart Tv
        h6 = self.addHost( 'h6', ip='10.0.6.10/24', defaultRoute='via 10.0.6.1' ) # Internet
        h7 = self.addHost( 'h7', ip='10.0.7.10/24', defaultRoute='via 10.0.7.1' )

 # connecting each host to a link to router
 # Each link is bidirectional
 # Can test upload and download
        ## R1 subnet
        self.addLink(h1, r1, intfName1 = f'h1-eth', intfName2 = f'r1-eth1', params2 = {'ip' : '10.0.1.1/24'}, bw=10)
        self.addLink(h2, r1, intfName1 = f'h2-eth', intfName2 = f'r1-eth2', params2 = {'ip' : '10.0.2.1/24'}, bw=10)
        self.addLink(h3, r1, intfName1 = f'h3-eth', intfName2 = f'r1-eth3', params2 = {'ip' : '10.0.3.1/24'}, bw=10)
        self.addLink(h4, r1, intfName1 = f'h4-eth', intfName2 = f'r1-eth4', params2 = {'ip' : '10.0.4.1/24'}, bw=10)
        self.addLink(h5, r1, intfName1 = f'h5-eth', intfName2 = f'r1-eth5', params2 = {'ip' : '10.0.5.1/24'}, bw=10)
        ##2
        self.addLink(h6, r2, intfName1 = f'h6-eth', intfName2 = f'r2-eth1', params2 = {'ip' : '10.0.6.1/24'}, bw=10)
        #R3
        self.addLink(h7, r3, intfName1 = f'h7-eth', intfName2 = f'r3-eth1', params2 = {'ip' : '10.0.7.1/24'}, bw=10)


 # connect bottleneck link to router
 # Bottleneck link to internet
        self.addLink(r1,r2, intfName1 = 'r1-eth6', intfName2 = 'r2-eth2', params1={'ip': '10.100.0.1/24'}, params2={'ip': '10.100.0.2/24'})
        self.addLink(r2,r3, intfName1 = 'r2-eth3', intfName2 = 'r3-eth2', params1={'ip': '10.101.0.1/24'}, params2={'ip': '10.101.0.2/24'})

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
    r1 = net['r1']
    r2 = net['r2']
    r3 = net['r3']
    r1.cmd('ip route list')
    # r's IPv4 addresses are set here, not above.
    # ifconfig command is used to produce links
    # Can check bandwidth,delay,etc.
    r1.cmd('ifconfig r1-eth1 10.0.1.1/24')
    r1.cmd('ifconfig r1-eth2 10.0.2.1/24')
    r1.cmd('ifconfig r1-eth3 10.0.3.1/24')
    r1.cmd('ifconfig r1-eth4 10.0.4.1/24')
    r1.cmd('ifconfig r1-eth5 10.0.5.1/24')
    r1.cmd('ip route add 10.0.6.0/24 via 10.100.0.2 dev r1-eth6')
    r1.cmd('ip route add 10.0.7.0/24 via 10.100.0.2 dev r1-eth6')

    r2.cmd('ip route list')
    r2.cmd('ifconfig r2-eth1 10.0.6.1/24')
    r2.cmd('ip route add 10.0.1.0/24 via 10.100.0.1 dev r2-eth2')
    r2.cmd('ip route add 10.0.2.0/24 via 10.100.0.1 dev r2-eth2')
    r2.cmd('ip route add 10.0.3.0/24 via 10.100.0.1 dev r2-eth2')
    r2.cmd('ip route add 10.0.4.0/24 via 10.100.0.1 dev r2-eth2')
    r2.cmd('ip route add 10.0.5.0/24 via 10.100.0.1 dev r2-eth2')
    r2.cmd('ip route add 10.0.7.0/24 via 10.101.0.2 dev r2-eth3')

    r3.cmd('ip route list')
    r3.cmd('ifconfig r3-eth1 10.0.7.1/24')
    r3.cmd('ip route add 10.0.1.0/24 via 10.101.0.1 dev r3-eth2')
    r3.cmd('ip route add 10.0.2.0/24 via 10.101.0.1 dev r3-eth2')
    r3.cmd('ip route add 10.0.3.0/24 via 10.101.0.1 dev r3-eth2')
    r3.cmd('ip route add 10.0.4.0/24 via 10.101.0.1 dev r3-eth2')
    r3.cmd('ip route add 10.0.5.0/24 via 10.101.0.1 dev r3-eth2')
    r3.cmd('ip route add 10.0.6.0/24 via 10.101.0.1 dev r3-eth2')

    # Declare host in topology
    h1 = net['h1']
    h2 = net['h2']
    h3 = net['h3']
    h4 = net['h4']
    h5 = net['h5']
    h6 = net['h6']
    h7 = net['h7']
    access_list = [h1,h2,h3,h4,h5]
    # Standardize Q discipline from hosts to routers
    for h in range(1,6):
        access_list[h-1].cmd(f'tc qdisc del dev h{h}-eth root')
        access_list[h-1].cmd(f'tc qdisc add dev h{h}-eth root fq')
    for h in [r1, r2, r3, h1, h2, h3, h4, h5, h6, h7]: h.cmd('/usr/sbin/sshd')

    # Bottleneck open up iperf to act as server
    h6.popen('iperf3 -s -p 5200')
    h6.popen('iperf3 -s -p 5201')
    h6.popen('iperf3 -s -p 5202')
    h6.popen('iperf3 -s -p 5203')
    h6.popen('iperf3 -s -p 5204')
    h7.popen('iperf3 -s -p 5200')
    h7.popen('iperf3 -s -p 5201')
    h7.popen('iperf3 -s -p 5202')
    h7.popen('iperf3 -s -p 5203')
    h7.popen('iperf3 -s -p 5204')


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
    algorithm.router_command(r1, "r1-eth6")
    algorithm2 = Algorithms(sys.argv[2])
    algorithm2.router_command(r2, "r2-eth2")
    algorithm2.router_command(r2, "r2-eth3")
    algorithm3 = Algorithms(sys.argv[3])
    algorithm3.router_command(r3, "r3-eth2")

    ##==============================================================================
    ## Ensure the hosts run iperf run on the same time
    threads = []
    for h in range(1,6):
        port = f'520{h-1}'
        #threads.append(multiprocessing.Process(target=algorithm.udpConnect, args=(access_list[h-1], port, "10.0.6.10", "1000g")))
        #threads.append(multiprocessing.Process(target=algorithm.tcpConnect, args=(access_list[h-1], port, "10.0.6.10", "1g", True)))
        threads.append(multiprocessing.Process(target=algorithm.tcpConnect, args=(access_list[h-1], port, "10.0.7.10", "1g", True)))

    for i in threads:
        i.start()
        
    for i in threads:
        i.join()
    CLI( net)
    net.stop()

setLogLevel('info')
main()
