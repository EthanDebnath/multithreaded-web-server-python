import socket
import threading
import os
import mimetypes

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
                # Default to index.html if root is requested
                if path == "/" or path == "/index.html":
                    path = "index.html"
                else:
                    # Remove leading slash from path
                    path = path[1:]

                # Handle 301 redirection (page1.html -> page2.html)
                if path == "page1.html":
                    response = "HTTP/1.0 301 Moved Permanently\r\n"
                    response += "Location: /page2.html\r\n\r\n"
                    client_socket.sendall(response.encode())
                # Serve files if they exist
                elif os.path.exists(path):
                    # Guess the MIME type (e.g., image/jpeg, text/html)
                    mime_type, _ = mimetypes.guess_type(path)
                    if mime_type is None:
                        mime_type = 'application/octet-stream'  # Default binary type

                    # Read the file content
                    with open(path, 'rb') as file:
                        content = file.read()

                    # Send the HTTP response
                    response = f"HTTP/1.0 200 OK\r\nContent-Type: {mime_type}\r\n\r\n"
                    client_socket.sendall(response.encode() + content)
                # Handle file not found (404) - Serve custom 404.html page
                else:
                    if os.path.exists('404.html'):
                        # Read the 404.html content
                        with open('404.html', 'rb') as file:
                            content = file.read()

                        response = "HTTP/1.0 404 Not Found\r\n"
                        response += "Content-Type: text/html\r\n\r\n"
                        client_socket.sendall(response.encode() + content)
                    else:
                        # Fallback 404 response if 404.html is not found
                        response = "HTTP/1.0 404 Not Found\r\n\r\n"
                        response += "<html><body><h1>404 Not Found</h1></body></html>"
                        client_socket.sendall(response.encode())
            else:
                # Method not supported
                response = "HTTP/1.0 405 Method Not Allowed\r\n\r\n"
                client_socket.sendall(response.encode())
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
