import socket
import sys
import json

def parse_HTTP_message(http_message: bytes):
    #recibimos mensaje completo y lo dividimos (head y body)
    partes = http_message.split(b"\r\n\r\n", 1)
    head = partes[0]
    body = partes [1]

    #decodificamos solo el head y dividimos por header
    head_string = head.decode("utf-8", errors="replace")
    lineas= head_string.split("\r\n")

    #parseamos primera linea
    request_line=lineas[0]
    metodo, path, version = request_line.split(" ")

    #parseamos los headers
    headers={}
    for linea in lineas[1:]:
        if ":" in linea:
            key, value = linea.split(":",1)
            headers[key.strip()]= value.strip()

    #retornamos la estructura de datos
    return {
        "metodo": metodo,
        "path": path,
        "version": version,
        "headers": headers,
        "body": body 
    }

def create_HTTP_message(parsed_data: dict):
    #hay que reconstruir la request status
    metodo = parsed_data.get("metodo", "GET")
    path = parsed_data.get("path", "/")
    version = parsed_data.get("version", "HTTP/1.1")
    start_line = f"{metodo} {path} {version}\r\n"

    #reconstruimos encabezados
    headers_string = ""
    for key, value in parsed_data.get("headers", {}).items():
        headers_string += f"{key}: {value}\r\n"

    #juntamos el head y lo unimos con el body
    head= f"{start_line}{headers_string}\r\n"
    body = parsed_data.get("body", b"")

    http_mesage = head.encode("utf-8") + body
    #retornamos mensaje en bytes
    return http_mesage


# Función que recibe todo el contenido del request
def receive_full_request(connection_socket, buffer_size):
    message = connection_socket.recv(buffer_size)
    while not ("\r\n\r\n" in message.decode()):
        message += connection_socket.recv(buffer_size)
    return message

# Función que recibe todo el contenido del response
def receive_full_response(connection_socket, buffer_size): 
    message = connection_socket.recv(buffer_size)
    while not ("</html>" in message.decode()):
        message += connection_socket.recv(buffer_size)
    return message


if __name__=="__main__":
    # Se reciben argumentos
    if len(sys.argv) < 2:
        print("error argumentos")
        sys.exit(1)

    #Se abre archivo json
    json_path = sys.argv[1]
    try:
        with open(json_path) as file:
            # usamos json para manejar los datos
            data = json.load(file)
            # Extraemos el nombre desde el JSON (si no existe, usa un valor por defecto)
            usuario = data.get("user", "NO se encontro nombre")
            print(f"usuario activo: {usuario}")
    except Exception as e:
        print(f"error al abrir o leer el archivo JSON: {e}")
        sys.exit(1)

    #Se crea socket 
    socket_address = ('10.0.2.15', 8000)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(socket_address)
    server_socket.listen(3)
    print('... Esperando clientes')
    try:
        while True:
            # Cuando la petición se crea nuevo socket de comunicación
            buffer_size=64
            new_socket, new_socket_address = server_socket.accept()
            request_bytes = receive_full_request(new_socket,buffer_size)
            #request_bytes = new_socket.recv(4096) #aca deberia cambiarse por la nueva funcion para recibir todo el mensaje
            if not request_bytes:
                new_socket.close()
                continue

            parsed_request = parse_HTTP_message(request_bytes)
            host = parsed_request.get('headers').get('Host')
            print(f"Petición recibida: {parsed_request.get('metodo')} en {parsed_request.get('path')}")
            #2.2 Se revisa si el path de la página está bloqueado
            path = parsed_request.get('path')
            bloqueados= data.get('blocked')
            bloqueo=False

            for i in bloqueados:
                if i in path:
                    bloqueo = True
                    break

            #Petición para archivo jpg local 
            if "jpg" in path:
                #sacar lo q hay entre el / y el jpg
                with open("gatitus.jpg", "rb") as imagen: #aca creo que es necesario agregar un response (pq igual es una peticion)
                    message = imagen.read()


            #Si esta bloqueado devuelve el siguiente html por defecto
            elif bloqueo:
                print ("esta bloqueado")
                html_content = (
                    "<!DOCTYPE html>\n"
                    "<html>\n"
                    "<head>\n"
                    "    <meta charset=\"UTF-8\">\n"
                    "    <title>Servidor HTTP de Coni e Isi c:</title>\n"
                    "<body>\n"
                    "  <h1>ERROR 403: PÁGINA BLOQUEADA >:C </h1>\n"
                    "  <img src= '/gatitus.jpg'> \n"
                    "</body>\n"
                    "</html>"
                ).encode("utf-8")


                #se arma estructura de response basado en la salida de curl
                response_data ={
                    "metodo": "HTTP/1.1",
                    "path": "403",
                    "version": "Forbidden",
                    "headers":{
                        "Content-Type": "text/html; charset=utf-8",
                        "Content-Length": str(len(html_content)),
                        "X-ElQuePregunta": usuario, #aca no se
                        "Connection": "close"
                    },
                    "body": html_content
                }
                #------------------------------------------
                #Cremaos  los bytes usadno funcion
                message = create_HTTP_message(response_data)


            #Caso en que página no está bloqueada
            else:
                socket_address_client=(host, 80)
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print(f"se crea socket cliente : {client_socket}")
                 
                # Agregamos el header de "X-ElQuePregunta" a la solicitud
                client_socket.connect(socket_address_client)
                print("se conectó")
                request_original = parse_HTTP_message(request_bytes)
                request_original["headers"]["X-ElQuePregunta"] = "Coni e Isi c:"
                request=create_HTTP_message(request_original)
                client_socket.send(request)
                print("se envio")

                #Reemplazo de palabras prohibidas a la respuesta
                buffer_size = 256
                message_original = receive_full_response(client_socket,buffer_size)
                message_dict = parse_HTTP_message(message_original) 
                body_original = message_dict.get("body").decode("utf-8")

                forbidden_words= data.get("forbidden_words")
                
                for dic in forbidden_words:
                    for x, y in dic.items():
                        body_original = body_original.replace(x,y)


                message_dict["body"]= body_original.encode()
                message_dict["headers"]["Content-Length"] = len(body_original)+1
                print(message_dict)
                message = create_HTTP_message(message_dict)
                variable= message.decode()
                print(variable)


                print("se recibe")
                client_socket.close()



            new_socket.sendall(message)
            new_socket.close()

    except KeyboardInterrupt:
            print("\nServidor detenido.")
    finally:
        
        server_socket.close()

        
