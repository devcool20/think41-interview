#!/usr/bin/env python3
"""
Simple HTTP Server for Milestone 6 Frontend
Handles static file serving and URL routing for department pages
"""

import http.server
import socketserver
import os
import urllib.parse
from pathlib import Path

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Handle department routes
        if path.startswith('/departments/'):
            # Serve index.html for department routes to enable client-side routing
            self.path = '/index.html'
        elif path == '/departments':
            # Serve index.html for departments list
            self.path = '/index.html'
        elif path == '/':
            # Serve index.html for root
            self.path = '/index.html'
        
        # Call the parent class method to serve the file
        return super().do_GET()

def run_server(port=8000):
    """Run the HTTP server on the specified port"""
    # Change to the directory containing this script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Create the server
    with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 Frontend server running at http://localhost:{port}")
        print(f"📁 Serving files from: {os.getcwd()}")
        print(f"🔗 Department pages: http://localhost:{port}/departments")
        print(f"🔗 Example: http://localhost:{port}/departments/1")
        print(f"📱 Press Ctrl+C to stop the server")
        print(f"=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped by user")
            httpd.shutdown()

if __name__ == "__main__":
    run_server() 