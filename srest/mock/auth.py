"""Mock Keycloak server for testing"""
import json
import jwt
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict

# Mock private key for JWT signing (only for testing!)
MOCK_KEY = "mock_secret_key"

class MockKeycloakHandler(BaseHTTPRequestHandler):
    """Mock Keycloak handler"""
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path.endswith('/protocol/openid-connect/token'):
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length).decode()
                params = dict(param.split('=') for param in body.split('&'))
                
                now = datetime.now()
                expires = now + timedelta(hours=1)
                refresh_expires = now + timedelta(days=30)
                
                # Create access token
                access_token = jwt.encode({
                    'sub': 'mock-user-id',
                    'preferred_username': 'mockuser',
                    'name': 'Mock User',
                    'email': 'mock@example.com',
                    'realm_access': {
                        'roles': ['slurm_user']
                    },
                    'iat': int(now.timestamp()),
                    'exp': int(expires.timestamp())
                }, MOCK_KEY, algorithm='HS256')
                
                # Create refresh token
                refresh_token = jwt.encode({
                    'sub': 'mock-user-id',
                    'typ': 'Refresh',
                    'iat': int(now.timestamp()),
                    'exp': int(refresh_expires.timestamp())
                }, MOCK_KEY, algorithm='HS256')
                
                response = {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': 3600,
                    'refresh_expires_in': 2592000,
                    'token_type': 'Bearer'
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(404)
                
        except Exception as e:
            self.send_error(500, str(e))

def start_mock_auth_server(port: int = 8081):
    """Start mock auth server"""
    server = HTTPServer(('localhost', port), MockKeycloakHandler)
    print(f"Mock Keycloak server running on http://localhost:{port}")
    server.serve_forever()
