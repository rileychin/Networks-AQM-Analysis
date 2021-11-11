#!/usr/bin/python3
# copyright 2017 Peter Dordal 
# licensed under the Apache 2.0 license
from time import sleep
"""router topology example for TCP competions.
   This remains the default version

router between two subnets:

   h1----+
         |
         r ---- h3
         |
   h2----+

For running a TCP competition, consider the runcompetition.sh script
"""

QUEUE=10
DELAY='110ms'		# r--h3 link
BottleneckBW=8		# Mbit/sec
BBR=False

# reno-bbr parameters:
if BBR:
    DELAY='40ms'	
    QUEUE=267
    # QUEUE=25
    QUEUE=10
    BottleneckBW=10

from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch, Controller, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel, info
import multiprocessing

#h1addr = '10.0.1.2/24'
#h2addr = '10.0.2.2/24'
#h3addr = '10.0.3.2/24'
#r1addr1= '10.0.1.1/24'
#r1addr2= '10.0.2.1/24'
#r1addr3= '10.0.3.1/24'

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
    #def __init__(self, **kwargs):
    #global r
    def build(self, **_opts):     # special names?
        # switch = self.addSwitch('s1')
        defaultIP = '10.0.1.1/24'  # IP address for r0-eth1
        r  = self.addNode( 'r', cls=LinuxRouter) # , ip=defaultIP )
        h1 = self.addHost( 'h1', ip='10.0.1.10/24', defaultRoute='via 10.0.1.1' )
        h2 = self.addHost( 'h2', ip='10.0.2.11/24', defaultRoute='via 10.0.2.1' )
        h3 = self.addHost( 'h3', ip='10.0.3.12/24', defaultRoute='via 10.0.3.1' )
        h4= self.addHost( 'h4', ip='10.0.4.13/24', defaultRoute='via 10.0.4.1' )
        h5 = self.addHost( 'h5', ip='10.0.5.10/24', defaultRoute='via 10.0.5.1' )

        #  h1---80Mbit---r---8Mbit/100ms---h2
 
        # Oct 2020: the params2 method for setting IPv4 addresses
        # doesn't always work; see below
        access_list = [h1,h2,h3,h4]
        for i in range(len(access_list)+1):
            if i == 0:
                continue    
            self.addLink(access_list[i-1], r, intfName1 = f'h{i}-eth', intfName2 = f'r-eth{i}', 
                 params2 = {'ip' : '10.0.{i}.1/24'}, bw=10)

        self.addLink( h5, r, intfName1 = 'h5-eth', intfName2 = 'r-eth5', 
                 params2 = {'ip' : '10.0.5.1/24'}, 
                 bw=0.01, delay=DELAY, max_queue_size=int(QUEUE)) 	# apparently queue is IGNORED here.

# delay is the ONE-WAY delay, and is applied only to traffic departing h3-eth.

# BBW=8: 1 KB/ms, for 1K packets; 110 KB in transit
# BBW=10: 1.25 KB/ms, or 50 KB in transit if the delay is 40 ms.
# queue = 267: extra 400 KB in transit, or 8x bandwidthxdelay

def udpConnect(h, port):
    port_no = port - 1
    h.cmd(f'iperf3 -c 10.0.5.10 -u -b 1000g -p 520{port_no} -J > h{port}_udp_result.json')

def tcpConnect(h, port):
    port_no = port - 1
    h.cmd(f'iperf3 -c 10.0.5.10 -b 1g -p 520{port_no} -J > h{port}_tcp_result.json')

def main():
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
    r.cmd('ifconfig r-eth1 10.0.1.1/24')
    r.cmd('ifconfig r-eth2 10.0.2.1/24')
    r.cmd('ifconfig r-eth3 10.0.3.1/24')
    r.cmd('ifconfig r-eth4 10.0.4.1/24')
    r.cmd('ifconfig r-eth5 10.0.5.1/24')
    r.cmd('sysctl net.ipv4.ip_forward=1')
    r.cmd('tc qdisc change dev r-eth5 handle 10: netem limit {}'.format(QUEUE))

    h1 = net['h1']
    h2 = net['h2']
    h3 = net['h3']
    h4 = net['h4']
    h5 = net['h5']
    access_list = [h1,h2,h3,h4]
    for h in range(1,5):
        access_list[h-1].cmd(f'tc qdisc del dev h{h}-eth root')
        access_list[h-1].cmd(f'tc qdisc add dev h{h}-eth root fq')
    for h in [r, h1, h2, h3, h4, h5]: h.cmd('/usr/sbin/sshd')
    h5.popen('iperf3 -s -p 5200')
    h5.popen('iperf3 -s -p 5201')
    h5.popen('iperf3 -s -p 5202')
    h5.popen('iperf3 -s -p 5203')
    ## Classless AQM
    # Queue_disc = 'pfifo'
    # r.cmd('tc qdisc del dev r-eth5 root')
    # r.cmd(f'tc qdisc add dev r-eth5 root {Queue_disc}')
    ## Classful AQM
    r.cmd('tc qdisc del dev r-eth5 root')
    r.cmd('tc qdisc add dev r-eth5 root handle 1: htb default 10')
    r.cmd('tc class add dev r-eth5 parent 1: classid 1:1 htb rate 10mbit')
    r.cmd('tc class add dev r-eth5 parent 1: classid 1:2 htb rate 100mbit')
    r.cmd('iptables --append FORWARD --table mangle --protocol tcp --dport 5200 --jump MARK --set-mark 2')
    r.cmd('tc filter add dev r-eth5 parent 1:1 protocol ip handle 2 fw classid 1:2')
    threads = []
    for h in range(1,5):
        threads.append(multiprocessing.Process(target=udpConnect, args=(access_list[h-1], h)))
        threads.append(multiprocessing.Process(target=tcpConnect, args=(access_list[h-1], h)))

    for i in threads:
        i.start()
        
    for i in threads:
        i.join()
    CLI( net)
    net.stop()

setLogLevel('info')
main()

"""
This leads to a queuing hierarchy on r with an htb node, 5:0, as the root qdisc. 
The class below it is 5:1. Below that is a netem qdisc with handle 10:, with delay 110.0ms.
We can change the limit (maximum queue capacity) with:

	tc qdisc change dev r-eth1 handle 10: netem limit 5 delay 110.0ms

"""