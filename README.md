# Touchpad Fix
Python script that fixes your touchpad on Windows and Linux

# Watch the demo
[![Watch the video(https://img.youtube.com/vi/1cvy7Dt8uI/0.jpg)](https://www.youtube.com/watch?v=I1cvy7Dt8uI)

## Installation
# First step
Download this repo, put the script anywhere you want
Open this script and change **DEVICE_NAME** to your touchpad name, you can find it by this command
```bash
evtest
```
# Second step
Change working directory and path to the script in touchpad.service
Put this script in
```
.config/systemd/user/
```
