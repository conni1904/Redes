import socket
import dnslib
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE

buffer_size = 4096 
root_ip = "198.41.0.4"

lista_consultas = []
dict_top_3 = {}

def act_lista (qname):
    lista_consultas.insert(0, qname)
    if len(lista_consultas)>20:
        lista_consultas.pop()

def act_top_3 (qname, respuesta):

    frecuencias = {}
    for elemento in lista_consultas:
        frecuencias[elemento] = frecuencias.get(elemento, 0) + 1
    elementos_ordenados = sorted(frecuencias.items(), key=lambda x: x[1], reverse=True)
    top_3_dominios = [item[0] for item in elementos_ordenados[:3]]
    if qname in top_3_dominios:
        if len(dict_top_3) == 3:
            for d in dict_top_3:
                if d not in top_3_dominios:
                    del dict_top_3[d]
        dict_top_3[qname] = respuesta


    
def parse_message_dns(message):
    parse_message= DNSRecord.parse(message)
    dictionary = {}
    headers = {}
    dictionary["qname"] = parse_message.get_q().get_qname()
    headers["ANCOUNT"] = parse_message.header.a
    headers["NSCOUNT"] = parse_message.header.auth
    headers["ARCOUNT"] = parse_message.header.ar
    dictionary["headers"] = headers
    dictionary["answer"] = parse_message.rr
    dictionary["authority"] = parse_message.auth
    dictionary["additional"] = parse_message.ar
    return dictionary


def resolver(mensaje_consulta: bytes, ip_addr=root_ip) -> bytes: 
    esta_guardado = False
    parse_consulta = parse_message_dns(mensaje_consulta)
    qname = str(parse_consulta["qname"])
    socket_address = (ip_addr, 53)
    if qname in dict_top_3:
        esta_guardado = True
        print(f"(debug) {qname} está guardado en el caché ")
        socket_address = (dict_top_3[qname], 53)

    
    
    
    socket_resolver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   
    socket_resolver.sendto(mensaje_consulta, socket_address)
    message, address = socket_resolver.recvfrom(buffer_size)
    socket_resolver.close()
    parse_message = parse_message_dns(message)

    # PArte b)

    for answer in parse_message["answer"]:
        type_a = QTYPE.get(answer.rtype)
        if type_a == 'A':
            #vamos a revisar si podemos agregar qname
            act_lista(qname)
            if not esta_guardado:
                act_top_3(qname, ip_addr)
            return message

    #Parte c)
    for auth in parse_message["authority"]:
        type_auth = QTYPE.get(auth.rtype)
        if type_auth == 'NS':
            #parte c) i)
            is_A = False
            for ad in parse_message["additional"]:
                type_ad = QTYPE.get(ad.rtype)
                if type_ad == 'A':
                    is_A = True
                    ad_ip= str(ad.rdata)
                    qname_respuesta= parse_message["qname"]
                    ns_respuesta= str(auth.rdata)
                    print(f"(debug) Consultando {qname_respuesta} a {ns_respuesta} con dirección IP {ad_ip}")
                    return resolver(mensaje_consulta, ad_ip)
                    
            if not is_A:
                name_server = str(auth.rdata)
                q = bytes(DNSRecord.question(name_server).pack())
               
                response_dns = resolver(q)
                parse_response = parse_message_dns(response_dns)
                ns_q = parse_response["answer"][0].rname
                print(f"(debug) Consultando {name_server} a {ns_q} con dirección IP {root_ip}")
                for ans in parse_response["answer"]:
                    type_ans = QTYPE.get(ans.rtype)
                    if type_ans == 'A':
                        ip_query= str(ans.rdata)
                        qname_respuesta = parse_message["qname"]
                        print(f"(debug) Consultando {qname_respuesta} a {name_server} con dirección IP {ip_query}")
                        return resolver(mensaje_consulta, ip_query)
 
    return message                  





if __name__=="__main__":
     #Se crea socket 
    socket_address = ('10.0.2.15', 8000)
    socket_dns = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_dns.bind(socket_address)
    try: 
        while True:
            message, address = socket_dns.recvfrom(buffer_size)
            parse_message = parse_message_dns(message)
            qname_consulta = parse_message["qname"]
            ns_consulta = parse_message["additional"][0].rname
            
            print(f"(debug) Consultando {qname_consulta} a {ns_consulta} con dirección IP {root_ip}")
            respuesta = resolver(message)
            socket_dns.sendto(respuesta, address)
            
        
    finally:
        socket_dns.close()
