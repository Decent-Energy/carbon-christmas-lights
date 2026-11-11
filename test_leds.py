"""Wiring test for the Pico 2 W: wipes the string red, green, blue, then off.

Run it from Thonny or with `mpremote run test_leds.py`. If red and green
come out swapped, set COLOUR_ORDER = "RGB" in config.py.
"""
import time

import machine
import neopixel

try:
    import config
    LED_PIN = config.LED_PIN
    LED_COUNT = config.LED_COUNT
    BRIGHTNESS = config.BRIGHTNESS
    COLOUR_ORDER = getattr(config, "COLOUR_ORDER", "GRB")
except ImportError:
    LED_PIN = 0
    LED_COUNT = 100
    BRIGHTNESS = 0.5
    COLOUR_ORDER = "GRB"

if COLOUR_ORDER == "RGB":
    neopixel.NeoPixel.ORDER = (0, 1, 2, 3)

strip = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)
level = int(255 * BRIGHTNESS)


def colour_wipe(colour, wait_ms=20):
    for i in range(len(strip)):
        strip[i] = colour
        strip.write()
        time.sleep_ms(wait_ms)


for name, colour in (("Red", (level, 0, 0)), ("Green", (0, level, 0)), ("Blue", (0, 0, level))):
    print(name)
    colour_wipe(colour)
    time.sleep(1)

colour_wipe((0, 0, 0))
print("Done")
