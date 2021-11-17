from .sfb_2 import SFB
from .ets_2 import ETS
from .red_2 import RED

class Algorithms:
    def __init__(self, name):
        try:
            if name == "sfb":
                self.algor = SFB()
            elif name == "ets":
                self.algor = ETS()
            elif name == "red":
                self.algor = RED()
        except:
            print("Algorithm not implemented")

    def router_command(self, router, interface):
        print("Executing router command for %s" % str(self.algor))
        self.algor.router_command(router, interface)
        print("Parameter for %s set" % str(self.algor))
    
    def udpConnect(self, host, port, target, size):
        print("Executing udp flow for %s on %s:%s" % (str(host),target,port))
        self.algor.udpConnect(host, port, target, size)
    
    def tcpConnect(self, host, port, target, size):
        print("Executing tcp flow for %s on %s:%s" % (str(host),target,port))
        self.algor.tcpConnect(host, port, target, size)