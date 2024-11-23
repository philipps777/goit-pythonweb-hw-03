from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import os
from datetime import datetime
import mimetypes
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('.'))


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/':
            self.send_html_file('index.html')
        elif parsed_path.path == '/message':
            self.send_html_file('message.html')
        elif parsed_path.path == '/read':
            self.show_messages()
        elif parsed_path.path.startswith('/') and os.path.exists(parsed_path.path[1:]):
            self.send_static_file(parsed_path.path[1:])
        else:
            self.send_html_file('error.html', 404)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(body)
            message_data = {
                "username": data["username"][0],
                "message": data["message"][0]
            }
            self.save_message(message_data)

            self.send_response(302)
            self.send_header('Location', '.')
            self.end_headers()
        else:
            self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_static_file(self, filepath):
        try:
            full_path = os.path.join('.', filepath)
            

            if not os.path.exists(full_path):
                self.send_html_file('error.html', 404)
                return

            self.send_response(200)

            mime_type, _ = mimetypes.guess_type(full_path)
            if mime_type:
                self.send_header('Content-type', mime_type)
            else:
                self.send_header('Content-type', 'application/octet-stream')

            self.end_headers()

            with open(full_path, 'rb') as file:
                self.wfile.write(file.read())
        except Exception as e:
            print(f"Error serving static file: {e}")
            self.send_html_file('error.html', 404)

    def save_message(self, message):
        timestamp = datetime.now().isoformat()
        if not os.path.exists('storage'):
            os.makedirs('storage')
        file_path = 'storage/data.json'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = {}
        data[timestamp] = message
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def show_messages(self):
        file_path = 'storage/data.json'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                messages = json.load(file)
        else:
            messages = {}
        template = env.get_template('read.html')
        rendered_content = template.render(messages=messages)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(rendered_content.encode('utf-8'))


def run():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, HttpHandler)       
    print('Starting server on port 3000...')
    httpd.serve_forever()
   


if __name__ == '__main__':
    run()