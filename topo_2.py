#!/usr/bin/python3
# copyright 2017 Peter Dordal 
# licensed under the Apache 2.0 license
from time import sleep

from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch, Controller, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel, info
import multiprocessing


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
        defaultIP = '10.0.1.1/24'  # IP address for r0-eth1
        r  = self.addNode( 'r', cls=LinuxRouter) # , ip=defaultIP )
        h1 = self.addHost( 'h1', ip='10.0.1.10/24', defaultRoute='via 10.0.1.1' ) # Smartphone
        h2 = self.addHost( 'h2', ip='10.0.2.11/24', defaultRoute='via 10.0.2.1' ) # Door alarm
        h3 = self.addHost( 'h3', ip='10.0.3.12/24', defaultRoute='via 10.0.3.1' ) # Health monitoring device
        h4= self.addHost( 'h4', ip='10.0.4.13/24', defaultRoute='via 10.0.4.1' )
  # Smart coffee maker
        h5 = self.addHost( 'h5', ip='10.0.5.10/24', defaultRoute='via 10.0.5.1' ) # Internet

 # connecting each host to a link to router
 # Each link is bidirectional
 # Can test upload and download
        access_list = [h1,h2,h3,h4]
        for i in range(len(access_list)+1):
            if i == 0:
                continue    
            self.addLink(access_list[i-1], r, intfName1 = 'h%i-eth' % i, intfName2 = 'r-eth%i' % i, 
                 params2 = {'ip' : '10.0.%i.1/24' % i}, bw=10)

 # connect bottleneck link to router
 # Bottleneck link to internet
        self.addLink( h5, r, intfName1 = 'h5-eth', intfName2 = 'r-eth5', 
                 params2 = {'ip' : '10.0.5.1/24'}, 
                 bw=0.01, delay='110ms', max_queue_size=int(10))
 

# Running Evaluation commands using iperf
# iPerf will run between 2 hosts, 

def udpConnect(h, port):
    port_no = port - 1
    h.cmd('iperf3 -c 10.0.5.10 -u -b 1000g -p 520%i -J > h%i_udp_result.json' % (port_no,port))

def tcpConnect(h, port):
    port_no = port - 1
    h.cmd('iperf3 -c 10.0.5.10 -b 1g -p 520%i -J > h%i_tcp_result.json' % (port_no,port))

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
    r.cmd('sysctl net.ipv4.ip_forward=1')

    # Declare host in topology
    h1 = net['h1']
    h2 = net['h2']
    h3 = net['h3']
    h4 = net['h4']
    h5 = net['h5']
    access_list = [h1,h2,h3,h4]
    
    # Standardize Q discipline from hosts to routers
    for h in range(1,5):
        access_list[h-1].cmd('tc qdisc del dev h%i-eth root' % h)
        access_list[h-1].cmd('tc qdisc add dev h%i-eth root fq' % h)
    for h in [r, h1, h2, h3, h4, h5]: h.cmd('/usr/sbin/sshd')

    # Bottleneck open up iperf to act as server
    h5.popen('iperf3 -s -p 5200')
    h5.popen('iperf3 -s -p 5201')
    h5.popen('iperf3 -s -p 5202')
    h5.popen('iperf3 -s -p 5203')
    ## Classless AQM
    # Queue_disc = 'pfifo'
    # r.cmd('tc qdisc del dev r-eth5 root')
    # r.cmd(f'tc qdisc add dev r-eth5 root {Queue_disc}')
## Classful AQM
    
    # Define Q discipline from linux tc (traffic control).
    # Experiment between whatever we send in the chat
    r.cmd('tc qdisc del dev r-eth5 root')
    r.cmd('tc qdisc add dev r-eth5 root handle 1: htb default 10')
    r.cmd('tc class add dev r-eth5 parent 1: classid 1:1 htb rate 10mbit')
    r.cmd('tc class add dev r-eth5 parent 1: classid 1:2 htb rate 100mbit')
    r.cmd('iptables --append FORWARD --table mangle --protocol tcp --dport 5200 --jump MARK --set-mark 2')
    r.cmd('tc filter add dev r-eth5 parent 1:1 protocol ip handle 2 fw classid 1:2')
    # Ensure the hosts run iperf run on the same time
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