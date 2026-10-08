import socket
import random

class SocketTCP:
    def __init__(self):
        self.socketudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dir_destino = None
        self.num_secuencia = None

    def bind(self, adress):
        self.socketudp.bind(adress)

    def connect(self, adress):
        self.dir_destino = adress
        dictionary= {}
        dictionary["ack"] = 0
        dictionary["syn"]= 1
        dictionary["fin"]= 0
        dictionary["seq"]= random.randint(0, 100)
        dictionary["datos"]= "".encode()
        head = create_segment(dictionary)
        self.num_secuencia= dictionary["seq"]
        self.socketudp.sendto(head, adress)
        print("Pidiendo conexión...")
        message, adress2 = self.socketudp.recvfrom(1024)
        mensaje = parse_segment(message)
        if mensaje["syn"] == 1 and mensaje["ack"] == 1 and mensaje["seq"] == self.num_secuencia + 1:
            puerto = int.from_bytes(mensaje["datos"])
            new_adress = (adress2[0],puerto)
            dictionary= {}
            dictionary["ack"] = 1
            dictionary["syn"]= 0
            dictionary["fin"]= 0
            dictionary["seq"]= mensaje["seq"] +1 
            dictionary["datos"]= "".encode()
            head = create_segment(dictionary)
            self.num_secuencia= dictionary["seq"]
            self.socketudp.sendto(head, adress)
            self.dir_destino = new_adress
            print("Cliente recibe confirmación...")

    def accept(self):
        message, adress = self.socketudp.recvfrom(7)
        mensaje = parse_segment(message)
        if mensaje["syn"] == 1:
            newSocket = SocketTCP()
            newSocket.bind(('0.0.0.0', 0))
            ip = self.socketudp.getsockname()[0]
            puerto = newSocket.socketudp.getsockname()[1]
            newSocket_adress = (ip,puerto)
            dictionary= {}
            dictionary["ack"] = 1
            dictionary["syn"]= 1
            dictionary["fin"]= 0
            dictionary["seq"]= mensaje["seq"] + 1 
            dictionary["datos"]= puerto.to_bytes(2)
            head = create_segment(dictionary)
            self.num_secuencia= dictionary["seq"]
            self.socketudp.sendto(head, adress)
            print("Servidor lo recibió...")
            message, adress = self.socketudp.recvfrom(7)
            mensaje = parse_segment(message)
            if mensaje["ack"] == 1 and mensaje["seq"] == self.num_secuencia + 1:
                # newSocket = SocketTCP()
                newSocket.num_secuencia = mensaje["seq"]
                newSocket.dir_destino = adress
                #newSocket_adress = newSocket.socketudp.getsockname()
                #newSocket.bind(newSocket.dir_destino)
                print(newSocket_adress)
                return [newSocket, newSocket_adress]

    def send(self, message):
        dictionary = {}
        dictionary["ack"] = 0
        dictionary["syn"]= 0
        dictionary["fin"]= 0
        dictionary["seq"]= self.num_secuencia
        dictionary["datos"]= len(message).to_bytes()
        print(len(message))
        print(message)
        print(dictionary["datos"])
        head = create_segment(dictionary)
        adress = ('0.0.0.0', 0)
        print(self.dir_destino)
        self.socketudp.sendto(head, self.dir_destino)
        try:
            self.socketudp.settimeout(0.5)
            # comentario
            response, adress3 = self.socketudp.recvfrom(1024)
            print("primer recv")
            respuesta = parse_segment(response)
            if respuesta["ack"] == 1 and respuesta["seq"] == self.num_secuencia + 1:
                self.num_secuencia = respuesta["seq"] + 1
                bloque = (len(message) + 15) // 16
                for i in range(bloque):
                    dic = {}
                    dic["ack"]= 0
                    dic["syn"]= 0
                    dic["fin"]= 0
                    dic["seq"]= self.num_secuencia
                    dic["datos"]= message[i * 16 : (i + 1) * 16]
                    segmento = create_segment(dic)
                    while True:
                        #try:
                        self.socketudp.sendto(segmento, self.dir_destino)
                        self.socketudp.settimeout(0.5)
                        response, adress3 = self.socketudp.recvfrom(1024)
                        respuesta = parse_segment(response)
                        if respuesta["ack"] == 1 and respuesta["seq"] == self.num_secuencia + 1:
                            self.num_secuencia = respuesta["seq"] +1
                            break
                        # except:
                        #     print(f"Reenviando sección {i}")
                
        except:
            print("fallo al enviar")
            self.send(message)


        
    def recv (self, buffer_size):
        largo_mensaje = 0
        response, adress = self.socketudp.recvfrom(1024)
        print("recibe largo ")
        respuesta = parse_segment(response)
        largo_mensaje = int.from_bytes(respuesta["datos"])
        print(largo_mensaje)
        print(respuesta["datos"])
        self.num_secuencia = respuesta["seq"] + 1
        mensaje = "".encode()

        while len(mensaje) < largo_mensaje:
            valido = False
            while not valido:
                dic = {}
                dic["ack"]= 1
                dic["syn"]= 0
                dic["fin"]= 0
                dic["seq"]= self.num_secuencia
                dic["datos"]= "".encode()
                head = create_segment(dic)
                self.socketudp.sendto(head, self.dir_destino)
                response, adress = self.socketudp.recvfrom(1024)
                print(mensaje.decode())
                respuesta = parse_segment(response)
                if respuesta["seq"] == self.num_secuencia + 1:
                    mensaje += respuesta["datos"]
                    valido = True
                    self.num_secuencia = respuesta["seq"] + 1
            print(len(mensaje))

        return mensaje



def parse_segment(segment):
    dictionary = {}
    dictionary["ack"]= segment[0]  
    dictionary["syn"]=segment[1]
    dictionary["fin"]= segment[2]
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

                            





