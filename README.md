# MSCS-631-Python-Lab5

# HTTP Proxy Server with Caching

This is a simple HTTP proxy server built with Python. The server can handle both HTTP and HTTPS requests. It supports caching for HTTP responses, serving cached data on subsequent requests to reduce redundant web traffic.

---

## Features
- Handles HTTP and HTTPS requests.
- Implements caching to serve repeated requests faster.
- Supports HTTP `GET` and HTTPS `CONNECT` methods.
- Logs incoming connections and requests.

---

## Requirements
Ensure the following software is installed:
- Python 3
- curl (for testing)

---

## Usage Instructions

### 1. Starting the Proxy Server
Run the proxy server with the following command:
```bash
python3 proxy_server.py <server_ip> <server_port>
```
Example:
```bash
python3 proxy_server.py 127.0.0.1 8888
```

### 2. Testing the Proxy Server
You can test HTTP and HTTPS requests using `curl`:

#### HTTP Request
```bash
curl -v --proxy http://127.0.0.1:8888 http://neverssl.com
```

#### HTTPS Request
```bash
curl -v --proxy http://127.0.0.1:8888 https://www.google.com
```

---

## Configuration
- The server listens on the IP address and port specified in the command line arguments.
- Cached files are saved locally with filenames based on the URL.


