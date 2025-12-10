import time
from rpi_ws281x import PixelStrip, Color

LED_COUNT = 100       # number of LEDs on your string
LED_PIN = 18          # GPIO18 = physical pin 12
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 128  # 0–255
LED_INVERT = False
LED_CHANNEL = 0

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Fill colors
colors = [Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)]

for c in colors:
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, c)
    strip.show()
    time.sleep(1)

# Clear LEDs
for i in range(strip.numPixels()):
    strip.setPixelColor(i, 0)
strip.show()