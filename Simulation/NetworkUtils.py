import socket

class NetworkUtils:
    def udp_init(self, IP: int, PORT: int) -> socket:
        print("Network Details")
        print("\tUDP target IP: %s" % IP)
        print("\tUDP target port: %s" % PORT)
        
        newSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return newSocket