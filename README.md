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

# How to run
1. ```python topo.py```
2. Evaluations will be placed n json file
3. if want to run manually
4. xterm hn, where n is the host number
5. Note IP of server host, run ```iperf3 -s -p 520x``` where x is the host number
6. xterm hn+1, where n is another host
7. run ```iperf3 -c 10.0.x.10 -u -b 1000g -p 520x ``` where x is the host + 1 number

# Completed
1. Simulated topology (nodes h1-h5, router r)

# TODO
1. Measure performance for diff algos (can also be the ones we never research about)
2. Expand topology & add multiple routers w/ diff queueueeuing discipline
