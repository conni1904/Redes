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


    #OTROS TESTS
    socket_client.connect(socket_address)
    # test 1
    message = "Mensje de len=16".encode()
    socket_client.send(message, "go_back_n")
    # test 2
    message = "Mensaje de largo 19".encode()
    socket_client.send(message, "go_back_n")
    # test 3
    message = "Mensaje de largo 19".encode()
    socket_client.send(message, "go_back_n")

    #test 4
    message = "Vamos rajados. Poco falta para ser eyectados a traves del parabrisas e incrustarnos en las casas de madera. Atras, mi madre se balancea con cada curva. Oye, ya, po. Esto no es nada la Autobahn le reclamo a Frank. Fijate en el limite de velocidad. Las nubes aun tapan las montanas cuando llegamos a la orilla. Hace frio, apenas aclara y no hay turistas. Frank sostiene a mi madre en brazos. Ya, mama. Hasta aca llegamos. Con los pies en el agua, espolvoreo el contenido del anfora en el rio. Las cenizas se mezclan con los minerales de la cordillera".encode()
    socket_client.send(message, "go_back_n")
    


    #PRUEBAS
    
    ruta = input("ruta por favor: ")
    with open(ruta, 'r') as file:
        contenido = file.read()
        #socket_client.connect(socket_address)
        socket_client.send(contenido.encode(), "go_back_n")
        socket_client.close()



