
import socketTCP
from socketTCP import SocketTCP

if __name__=="__main__":
    socket_address = ('10.0.2.15', 8000)
    socket_serv = SocketTCP()
    socket_serv.bind(socket_address)

    # #PRUEBAS
    new_socket, new_socket_adress = socket_serv.accept()
    buff_size = 16
    full_message_1 = new_socket.recv(buff_size)
    full_message_2 = new_socket.recv(buff_size)
    full_message_3 = new_socket.recv(buff_size)

    print((full_message_1+full_message_2+full_message_3).decode())
    new_socket.recv_close()




    