import routerttl
import sys
import socket

if __name__=="__main__":

    #test parte 7
    ip_a= (127).to_bytes(1)
    ip_b = (0).to_bytes(1)
    ip_c = (0).to_bytes(1)
    ip_d = (1).to_bytes(1)
    puerto = (8881).to_bytes(2)
    ttl = (10).to_bytes(1)
    id = (1).to_bytes(4)
    offset = (0).to_bytes(4)
    tamano = (4).to_bytes(4)
    flag = (0).to_bytes(1)
    mensaje = ("hola").encode()
    IP_packet_v1 = ip_a+ip_b+ip_c+ip_d+puerto+ttl+id+offset+tamano+flag+mensaje

    ip_a= (127).to_bytes(1)
    ip_b = (0).to_bytes(1)
    ip_c = (0).to_bytes(1)
    ip_d = (1).to_bytes(1)
    puerto = (8881).to_bytes(2)
    ttl = (10).to_bytes(1)
    id = (2).to_bytes(4)
    offset = (0).to_bytes(4)
    tamano = (20).to_bytes(4)
    flag = (0).to_bytes(1)
    mensaje = ("pan de huevo merenge").encode()
    IP_packet2_v1 = ip_a+ip_b+ip_c+ip_d+puerto+ttl+id+offset+tamano+flag+mensaje

    frag1 = routerttl.fragment_IP_packet(IP_packet_v1,22)
    frag2 = routerttl.fragment_IP_packet(IP_packet2_v1,25)


    socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_adress = ('127.0.0.1', 8881) 

    #test en orden
    # print("Test en orden")
    # for i in range(len(frag1)):
    #     socket_client.sendto(frag1[i], socket_adress)
    # for i in range(len(frag2)):
    #     socket_client.sendto(frag2[i], socket_adress)

    #test desorsen
    # print("Test en desorden")
    # socket_client.sendto(frag1[1], socket_adress)
    # socket_client.sendto(frag1[0], socket_adress)
    # socket_client.sendto(frag2[3], socket_adress)
    # socket_client.sendto(frag2[1], socket_adress)
    # socket_client.sendto(frag2[0], socket_adress)
    # socket_client.sendto(frag2[2], socket_adress)

    #test intercalando id's
    # print("Test con id intercalados")
    # socket_client.sendto(frag2[1], socket_adress)
    # socket_client.sendto(frag1[1], socket_adress)
    # socket_client.sendto(frag2[3], socket_adress)
    # socket_client.sendto(frag1[0], socket_adress)
    # socket_client.sendto(frag2[0], socket_adress)
    # socket_client.sendto(frag2[2], socket_adress)

    #prueba 1
    # print("prueba 1")
    # ip_a= (127).to_bytes(1)
    # ip_b = (0).to_bytes(1)
    # ip_c = (0).to_bytes(1)
    # ip_d = (1).to_bytes(1)
    # puerto = (8885).to_bytes(2)
    # ttl = (10).to_bytes(1)
    # id = (347).to_bytes(4)
    # offset = (0).to_bytes(4)
    # tamano = (5).to_bytes(4)
    # flag = (0).to_bytes(1)
    # mensaje = ("hola!").encode()
    # prueba = ip_a+ip_b+ip_c+ip_d+puerto+ttl+id+offset+tamano+flag+mensaje
    # socket_client.sendto(prueba, socket_adress)



    #prueba 2
    print("prueba 2")
    ip_a= (127).to_bytes(1)
    ip_b = (0).to_bytes(1)
    ip_c = (0).to_bytes(1)
    ip_d = (1).to_bytes(1)
    puerto = (8885).to_bytes(2)
    ttl = (30).to_bytes(1)
    id = (347).to_bytes(4)
    offset = (0).to_bytes(4)
    tamano = (130).to_bytes(4)
    flag = (0).to_bytes(1)
    mensaje = ("Mi gato dice miau miau cuando quiere rascar el sillon. Lo reto porque me tiene el sillon para la cagada, pero yo lo quiero mucho<3").encode()
    prueba = ip_a+ip_b+ip_c+ip_d+puerto+ttl+id+offset+tamano+flag+mensaje
    socket_client.sendto(prueba, socket_adress)
    
    

    socket_client.close()



    
