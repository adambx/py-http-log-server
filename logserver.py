import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

class TailRequestHandler(BaseHTTPRequestHandler):
    tail_length = int(os.getenv("TAIL_LENGTH", "2048"))
    file_paths = os.getenv("FILE_PATHS", "").split(",")
    file_mod_times = {}

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            content = "<html><body>"
            for path in self.file_paths:
                file_name = os.path.basename(path)
                content += f"<h2>{file_name}</h2>"
                content += f"<form><textarea id=\"{file_name}\" rows=\"20\" cols=\"80\" readonly>"
                if os.path.isfile(path):
                    with open(path, "rb") as f:
                        content += f.read().decode()
                content += "</textarea></form>"

            content += "</body></html>"
            self.wfile.write(content.encode())

        else:
            path = os.path.basename(self.path.removesuffix("/stream"))
            if path in [os.path.basename(fp) for fp in self.file_paths]:
                file_path = next((fp for fp in self.file_paths if os.path.basename(fp) == path), None)
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
                            self.send_line_data(tail_data)

                        while True:
                            time.sleep(0.1)
                            file_mod_time = os.path.getmtime(file_path)
                            if file_mod_time > self.file_mod_times[file_path]:
                                self.file_mod_times[file_path] = file_mod_time
                                with open(file_path, "rb") as f:
                                    f.seek(tail_start)
                                    new_data = f.read() - tail_data
                                    if new_data:
                                        self.send_line_data(new_data)

                    else:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()

                        content = "<html><body>"
                        content += f"<h2>{path}</h2>"
                        content += f"<form><textarea id=\"{path}\" rows=\"20\" cols=\"80\" readonly>"
                        with open(file_path, "rb") as f:
                            content += f.read().decode()
                        content += "</textarea></form>"
                        content += f"<script>var es = new EventSource(\"/{path}/stream\");es.onmessage = function(event){{document.getElementById(\"{path}\").value += event.data + \"\\n\"}};</script>"
                        content += "</body></html>"
                        self.wfile.write(content.encode())

                else:
                    self.send_error(404)

            else:
                self.send_error(404)

    def send_line_data(self, data):
        for line in data.splitlines():
            self.send_event_data(line.decode())

    def send_event_data(self, data):
        self.wfile.write(b"data: " + data.encode() + b"\n\n")

if __name__ == "__main__":
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, TailRequestHandler)
    for path in TailRequestHandler.file_paths:
        print(f"Serving tail of '{path}' on 'http://localhost:8000/{os.path.basename(path)}/stream'")
    print(f"Tail length is {TailRequestHandler.tail_length} bytes")
    httpd.serve_forever()

