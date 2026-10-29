from evdev import InputDevice, ecodes, UInput, list_devices
import time
import math

# Not neccessary to put full name
# if device name is 'AB-123 34s-df Touchpad', you can put 'Touchpad'
DEVICE_NAME = "Touchpad"  

# CONFIG
CLICK_COOLDOWN = 0.1      # Cooldown delay in-between clicks
CLICK_DELAY = 0.2         # To prevent clicking on right click
MAX_MOVE = 12             # To prevent clicking after scroll (px)

# AUTO FIND DEVICE
def find_touchpad():
    for path in list_devices():
        dev = InputDevice(path)
        if DEVICE_NAME in dev.name:
            print("Using touchpad:", dev.path, dev.name)
            return dev
    return None

dev = find_touchpad()

ui = UInput({
    ecodes.EV_KEY: [ecodes.BTN_LEFT]
}, name="touchpad-gesture-click")

last_click = 0

start_x = None
start_y = None
tracking = False
touching = False
first_touch_time = None
suppress_click = False
apply_click = False

print("Touchpad gesture click daemon running...")

for event in dev.read_loop():
    if apply_click:
        if (event.type == ecodes.EV_KEY
            and event.code == ecodes.BTN_TOOL_TRIPLETAP
            ): 
            apply_click = False
            tracking = False
            suppress_click = False
            continue

        print("CLICK")

        ui.write(ecodes.EV_KEY, ecodes.BTN_LEFT, 1)
        ui.syn()
        time.sleep(0.01)
        ui.write(ecodes.EV_KEY, ecodes.BTN_LEFT, 0)
        ui.syn()

        last_click = now

        apply_click = False

    now = time.time()

    # store position continuously
    if event.type == ecodes.EV_ABS:
        if event.code == ecodes.ABS_X:
            start_x = event.value
        elif event.code == ecodes.ABS_Y:
            start_y = event.value

    # track first finger touch time to suppress quick two-finger click gestures
    if event.type == ecodes.EV_KEY and event.code == ecodes.BTN_TOUCH:
        if event.value == 1:
            if not touching:
                touching = True
                first_touch_time = now
        elif event.value == 0:
            touching = False
            first_touch_time = None

    # second finger appears -> start tracking potential click
    if (
        event.type == ecodes.EV_KEY
        and event.code == ecodes.BTN_TOOL_DOUBLETAP
        and event.value == 1
    ):
        tracking = True
        # snapshot start position
        sx = start_x
        sy = start_y
        start_time = now
        suppress_click = False
        if first_touch_time is not None:
            if now - first_touch_time < CLICK_DELAY:
                suppress_click = True
                print('Quick two-finger click suppressed (%.3fs)' % (now - first_touch_time,))

    # if third finger appears suppress click
    if (
        event.type == ecodes.EV_KEY
        and event.code == ecodes.BTN_TOOL_TRIPLETAP
        and tracking
        ):
        tracking = False

    # finger released / gesture ended
    if (
        event.type == ecodes.EV_KEY
        and event.code == ecodes.BTN_TOOL_DOUBLETAP
        and event.value == 0
        and tracking
    ):
        tracking = False

        cooldown_ok = (now - last_click) > CLICK_COOLDOWN

        if sx is not None and sy is not None and cooldown_ok:

            if suppress_click:
                continue

            dx = abs(start_x - sx)
            dy = abs(start_y - sy)

            dist = math.sqrt(dx*dx + dy*dy)

            # REAL CLICK CONDITION
            if dist < MAX_MOVE:
                apply_click = True
