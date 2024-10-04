import socket
import threading
import os

# Function to handle a single client request
def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Received request:\n{request}")

        # Parsing the request
        request_lines = request.splitlines()
        if len(request_lines) > 0:
            first_line = request_lines[0]
            # Extract the requested path
            method, path, _ = first_line.split()
            
            if method == 'GET':
                # Remove leading slash from path
                if path == '/':
                    path = "/index.html"  # Default to index.html
                else:
                    path = path[1:]
                
                # Handle 301 redirection (page1.html -> page2.html)
                if path == "page1.html":
                    response = "HTTP/1.0 301 Moved Permanently\r\n"
                    response += "Location: /page2.html\r\n\r\n"
                    client_socket.sendall(response.encode())
                # Handle valid requests (200 OK)
                elif os.path.exists(path):
                    # Read the requested file
                    with open(path, 'rb') as file:
                        content = file.read()
                    response = "HTTP/1.0 200 OK\r\n"
                    response += "Content-Type: text/html\r\n\r\n"
                    client_socket.sendall(response.encode() + content)
                # Handle file not found (404)
                else:
                    response = "HTTP/1.0 404 Not Found\r\n\r\n"
                    response += "<html><body><h1>404 Not Found</h1></body></html>"
                    client_socket.sendall(response.encode())
            else:
                # Method not supported
                response = "HTTP/1.0 405 Method Not Allowed\r\n\r\n"
                client_socket.sendall(response.encode())
        else:
            # Empty request, close connection
            client_socket.close()
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        # Close client connection
        client_socket.close()

# Start the web server
def start_server():
    # Create socket for IPv4 and TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 8080))
    server_socket.listen(5)  # Max 5 clients in queue
    print("Server is listening on port 8080...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        # Handle each client in a new thread
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
