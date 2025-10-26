

from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

from api_rate_limiter.auth import authenticate_token


# this function will take a username and an algorithm and test if user is within defined algorithm limits and return a boolean if it is or not
def check_rate(username):
    pass

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    # Target server to proxy requests to
    TARGET_SERVER = 'http://localhost:8000 ' # Default target for testing

    def do_request(self, method):
        # Prepare headers (excluding Host)
        headers = {k: v for k, v in self.headers.items() 
                    if k.lower() != 'host'}
        if self.path != "/login":
            if auth := headers.get("Authorization"):
                tokens = auth.split(" ")
                username = authenticate_token(tokens[1])
                if check_rate(username):
                    self.forward_request(headers, method)
            else:
                self.send_response(401)
                
        elif self.path == "/login":
            pass

    def forward_request(self, headers, method):
        try:
            # Read body for POST/PUT
            body = None
            if method in ['POST', 'PUT']:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
            
            # Construct full URL
            target_url = self.TARGET_SERVER + self.path
            
            # Make the request
            response = requests.request(
                method=method,
                url=target_url,
                headers=headers,
                data=body,
                allow_redirects=False,
                stream=True
            )
            
            # Send response
            self.send_response(response.status_code)
            for header, value in response.headers.items():
                if header.lower() not in ['transfer-encoding', 'connection']:
                    self.send_header(header, value)
            self.end_headers()
            
            # Stream response body
            for chunk in response.iter_content(chunk_size=8192):
                self.wfile.write(chunk)
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_GET(self):
        self.do_request('GET')
    
    def do_POST(self):
        self.do_request('POST')
    
    def do_PUT(self):
        self.do_request('PUT')
    
    def do_DELETE(self):
        self.do_request('DELETE')

if __name__ == '__main__':
    proxy = HTTPServer(('localhost', 8080), ProxyHTTPRequestHandler)
    print('Proxy server running on http://localhost:8080')
    proxy.serve_forever()