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
        "body": body #no esta decodificado...
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

if __name__=="__main__":
    #lo del archivo json deberia ir aca ....
    if len(sys.argv) < 2:
        print("error argumentos")
        sys.exit(1)

    json_path = sys.argv[1]
    try:
        with open(json_path) as file:
            # usamos json para manejar los datos
            data = json.load(file)
            # Extraemos el nombre desde el JSON (si no existe, usa un valor por defecto)
            nombre_usuario = data.get("nombre", "Coni e Isi")
            print(f"usuario activo: {nombre_usuario}")
    except Exception as e:
        print(f"error al abrir o leer el archivo JSON: {e}")
        sys.exit(1)

    new_socket_address = ('10.0.2.15', 8000)
    # armamos el socket
    # los parámetros que recibe el socket indican el tipo de conexión
    # socket.SOCK_STREAM = socket orientado a conexión
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #esto sirve para que si cortmaos la conexion e intentamos reanudarla no pida esperar segundos
    # le indicamos al server socket que debe atender peticiones en la dirección address
    # para ello usamos bind
    server_socket.bind(new_socket_address)
 
    # luego con listen (función de sockets de python) le decimos que puede
    # tener hasta 3 peticiones de conexión encoladas
    # si recibiera una 4ta petición de conexión la va a rechazar
    server_socket.listen(3)
    print('... Esperando clientes')
    try:
        while True:
            # cuando llega una petición de conexión la aceptamos
            # y se crea un nuevo socket que se comunicará con el cliente
            new_socket, new_socket_address = server_socket.accept()
            # Recibimos la request del navegador /esto es sacado de gemini
            request_bytes = new_socket.recv(4096)
            if not request_bytes:
                new_socket.close()
                continue

            parsed_request = parse_HTTP_message(request_bytes)
            print(f"Petición recibida: {parsed_request.get('metodo')} en {parsed_request.get('path')}")

            html_content = (
                "<!DOCTYPE html>\n"
                "<html>\n"
                "<head>\n"
                "    <meta charset=\"UTF-8\">\n"
                "    <title>Servidor HTTP de Coni e Isi c:</title>\n"
                "<body>\n"
                "  <h1>HOLAAAA somos Coni e Isi c:</h1>\n"
                "  <p>Respuesta generada correctamente usando create_HTTP_message.</p>\n"
                "</body>\n"
                "</html>"
            ).encode("utf-8")


            #se arma estructura de response basado en la salida de curl
            response_data ={
                "metodo": "HTTP/1.1",
                "path": "200",
                "version": "OK",
                "headers":{
                    "Content-Type": "text/html; charset=utf-8",
                    "Content-Length": str(len(html_content)),
                    "X-ElQuePregunta": "nombre", #aca no se
                    "Connection": "close"
                },
                "body": html_content
            }

            #Cremaos  los bytes usadno funcion
            response_bytes = create_HTTP_message(response_data)
            #enviamos al cliente y cerramos
            new_socket.sendall(response_bytes)
            new_socket.close()

    except KeyboardInterrupt:
            print("\nServidor detenido.")
    finally:
        server_socket.close()

        
