import socket
from socketUDP import SocketUDP 
from Actividad4.slidingWindowCC import SlidingWindowCC
import random
from threading import Timer
from CongestionControl import CongestionControl

class SocketTCP:
    def __init__(self):
        self.socketudp = SocketUDP()
        self.dir_destino = None
        self.num_secuencia = None
        self.buffer_acumulado = b""
        self.congestion_controler_on = False
        self.number_of_segment = 0 

    def setter(self, nuevo_valor):
        self.congestion_controler_on = nuevo_valor


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
        self.socketudp.socket_udp.settimeout(0.0)
            
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

        self.socketudp.socket_udp.settimeout(0.0)
        newSocket.socketudp.socket_udp.settimeout(0.0)
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
        print("--------------------------")
        print("inicio del send")
        congestion_controler = CongestionControl(8)

        data_list = self.divide_message(message, 8)
        initial_seq = self.num_secuencia + 1
        
        if self.congestion_controler_on:
            window_size = congestion_controler.get_MSS_in_cwnd()
            
        else:
            window_size = 8
        data_window= SlidingWindowCC(window_size,data_list, initial_seq)

        print(data_window)
        if congestion_controler.get_MSS_in_cwnd() == 1:
            print("valor de window size = 1")
        
        self.socketudp.set_timer_list_length(1)
        self.socketudp.settimeout(0.5)
        siguiente= 0
        while True:
            #Para enviar todo lo que se pueda de la ventana
            while siguiente < window_size and data_window.get_data(siguiente) is not None:
                
                current_data = data_window.get_data(siguiente)
                current_seq = data_window.get_sequence_number(siguiente)
                current_segment = self.wrap_data_as_segment(current_data, current_seq)
                print(f"se envia current data: {current_data.decode()} con numero de seq: {current_seq}")
                
                
                self.socketudp.sendto(current_segment, self.dir_destino, timer_index=0)
                self.number_of_segment += 1
                siguiente += 1
            
            if data_window.get_data(0) is None:
                break  

            try:
                answer, address = self.socketudp.recvfrom(23)
                respuesta = parse_segment(answer)
                
                if respuesta["ack"] ==1:
                    print(f"se recibe ack con num seq: {respuesta["seq"]}")
                    #los pasos que avanza en caso de perder el ack
                    pasos = 0 
                    for i in range(window_size):
                        secuencia_i = data_window.get_sequence_number(i)
                        if secuencia_i is not None and respuesta["seq"] >= secuencia_i:
                            pasos +=1
                        else:
                            break
                   
                    if pasos > 0:
                        self.socketudp.stop_timer(timer_index=0) # solo hay un timer
                        data_window.move_window(pasos)
                        self.num_secuencia = respuesta["seq"]
                        siguiente -= pasos
                        if siguiente > 0:
                            self._restart_timer()
                        
                        if self.congestion_controler_on:
                            congestion_controler.event_ack_received()
                            window_size = congestion_controler.get_MSS_in_cwnd()
                            data_window.update_window_size(window_size)
                            print(f"nuevo window size por ack: {window_size}")
                            if (congestion_controler.is_state_slow_start):
                                print("esta en slow start")
                            else:
                                print("esta en congestion avoidance")

            except TimeoutError:
                ("reenviando ventana")
                if self.congestion_controler_on:
                    congestion_controler.event_timeout()
                    window_size = congestion_controler.get_MSS_in_cwnd()
                    data_window.update_window_size(window_size)
                    print(f"nuevo window size por timeout: {window_size}")
                    if (congestion_controler.is_state_slow_start):
                        print("esta en slow start")
                    else:
                        print("esta en congestion avoidance")

                if self.socketudp.timer_list[0] is not None:
                    self.socketudp.stop_timer(0)
                                  
                siguiente=0

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
        print("----------------------")
        print("inicia recived")
        if len(self.buffer_acumulado) == 0:
            largo_mensaje = None
            mensaje = "".encode()
            largo_anterior = 0
            while largo_mensaje is None or len(mensaje) < largo_mensaje:
                response, _ = self.socketudp.recvfrom(23)
                respuesta = parse_segment(response)

                print(f"respuesta seq: {respuesta['seq']}")
                print(f"num secuencia: {self.num_secuencia}")
               
                if respuesta["seq"]== self.num_secuencia +1 and largo_mensaje is None:
                    largo_mensaje = int(respuesta["datos"].decode())
                    self.num_secuencia = respuesta["seq"]
                    print(f"largo de mensaje {largo_mensaje}")
                    largo_anterior = len(respuesta["datos"])
                elif respuesta["seq"] == self.num_secuencia + largo_anterior and largo_mensaje is not None:
                    print("entra en el elif")
                
                    mensaje += respuesta["datos"]
                    self.num_secuencia = respuesta["seq"]
                    largo_anterior = len(respuesta["datos"])

                print(f"largo anterior {largo_anterior}")
                # nuevo o duplicado: siempre se responde con el último ACK
                dic = {}
                dic["ack"] = 1
                dic["syn"] = 0
                dic["fin"] = 0
                dic["seq"] = self.num_secuencia
                print(f"se envia ack con numero seq:{dic['seq']}")
                dic["datos"] = "".encode()
                self.socketudp.socket_udp.sendto(create_segment(dic), self.dir_destino)
            
            self.buffer_acumulado = mensaje
        retorno = self.buffer_acumulado[:buffer_size]
        self.buffer_acumulado = self.buffer_acumulado[buffer_size:]
        print("termina recived")
        return retorno


    def close(self):
        print("----------------------------")
        print("inicia close")
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
            self.socketudp.socket_udp.sendto(segmento_fin, self.dir_destino)
            try:
                # se ignoran segmentos que no sean el FIN+ACK esperado
                while True:

                    response, _ = self.socketudp.socket_udp.recvfrom(23)
                    respuesta = parse_segment(response)
                    if (respuesta["ack"] == 1 and respuesta["fin"] == 1
                            and respuesta["seq"] == seq_fin + 1):
                        recibido = True
                        break
            except :
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
                print("enviando ack final")
                self.socketudp.socket_udp.sendto(segmento_ack, self.dir_destino)
                try:
                    self.socketudp.socket_udp.recvfrom(23)
                except:
                    
                    self.socketudp.socket_udp.settimeout(0.5)
                    pass
        else:
            print("close: no hubo respuesta, se asume que la contraparte cerró")

        self.socketudp.close()
        print("Conexión cerrada")


    def recv_close(self):
        print("---------------------------")
        print("inicia recv close")
        self.socketudp.socket_udp.settimeout(None)

        while True:
            message, _ = self.socketudp.socket_udp.recvfrom(23)
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
        print("se recivio FIN")
        fin_ack = {}
        fin_ack["ack"] = 1
        fin_ack["syn"] = 0
        fin_ack["fin"] = 1
        fin_ack["seq"] = mensaje["seq"] + 1
        fin_ack["datos"] = "".encode()
        self.num_secuencia = fin_ack["seq"]
        segmento = create_segment(fin_ack)

        self.socketudp.socket_udp.settimeout(0.5)
        timeouts = 0
        ack_final = False
        while timeouts < 3 and not ack_final:
            self.socketudp.socket_udp.sendto(segmento, self.dir_destino)
            try:
                while True:
                    message, _ = self.socketudp.socket_udp.recvfrom(23)
                    m = parse_segment(message)
                    if (m["ack"] == 1 and m["fin"] == 0
                            and m["seq"] == self.num_secuencia + 1):
                        ack_final = True
                        break
                    if m["fin"] == 1:
                        # el cliente reenvió el FIN: se perdió nuestro FIN+ACK
                        self.socketudp.socket_udp.sendto(segmento, self.dir_destino)
            except :
                timeouts += 1
                print("reenviando FIN+ACK...")

        if not ack_final:
            print("recv_close: no llegó el ACK final, se asume que la otra parte cerró")
        self.socketudp.socket_udp.close()
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