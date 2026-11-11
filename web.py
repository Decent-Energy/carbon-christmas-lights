"""A very small web server for the Pico 2 W: serves index.html to browsers.

The page does the real work itself: the visitor's browser fetches the grid
data straight from the Carbon Intensity API. The Pico only hands over the
file, between steps of the lights program.

    web.start()        # open port 80
    web.sleep(0.3)     # like time.sleep, but answers requests while waiting
"""
import os
import select
import socket
import time

PAGE = "index.html"
CHUNK = 1024

_server = None
_poller = None


def start(port=80):
    """Begin listening. Safe to call again; returns True if the server is up."""
    global _server, _poller
    if _server is not None:
        return True
    try:
        os.stat(PAGE)
        server = socket.socket()
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(socket.getaddrinfo("0.0.0.0", port)[0][-1])
        server.listen(2)
    except Exception as error:
        print("Web page not started:", error)
        return False
    _poller = select.poll()
    _poller.register(server, select.POLLIN)
    _server = server
    return True


def stop():
    global _server, _poller
    try:
        _server.close()
    except Exception:
        pass
    _server = _poller = None


def _send_page(client):
    size = os.stat(PAGE)[6]
    client.sendall(("HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n"
                    "Content-Length: %d\r\nCache-Control: no-cache\r\nConnection: close\r\n\r\n" % size).encode())
    with open(PAGE, "rb") as f:
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            client.sendall(chunk)


def _serve_one():
    try:
        client = _server.accept()[0]
    except OSError:
        return
    try:
        client.settimeout(1)  # a browser that connects and says nothing must not stall the lights
        request = client.recv(1024)
        parts = request.split(b"\r\n", 1)[0].split(b" ")
        path = parts[1].split(b"?")[0] if len(parts) > 1 else b""
        if parts[0] == b"GET" and path in (b"/", b"/index.html"):
            _send_page(client)
        else:
            client.sendall(b"HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\nNot found\n")
    except Exception as error:
        print("Web request failed:", error)
    finally:
        client.close()


def sleep(seconds):
    """Wait like time.sleep, answering any web requests that arrive meanwhile."""
    if _server is None:
        time.sleep(seconds)
        return
    deadline = time.ticks_add(time.ticks_ms(), int(seconds * 1000))
    while True:
        remaining = time.ticks_diff(deadline, time.ticks_ms())
        if remaining <= 0:
            return
        try:
            if _poller.poll(min(remaining, 1000)):
                _serve_one()
        except Exception as error:  # the lights matter more than the page: give up serving
            print("Web page stopped:", error)
            stop()
            time.sleep(max(time.ticks_diff(deadline, time.ticks_ms()), 0) / 1000)
            return
