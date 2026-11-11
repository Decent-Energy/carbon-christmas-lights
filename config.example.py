# Copy this file to config.py, fill it in, and copy config.py to the Pico.
# config.py is git-ignored so the WiFi password stays out of the repo.

WIFI_SSID = "your-network-name"
WIFI_PASSWORD = "your-wifi-password"
WIFI_COUNTRY = "GB"

LED_PIN = 0          # GP0 (physical pin 1) -> string data wire
LED_COUNT = 100      # LEDs on the string, one per half-hour period
BRIGHTNESS = 0.5     # 0.0 to 1.0; lower it if the far end of the string dims
COLOUR_ORDER = "GRB" # change to "RGB" if test_leds.py shows red and green swapped
