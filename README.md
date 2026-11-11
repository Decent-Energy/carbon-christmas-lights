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
3. Copy the code and your config to the Pico, with Thonny or:

   ```bash
   mpremote cp main.py remote.py lights.py test_leds.py config.py :
   ```

4. Check the wiring and colours: `mpremote run test_leds.py` wipes the string
   red, green, blue, then shows each carbon intensity colour in turn and all
   of them side by side. If red and green are swapped, change `COLOUR_ORDER`
   in `config.py` between `"RGB"` and `"GRB"`.
5. Reset the Pico (`mpremote reset`). `main.py` starts on its own at power-up.

The onboard LED blinks while joining WiFi, stays on while updates succeed,
and goes off if an update fails (it retries every minute).

| File | What it does |
|---|---|
| `main.py` | Start-up file; hands over to `remote.py` |
| `remote.py` | WiFi, WebREPL and self-updating, then runs the lights |
| `lights.py` | The lights program: fetches the data and drives the string |
| `test_leds.py` | Wiring and colour test |
| `config.py` | Your settings; not in git |

## Updating without a cable

Both methods are off until you add their settings to `config.py` (see
`config.example.py`) and copy it to the Pico once over USB.

### Self-update from GitHub

Set `UPDATE_REPO` and `UPDATE_BRANCH`, plus `GITHUB_TOKEN` if the repo is
private (a fine-grained token with read-only Contents access to this repo).
At power-up and before each half-hourly refresh, the Pico compares the
branch's latest commit with the one it is running. If it differs, it
downloads the files listed in `update_files.txt` and restarts.

- Push to the branch, then wait up to half an hour or power-cycle the Pico.
- Code with a syntax error is refused. Code that crashes, or that hasn't
  completed a refresh within three starts, is replaced by the previous
  version, and that commit is skipped until a newer one arrives.
- `main.py`, `remote.py` and `config.py` are never updated this way.
- GitHub becomes the source of truth: files copied by hand are overwritten
  by the next commit.

### WebREPL

Set `WEBREPL_PASSWORD` (4 to 9 characters). The Pico then accepts file
uploads and a remote prompt from computers on the same network, at
`carbon-lights.local` or the IP address it prints at start-up.

Get `webrepl_cli.py` from <https://github.com/micropython/webrepl>, then:

```bash
python webrepl_cli.py -p YOUR_PASSWORD lights.py carbon-lights.local:/lights.py
```

Restart the Pico to run the new file: open the prompt with
`python webrepl_cli.py -p YOUR_PASSWORD carbon-lights.local`, press Ctrl-C,
then enter `import machine; machine.reset()`.

WebREPL is unencrypted and guarded only by that password, so use it on a
network you trust.
