import os
from network import WLAN, AP_IF, STA_IF
import usocket as socket

# Configura la red Wi-Fi
wlan = WLAN(STA_IF)
ap = WLAN(AP_IF)
wlan.active(True)

# Conecta a tu red Wi-Fi
wlan.connect('RaspberryPiBuenosAires', 'Visita_la_Web')

# Espera hasta que se establezca la conexión
while not wlan.isconnected():
    pass

def ap_mode(ssid, password):
    ap.active(True)
    ap.config(essid='Campus', password='Virtual2024')
    
    while not ap.active():
        pass
    
    print('AP Mode Is Active, You Can Now Connect')
    print('IP Address To Connect to:', ap.ifconfig()[0])

# Función para manejar las solicitudes web
def handle_request(client_socket):
    req = client_socket.recv(1024)
    req_str = req.decode('utf-8')
    
    if req_str.startswith('GET /'):
        client_socket.send('HTTP/1.1 200 OK\nContent-Type: text/html\n\n')
        client_socket.send('<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body>')
        client_socket.send('<h1>Campus sin WiFi:</h1>')
        
        # Listar archivos en el sistema de archivos interno
        files = os.listdir('/')
        client_socket.send('<ul>')  # Comienza una lista desordenada
        for file in files:
            client_socket.send('<li><a href="/download/{}" download>{}</a></li>'.format(file, file))
        client_socket.send('</ul>')  # Termina la lista desordenada
        
        client_socket.send('</body></html>')
    elif req_str.startswith('GET /download/'):
        parts = req_str.split(' ')
        path = parts[1][10:]  # Elimina '/download/' del inicio
        try:
            filename = os.path.basename(path)
            with open(path, 'rb') as file:
                content = file.read()
                client_socket.send('HTTP/1.1 200 OK\nContent-Type: application/octet-stream\nContent-Disposition: attachment; filename="{}"\n\n'.format(filename))
                client_socket.sendall(content)
        except:
            client_socket.send('HTTP/1.1 404 Not Found\n\n')
    else:
        client_socket.send('HTTP/1.1 404 Not Found\n\n')
        
    client_socket.close()

# Crea un socket de servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('', 80))
server_socket.listen(5)

# Espera por las solicitudes de los clientes
while True:
    client_socket, addr = server_socket.accept()
    handle_request(client_socket)
    ap_mode('Campus', 'Virtual2024')
