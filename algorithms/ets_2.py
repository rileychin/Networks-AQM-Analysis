import os

class ETS:
    def __init__(self):
        self.filename = "ets"

    def router_command(self, router, interface):
        router.cmd('tc qdisc del dev %s root' % interface)
        router.cmd('tc qdisc add dev %s root ets' % interface)

    def getFileDirectory(self, hostname, protocol):
        directory = './Results/%s' % self.filename
        if not os.path.exists(directory):
            os.makedirs(directory)
        return "%s/%s_%s.json" % (directory,protocol,hostname)

    def udpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(host, "udp")
        host.cmd('iperf3 -c %s -u -b %s -p %s -J > %s' % (target,size,port,fileDirectory))
    
    def tcpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(str(host), "tcp")
        print('FileDirectory is : %s' % fileDirectory)
        host.cmd('iperf3 -c %s -b %s -p %s -J > %s' % (target,size,port,fileDirectory))
        print('iperf3 done on %s' % str(host))
    
    def __str__(self):
        return self.filename