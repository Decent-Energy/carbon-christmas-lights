"""Start-up file for the Pico 2 W: MicroPython runs main.py at power-up.

It hands over to remote.py, which joins WiFi, picks up any new code and then
runs the lights program in lights.py.
"""
import remote

remote.launch()
