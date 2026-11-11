"""Carbon intensity Christmas lights for the Raspberry Pi Pico 2 W (MicroPython).

Shows the last 100 half-hour periods of GB grid carbon intensity on a
100-LED WS2812B string: one LED per period, oldest first, coloured by the
Carbon Intensity API's index.

main.py starts this at power-up, through remote.py. To run it by hand:
`mpremote run lights.py`.
"""
import gc
import time

import machine
import neopixel
import ntptime

try:
    import requests
except ImportError:  # older MicroPython builds
    import urequests as requests

import remote  # WiFi, WebREPL and updates from GitHub; also checks config.py exists
import config

PERIOD_S = 30 * 60          # the API reports in half-hour periods
SCROLL_LOOPS = 4            # times the pattern runs round the string after an update
SCROLL_DELAY_S = 0.3        # pause between scroll steps
RETRY_DELAY_S = 60          # wait after a failed update
SETTLE_S = 90               # wait after a period starts before asking for it
NTP_RESYNC_S = 12 * 60 * 60

# Colours as (red, green, blue) at full brightness, by API index.
INDEX_COLOURS = {
    "very low": (0, 110, 0),     # dark green
    "low": (90, 255, 0),         # light green
    "moderate": (255, 180, 0),   # yellow
    "high": (255, 80, 0),        # amber
    "very high": (255, 0, 0),    # red
}
OFF = (0, 0, 0)


def scale(colour, brightness):
    """Dim a colour; the neopixel driver has no brightness setting of its own."""
    return tuple(int(c * brightness) for c in colour)


def period_window(now_s, count):
    """Return (start, end) epoch seconds covering the last `count` periods."""
    end = now_s - now_s % PERIOD_S
    return end - count * PERIOD_S, end


def iso_minute(epoch_s):
    t = time.gmtime(epoch_s)
    return "%04d-%02d-%02dT%02d:%02dZ" % (t[0], t[1], t[2], t[3], t[4])


def intensity_url(now_s, count):
    start, end = period_window(now_s, count)
    return "https://api.carbonintensity.org.uk/intensity/%s/%s" % (iso_minute(start), iso_minute(end))


def colours_from_entries(entries, count, brightness):
    """Turn API entries into one colour per LED, keeping the newest `count`."""
    colours = []
    for entry in entries[-count:]:
        index = (entry.get("intensity") or {}).get("index")
        colours.append(scale(INDEX_COLOURS.get(index, OFF), brightness))
    return colours


# --- hardware ---------------------------------------------------------------

if getattr(config, "COLOUR_ORDER", "GRB") == "RGB":
    neopixel.NeoPixel.ORDER = (0, 1, 2, 3)

strip = neopixel.NeoPixel(machine.Pin(config.LED_PIN), config.LED_COUNT)


def show(colours, offset=0):
    n = len(strip)
    strip.fill(OFF)
    for i, colour in enumerate(colours):
        strip[(i + offset) % n] = colour
    strip.write()


def fetch_colours():
    url = intensity_url(time.time(), config.LED_COUNT)
    print("Fetching", url)
    gc.collect()
    response = requests.get(url, headers={"Accept": "application/json"}, timeout=20)
    try:
        if response.status_code != 200:
            raise RuntimeError("API returned status %d" % response.status_code)
        entries = response.json().get("data")
    finally:
        response.close()
    if not entries:
        raise RuntimeError("API returned no data")
    counts = {}
    for entry in entries[-config.LED_COUNT:]:
        index = (entry.get("intensity") or {}).get("index")
        counts[index] = counts.get(index, 0) + 1
    print("Periods by index:", counts)
    colours = colours_from_entries(entries, config.LED_COUNT, config.BRIGHTNESS)
    del entries
    gc.collect()
    return colours


def animate(colours):
    for _ in range(SCROLL_LOOPS):
        for offset in range(len(strip)):
            show(colours, offset)
            time.sleep(SCROLL_DELAY_S)
    show(colours)  # settle with the oldest period on the first LED


def main():
    show([])  # clear whatever the string powered up showing
    last_ntp = None
    while True:
        try:
            remote.connect_wifi()
            if last_ntp is None or time.time() - last_ntp > NTP_RESYNC_S:
                ntptime.settime()  # sets the clock to UTC, which the API expects
                last_ntp = time.time()
            remote.check_for_update()  # restarts the Pico if it installs new code
            colours = fetch_colours()
        except Exception as error:  # keep the current display and try again
            print("Update failed:", error)
            remote.status_led.off()
            time.sleep(RETRY_DELAY_S)
            continue

        remote.confirm()  # a full refresh worked, so keep any newly installed code
        remote.status_led.on()
        animate(colours)

        # Hold the display until shortly after the next half-hour begins.
        now = time.time()
        wait = PERIOD_S - now % PERIOD_S + SETTLE_S
        print("Next update in", wait, "seconds")
        time.sleep(wait)


if __name__ == "__main__":
    main()
