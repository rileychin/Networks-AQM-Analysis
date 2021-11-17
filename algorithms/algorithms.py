from .sfb import SFB
from .ets import ETS
from .red import RED

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
        print(f"Executing router command for {str(self.algor)}")
        self.algor.router_command(router, interface)
        print(f"Parameter for {str(self.algor)} set")
    
    def udpConnect(self, host, port, target, size):
        print(f"Executing udp flow for {str(host)} on {target}:{port}")
        self.algor.udpConnect(host, port, target, size)
    
    def tcpConnect(self, host, port, target, size):
        print(f"Executing tcp flow for {str(host)} on {target}:{port}")
        self.algor.tcpConnect(host, port, target, size)