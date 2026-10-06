
import socketTCP
from socketTCP import SocketTCP

if __name__=="__main__":
    socket_address = ('10.0.2.15', 8000)
    socket_serv = SocketTCP()
    socket_serv.bind(socket_address)
    texto = ""
    while True:
        #PARTE 1
        # message, adress = socket_serv.socketudp.recvfrom(23)
        # mensaje = socketTCP.parse_segment(message)
        # texto += mensaje["datos"].decode()
        # print(mensaje)
        # print(texto)
        new_socket, new_socket_adress = socket_serv.accept()
        # test 1
        buff_size = 16
        full_message = new_socket.recv(buff_size)
        print("Test 1 received:", full_message)
        if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
        else: print("Test 1: Failed")

        # test 2
        # buff_size = 19
        # full_message = new_socket.recv(buff_size)
        # print("Test 2 received:", full_message)
        # if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
        # else: print("Test 2: Failed")

        # # test 3
        # buff_size = 14
        # message_part_1 = new_socket.recv(buff_size)
        # message_part_2 = new_socket.recv(buff_size)
        # print("Test 3 received:", message_part_1 + message_part_2)
        # if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
        # else: print("Test 3: Failed")

    