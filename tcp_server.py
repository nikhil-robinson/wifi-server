import socket

# Define server address and port
SERVER_ADDRESS = '127.0.0.1'  # Loopback address for localhost
SERVER_PORT = 12345        # Port number for the server

# Create a TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(1)

print(f"TCP server is listening on {SERVER_ADDRESS}:{SERVER_PORT}...")

while True:
    # Accept a new client connection
    client_socket, client_address = server_socket.accept()

    print(f"Connection established from {client_address}")

    while True:
        # Receive data from the client
        data = client_socket.recv(1024).decode()
        if not data:
            # If no data received, the client has closed the connection
            print(f"Client {client_address} has closed the connection.")
            break

        print(f"Received data from {client_address}: {data}")

        # Process the received data as needed (e.g. perform some operation, send a response, etc.)
        # ...

        # Send a response back to the client
        response = f"Hello, {client_address[0]}! I received your message: '{data}'"
        client_socket.sendall(response.encode())

    # Close the client socket
    client_socket.close()

# Close the server socket
server_socket.close()
