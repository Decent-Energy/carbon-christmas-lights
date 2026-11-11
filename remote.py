"""WiFi, remote access and self-updating for the Pico 2 W (MicroPython).

main.py calls launch(), which:

1. joins WiFi,
2. starts WebREPL if config.WEBREPL_PASSWORD is set, so files can be pushed
   to the Pico over the local network,
3. installs new code from GitHub if config.UPDATE_REPO is set, and
4. runs the lights program (lights.py).

A GitHub update replaces the files listed in update_files.txt. The previous
copies are kept until the new code has completed one successful refresh; if
it crashes or fails to get that far in three starts, the previous copies are
put back and that commit is skipped.

This file and main.py are not updated from GitHub, so a bad push cannot break
the updater itself. Change them over USB or WebREPL.
"""
import gc
import os
import sys
import time

import machine
import network
import rp2

try:
    import requests
except ImportError:  # older MicroPython builds
    import urequests as requests

try:
    import config
except ImportError:
    raise RuntimeError("config.py not found: copy config.example.py to config.py and fill it in")

API = "https://api.github.com/repos/"
RAW = "application/vnd.github.raw"
MANIFEST = "update_files.txt"   # in the repo: the files to keep up to date
PROTECTED = ("config.py", "main.py", "remote.py")
VERSION_FILE = "version.txt"            # commit the installed code came from
PENDING_FILE = "update_pending.txt"     # new commit, previous commit, starts so far
BAD_FILE = "bad_version.txt"            # commit that was rolled back
MAX_STARTS = 3                          # unconfirmed starts before rolling back
RECOVERY_CHECK_S = 30 * 60

status_led = machine.Pin("LED", machine.Pin.OUT)
wlan = network.WLAN(network.STA_IF)

try:
    _compile = compile
except NameError:  # builds without compile(): skip the syntax check
    _compile = None


def _read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError:
        return None


def _write(path, text):
    with open(path, "w") as f:
        f.write(text)


def _remove(path):
    try:
        os.remove(path)
    except OSError:
        pass


def _remove_ending(suffix):
    for name in os.listdir():
        if name.endswith(suffix):
            _remove(name)


def _print_error(error):
    if hasattr(sys, "print_exception"):
        sys.print_exception(error)
    else:
        print("Error:", repr(error))


# --- WiFi and WebREPL -------------------------------------------------------

def connect_wifi(timeout_s=30):
    if wlan.isconnected():
        return
    rp2.country(getattr(config, "WIFI_COUNTRY", "GB"))
    try:
        network.hostname(getattr(config, "HOSTNAME", "carbon-lights"))
    except Exception:
        pass  # older firmware: reachable by IP address only
    wlan.active(True)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    deadline = time.time() + timeout_s
    while not wlan.isconnected():
        if time.time() > deadline:
            raise RuntimeError("WiFi connection timed out")
        status_led.toggle()
        time.sleep(0.25)
    status_led.on()
    print("WiFi connected:", wlan.ifconfig()[0])


def start_webrepl():
    password = getattr(config, "WEBREPL_PASSWORD", "")
    if not password:
        return
    import webrepl
    webrepl.start(password=password)


# --- updates from GitHub ----------------------------------------------------

