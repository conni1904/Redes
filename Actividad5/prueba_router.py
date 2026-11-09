import sys
import socket
import routerttl


if __name__=="__main__":
    if (len(sys.argv)<4):
        print("error")
        sys.exit(1)
    with open("texto.txt", 'r') as file:
        contenido = file.read()
    head = sys.argv[1].split(";")
    diccionario = {}
    ip= head[0].split(".")
    diccionario["ip_a"] = int(ip[0])
    diccionario["ip_b"] = int(ip[1])
    diccionario["ip_c"] = int(ip[2])
    diccionario["ip_d"] = int(ip[3])
    diccionario["puerto"] = int(head[1])
    diccionario["ttl"] = int(head[2])

    socket_address = (sys.argv[2], int(sys.argv[3]))
    socket_router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for linea in contenido.splitlines():
        diccionario["mensaje"] = linea.encode()
        paquete = routerttl.create_packet(diccionario)
        socket_router.sendto(paquete, socket_address)
    
    