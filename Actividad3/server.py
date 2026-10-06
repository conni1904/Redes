import socket
import socketTCP

if __name__=="__main__":
    socket_address = ('10.0.2.15', 8000)
    socket_serv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_serv.bind(socket_address)

    while True:
        message, adress = socket_serv.recvfrom(23)
        mensaje = socketTCP.parse_segment(message)
        print(mensaje)
