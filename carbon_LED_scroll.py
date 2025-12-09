import requests
from datetime import datetime, timedelta, timezone
import time

# Try to import the rpi_ws281x library, and mock it if unavailable
try:
    from rpi_ws281x import PixelStrip, Color
except ModuleNotFoundError:
    print("rpi_ws281x library not found. Using mock implementation.")

    class PixelStrip:
        def __init__(self, num, pin, freq_hz, dma, invert, brightness, channel):
            self.num = num

        def begin(self):
            print("Mock PixelStrip initialized.")

        def numPixels(self):
            return self.num

        def setPixelColor(self, n, color):
            print(f"Mock: Setting LED {n} to color {color}")

        def show(self):
            print("Mock: Updating LED strip.")

    class Color:
        def __init__(self, r, g, b):
            self.r = r
            self.g = g
            self.b = b

# LED strip configuration
LED_COUNT = 100      # Number of LEDs in your string
LED_PIN = 18         # GPIO pin for DATA
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 255
LED_INVERT = False
LED_CHANNEL = 0

# Initialize the LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def fetch_last_100_periods():
    """Fetch the last 100 30-minute periods of carbon intensity data."""
    now = datetime.now(timezone.utc)
    minute = 30 if now.minute >= 30 else 0
    end = now.replace(minute=minute, second=0, microsecond=0)

    # Calculate the start time for 100 30-minute periods (50 hours)
    start = end - timedelta(minutes=30 * 100)

    start_str = start.strftime("%Y-%m-%dT%H:%MZ")
    end_str = end.strftime("%Y-%m-%dT%H:%MZ")

    url = f"https://api.carbonintensity.org.uk/intensity/{start_str}/{end_str}"
    print(f"Fetching data from URL: {url}")

    response = requests.get(url)
    if response.status_code != 200:
        raise RuntimeError(f"API request failed with status code {response.status_code}: {response.text}")

    json_data = response.json()
    if "data" not in json_data:
        raise RuntimeError(f"Unexpected API response: {json_data}")

    entries = json_data["data"]
    if not entries:
        raise RuntimeError("No data entries found in the API response.")

    # Create an array of 30-minute periods with timestamps and index values
    periods_with_index = []
    for entry in entries:
        timestamp = entry.get("from")
        index = entry.get("intensity", {}).get("index")
        if timestamp and index:
            periods_with_index.append({"timestamp": timestamp, "index": index})

    return periods_with_index

def set_led_color(index):
    """Set the LED color based on the carbon intensity index."""
    if index == "low":
        return Color(0, 255, 0), "Green"  # Green
    elif index == "moderate":
        return Color(255, 255, 0), "Yellow"  # Yellow
    elif index == "high":
        return Color(255, 165, 0), "Amber"  # Amber
    elif index == "very high":
        return Color(255, 0, 0), "Red"  # Red
    else:
        return Color(0, 0, 0), "Off"  # Off (default for unknown index)

def display_carbon_intensity(periods_with_index):
    """Display the carbon intensity on the LED strip with animation."""
    print("Starting LED animation...")
    for _ in range(4):  # Repeat the animation 4 times
        for offset in range(strip.numPixels()):  # Create the running effect
            for i, period in enumerate(periods_with_index):
                if i >= strip.numPixels():
                    break  # Ensure we don't exceed the number of LEDs
                index = period["index"]
                color, color_name = set_led_color(index)
                led_position = (i + offset) % strip.numPixels()  # Wrap around the strip
                strip.setPixelColor(led_position, color)
                print(f"LED {led_position}: {color_name} (Index: {index})")
            strip.show()
            time.sleep(0.3)  # Slower animation speed (adjusted from 0.1 to 0.3)

    print("Holding static colors for 1 minute...")
    for i, period in enumerate(periods_with_index):
        if i >= strip.numPixels():
            break
        index = period["index"]
        color, color_name = set_led_color(index)
        strip.setPixelColor(i, color)
        print(f"LED {i}: {color_name} (Index: {index})")
    strip.show()
    time.sleep(60)  # Hold the static display for 1 minute

if __name__ == "__main__":
    while True:
        periods_with_index = fetch_last_100_periods()
        print(periods_with_index)  # Print the array of timestamps and indices
        display_carbon_intensity(periods_with_index)
        print("Waiting 30 minutes for the next update...")
        time.sleep(1800)  # Wait 30 minutes before fetching new data