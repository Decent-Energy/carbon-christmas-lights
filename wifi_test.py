"""WiFi check for the Pico 2 W: is the network in range, and can the Pico join?

Run it with `mpremote run wifi_test.py`. It needs config.py on the Pico and
prints no passwords.
"""
import time

import network
import rp2

import config

STATUS = {
    0: "idle",
    1: "joining",
    2: "joined, waiting for an address",
    3: "connected",
    -1: "failed",
    -2: "network not found",
    -3: "wrong password",
}

rp2.country(getattr(config, "WIFI_COUNTRY", "GB"))
wlan = network.WLAN(network.STA_IF)
wlan.active(False)  # start from a clean state
time.sleep(1)
wlan.active(True)

print("Looking for %r (name is %d characters, password is %d)"
      % (config.WIFI_SSID, len(config.WIFI_SSID), len(config.WIFI_PASSWORD)))

seen = {}
for entry in wlan.scan():
    try:
        name = entry[0].decode()
    except Exception:
        name = repr(entry[0])
    if name not in seen or entry[3] > seen[name][1]:
        seen[name] = (entry[2], entry[3])  # channel, signal strength

if config.WIFI_SSID in seen:
    channel, signal = seen[config.WIFI_SSID]
    print("Found it: channel %d, signal %d dBm (above -70 is good, below -80 is weak)" % (channel, signal))
else:
    print("Not found. The Pico only sees 2.4 GHz networks. It can see:")
    for name in sorted(seen):
        print("  %r  signal %d dBm" % (name, seen[name][1]))

print("Joining...")
wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
last = None
for second in range(30):
    status = wlan.status()
    if status != last:
        print("  %2d s: %s" % (second, STATUS.get(status, status)))
        last = status
    if status == 3:
        break
    time.sleep(1)

if wlan.isconnected():
    print("Connected, address", wlan.ifconfig()[0])
else:
    print("Did not connect; last status:", STATUS.get(wlan.status(), wlan.status()))
