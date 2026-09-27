from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8000

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Hello, World! Status: 200 OK")

    def do_POST(self):
        self.send_response(201)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Received POST request! Status: 201 Created")

if __name__ == "__main__":
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"Server is listening on port {PORT}")
    httpd.serve_forever()
