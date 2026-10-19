
import socketTCP
from socketTCP import SocketTCP

if __name__=="__main__":
    socket_address = ('10.0.2.15', 8000)
    socket_serv = SocketTCP()
    socket_serv.bind(socket_address)

    #OTROS TESTS
    new_socket, new_socket_adress = socket_serv.accept()
    # test 1
    buff_size = 16
    full_message = new_socket.recv(buff_size, "go_back_n")
    print("Test 1 received:", full_message)
    if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
    else: print("Test 1: Failed")

    # test 2
    buff_size = 19
    full_message = new_socket.recv(buff_size,"go_back_n")
    print("Test 2 received:", full_message)
    if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
    else: print("Test 2: Failed")

    # test 3
    buff_size = 14
    message_part_1 = new_socket.recv(buff_size,"go_back_n")
    message_part_2 = new_socket.recv(buff_size,"go_back_n")
    print("Test 3 received:", message_part_1 + message_part_2)
    if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
    else: print("Test 3: Failed")

    #test 4
    buff_size = 128
    message_part_1 = new_socket.recv(buff_size,"go_back_n")
    message_part_2 = new_socket.recv(buff_size,"go_back_n")
    message_part_3 = new_socket.recv(buff_size,"go_back_n")
    message_part_4 = new_socket.recv(buff_size,"go_back_n")
    message_part_5 = new_socket.recv(buff_size,"go_back_n")
    print("Test 4 received:", message_part_1 + message_part_2+message_part_3+message_part_4+message_part_5)
    if (message_part_1 + message_part_2+message_part_3+message_part_4+message_part_5) == "Vamos rajados. Poco falta para ser eyectados a traves del parabrisas e incrustarnos en las casas de madera. Atras, mi madre se balancea con cada curva. Oye, ya, po. Esto no es nada la Autobahn le reclamo a Frank. Fijate en el limite de velocidad. Las nubes aun tapan las montanas cuando llegamos a la orilla. Hace frio, apenas aclara y no hay turistas. Frank sostiene a mi madre en brazos. Ya, mama. Hasta aca llegamos. Con los pies en el agua, espolvoreo el contenido del anfora en el rio. Las cenizas se mezclan con los minerales de la cordillera".encode("utf-8"): print("Test 4: Passed")
    else: print("Test 4: Failed")

    # #PRUEBAS
    
    buff_size = 16
    full_message_1 = new_socket.recv(buff_size, "go_back_n")
    full_message_2 = new_socket.recv(buff_size,"go_back_n")
    full_message_3 = new_socket.recv(buff_size,"go_back_n")

    print((full_message_1+full_message_2+full_message_3).decode())
    new_socket.recv_close()
  