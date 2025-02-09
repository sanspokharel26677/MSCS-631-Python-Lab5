from socket import *
import sys
import select

def start_proxy_server(server_ip, server_port):
    """
    Starts the proxy server to listen on the specified IP address and port.
    """
    tcpSerSock = socket(AF_INET, SOCK_STREAM)
    tcpSerSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    try:
        tcpSerSock.bind((server_ip, server_port))
        tcpSerSock.listen(5)
        print(f"Proxy server running on {server_ip}:{server_port}...")
    except Exception as e:
        print(f"Error binding socket: {e}")
        sys.exit(1)

    while True:
        print('Ready to serve...')
        tcpCliSock, addr = tcpSerSock.accept()
        print('Received a connection from:', addr)

        try:
            message = tcpCliSock.recv(4096).decode()
            print(f"Received message: {message}")

            if not message:
                continue

            # Extract method, URL, and protocol from the request line
            request_line = message.splitlines()[0]
            method, url, _ = request_line.split()

            if method == "CONNECT":
                # Handle HTTPS CONNECT requests
                hostn, port = url.split(":")
                port = int(port)
                handle_connect_request(tcpCliSock, hostn, port)
            else:
                # Handle normal HTTP requests
                handle_http_request(tcpCliSock, message, url)
        except Exception as e:
            print(f"Error processing request: {e}")
        finally:
            tcpCliSock.close()

def handle_http_request(client_sock, message, url):
    """
    Handles HTTP GET requests by fetching the content from the web server or the cache.
    """
    if "//" in url:
        protocol, url = url.split("//", 1)
    else:
        protocol = "http"

    # Parse hostname and path
    host_and_path = url.split("/", 1)
    hostn = host_and_path[0]
    path = "/" + host_and_path[1] if len(host_and_path) > 1 else "/"

    print(f"Extracted hostname: {hostn}")
    print(f"Request path: {path}")

    cache_file_path = "./" + hostn.replace("/", "_") + path.replace("/", "_")

    try:
        with open(cache_file_path, "r") as cache_file:
            outputdata = cache_file.readlines()
            print('Read from cache')

            client_sock.send("HTTP/1.0 200 OK\r\n".encode())
            client_sock.send("Content-Type: text/html\r\n\r\n".encode())
            for line in outputdata:
                client_sock.send(line.encode())
    except IOError:
        print('Cache miss. Fetching from web server...')
        fetch_from_web_server(client_sock, hostn, path, cache_file_path)

def fetch_from_web_server(client_sock, hostn, path, cache_file_path):
    """
    Fetches the requested content from the web server and sends it to the client.
    """
    web_server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        web_server_ip = gethostbyname(hostn)
        print(f"Resolved IP address: {web_server_ip}")

        web_server_socket.connect((web_server_ip, 80))

        request_line = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {hostn}\r\n"
            f"User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36\r\n"
            f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
            f"Connection: close\r\n"
            f"Upgrade-Insecure-Requests: 1\r\n\r\n"
        )
        web_server_socket.send(request_line.encode())

        response_data = b""
        while True:
            data = web_server_socket.recv(4096)
            if not data:
                break
            response_data += data
            client_sock.send(data)

        with open(cache_file_path, "wb") as tmpFile:
            tmpFile.write(response_data)
    except Exception as e:
        print(f"Error fetching from web server: {e}")
    finally:
        web_server_socket.close()

def handle_connect_request(client_sock, host, port):
    """
    Handles HTTPS CONNECT requests by establishing a tunnel between the client and the web server.
    """
    try:
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.connect((host, port))
        client_sock.send("HTTP/1.1 200 Connection Established\r\n\r\n".encode())
        print(f"Tunnel established with {host}:{port}")

        sockets = [client_sock, server_sock]
        while True:
            readable, _, _ = select.select(sockets, [], [])
            for sock in readable:
                data = sock.recv(4096)
                if not data:
                    print("Closing connection")
                    return
                if sock is client_sock:
                    server_sock.sendall(data)
                else:
                    client_sock.sendall(data)
    except Exception as e:
        print(f"Error handling CONNECT request: {e}")
    finally:
        server_sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: python ProxyServer.py <server_ip> <server_port>')
        sys.exit(2)

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    start_proxy_server(server_ip, server_port)

