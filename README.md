# Carbon Christmas Lights

A string of 100 fairy lights that shows how clean or dirty Great Britain's
electricity has been over the last 50 hours. Each light is one half-hour.
Green means the power was low-carbon; red means it was carbon-heavy.

Built by [Decent Energy](https://www.decentenergy.io) for the Christmas tree
in the foyer of the Cambridge Institute for Sustainability Leadership (CISL).

## What you are looking at

| Light colour | Carbon intensity band |
|---|---|
| Dark green | Very low |
| Light green | Low |
| Yellow | Moderate |
| Amber | High |
| Red | Very high |

- The first light on the string is 50 hours ago; the last is the most recent
  half-hour. Read along the string and you are reading two days of the
  electricity grid.
- Every half-hour the lights fetch new data. The pattern runs round the
  string four times to show it has updated, then holds still.
- The Pico also serves a web page that explains, in a sentence or two, why
  the lights are the colour they are right now. See
  [The explainer page](#the-explainer-page).

## Why it is worth a second look

**Electricity is not equally clean all day.** Carbon intensity is the CO₂
released to generate one kilowatt-hour of electricity. In Great Britain it
can be several times higher at one moment than another, depending on what is
generating. The lights make that visible without a single number.

**The weather is written on the tree.** A windy couple of days turns the
string green, because wind farms are doing most of the work. A still, grey
spell under high pressure, which forecasters call anticyclonic gloom, leaves
turbines and solar panels idle; gas power stations fill the gap and the
string turns amber and red. You can often guess the weather of the last two
days from the colours alone.

**You can see the daily rhythm.** Demand peaks in the early evening, when
the last and least efficient power stations are switched on, and falls
overnight. On a mixed day the string shows that as a repeating pattern of
warmer and cooler colours, roughly every 48 lights.

**It makes the case for flexibility.** If the same kettle, car charge or
battery cycle causes less carbon at a green moment than a red one, then
*when* we use electricity matters as much as how much we use. Shifting
demand into the cleaner half-hours is the idea behind Decent Energy's work:
decarbonise energy demand, not just supply.

**It is honest about bad days.** The lights do not flatter. A week of red in
December is a fair picture of how much the grid still leans on gas when the
wind drops, and a good conversation starter about storage, interconnectors
and demand that can move.

Questions the tree tends to prompt:

- Why is it red at teatime and green at 3 am?
- What was the weather doing when that amber stretch happened?
- How much of the string was green this time last year? The bands are set by
  the Carbon Intensity API and tighten year by year as the grid decarbonises.

## Where the data comes from

The [Carbon Intensity API](https://carbonintensity.org.uk/) is run by the
National Energy System Operator. For every half-hour it publishes the carbon
intensity of electricity in Great Britain, in grams of CO₂ per kilowatt-hour,
and sorts it into five bands from "very low" to "very high". It also
publishes the generation mix: how much came from gas, wind, nuclear, solar,
imports and so on. The API is free and needs no account.

The lights use the band for each of the last 100 half-hours. The explainer
page uses the bands and the generation mix.

## How it works

1. At power-up the Pico joins WiFi and sets its clock from the internet.
2. It asks the API for the last 100 half-hours and turns each band into a
   colour.
3. It writes those 100 colours to the LED string, scrolls them round four
   times, then holds them in place.
4. About 90 seconds after each new half-hour begins, it does it again.
5. Between steps it answers requests for the explainer page.
6. If a refresh fails, the string keeps its last colours and the Pico tries
   again a minute later.

| File | What it does |
|---|---|
| `main.py` | Start-up file; hands over to `remote.py` |
| `remote.py` | WiFi, WebREPL and self-updating, then runs the lights |
| `lights.py` | The lights program: fetches the data and drives the string |
| `web.py` | Small web server that serves the explainer page |
| `index.html` | The explainer page |
| `test_leds.py` | Wiring and colour test |
| `wifi_test.py` | WiFi diagnostic |
| `config.py` | Your settings; not in git |

## The explainer page

`index.html` is a single-screen display designed for a foyer monitor, in
Decent Energy's brand style. It shows:

- a headline question, such as "Why are the lights amber and red?"
- a short answer worked out from the live generation mix, for example that
  gas is generating most of the power because there has been little wind
- the current carbon intensity, with a bulb in the matching colour
- the string of 100 lights as it currently appears on the tree
- the four biggest sources of electricity right now

The page fetches its data in the viewer's browser, straight from the Carbon
Intensity API, and refreshes itself every half-hour. The data does not
include the weather, so anything the page says about wind or sun is inferred
from how much the turbines and panels are producing.

Three ways to show it:

- **From the Pico:** browse to `http://carbon-lights.local/`, or to the IP
  address the Pico prints at start-up. The viewing device must be on the
  same network as the Pico and have internet access.
- **From a file:** open `index.html` in a browser. Nothing else is needed.
- **From a web host:** it is one self-contained file, so any static host
  works, including GitHub Pages.

The page loads its fonts from Google Fonts and falls back to system fonts
without them.

## Hardware

- Raspberry Pi Pico 2 W
- BTF-LIGHTING WS2812B fairy string: 100 LEDs, 10 m, 5 V, IP65
- 5 V power supply. At the default half brightness the string draws under
  2 A, and no more than about 6 A at full-brightness white, so a 5 V 4 A
  supply is enough for normal use.
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
- A supply with exposed mains terminals must be fitted in an enclosure with
  a fused mains lead. For a public space, a sealed plug-in 5 V adapter is
  the safer choice.
- If the far end of the string dims or changes colour, lower `BRIGHTNESS` or
  feed 5 V into both ends.
- After switching the supply off, wait about 30 seconds before switching it
  back on.

## Setup

1. Flash the [MicroPython firmware for the Pico 2 W](https://micropython.org/download/RPI_PICO2_W/).
2. Copy `config.example.py` to `config.py` and set the WiFi name and password.
3. Copy the code, the page and your config to the Pico, with Thonny or:

   ```bash
   mpremote cp main.py remote.py lights.py web.py index.html test_leds.py wifi_test.py config.py :
   ```

4. Check the wiring and colours: `mpremote run test_leds.py` wipes the string
   red, green, blue, then shows each carbon intensity colour in turn and all
   of them side by side. If red and green are swapped, change `COLOUR_ORDER`
   in `config.py` between `"RGB"` and `"GRB"`.
5. Reset the Pico (`mpremote reset`). `main.py` starts on its own at power-up.

The onboard LED blinks while joining WiFi, stays on while updates succeed,
and goes off if an update fails (it retries every minute). If it never
connects, `mpremote run wifi_test.py` shows whether the network is in range
and where joining fails.

The Pico joins 2.4 GHz networks that use a shared password (WPA2 or WPA3
Personal). It cannot join networks that need a username as well as a
password, such as eduroam, or ones with a sign-in web page.

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
