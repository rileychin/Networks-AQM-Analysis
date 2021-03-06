import os

class RED:
    def __init__(self):
        self.filename = "red"

    def router_command(self, router, interface):
        router.cmd(f'tc qdisc del dev {interface} root')
        router.cmd(f'tc qdisc add dev {interface} root red bandwidth 100Mbit limit 25000 avpkt 1000')

    def getFileDirectory(self, hostname, protocol, multi):
        directory = f'./Results/{self.filename}'
        if multi:
            directory = f'./Results/multi/{self.filename}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        return f"{directory}/diff_{protocol}_{hostname}.json"

    def udpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(host, "udp")
        host.cmd(f'iperf3 -c {target} -u -b {size} -p {port} -J > {fileDirectory}')
    
    def tcpConnect(self, host, port, target, size, multi):
        fileDirectory = self.getFileDirectory(str(host), "tcp", multi)
        print(f'FileDirectory is : {fileDirectory}')
        host.cmd(f'iperf3 -c {target} -b {size} -p {port} -J > {fileDirectory}')
        print(f'iperf3 done on {str(host)}')
    
    def __str__(self):
        return self.filename