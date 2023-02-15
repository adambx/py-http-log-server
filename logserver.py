from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

import os
import socket
from string import Template
import time

class TailRequestHandler(BaseHTTPRequestHandler):
    tail_length = int(os.getenv("TAIL_LENGTH", "2048"))
    file_paths = os.getenv("FILE_PATHS", "").split(",")
    file_mod_times = {}

    def do_GET(self):
        path = self.path.rstrip("/stream")
        file_name = os.path.basename(path)

        if file_name in [os.path.basename(fp) for fp in self.file_paths]:
            file_path = next((fp for fp in self.file_paths if os.path.basename(fp) == file_name), None)
            if file_path and os.path.isfile(file_path):
                if self.path.endswith("/stream"):
                    self.send_response(200)
                    self.send_header("Content-type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()

                    file_mod_time = os.path.getmtime(file_path)
                    self.file_mod_times[file_path] = file_mod_time

                    file_size = os.path.getsize(file_path)
                    if file_size > self.tail_length:
                        tail_start = max(file_size - self.tail_length, 0)
                    else:
                        tail_start = 0

                    with open(file_path, "rb") as f:
                        f.seek(tail_start)
                        tail_data = f.read()

                    while True:
                        time.sleep(1)
                        file_mod_time = os.path.getmtime(file_path)
                        if file_mod_time > self.file_mod_times[file_path]:
                            self.file_mod_times[file_path] = file_mod_time
                            with open(file_path, "rb") as f:
                                f.seek(tail_start + len(tail_data))
                                new_data = f.read()
                                tail_data += new_data
                                if new_data:
                                    self.send_line_data(new_data)

                else:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.send_header("Pragma", "no-cache")
                    self.send_header("Expires", "0")
                    self.end_headers()

                    # Define the HTML template
                    with open('template.html', 'r') as f:
                        template_content = f.read()
                        template = Template(template_content)
                    
                    with open(file_path, "rb") as f:
                        file_contents = f.read().decode()

                    sse_url = f"/{file_name}/stream"

                    content = template.safe_substitute(file_name=file_name, file_contents=file_contents, sse_url=sse_url)
                    self.wfile.write(content.encode())

            else:
                self.send_error(404)

        else:
            self.send_error(404)

    def send_line_data(self, data):
        for line in data.splitlines():
            self.send_event_data(line.decode())

    def send_event_data(self, data):
        try:
            self.wfile.write(b"data: " + data.encode() + b"\n\n")
        except BrokenPipeError:
            pass

if __name__ == "__main__":
    server_address = ("", 8000)
    httpd = ThreadingHTTPServer(server_address, TailRequestHandler)
    for path in TailRequestHandler.file_paths:
        print(f"Serving tail of '{path}' on 'http://localhost:8000/{os.path.basename(path)}'")
    print(f"Serving landing pages on 'http://localhost:8000/[filename]'")
    httpd.serve_forever()