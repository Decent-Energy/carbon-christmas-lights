# Setting up the Pimoroni Plasma 2350 W

Instructions for getting the carbon Christmas lights running on a new
Pimoroni Plasma 2350 W, written so that Claude Code can carry them out on
the machine the board is plugged into. Steps marked **(person)** need hands
on the hardware.

## Where things stand

- This branch, `plasma-2350`, holds the code for the Plasma board. The
  original Raspberry Pi Pico 2 W build is on `claude/youthful-mendel-v86smr`
  and is already running.
- The Plasma changes were tested only against stubbed hardware. **Nothing on
  this branch has run on a real Plasma 2350 W yet**, so check each stage
  before moving on, and expect to fix small things.
- The machine is Windows with PowerShell. `mpremote` is installed but not on
  the PATH, so run it as `python -m mpremote ...` (or `py -m mpremote ...`).
- `config.py` is git-ignored and holds the WiFi password and WebREPL
  password. Never print its contents, paste it into a reply, or commit it.

## What differs from the Pico build

| | Pico 2 W | Plasma 2350 W |
|---|---|---|
| Firmware | Standard MicroPython | Pimoroni's build, from `pimoroni/plasma` |
| LED data pin | GP0 | GP15 (the board's data screw terminal) |
| Status light | Single LED, on when the pin is high | Green part of a colour LED, on when the pin is **low** |
| Power | Separate 5 V supply, VSYS wiring | One USB-C cable, 3 A limit |

`remote.py` detects the board from `os.uname().machine` (it looks for
"Plasma") and inverts the status light. `STATUS_LED_INVERTED = True` or
`False` in `config.py` overrides the detection.

## Steps

### 1. Firmware **(person, then check)**

1. **(person)** Plug the board into the computer with a USB-C cable. Leave
   the LED string disconnected.
2. **(person)** Hold **BOOT** and tap **RST**. A drive named `RP2350` appears.
3. Download the latest release from
   <https://github.com/pimoroni/plasma/releases/latest>. Take the asset whose
   name starts `plasma_2350_w` and ends `-micropython.uf2`. Do **not** take
   the `-with-filesystem` one: it erases the board's files and adds example
   scripts.
4. Copy the `.uf2` onto the `RP2350` drive. The drive disappears when done.
5. Check the board answers:

   ```powershell
   python -m mpremote exec "import os; print(os.uname().machine)"
   ```

   Expected: a line containing `Pimoroni Plasma 2350`. If `mpremote` finds no
   device, wait a few seconds, try another cable or port, and make sure
   Thonny is closed.

6. Check the modules the code needs are present:

   ```powershell
   python -m mpremote exec "import neopixel, ntptime, requests, webrepl, network, rp2, select, socket; print('modules ok')"
   ```

   If `requests` is missing, `import urequests` should work instead; the code
   falls back to it. Any other failure needs a code change, so stop and report.

### 2. Check out this branch

```powershell
cd C:\dev\carbon-christmas-lights
git fetch origin plasma-2350
git checkout plasma-2350
git pull
```

### 3. Configure

`config.py` already exists in the folder, set up for the Pico.

1. Copy it to `config-pico.py` so the Pico's settings are kept. Confirm
   `config-pico.py` is not tracked by git (add it to `.gitignore` if `git
   status` shows it).
2. In `config.py`, set these and leave the WiFi lines alone:

   ```python
   LED_PIN = 15
   HOSTNAME = "carbon-plasma"
   UPDATE_BRANCH = "plasma-2350"
   BRIGHTNESS = 0.2   # temporary, while powered from the computer's USB port
   ```

3. Check, without printing values, that the file also defines `WIFI_SSID`,
   `WIFI_PASSWORD`, `LED_COUNT`, `COLOUR_ORDER`, `UPDATE_REPO` and
   `WEBREPL_PASSWORD`, and that `WEBREPL_PASSWORD` is 4 to 9 characters or
   empty. Compare against `config.example.py` for anything missing.

### 4. Copy the files to the board

```powershell
python -m mpremote cp main.py remote.py lights.py web.py index.html test_leds.py wifi_test.py config.py :
python -m mpremote ls
```

All eight files should be listed. A fresh board may also hold Pimoroni's
example files; they are harmless, but any existing `main.py` is replaced by
ours.

### 5. Status light check

```powershell
python -m mpremote exec "import remote, time; remote.status_led.on(); time.sleep(3); remote.status_led.off(); time.sleep(1); print('PLASMA =', remote.PLASMA)"
```

Expected: `PLASMA = True`, and **(person)** the board's small light shows
green for three seconds, then goes off. If it is off for three seconds and
then on, the inversion is wrong: add `STATUS_LED_INVERTED = False` to
`config.py`, copy it again, and report it.

### 6. Wire the string **(person)**

1. Unplug the USB cable.
2. Connect the string's three wires to the screw terminals: 5 V to `5V`,
   data to the data terminal (expected to be marked `DA` or `DAT`), ground to
   `-` or `GND`. Leave the clock terminal (`CL` or `CLK`) empty.
3. Plug the USB cable back in.

The terminal labels above were not checked against a real board. Go by what
is printed on it, and note the actual labels in the report.

### 7. Test the LEDs

```powershell
python -m mpremote run test_leds.py
```

Expected: the string wipes red, green, blue, then shows the five carbon
colours one at a time and side by side, then goes dark.

- Nothing lights: check the data wire is in the data terminal and at the
  string's input end; confirm `LED_PIN = 15` reached the board with
  `python -m mpremote exec "import config; print(config.LED_PIN)"`.
- Red and green swapped: switch `COLOUR_ORDER` between `"RGB"` and `"GRB"`.
- The board restarts or disconnects when the string lights: the computer's
  USB port cannot supply enough current. Lower `BRIGHTNESS` further, or do
  this step on the charger and skip to step 9.

### 8. Run the program

```powershell
python -m mpremote run main.py
```

Expected, in order:

1. `WiFi connected: <address>`
2. `WebREPL server started on ...` (if a WebREPL password is set)
3. Either nothing about updates, or `Updating to ...` and a restart. After a
   restart the command exits; run `python -m mpremote repl` to keep watching.
4. `Web page at http://<address>/`
5. `Fetching https://api.carbonintensity.org.uk/...`
6. `Periods by index: {...}`, and the string lights and scrolls
7. About two minutes later, `Next update in ... seconds`

Then open `http://<address>/` in a browser on the same network; the
explainer page should load from the board.

- `WiFi not ready: WiFi connection timed out`: run
  `python -m mpremote run wifi_test.py` and read its output.
- `Update check failed: GitHub returned status 404`: the repo is private and
  `GITHUB_TOKEN` in `config.py` is empty or lacks read access. The lights
  still run.

### 9. Move to the charger **(person, with a config change)**

1. Set `BRIGHTNESS = 0.5` in `config.py` (anything up to 0.85 is within the
   board's 3 A USB-C limit) and copy it:

   ```powershell
   python -m mpremote cp config.py :
   ```

2. **(person)** Unplug from the computer and plug the board into a USB-C
   charger rated 5 V 3 A.
3. **(person)** Confirm the status light blinks green, goes steady, and the
   string fills within about 15 seconds.

## If code needs changing

- Fix it on this branch, commit and push. Files listed in `update_files.txt`
  (`lights.py`, `test_leds.py`, `web.py`, `index.html`) reach the board by
  themselves at its next half-hourly refresh or at power-up.
- `main.py`, `remote.py` and `config.py` never self-update. Copy them over
  USB with `mpremote cp`.
- `lights.py`, `web.py` and `index.html` are meant to stay identical on both
  branches. If a fix to one of those also applies to the Pico, say so in the
  report so it can be applied to `claude/youthful-mendel-v86smr` too.
- The Pico and the Plasma may be on the same network. Keep their `HOSTNAME`
  values different.

## Report back

When finished, summarise:

- the firmware version installed and what `os.uname().machine` printed
- the actual labels on the screw terminals
- whether the status light behaved as described in step 5
- the output of steps 7 and 8, with any error lines in full
- any code or config changes that were needed, and whether they were pushed
