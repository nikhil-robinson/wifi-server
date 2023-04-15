import socket

# Define the server address and port
server_address = '127.0.0.1'
server_port = 12345

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the server address and port
server_socket.bind((server_address, server_port))

print('UDP server started.')

while True:
    # Receive data and address from client
    data, client_address = server_socket.recvfrom(1024)
    data = data.decode()

    print(f'Received data from {client_address}: {data}')

    # Process the received data here as needed

    # Send response back to the client
    response = 'Server response: ' + data.upper()
    server_socket.sendto(response.encode(), client_address)
