import sys
import socketTCP
from socketTCP import SocketTCP


if __name__=="__main__":
    if len(sys.argv) < 3:
            print("error argumentos")
            sys.exit(1)
    print(sys.argv[2])
    if sys.argv[1] == '10.0.2.15' or sys.argv[2] == '8000':
        socket_address = ('10.0.2.15', 8000)
        socket_client = SocketTCP()
        contenido = sys.stdin.read()
        socket_client.connect(socket_address)
        socket_client.send(contenido.encode())
        socket_client.close()
    