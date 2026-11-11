"""LED test for the Pico 2 W: checks the wiring, then previews every colour.

Run it with `mpremote run test_leds.py` (or from Thonny). It needs main.py
and config.py on the Pico, because it uses the colours and settings from
them; copy main.py again after changing a colour.

1. Wipes the string red, green, blue. If red and green come out swapped,
   switch COLOUR_ORDER in config.py between "RGB" and "GRB".
2. Fills the whole string with each carbon intensity colour in turn.
3. Shows all the colours side by side, cleanest first, then switches off.
"""
import time

import config
from main import INDEX_COLOURS, OFF, scale, show, strip

# MicroPython dictionaries don't keep their order, so spell it out here.
BANDS = ("very low", "low", "moderate", "high", "very high")

FILL_HOLD_S = 3      # time on each full-string colour
BLOCKS_HOLD_S = 20   # time on the side-by-side view

n = len(strip)
level = int(255 * config.BRIGHTNESS)


def wipe(colour, wait_ms=10):
    for i in range(n):
        strip[i] = colour
        strip.write()
        time.sleep(wait_ms / 1000)


print("Wiring check")
for name, colour in (("red", (level, 0, 0)), ("green", (0, level, 0)), ("blue", (0, 0, level))):
    print(" ", name)
    wipe(colour)
    time.sleep(1)

print("Carbon intensity colours, one at a time")
for band in BANDS:
    colour = scale(INDEX_COLOURS[band], config.BRIGHTNESS)
    print("  %-9s %s" % (band, colour))
    strip.fill(colour)
    strip.write()
    time.sleep(FILL_HOLD_S)

print("All colours side by side, very low first, for", BLOCKS_HOLD_S, "seconds")
show([scale(INDEX_COLOURS[BANDS[i * len(BANDS) // n]], config.BRIGHTNESS) for i in range(n)])
time.sleep(BLOCKS_HOLD_S)

strip.fill(OFF)
strip.write()
print("Done")
