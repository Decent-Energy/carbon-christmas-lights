# Copy this file to config.py, fill it in, and copy config.py to the Pico.
# config.py is git-ignored so the WiFi password stays out of the repo.

WIFI_SSID = "your-network-name"
WIFI_PASSWORD = "your-wifi-password"
WIFI_COUNTRY = "GB"

LED_PIN = 0          # GP0 (physical pin 1) -> string data wire
LED_COUNT = 100      # LEDs on the string, one per half-hour period
BRIGHTNESS = 0.5     # 0.0 to 1.0; lower it if the far end of the string dims
COLOUR_ORDER = "RGB" # this string is RGB; use "GRB" if test_leds.py shows red and green swapped

# --- Remote access and updates (both optional) ---

HOSTNAME = "carbon-lights"   # the Pico answers to carbon-lights.local on most networks

# Web page: the Pico serves index.html, which explains the lights, at
# http://carbon-lights.local/ (or its IP address). Set to False to switch off.
WEB_PAGE = True

# WebREPL: push files to the Pico over the local network. 4 to 9 characters;
# leave empty to keep it switched off.
WEBREPL_PASSWORD = ""

# Self-update: the Pico installs new commits from this GitHub repo and branch
# at power-up and every half-hour. Leave UPDATE_REPO empty to switch it off.
UPDATE_REPO = ""             # e.g. "Decent-Energy/carbon-christmas-lights"
UPDATE_BRANCH = "main"
GITHUB_TOKEN = ""            # private repos only: a token with read-only Contents access
