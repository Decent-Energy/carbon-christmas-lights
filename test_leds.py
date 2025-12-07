import time
from rpi_ws281x import PixelStrip, Color

LED_COUNT = 100      # number of LEDs in your string
LED_PIN = 18         # GPIO pin for DATA

LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def colorWipe(color, wait_ms=20):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

# TEST SEQUENCE
colorWipe(Color(255, 0, 0))   # Red
time.sleep(1)

colorWipe(Color(0, 255, 0))   # Green
time.sleep(1)

colorWipe(Color(0, 0, 255))   # Blue
time.sleep(1)

colorWipe(Color(0, 0, 0))     # Off
