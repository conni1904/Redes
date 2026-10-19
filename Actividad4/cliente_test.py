import socketTCP
from socketTCP import SocketTCP
import time

socket_address = ('10.0.2.15', 8000)
socket_client = SocketTCP()


if __name__=="__main__":

    socket_client.connect(socket_address)

    message = "Vamos rajados. Poco falta para ser eyectados a traves del parabrisas e incrustarnos en las casas de madera. Atras, mi madre se balancea con cada curva. Oye, ya, po. Esto no es nada la Autobahn le reclamo a Frank. Fijate en el limite de velocidad. Las nubes aun tapan las montanas cuando llegamos a la orilla. Hace frio, apenas aclara y no hay turistas. Frank sostiene a mi madre en brazos. Ya, mama. Hasta aca llegamos. Con los pies en el agua, espolvoreo el contenido del anfora en el rio. Las cenizas se mezclan con los minerales de la cordillera".encode()
    tiempo_ini = time.time()
    socket_client.send(message, "go_back_n")
    tiempo_fin = time.time()

    tiempo = tiempo_fin - tiempo_ini

    if socket_client.congestion_controler_on:
        print("Con congestión de control")
    else:
        print("Sin control de congestion")
    
    print(f"cantidad de segmentos enviados: {socket_client.number_of_segment}")
    print(f"tiempo de ejecución: {tiempo}")


    socket_client.close()