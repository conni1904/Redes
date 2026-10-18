import socket
from socketUDP import SocketUDP 
from slidingWindowCC import SlidingWindowCC
import random
from threading import Timer
from CongestionControl import CongestionControl

class SocketTCP:
    def __init__(self):
        self.socketudp = SocketUDP()
        self.dir_destino = None
        self.num_secuencia = None
        self.buffer_acumulado = b""


    def divide_message(self, message, tamano):
        lista = [str(len(message)).encode()]
        for i in range(0, len(message), tamano):
            lista.append(message[i:i + tamano])
        return lista




    def wrap_data_as_segment(self, data, seq):
        dic = {}
        dic["ack"] = 0
        dic["syn"] = 0
        dic["fin"] = 0
        dic["seq"] = seq
        dic["datos"] = data
        return create_segment(dic)
        

    def is_valid_ack_stop_and_wait(self, segment, response):
        segmento_parseado = parse_segment(segment)
        respuesta_parseada = parse_segment(response)
        largo = len(segmento_parseado["datos"])
        if respuesta_parseada["seq"] == segmento_parseado["seq"]:
            return True
        else:
            return False



    def bind(self, adress):
        self.socketudp.bind(adress)

    def connect(self, adress):
        syn = {}
        syn["ack"] = 0
        syn["syn"] = 1
        syn["fin"] = 0
        syn["seq"] = random.randint(0,100)
        syn["datos"] = "".encode()
        self.num_secuencia = syn["seq"]
        self.socketudp.socket_udp.settimeout(0.5)

        while True:
            try:
                self.socketudp.socket_udp.sendto(create_segment(syn), adress)
                message, adress2 = self.socketudp.socket_udp.recvfrom(23)

            except socket.timeout:
                print("Se perdió el SYN o el SYN-ACK, reenviando...")
                continue

            mensaje = parse_segment(message)
            if (mensaje["syn"] == 1 and mensaje["ack"] == 1
                    and mensaje["seq"] == self.num_secuencia + 1):
                break

        puerto = int.from_bytes(mensaje["datos"][:2])
        self.dir_destino = (adress2[0], puerto)
        self.num_secuencia = mensaje["seq"] + 1

        ack = {}
        ack["ack"] = 1
        ack["syn"] = 0
        ack["fin"] = 0
        ack["seq"] = self.num_secuencia
        ack["datos"] = "".encode()
        self.socketudp.socket_udp.sendto(create_segment(ack), adress)

            
    def accept(self):
        self.socketudp.socket_udp.settimeout(None)
        while True:
            message, adress = self.socketudp.socket_udp.recvfrom(23)
            mensaje = parse_segment(message)
            if mensaje["syn"] == 1 and mensaje["ack"] == 0:
                break

        newSocket = SocketTCP()
        newSocket.bind(('0.0.0.0', 0))
        puerto = newSocket.socketudp.socket_udp.getsockname()[1]
        newSocket_adress = (self.socketudp.socket_udp.getsockname()[0], puerto)

        synack = {}
        synack["ack"] =1
        synack["syn"] =1
        synack["fin"] =0
        synack["seq"] = mensaje["seq"] + 1
        synack["datos"] = puerto.to_bytes(2, "big")
        head = create_segment(synack)

        while True:
            self.socketudp.socket_udp.settimeout(0.25)
            self.socketudp.socket_udp.sendto(head, adress)

            #ACK normal, llega al socket de escucha
            
            try:
                message, adress_cli = self.socketudp.socket_udp.recvfrom(23)
                m = parse_segment(message)
                if (m["syn"] == 0 and m["ack"] == 1
                        and m["seq"] == synack["seq"] + 1):
                    break
            except socket.timeout:
                pass

            # caso feo, el ACK se perdió y el cliente ya mandó datos
            newSocket.socketudp.socket_udp.settimeout(0.25)
            try:
                message, adress_cli = newSocket.socketudp.socket_udp.recvfrom(23)
                m = parse_segment(message)
                if m["syn"] == 0 and m["ack"] == 0 and m["fin"] == 0:
                    break
            except socket.timeout:
                print("Reenviando SYN-ACK...")

        newSocket.num_secuencia = synack["seq"] + 1   
        newSocket.dir_destino = adress_cli

        self.socketudp.socket_udp.settimeout(None)
        newSocket.socketudp.socket_udp.settimeout(None)
        return [newSocket, newSocket_adress]


    def send(self, message, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            self.send_using_stop_and_wait(message)
        elif mode == "go_back_n":
            self.send_using_go_back_n(message)



    def send_using_stop_and_wait(self, message):
        # el primer trozo es el largo, los siguientes son el mensaje en pedazos de 16
            trozos = [len(message).to_bytes(2, "big")]
            for i in range(0, len(message), 16):
                trozos.append(message[i:i + 16])
    
            self.socketudp.settimeout(0.5)
            for trozo in trozos:
                seq = self.num_secuencia + 1
                dic = {}
                dic["ack"] = 0
                dic["syn"] = 0
                dic["fin"] = 0
                dic["seq"] = seq
                dic["datos"] = trozo
                segmento = create_segment(dic)
    
                while True:
                    self.socketudp.sendto(segmento, self.dir_destino)
                    try:
                        response, _ = self.socketudp.recvfrom(23)
                    except socket.timeout:
                        print("Reenviando segmento...")
                        continue
                    respuesta = parse_segment(response)
                    if respuesta["ack"] == 1 and respuesta["seq"] == seq + 1:
                        self.num_secuencia = respuesta["seq"]
                        break

    def send_using_go_back_n(self, message):
        data_list = self.divide_message(message, 16)
        initial_seq = self.num_secuencia + 1
        
        data_to_send = SlidingWindowCC(8, data_list, initial_seq)
      
        
        wnd_index = 0
        self.socketudp.set_timer_list_length(1)
        self.socketudp.settimeout(0.5)
        siguiente= 0
        while True:
            #Para enviar todo lo que se pueda de la ventana
            while siguiente < 8 and data_to_send.get_data(siguiente) is not None:
                
                current_data = data_to_send.get_data(siguiente)
                current_seq = data_to_send.get_sequence_number(siguiente)
                current_segment = self.wrap_data_as_segment(current_data, current_seq)
                
                #primero de la ventana marca el tiempo
                if siguiente == 0:
                    self.socketudp.sendto(current_segment, self.dir_destino, timer_index=0)
                #los siguientes solo se envian
                else:
                    self.socketudp.sendto(current_segment, self.dir_destino) 
                siguiente += 1
            
            if data_to_send.get_data(0) is None:
                
                break  
            try:
                answer, address = self.socketudp.recvfrom(23)
                respuesta = parse_segment(answer)
                

                if respuesta["ack"] ==1:
                    

                    #los pasos que avanza en caso de perder el ack
                    pasos = 0 
                    for i in range(8):
                        secuencia_i = data_to_send.get_sequence_number(i)
                        
                        if secuencia_i is not None and respuesta["seq"] >= secuencia_i:
                            pasos +=1
                        else:
                            break
                   
                    if pasos > 0:
                        self.socketudp.stop_timer(timer_index=0) # solo hay un timer
                        data_to_send.move_window(pasos)
                        self.num_secuencia = respuesta["seq"]
                        siguiente -= pasos
                        if data_to_send.get_data(0) is not None:
                            
                            self.socketudp.timer_list[0] = Timer(self.socketudp.timeout, self.socketudp._time_up_function, args=(0,))

                            

            except TimeoutError:
                ("reenviando ventana")
                self.socketudp.stop_timer(timer_index=0)
                siguiente=0

        try:
            self.socketudp.stop_timer(0)
        except:
            pass
        print("send terminado")

        
        
        



        
    def recv(self, buff_size, mode="stop_and_wait"):
        if mode == "stop_and_wait":
            return self.recv_using_stop_and_wait(buff_size)
        if mode == "go_back_n":
            return self.recv_using_go_back_n(buff_size)


    def recv_using_stop_and_wait(self, buffer_size):
        if len(self.buffer_acumulado) == 0:
            largo_mensaje = None
            mensaje = "".encode()
            while largo_mensaje is None or len(mensaje) < largo_mensaje:
                response, _ = self.socketudp.recvfrom(23)
                respuesta = parse_segment(response)

                if respuesta["seq"] == self.num_secuencia + 1:
                    if largo_mensaje is None:
                        largo_mensaje = int.from_bytes(respuesta["datos"][:2], "big")
                    else:
                        mensaje += respuesta["datos"]
                    self.num_secuencia = respuesta["seq"] + 1

                # nuevo o duplicado: siempre se responde con el último ACK
                dic = {}
                dic["ack"] = 1
                dic["syn"] = 0
                dic["fin"] = 0
                dic["seq"] = self.num_secuencia
                dic["datos"] = "".encode()
                self.socketudp.sendto(create_segment(dic), self.dir_destino)

            self.buffer_acumulado = mensaje

        retorno = self.buffer_acumulado[:buffer_size]
        self.buffer_acumulado = self.buffer_acumulado[buffer_size:]
        return retorno

    
    def recv_using_go_back_n(self, buffer_size):
        if len(self.buffer_acumulado) == 0:
            largo_mensaje = None
            mensaje = "".encode()
            largo_anterior = -1
            while largo_mensaje is None or len(mensaje) < largo_mensaje:
                response, _ = self.socketudp.recvfrom(23)
                respuesta = parse_segment(response)
                
               
        
                if respuesta["seq"]== self.num_secuencia +1 and largo_mensaje is None:
                    largo_mensaje = int(respuesta["datos"].decode())
                    self.num_secuencia = respuesta["seq"]
                
                elif respuesta["seq"] == self.num_secuencia + largo_anterior:
                
                    mensaje += respuesta["datos"]
                    self.num_secuencia = respuesta["seq"]

               
                largo_anterior = len(respuesta["datos"])
                # nuevo o duplicado: siempre se responde con el último ACK
                dic = {}
                dic["ack"] = 1
                dic["syn"] = 0
                dic["fin"] = 0
                dic["seq"] = self.num_secuencia
                dic["datos"] = "".encode()
                self.socketudp.settimeout(60.0)
                self.socketudp.sendto(create_segment(dic), self.dir_destino)
            
                

                
            self.buffer_acumulado = mensaje
        retorno = self.buffer_acumulado[:buffer_size]
        self.buffer_acumulado = self.buffer_acumulado[buffer_size:]
        return retorno



    def close(self):
        seq_fin = self.num_secuencia + 1
        fin = {}
        fin["ack"] = 0
        fin["syn"] = 0
        fin["fin"] = 1
        fin["seq"] =seq_fin
        fin["datos"] = "".encode()
        segmento_fin = create_segment(fin)

        self.socketudp.settimeout(0.5)
        timeouts = 0
        recibido = False
        while timeouts < 3 and not recibido:
            self.socketudp.sendto(segmento_fin, self.dir_destino)
            try:
                # se ignoran segmentos que no sean el FIN+ACK esperado
                while True:

                    response, _ = self.socketudp.recvfrom(23)
                    respuesta = parse_segment(response)
                    if (respuesta["ack"] == 1 and respuesta["fin"] == 1
                            and respuesta["seq"] == seq_fin + 1):
                        recibido = True
                        break
            except socket.timeout:
                timeouts += 1
                print(" reenviando FIN...")
       
        if recibido:
           
            self.num_secuencia = seq_fin + 1
            ack= {}
            ack["ack"]= 1
            ack["syn"]= 0
            ack["fin"]=0
            ack["seq"]= self.num_secuencia + 1
            ack["datos"]= "".encode()
            segmento_ack = create_segment(ack)

            
            for i in range(3):
               
                self.socketudp.socket_udp.sendto(segmento_ack, self.dir_destino)
                try:
                    self.socketudp.recvfrom(23)
                except socket.timeout:
                    
                    self.socketudp.socket_udp.settimeout(0.5)
                    pass
        else:
            print("close: no hubo respuesta, se asume que la contraparte cerró")

        self.socketudp.close()
        print("Conexión cerrada")


    def recv_close(self):
        self.socketudp.settimeout(None)

        try:
            self.socketudp.stop_timer(0)
        except:
            pass

        while True:
            message, _ = self.socketudp.recvfrom(23)
            mensaje = parse_segment(message)
            if mensaje["fin"] == 1 and mensaje["seq"] == self.num_secuencia + 1:
                break
            # duplicado de datos: se perdió nuestro último ACK, se reenvía
            dic = {}
            dic["ack"] = 1
            dic["syn"] = 0
            dic["fin"] = 0
            dic["seq"] = self.num_secuencia
            dic["datos"] = "".encode()
            self.socketudp.socket_udp.sendto(create_segment(dic), self.dir_destino)

        fin_ack = {}
        fin_ack["ack"] = 1
        fin_ack["syn"] = 0
        fin_ack["fin"] = 1
        fin_ack["seq"] = mensaje["seq"] + 1
        fin_ack["datos"] = "".encode()
        self.num_secuencia = fin_ack["seq"]
        segmento = create_segment(fin_ack)

        self.socketudp.settimeout(0.5)
        timeouts = 0
        ack_final = False
        while timeouts < 3 and not ack_final:
            self.socketudp.socket_udp.sendto(segmento, self.dir_destino)
            try:
                while True:
                    message, _ = self.socketudp.recvfrom(23)
                    m = parse_segment(message)
                    if (m["ack"] == 1 and m["fin"] == 0
                            and m["seq"] == self.num_secuencia + 1):
                        ack_final = True
                        break
                    if m["fin"] == 1:
                        # el cliente reenvió el FIN: se perdió nuestro FIN+ACK
                        self.socketudp.socket_udp.sendto(segmento, self.dir_destino)
            except socket.timeout:
                timeouts += 1
                print("reenviando FIN+ACK...")

        if not ack_final:
            print("recv_close: no llegó el ACK final, se asume que la otra parte cerró")
        self.socketudp.close()
        print("Terminó conexión")

    


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