import socket
import socketTCP

socket_address = ('10.0.2.15', 8000)
socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if __name__=="__main__":
    ruta = input("ruta por favor: ")
    with open(ruta, 'r') as file:
        contenido = file.read()
        #aca pa q el mensaje se divida en 16 bytes
        dic = {}
        dic["ack"]= 1
        dic["syn"]= 1
        dic["fin"]= 0
        dic["seq"]= 1
        dic["datos"]= contenido.encode('utf-8')
        print((dic["ack"]))
        print((dic["syn"]))
        print(type(dic["seq"]))
        print(type(dic["syn"]))
        print(type(dic["ack"]))
        segmento = socketTCP.create_segment(dic)

        if len(segmento)%16 == 0:
            bloque = len(segmento)/16
        else:
            bloque = int(len(segmento)/16) + 1

        for i in range(bloque):
            dic = {}
            dic["ack"]= 1
            dic["syn"]= 1
            dic["fin"]= 0
            dic["seq"]= 1
            dic["datos"]= contenido[i * 16 : (i + 1) * 16].encode('utf-8')
            print((dic["ack"]))
            print((dic["syn"]))
            print(type(dic["seq"]))
            print(type(dic["syn"]))
            print(type(dic["ack"]))
            segmento = socketTCP.create_segment(dic)
            socket_client.sendto(segmento, socket_address)



    
    
