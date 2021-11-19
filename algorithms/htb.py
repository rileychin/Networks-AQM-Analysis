import os

class HTB:
    def __init__(self):
        self.filename = "htb"

    def router_command(self, router, interface):
        router.cmd(f'tc qdisc del dev {interface} root')
        router.cmd(f'tc qdisc add dev {interface} root handle 1: htb default 10')
        router.cmd(f'tc class add dev {interface} parent 1: classid 1:1 htb rate 1000mbit')
        router.cmd(f'tc class add dev {interface} parent 1: classid 1:2 htb rate 1000mbit')
        router.cmd(f'tc class add dev {interface} parent 1: classid 1:10 htb rate 500mbit')
        router.cmd('iptables --append FORWARD --table mangle --protocol tcp --dport 5200 --jump MARK --set-mark 2')
        router.cmd('iptables --append FORWARD --table mangle --protocol tcp --dport 5201 --jump MARK --set-mark 2')
        router.cmd('iptables --append FORWARD --table mangle --protocol udp --dport 5200 --jump MARK --set-mark 2')
        router.cmd(f'tc filter add dev {interface} parent 1:0 protocol ip handle 2 fw classid 1:2')

    def getFileDirectory(self, hostname, protocol):
        directory = f'./Results/{self.filename}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        return f"{directory}/last_{protocol}_{hostname}.json"

    def udpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(str(host), "udp")
        host.cmd(f'iperf3 -c {target} -u -b {size} -p {port} -J > {fileDirectory}')
        print(f'UDP iperf3 done on {str(host)}')
        #host.cmd(f'flent udp_flood -p totals -l 60 -H {target} --netperf-control-port {port} -t udpUpload_Testing -o ./Results/{self.filename}/{str(host)}_udpUpload_Testing.png')
    
    def tcpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(str(host), "tcp")
        print(f'FileDirectory is : {fileDirectory}')
        host.cmd(f'iperf3 -V -t 120 -c {target} -b {size} -p {port} -J > {fileDirectory}')
        print(f'iperf3 done on {str(host)}')
        #host.cmd(f'flent tcp_upload -p totals -l 60 -H {target} --netperf-control-port {port} -t tcpUpload_Testing -o ./Results/{self.filename}/{str(host)}_tcpUpload_Testing.png')
    
    def __str__(self):
        return self.filename
