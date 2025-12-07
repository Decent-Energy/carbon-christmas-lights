import adafruit_neopixel as neopixel
from gpiozero import Device

# Use the built-in neopixel driver device
pixels = neopixel.NeoPixel(
    pin=None,             # No GPIO pin (hardware driver)
    n=100,                # Number of LEDs
    pixel_order=neopixel.GRB,
)

# Test sequence
pixels.fill((255, 0, 0))
pixels.show()
input("Red... Press Enter")

pixels.fill((0, 255, 0))
pixels.show()
input("Green... Press Enter")

pixels.fill((0, 0, 255))
pixels.show()
input("Blue... Press Enter")

pixels.fill((0, 0, 0))
pixels.show()
