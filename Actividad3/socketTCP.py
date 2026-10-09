import socket
import random

class SocketTCP:
    def __init__(self):
        self.socketudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dir_destino = None
        self.num_secuencia = None
        self.buffer_acumulado = b""

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
        while True:
            try:
                self.socketudp.sendto(head, adress)
                print("Pidiendo conexión...")
                self.socketudp.settimeout(0.5)
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
                break
            except:
                print("se perdio el primer SYN")
        


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
            ack_recibido = False
            while not ack_recibido:
                try:
                    self.socketudp.sendto(head, adress)
                    self.socketudp.settimeout(0.5)
                    message, adress = self.socketudp.recvfrom(1024)
                    mensaje = parse_segment(message)
                    #caso que se recibe ultimo ack normal
                    if mensaje["ack"] == 1 and mensaje["seq"] == self.num_secuencia + 1:
                        newSocket.num_secuencia = mensaje["seq"] +1
                        newSocket.dir_destino = adress
                        ack_recibido = True
                        print("recibio el ultimo ack")

                    #Caso feo
                    elif mensaje["ack"] == 0 and mensaje["syn"] == 0 and mensaje["fin"] == 0:
                        newSocket.num_secuencia = mensaje["seq"] - 1
                        newSocket.dir_destino = adress
                        newSocket.buffer_acumulado += message
                        print("se perdio el ultimo ack y se envian datosss")
                        ack_recibido = True
                    

                except:
                    print ("Reenviando syn ack")

            return [newSocket, newSocket_adress]


