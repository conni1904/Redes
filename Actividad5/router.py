import sys
import socket

contador_visitas = 0
hay_ruta = False

def parse_packet(IP_packet: bytes):
    dictionary = {}
    dictionary["ip_a"] = IP_packet[0]
    dictionary["ip_b"] = IP_packet[1]
    dictionary["ip_c"] = IP_packet[2]
    dictionary["ip_d"] = IP_packet[3]
    dictionary["puerto"] = int.from_bytes( IP_packet[4:6])
    dictionary["mensaje"] = IP_packet[6:]
    return dictionary


def create_packet(parsed_IP_packet):
    ip_a = parsed_IP_packet["ip_a"].to_bytes(1)
    ip_b = parsed_IP_packet["ip_b"].to_bytes(1)
    ip_c = parsed_IP_packet["ip_c"].to_bytes(1)
    ip_d = parsed_IP_packet["ip_d"].to_bytes(1)
    puerto = parsed_IP_packet["puerto"].to_bytes(2)
    mensaje = parsed_IP_packet["mensaje"]
    return ip_a+ip_b+ip_c+ip_d+puerto+mensaje



def check_routes(routes_file_name: str, destination_address: tuple[str, int])-> tuple[str, int]:
    global contador_visitas
    global hay_ruta
    with open(routes_file_name, 'r') as file:
        contenido = file.read()
    contador = 1
    for linea in contenido.splitlines():
        palabras = linea.split()
        if (destination_address[0] in palabras[0]) and (int(palabras[1]) <= destination_address[1] <= int(palabras[2])):
            hay_ruta = True
            if contador == contador_visitas:
                return (palabras[3], int(palabras[4]))  
            contador += 1
    if hay_ruta:
        print("reiniciando rutas")
        contador_visitas = 1
        return check_routes(routes_file_name,destination_address)
        



if __name__=="__main__":
    if (len(sys.argv)<4):
        print("error")
        sys.exit(1)
    with open(sys.argv[3], 'r') as file:
            contenido = file.read()


    #test parte 1
    # print(sys.argv[1])
    # print(sys.argv[2])
    # print(f"{sys.argv[3]}: {contenido}")

    #test parte 4
    # ip_a= (127).to_bytes(1)
    # ip_b = (0).to_bytes(1)
    # ip_c = (0).to_bytes(1)
    # ip_d = (1).to_bytes(1)
    # puerto = (8881).to_bytes(2)
    # mensaje = ("hola").encode()
    # IP_packet_v1 = ip_a+ip_b+ip_c+ip_d+puerto+mensaje
    # parsed_IP_packet = parse_packet(IP_packet_v1)
    # IP_packet_v2 = create_packet(parsed_IP_packet)
    # print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))


    #UN ROUTER RECIBE SU IP, SU PUERTO Y SUS RUTAS
    socket_address = (sys.argv[1], int(sys.argv[2]))
    socket_router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_router.bind(socket_address)

    while True:
        buffer_size = 1024
        message, address = socket_router.recvfrom(buffer_size)
        contador_visitas +=1
        mensaje_par = parse_packet(message)
        ip = str(mensaje_par["ip_a"]) + "." +str(mensaje_par["ip_b"]) +"."+ str(mensaje_par["ip_c"])+ "." +str(mensaje_par["ip_d"])
        if (socket_address[0] == ip) and (socket_address[1] == mensaje_par["puerto"]): 
            print(f" Mensaje: {(mensaje_par["mensaje"]).decode()}")

        else:
            nueva_dir = check_routes(sys.argv[3], (ip, mensaje_par["puerto"]))
            if nueva_dir == None:
                print(f"No hay rutas hacia ({ip}, {mensaje_par['puerto']}) para paquete [paquete_ip]")
            else:
                print(f"redirigiendo paquete [paquete_ip] con destino final ({ip}, {mensaje_par['puerto']}) desde ({socket_address[0]}, {socket_address[1]}) hacia {nueva_dir}")
                
                socket_router.sendto(message,nueva_dir)

    socket_router.close()
            


    