def _github(path, accept):
    headers = {"Accept": accept, "User-Agent": "carbon-christmas-lights"}
    token = getattr(config, "GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    gc.collect()
    response = requests.get(API + config.UPDATE_REPO + path, headers=headers, timeout=20)
    try:
        if response.status_code != 200:
            raise RuntimeError("GitHub returned status %d for %s" % (response.status_code, path))
        return response.content
    finally:
        response.close()


def _install(commit):
    """Download the commit's files and swap them in. True if any file changed."""
    listing = _github("/contents/%s?ref=%s" % (MANIFEST, commit), RAW).decode()
    names = [line.strip() for line in listing.split("\n")]
    names = [n for n in names if n and not n.startswith("#") and n not in PROTECTED]

    # Download everything first, so a failure part-way leaves the Pico untouched.
    changed = []
    for name in names:
        data = _github("/contents/%s?ref=%s" % (name, commit), RAW)
        if not data:
            raise RuntimeError(name + " came back empty")
        if _compile and name.endswith(".py"):
            _compile(data, name, "exec")  # refuse code that will not even load
        try:
            with open(name, "rb") as f:
                current = f.read()
        except OSError:
            current = None
        if data != current:
            with open(name + ".new", "wb") as f:
                f.write(data)
            changed.append(name)
        del data, current
        gc.collect()

    if not changed:
        _write(VERSION_FILE, commit)
        return False

    _remove_ending(".bak")
    _write(PENDING_FILE, "%s\n%s\n0" % (commit, _read(VERSION_FILE) or ""))
    for name in changed:
        try:
            os.rename(name, name + ".bak")
        except OSError:
            pass  # a new file: nothing to keep
        os.rename(name + ".new", name)
    _write(VERSION_FILE, commit)
    return True


def check_for_update():
    """Install new code from GitHub, then restart. Does nothing if up to date."""
    if not getattr(config, "UPDATE_REPO", ""):
        return
    try:
        branch = getattr(config, "UPDATE_BRANCH", "main")
        latest = _github("/commits/" + branch, "application/vnd.github.sha").decode().strip()
        if latest == _read(VERSION_FILE):
            return
        if latest == _read(BAD_FILE):
            print("Update", latest[:7], "was rolled back; waiting for a newer one")
            return
        print("Updating to", latest[:7])
        if not _install(latest):
            print("No code changes in", latest[:7])
            return
    except Exception as error:
        _remove_ending(".new")
        print("Update check failed:", error)
        return
    print("Update installed; restarting")
    time.sleep(1)
    machine.reset()


def confirm():
    """The new code works: stop watching it and drop the previous copies."""
    if _read(PENDING_FILE) is not None:
        _remove(PENDING_FILE)
        _remove_ending(".bak")
        print("Update confirmed")


def roll_back():
    """Put back the files from before an unconfirmed update. True if it did."""
    pending = _read(PENDING_FILE)
    if pending is None:
        return False
    lines = pending.split("\n")
    for name in os.listdir():
        if name.endswith(".bak"):
            _remove(name[:-4])
            os.rename(name, name[:-4])
    _write(BAD_FILE, lines[0])
    if len(lines) > 1 and lines[1]:
        _write(VERSION_FILE, lines[1])
    else:
        _remove(VERSION_FILE)
    _remove(PENDING_FILE)
    print("Rolled back update", lines[0][:7])
    return True


def _count_start():
    """Roll back an update that still has not proved itself after MAX_STARTS."""
    pending = _read(PENDING_FILE)
    if pending is None:
        return
    lines = (pending.split("\n") + ["", "0"])[:3]
    try:
        starts = int(lines[2]) + 1
    except ValueError:
        starts = 1
    if starts > MAX_STARTS:
        roll_back()
    else:
        _write(PENDING_FILE, "%s\n%s\n%d" % (lines[0], lines[1], starts))


# --- start-up ---------------------------------------------------------------

def launch(module="lights"):
    try:
        connect_wifi()
    except Exception as error:
        print("WiFi not ready:", error)
    try:
        start_webrepl()
    except Exception as error:
        print("WebREPL not started:", error)

    _count_start()
    check_for_update()

    try:
        __import__(module).main()
    except Exception as error:
        _print_error(error)
        if roll_back():
            time.sleep(1)
            machine.reset()

    # The program has stopped and there is no earlier version to go back to.
    status_led.off()
    print("The program stopped. Looking for a fixed version every 30 minutes.")
    while True:
        time.sleep(RECOVERY_CHECK_S)
        try:
            connect_wifi()
        except Exception as error:
            print("WiFi not ready:", error)
        check_for_update()
