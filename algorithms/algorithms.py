from .sfb import SFB
from .fq_codel import FQ_CODEL
from .ets import ETS
from .red import RED
from .htb import HTB
from .codel import CODEL
from .cbq import CBQ

class Algorithms:
    def __init__(self, name, subAlgor='pfifo'):
        try:
            if name == "sfb":
                self.algor = SFB()
            elif name == "fq_codel":
                self.algor = FQ_CODEL()
            elif name == "ets":
                self.algor = ETS()
            elif name == "red":
                self.algor = RED()
            elif name == "codel":
                self.algor = CODEL()
            elif name == 'htb':
                self.algor = HTB()
            elif name == 'cbq':
                print(f"Current subalgor is {subAlgor}")
                self.algor = CBQ(subAlgor)
        except:
            print("Algorithm not implemented")

    def router_command(self, router, interface):
        print(f"Executing router command for {str(self.algor)}")
        self.algor.router_command(router, interface)
        print(f"Parameter for {str(self.algor)} set")
    
    def udpConnect(self, host, port, target, size):
        print(f"Executing udp flow for {str(host)} on {target}:{port}")
        self.algor.udpConnect(host, port, target, size)
    
    def tcpConnect(self, host, port, target, size, multi=False):
        print(f"Executing tcp flow for {str(host)} on {target}:{port}")
        self.algor.tcpConnect(host, port, target, size, multi)