#REVUSAR !! NO SE ENVIA EL PRIMER MENSAJE
    def send(self, message):
        dictionary = {}
        dictionary["ack"] = 0
        dictionary["syn"]= 0
        dictionary["fin"]= 0
        dictionary["seq"]= self.num_secuencia
        dictionary["datos"]= len(message).to_bytes(2)
        head = create_segment(dictionary)
        self.socketudp.sendto(head, self.dir_destino) 
        print(f"largo de mensaje a enviar: {len(message)}") 
        print(f"primer numero de secuencia: {self.num_secuencia}") 
        try:
            self.socketudp.settimeout(0.5)
            # comentario
            response, adress3 = self.socketudp.recvfrom(1024)
            respuesta = parse_segment(response)
            print(f"self secuencia : {self.num_secuencia}")
            print(f"secuencia de respuesta: {respuesta["seq"]}")
            print(f"respuesta datos: {respuesta["datos"].decode()}")
            if respuesta["ack"] == 1 and respuesta["seq"] == self.num_secuencia + 1:
                print("Entra al if ")
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
                        try:
                            print(f"mensaje a enviar {dic["datos"]}")
                            self.socketudp.sendto(segmento, self.dir_destino)
                            self.socketudp.settimeout(0.5)
                            response, adress3 = self.socketudp.recvfrom(1024)
                            respuesta = parse_segment(response)
                            if respuesta["ack"] == 1 and respuesta["seq"] == self.num_secuencia + 1:
                                self.num_secuencia = respuesta["seq"] +1
                                break
                        except:
                            print(f"Reenviando sección {i}")
                
        except:
            print("fallo al enviar")
            self.send(message)
        print("-------------------------------------------------------")


        
    def recv (self, buffer_size):
        if len(self.buffer_acumulado) == 0:
            while True:

                largo_mensaje = 0
                response, adress = self.socketudp.recvfrom(1024)
                respuesta = parse_segment(response)
                print(f"respuesta secuencia: {respuesta['seq']}")
                print(f"self secuencia: {self.num_secuencia}")
                if respuesta["seq"] == self.num_secuencia + 1: #respuesta apropiada
                    break
                print("recibió basura...")
                dic = {}
                dic["ack"]= 1
                dic["syn"]= 0
                dic["fin"]= 0
                dic["seq"]= self.num_secuencia
                dic["datos"]= "".encode()
                head = create_segment(dic)
                self.socketudp.sendto(head, self.dir_destino)

            print("recibe largo ")
            largo_mensaje = int.from_bytes(respuesta["datos"])
            print(f"Largo mensaje original: {largo_mensaje}")
            print(respuesta["datos"].decode())
            print(respuesta["seq"])
            self.num_secuencia = respuesta["seq"] + 1
            mensaje = "".encode()
            dic = {}
            dic["ack"]= 1
            dic["syn"]= 0
            dic["fin"]= 0
            dic["seq"]= self.num_secuencia
            dic["datos"]= "".encode()
            head = create_segment(dic)
            self.socketudp.sendto(head, self.dir_destino)
            print(f"segundo numero de secuencia {self.num_secuencia}")
            while len(mensaje) < largo_mensaje:
                print("entra al primer whilw")
                valido = False
                while not valido:
                    print("entrando al segundo while")
                    response, adress = self.socketudp.recvfrom(1024)
                    respuesta = parse_segment(response)
                    print(respuesta)
                    if len(respuesta["datos"]) != 16 and respuesta["seq"] == self.num_secuencia + 1:
                        print("mensaje incompleto")
                        # print(respuesta["datos"].decode())
                        # print(largo_mensaje)
                        break
                    if respuesta["seq"] == self.num_secuencia + 1:
                        # print(respuesta["datos"].decode())
                        print("llego completo")
                        valido = True
                        self.num_secuencia = respuesta["seq"] + 1
                        mensaje += respuesta["datos"]
                    dic = {}
                    dic["ack"]= 1
                    dic["syn"]= 0
                    dic["fin"]= 0
                    dic["seq"]= self.num_secuencia
                    dic["datos"]= "".encode()
                    head = create_segment(dic)
                    self.socketudp.sendto(head, self.dir_destino)
            self.buffer_acumulado = mensaje

        retorno = self.buffer_acumulado[:buffer_size]
        self.buffer_acumulado = self.buffer_acumulado[buffer_size:]
        print("-----------------------------------------")
        return retorno


    def close(self):
            #hay que enviar el fin
            dic_fin = {}
            dic_fin["ack"] = 0
            dic_fin["syn"] = 0
            dic_fin["fin"] = 1
            dic_fin["seq"] = self.num_secuencia
            dic_fin["datos"] = "".encode()
            segmento_final = create_segment(dic_fin)
    
            ack_recv = False
            while not ack_recv:
                
                print(self.dir_destino)
                self.socketudp.sendto(segmento_final, self.dir_destino)
                self.socketudp.settimeout(0.5)
                response, _ = self.socketudp.recvfrom(1024)
                print("Se recibió el primer ack")
                respuesta = parse_segment(response)

                if respuesta["ack"] == 1 and respuesta["fin"] == 1 and respuesta["seq"] == self.num_secuencia + 1:
                    self.num_secuencia = respuesta["seq"] + 1
                    ack_recv = True
                # except socket.timeout:
                #     print("Reenviando segmento final...")
    
    
            #enviamos ack final
            dic_ack = {}
            dic_ack["ack"] = 1
            dic_ack["syn"] = 0
            dic_ack["fin"] = 0
            dic_ack["seq"] = self.num_secuencia
            dic_ack["datos"] = "".encode()
            self.socketudp.sendto(create_segment(dic_ack), self.dir_destino)
    
            #liberamos
            self.socketudp.close()
            print("Conexión cerrada")


    def recv_close(self):
        message, adress = self.socketudp.recvfrom(1024)
        print("recibio solicitud de cierre")
        mensaje = parse_segment(message)
        if mensaje["fin"] == 1 and mensaje["seq"] == self.num_secuencia + 1:
            dic_ack = {}
            dic_ack["ack"] = 1
            dic_ack["syn"] = 0
            dic_ack["fin"] = 1
            dic_ack["seq"] = mensaje["seq"] + 1
            dic_ack["datos"] = "".encode()
            self.num_secuencia = dic_ack["seq"]
            self.socketudp.sendto(create_segment(dic_ack), self.dir_destino)
            print("envia primer ack de cierre")
            message, adress = self.socketudp.recvfrom(1024)
            mensaje = parse_segment(message)
            if mensaje["ack"] == 1 and mensaje["seq"] == self.num_secuencia + 1:
                self.socketudp.close()
                print ("Terminó conexión")






def parse_segment(segment):
    dictionary = {}
    dictionary["ack"]= segment[0]  
    dictionary["syn"]=segment[1]
    dictionary["fin"]= segment[2]
    dictionary["seq"]= int.from_bytes(segment[3:7])
    dictionary["datos"]= segment[7:]
    return dictionary

def create_segment(dicti):
    ack = dicti["ack"].to_bytes(1)
    syn = dicti["syn"].to_bytes(1)
    fin = dicti["fin"].to_bytes(1)
    seq = dicti["seq"].to_bytes(4)
    datos = dicti["datos"]
    
    return ack+syn+fin+seq+datos