import os

class CBQ:
    def __init__(self, subAlgor):
        self.filename = "cbq"
        self.subAlgor = subAlgor

    def router_command(self, router, interface):
        router.cmd(f'tc qdisc del dev {interface} root')
        router.cmd(f'tc qdisc add dev {interface} root handle 1: cbq bandwidth 100Mbit avpkt 1000')
        router.cmd(f'tc class add dev {interface} parent 1: classid 1:1 cbq bandwidth 100Mbit rate 100Mbit allot 1514 prio 2 avpkt 1000')
        router.cmd(f'tc class add dev {interface} parent 1: classid 1:2 cbq bandwidth 100Mbit rate 100Mbit allot 1514 prio 1 avpkt 1000')
        router.cmd(f'tc class add dev {interface} parent 1: classid 1:10 cbq bandwidth 100Mbit rate 100Mbit allot 1514 prio 3 avpkt 1000') ##Default class
        router.cmd(f'tc class show dev {interface}')
        if self.subAlgor == 'pfifo':
            router.cmd(f'tc qdisc add dev {interface} parent 1:2 pfifo limit 1000')
            router.cmd(f'tc qdisc add dev {interface} parent 1:10 pfifo limit 1000')
        elif self.subAlgor == 'fq_codel':
            router.cmd(f'tc qdisc add dev {interface} parent 1:2 fq_codel limit 1000 quantum 300 noecn')
            router.cmd(f'tc qdisc add dev {interface} parent 1:10 fq_codel limit 1000 quantum 300 noecn ')
        elif self.subAlgor == 'red':
            router.cmd(f'tc qdisc add dev {interface} parent 1:2 red bandwidth 100Mbit limit 25000 avpkt 1000')
            router.cmd(f'tc qdisc add dev {interface} parent 1:10 red bandwidth 100Mbit limit 25000 avpkt 1000')
        router.cmd('iptables --append FORWARD --table mangle --protocol tcp --dport 5200 --jump MARK --set-mark 2')
        router.cmd('iptables --append FORWARD --table mangle --protocol udp --dport 5200 --jump MARK --set-mark 2')
        # router.cmd('iptables --append FORWARD --table mangle --protocol tcp --dport 5201 --jump MARK --set-mark 2')
        # router.cmd('iptables --append FORWARD --table mangle --protocol udp --dport 5202 --jump MARK --set-mark 2')
        router.cmd(f'tc filter add dev {interface} parent 1:0 protocol ip handle 2 fw classid 1:2')

    def getFileDirectory(self, hostname, protocol):
        directory = f'./Results/{self.filename}/{self.subAlgor}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        return f"{directory}/{protocol}_{hostname}.json"

    def udpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(str(host), "udp")
        host.cmd(f'iperf3 -c {target} -u -b {size} -p {port} -J > {fileDirectory}')
        print(f'UDP iperf3 done on {str(host)}')
        #host.cmd(f'flent udp_flood -p totals -l 60 -H {target} --netperf-control-port {port} -t udpUpload_Testing -o ./Results/{self.filename}/{str(host)}_udpUpload_Testing.png')
    
    def tcpConnect(self, host, port, target, size):
        fileDirectory = self.getFileDirectory(str(host), "tcp")
        print(f'FileDirectory is : {fileDirectory}')
        host.cmd(f'iperf3 -c {target} -b {size} -p {port} -J > {fileDirectory}')
        print(f'iperf3 done on {str(host)}')
        #host.cmd(f'flent tcp_upload -p totals -l 60 -H {target} --netperf-control-port {port} -t tcpUpload_Testing -o ./Results/{self.filename}/{str(host)}_tcpUpload_Testing.png')
    
    def __str__(self):
        return self.filename
