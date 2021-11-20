import os

class FQ_CODEL:
    def __init__(self):
        self.filename = "fq_codel"

    def router_command(self, router, interface):
    	# tc qdisc ... fq_codel [ limit PACKETS ] [ flows NUMBER ] [ target TIME ] [ interval TIME ] [ quantum BYTES ] [ ecn | noecn ] [ ce_threshold TIME ] [ memory_limit BYTES ]
        router.cmd(f'tc qdisc del dev {interface} root')
        router.cmd(f'tc qdisc add dev {interface} root fq_codel limit 1000 quantum 300 noecn')

    def getFileDirectory(self, hostname, protocol):
        directory = f'./Results/{self.filename}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        return f"{directory}/{protocol}_{hostname}.json"

    def udpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(host, "udp")
        host.cmd(f'iperf3 -c {target} -u -b {size} -p {port} -J > {fileDirectory}')
    
    def tcpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(str(host), "tcp")
        print(f'FileDirectory is : {fileDirectory}')
        host.cmd(f'iperf3 -c {target} -b {size} -p {port} -J > {fileDirectory}')
        print(f'iperf3 done on {str(host)}')
    
    def __str__(self):
        return self.filename
