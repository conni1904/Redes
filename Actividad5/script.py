import router
import sys
import socket


if __name__=="__main__":
    if (len(sys.argv) < 4):
        print("error")
        sys.exit(1)

    dic = {}
    dic["puerto"] = int(sys.argv[2])
    dic["mensaje"] = sys.argv[3].encode()
    ip = sys.argv[1].split(".")
    dic["ip_a"] = int(ip[0])
    dic["ip_b"] = int(ip[1])
    dic["ip_c"] = int(ip[2])
    dic["ip_d"] = int(ip[3])
    paquete = router.create_packet(dic)

    socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_adress = ('127.0.0.1', 8881) #asumimos que siempre se iniciara desde el router 1.....
    socket_client.sendto(paquete, socket_adress)
    socket_client.close()



    
