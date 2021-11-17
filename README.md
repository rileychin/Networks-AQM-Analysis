## Networks-AQM-Analysis

For 50.012 Networks 2021 project about AQM analysis

# Note
1. topo.py is for python 3.8.0 above
2. topo_2.py is for python < 3.8.0 

# Requirements
1. Linux VM 
2. ```mininet``` version 2.3.0, install via http://mininet.org/download/
3. python = 3.8.0
4. iperf3

# Topo
```
        10.0.1.0
h1 ------------------ r
    h1-eth     r-eth1

        10.0.2.0
h2 ------------------ r
    h2-eth     r-eth2

        10.0.3.0                  10.0.6.0
h3 ------------------ r||r --------------------- h6
    h3-eth     r-eth3       r-eth6         h6-eth

        10.0.4.0
h4 ------------------ r
    h4-eth     r-eth4

        10.0.5.0
h5 ------------------ r
    h5-eth     r-eth5

# How to run
1. ```sudo python topo.py z``` where z is the algorithm to use for the test. Eg. sfb/ets
2. Evaluations will be placed in json file
3. if want to run manually
4. xterm hn, where n is the host number
5. Note IP of server host, run ```iperf3 -s -p 520x``` where x is the host number
6. xterm hn+1, where n is another host
7. run ```iperf3 -c 10.0.x.10 -u -b 1000g -p 520x ``` where x is the server host number

# Completed
1. Simulated topology (nodes h1-h6, router r)

# TODO
1. Measure performance for diff algos (can also be the ones we never research about)
2. Expand topology & add multiple routers w/ diff queueueeuing discipline
