"""
    ServeMe.py / ServeMe.exe

    A minimalist wrapper around http.server which will serve the directory in which it is
    started, mainly design to serve local documentation.

    ServeMe:
    - will only bind to the loopback address (127.0.0.1 or localhost)
    - will try to bind to the first available port between 42000 and 42999
    - will only serv static files (no processing)
    - will not allow browsing outside the process directory and its children
    - will self-terminate after 3 hours of inactivity
    - can be started multiple times from different directory concurrently

    Build using pyInstaller:
    pyInstaller -F -w ServeMe.py

    MIT License
    Copyright (c) 2022 HgAlexx
"""
import datetime
import http.server
import os.path
import socketserver
import webbrowser
import filelock
import threading
import time
import signal


INITIAL_PORT = 42000  # starting port to try
MAX_PORT_TRY = 999  # maximum number of try
SEPPUKU = 60*60*3  # 3 hours: time in seconds before the process self-terminate


class Main:
    watcher = None
    handler = None
    started = False
    httpd = None
    last_request = datetime.datetime.now()
    base_path = ""

    @staticmethod
    def thread_function():
        while Main.started:
            if Main.last_request is not None:
                diff = datetime.datetime.now() - Main.last_request
                if diff.total_seconds() >= SEPPUKU:
                    Main.shutdown()
            time.sleep(10)

    @staticmethod
    def shutdown(*args):
        Main.started = False
        if Main.httpd is not None:
            Main.httpd.shutdown()

    @staticmethod
    def run():
        global INITIAL_PORT, MAX_PORT_TRY

        Main.base_path = os.getcwd()

        lock = filelock.FileLock("ServeMe.lock")
        try:
            lock.acquire(timeout=1)
            try:
                Main.handler = ServeMeHandler
                tries = 1
                Main.started = False

                while tries < MAX_PORT_TRY and not Main.started:
                    try:
                        Main.httpd = socketserver.TCPServer(("127.0.0.1", INITIAL_PORT), Main.handler)
                        Main.started = True
                    except OSError:
                        INITIAL_PORT = INITIAL_PORT + 1
                        tries = tries + 1

                if Main.started:
                    webbrowser.open("http://localhost:" + str(INITIAL_PORT))
                    Main.watcher = threading.Thread(target=Main.thread_function, daemon=True)
                    Main.watcher.start()
                    Main.httpd.serve_forever()

            finally:
                lock.release()
                if Main.httpd is not None:
                    Main.httpd.server_close()

        except filelock.Timeout:
            # process is already running for this folder, just open the url
            webbrowser.open("http://localhost:" + str(INITIAL_PORT))


class ServeMeHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        Main.last_request = datetime.datetime.now()
        path = self.translate_path(self.path)
        # most browsers and tools strip double-dot from url, but better safe than sorry
        if os.path.commonprefix([path, Main.base_path]) == Main.base_path:
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_error(404)
            return None


Main.run()
