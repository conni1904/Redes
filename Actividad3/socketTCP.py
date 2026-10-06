import socket

class SocketTCP:
    def __init__(self):
        self.socketudp = None
        self.dir_destino = None
        self.num_secuencia = None

def parse_segment(segment):
    dictionary = {}
    dictionary["ack"]= segment[0]
    print(segment[0])  #pasarlo de bytes a int
    print(type(segment[0])) 
    dictionary["syn"]=segment[1]
    print(segment[1])
    dictionary["fin"]= segment[2]
    print(segment[2])
    dictionary["seq"]= int.from_bytes(segment[3:7])
    dictionary["datos"]= segment[7:]
    return dictionary

def create_segment(dicti):
    ack = dicti["ack"].to_bytes()
    syn = dicti["syn"].to_bytes()
    fin = dicti["fin"].to_bytes()
    seq = dicti["seq"].to_bytes(4)
    datos = dicti["datos"]
    
    return ack+syn+fin+seq+datos

        