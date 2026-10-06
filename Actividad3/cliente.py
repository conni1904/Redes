import socketTCP
from socketTCP import SocketTCP

socket_address = ('10.0.2.15', 8000)
socket_client = SocketTCP()

if __name__=="__main__":
    #PARTE 1
    # ruta = input("ruta por favor: ")
    # with open(ruta, 'r') as file:
    #     contenido = file.read()
    #     if len(contenido)%16 == 0:
    #         bloque = len(contenido)/16
    #     else:
    #         bloque = int(len(contenido)/16) + 1

    #     for i in range(bloque):
    #         dic = {}
    #         dic["ack"]= 1
    #         dic["syn"]= 1
    #         dic["fin"]= 0
    #         dic["seq"]= 1
    #         dic["datos"]= contenido[i * 16 : (i + 1) * 16].encode('utf-8')
    #         segmento = socketTCP.create_segment(dic)
    #         socket_client.socketudp.sendto(segmento, socket_address)
    socket_client.connect(socket_address)
    # test 1
    message = "Mensje de len=16".encode()
    socket_client.send(message)
    # # test 2
    # message = "Mensaje de largo 19".encode()
    # socket_client.send(message)
    # # test 3
    # message = "Mensaje de largo 19".encode()
    # socket_client.send(message)



    
    

    
    
