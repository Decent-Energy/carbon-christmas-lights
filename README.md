# carbon-christmas-lights

A string of 100 fairy lights that shows the last 50 hours of GB grid carbon
intensity: one LED per half-hour period, oldest first, coloured by the
[Carbon Intensity API](https://carbonintensity.org.uk/) index.

| Index | Colour |
|---|---|
| very low | dark green |
| low | light green |
| moderate | yellow |
| high | amber |
| very high | red |

After each update the pattern runs round the string four times, then holds
still until the next half-hour.

## Hardware

- Raspberry Pi Pico 2 W
- BTF-LIGHTING WS2812B fairy string: 100 LEDs, 10 m, 5 V, IP65
- 5 V 20 A (100 W) switching power supply (indoor use only)
- 1000 µF 10 V electrolytic capacitor
- Recommended: 330 Ω resistor for the data line

## Wiring

| From | To |
|---|---|
| Supply V+ (5 V) | String 5 V, and Pico VSYS (pin 39) |
| Supply V− | String GND, and Pico GND (pin 38) |
| Pico GP0 (pin 1) | String data in, through the 330 Ω resistor |
| Capacitor | Across 5 V and GND at the start of the string, stripe to GND |

- Don't plug in USB while the Pico is powered from the supply through VSYS,
  unless there is a diode between the supply and VSYS.
- The Pico's 3.3 V data signal is slightly below what 5 V WS2812Bs ask for.
  Keep the data wire short; if the string flickers, add a 74AHCT125 level
  shifter.
- The supply has exposed mains terminals: fit it in an enclosure and use a
  fused mains lead.
- If the far end of the string dims or changes colour, lower `BRIGHTNESS` or
  feed 5 V into both ends.

## Setup

1. Flash the [MicroPython firmware for the Pico 2 W](https://micropython.org/download/RPI_PICO2_W/).
2. Copy `config.example.py` to `config.py` and set the WiFi name and password.
3. Copy `main.py`, `config.py` and `test_leds.py` to the Pico, with Thonny or:

   ```bash
   mpremote cp main.py config.py test_leds.py :
   ```

4. Check the wiring and colours: `mpremote run test_leds.py` wipes the string
   red, green, blue, then shows each carbon intensity colour in turn and all
   of them side by side. If red and green are swapped, change `COLOUR_ORDER`
   in `config.py` between `"RGB"` and `"GRB"`.
5. Reset the Pico. `main.py` starts on its own at power-up.

The onboard LED blinks while joining WiFi, stays on while updates succeed,
and goes off if an update fails (it retries every minute).
