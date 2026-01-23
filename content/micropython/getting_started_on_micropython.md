Title: Getting Started with MicroPython (Raspberry Pi Pico)
Date: 2026-01-23
Modified: 2026-01-23
Category: MicroPython
Tags: micropython, raspberry-pi, pico, embedded

If you’ve just unboxed a Pico (or any similar MicroPython-capable board), the first hour can be surprisingly fiddly: flashing the right firmware, getting a REPL, and figuring out how to copy a script over without reinventing the wheel. I’m just getting started with MicroPython myself, so this post is basically my “here’s what worked” notes from that first setup.

One thing that helped early on was doing a quick “sanity check” with the Pico C/C++ SDK: build and flash a tiny example once. It doesn’t teach you Python, but it *does* confirm your USB connection and board setup are solid.

After that, here’s the shortest path I found to a working MicroPython REPL.

## Flash MicroPython (UF2)

1. Download the MicroPython firmware (a `.uf2` file) from the official docs: [Raspberry Pi MicroPython documentation](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html). Make sure you pick the firmware for **your exact board**.
2. Unplug the board (if it’s connected).
3. Hold **BOOTSEL** (the small white button on top), then plug the board back in. It should mount as a USB drive.
4. Copy the `.uf2` onto that drive. The board will reboot automatically once the copy completes.

## Connect to the REPL

After flashing, connect to the serial REPL - the interactive Python command line:

```bash
minicom -o -D /dev/ttyACM0
```

Then you can run Python command (if you don't see a prompt at first, try just pressing enter to activate the REPL).
Good to know: to exit Minicom, press Ctrl+A then X.

If you hit permission errors accessing `/dev/ttyACM0`, add your user to the `dialout` group and re-login:

```bash
sudo usermod -aG dialout "$USER"
```

## First test: turn on the built-in LED

At the REPL, try turning on the built-in LED:

```python
from machine import Pin

led = Pin("LED", Pin.OUT)
led.value(1)
```

## Copy scripts to the board with `rshell`

To upload a script (and have it run automatically on boot), copy it to `main.py` using `rshell`:

```bash
# first, install rshell
uv tool install rshell

# copy a file to run automatically
rshell cp my_file.py /pyboard/main.py

# inspect files on the device
rshell ls /pyboard
```

Restart the device, and it will run the program.  To restart, the most straightforward is unplug / replug, but you can also connect to the REPL using minicom and press Ctrl+D, or use machine.reset():

```python
import machine
machine.reset()
```


That’s it for the initial setup. Next up I want to explore the ecosystem a bit more (sensors, simple displays, maybe a small servo project). So far, MicroPython looks like a great way to make programming feel tangible quickly—and a really promising tool for introducing kids to coding and robotics without getting stuck in tooling.



