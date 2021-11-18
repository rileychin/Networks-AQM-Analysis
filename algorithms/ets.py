import os

class ETS:
    def __init__(self):
        self.filename = "ets"

    def router_command(self, router, interface):
        router.cmd(f'tc qdisc del dev {interface} root')
        #router.cmd(f'tc qdisc add dev {interface} root ets')
        # tc  qdisc  ...  ets  [ bands number ] [ strict number ] [ quanta bytes bytes bytes...  ] [priomap band band band...  ]
        #router.cmd(f'tc qdisc add dev {interface} root ets bands 8 strict 8 priomap 7 6 5 4 3 2 1 0 7 7 7 7 7 7 7 7')
        
        #router.cmd(f'tc qdisc add dev {interface} root handle 1: ets bands 5 priomap 4 3 2 1 0')
        router.cmd(f'tc qdisc add dev {interface} root handle 1: ets strict 5 priomap 4 3 2 1 0')

    def getFileDirectory(self, hostname, protocol):
        directory = f'./Results/{self.filename}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        return f"{directory}/{protocol}_{hostname}.json"

    def udpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(host, "udp")
        print("udp size: %s" % str(size))
        host.cmd(f'iperf3 -c {target} -u -b {size} -p {port} -J > {fileDirectory}')
    
    def tcpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(str(host), "tcp")
        print(f'FileDirectory is : {fileDirectory}')
        host.cmd(f'iperf3 -c {target} -b {size} -p {port} -J > {fileDirectory}')
        print(f'iperf3 done on {str(host)}')
    
    def __str__(self):
        return self.filename
