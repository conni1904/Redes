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
    dictionary["ttl"] = IP_packet[6]
    dictionary["id"] = int.from_bytes( IP_packet[7:11])
    dictionary["offset"] = int.from_bytes(IP_packet[11:15])
    dictionary["tamano"] = int.from_bytes(IP_packet[15:19])
    dictionary["flag"] = IP_packet[19]
    dictionary["mensaje"] = IP_packet[20:]
    return dictionary


def create_packet(parsed_IP_packet):
    ip_a = parsed_IP_packet["ip_a"].to_bytes(1)
    ip_b = parsed_IP_packet["ip_b"].to_bytes(1)
    ip_c = parsed_IP_packet["ip_c"].to_bytes(1)
    ip_d = parsed_IP_packet["ip_d"].to_bytes(1)
    puerto = parsed_IP_packet["puerto"].to_bytes(2)
    ttl = parsed_IP_packet["ttl"].to_bytes(1)
    id = parsed_IP_packet["id"].to_bytes(4)
    offset = parsed_IP_packet["offset"].to_bytes(4)
    tamano = parsed_IP_packet["tamano"].to_bytes(4)
    flag = parsed_IP_packet["flag"].to_bytes(1)
    mensaje = parsed_IP_packet["mensaje"]
    return ip_a+ip_b+ip_c+ip_d+puerto+ttl+id+offset+tamano+flag+mensaje

def fragment_IP_packet(IP_packet, MTU):
    fragmentos = []
    if len(IP_packet) >  MTU: #caso que hay q fragmentar
        dic= parse_packet(IP_packet)
        mensaje = dic["mensaje"]
        tamano_ant= 0
        while len(mensaje) != 0: #guardamos el fragmento y dsp lo eliminamos
            frag_mesj= mensaje[0:(MTU-20)]
            mensaje = mensaje[(MTU-20):]
            dic["mensaje"] = frag_mesj
            dic["tamano"] = len(dic["mensaje"])
            dic["offset"] = dic["offset"] + tamano_ant
            if len(mensaje) == 0:
                dic["flag"] = 0
            else: 
                dic["flag"] = 1

            paquete = create_packet(dic)
            fragmentos.append(paquete)

            tamano_ant = dic["tamano"]

    
    else: # caso no fragmentar
        fragmentos.append(IP_packet)
    return fragmentos

def reassemble_IP_packet(fragment_list):
    if len(fragment_list) == 1:
        parseo = parse_packet(fragment_list[0])
        if parseo["offset"] == 0 and parseo["flag"] == 0:
            print("no se fragmentó")
            return fragment_list[0]
        else:
            print("fragmento incompleto")
            return None

    else:
        parse_lista = []
        for i in range(len(fragment_list)):
            parse_lista.append(parse_packet(fragment_list[i]))

        parse_lista.sort(key=lambda x: x["offset"]) #se ordena lista

        contador = 0
        for i in range(len(parse_lista)):
            if parse_lista[i]["offset"] != contador:
                print("se perdió un fragmento intermedio")
                return None
            contador += parse_lista[i]["tamano"]

        if parse_lista[len(parse_lista)-1]["flag"] != 0:
            print("se perdio el fragmento final")
            return None

        dic = {}
        dic["puerto"] = parse_lista[0]["puerto"]
        dic["mensaje"] = ("").encode()
        for i in range(len(parse_lista)):
            dic["mensaje"] += parse_lista[i]["mensaje"]
        dic["ip_a"] = parse_lista[0]["ip_a"]
        dic["ip_b"] = parse_lista[0]["ip_b"]
        dic["ip_c"] = parse_lista[0]["ip_c"]
        dic["ip_d"] = parse_lista[0]["ip_d"]
        dic["ttl"] = parse_lista[0]["ttl"]
        dic["id"] = parse_lista[0]["id"]
        dic["offset"] = int(0)
        dic["tamano"] = len(dic["mensaje"])
        dic["flag"] = int(0)
        paquete = create_packet(dic)

        return paquete



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
                return ((palabras[3], int(palabras[4])), int(palabras[5]))  
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

    #Test 1
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
    # parsed_IP_packet = parse_packet(IP_packet_v1)
    # IP_packet_v2 = create_packet(parsed_IP_packet)
    # print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

    #test parte 3
    # mayor_mtu = fragment_IP_packet(IP_packet_v1, 30)
    # if len(mayor_mtu) == 1:
    #     print(f"Funciona para MTU mayores que el paquete :)")
    # else:
    #     print("Falló :(")

    # menor_mtu = fragment_IP_packet(IP_packet_v1, 22)
    # if len(menor_mtu) == 2:
    #     print(f"Funciona para MTU menores que el paquete :)")
    # else:
    #     print("Falló :(")


    #test parte 5
    # MTU = 22
    # fragment_list = fragment_IP_packet(IP_packet_v1, MTU)
    # IP_packet_v2 = reassemble_IP_packet(fragment_list)
    # print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))



        
    

    #UN ROUTER RECIBE SU IP, SU PUERTO Y SUS RUTAS
    socket_address = (sys.argv[1], int(sys.argv[2]))
    socket_router = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_router.bind(socket_address)

    dic = {}
    while True:
        buffer_size = 1024
        message, address = socket_router.recvfrom(buffer_size)
        contador_visitas +=1
        mensaje_par = parse_packet(message)
        print(f"llegó paquete de {mensaje_par["tamano"]}")
        if mensaje_par["ttl"] > 0:
            ip = str(mensaje_par["ip_a"]) + "." +str(mensaje_par["ip_b"]) +"."+ str(mensaje_par["ip_c"])+ "." +str(mensaje_par["ip_d"])
            if (socket_address[0] == ip) and (socket_address[1] == mensaje_par["puerto"]): 
                print(f" Mensaje: {(mensaje_par["mensaje"]).decode()}")
                try:
                    dic[mensaje_par["id"]].append(message)
                except:
                    dic[mensaje_par["id"]] = []
                    dic[mensaje_par["id"]].append(message)

                ensamblado = reassemble_IP_packet(dic[mensaje_par["id"]])
                if ensamblado == None:
                    print("faltan fragmentos")

                else:
                    print("Llegó el mensaje :)")
                    parse_ensam= parse_packet(ensamblado)
                    print(f" Mensaje final armado: {(parse_ensam["mensaje"]).decode()}")


            else:
                ruta_mtu = check_routes(sys.argv[3], (ip, mensaje_par["puerto"]))
                if ruta_mtu == None:
                    print(f"No hay rutas hacia ({ip}, {mensaje_par['puerto']}) para paquete [paquete_ip]")
                else:
                    nueva_dir = ruta_mtu[0]
                    mtu = ruta_mtu[1]
                    print(f"redirigiendo paquete [paquete_ip] con destino final ({ip}, {mensaje_par['puerto']}) desde ({socket_address[0]}, {socket_address[1]}) hacia {nueva_dir}")
                    mensaje_par["ttl"] -= 1
                    nuevo_mensaje = create_packet(mensaje_par)
                    fragmentos = fragment_IP_packet(nuevo_mensaje,mtu)
                    print(f"se fragmentó en {len(fragmentos)} fragmentos")
                    for i in range(len(fragmentos)):
                        socket_router.sendto(fragmentos[i],nueva_dir)


                    
        else:
            print("Se recibió paquete [paquete_ip] con TTL 0")

    socket_router.close()
            


    
