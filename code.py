# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This example shows connecting to the PN532 with I2C (requires clock
stretching support), SPI, or UART. SPI is best, it uses the most pins but
is the most reliable and universally supported.
After initialization, try waving various 13.56MHz RFID cards over it!
"""

import time
import board
import busio
from digitalio import DigitalInOut, Direction, Pull

# NFC Reader
from adafruit_pn532.i2c import PN532_I2C

# Indicator light
led = DigitalInOut(board.GP15)
led.direction = Direction.OUTPUT

# Radio
radio = DigitalInOut(board.GP18)
radio.direction = Direction.OUTPUT

# from adafruit_pn532.spi import PN532_SPI
# from adafruit_pn532.uart import PN532_UART

# rpi_scl = DigitalInOut(board.GP5)
# rpi_sda = DigitalInOut(board.GP4)
# rpi_scl.pull = Pull.UP
# rpi_sda.pull = Pull.UP

# I2C connection:
i2c = busio.I2C(board.GP5, board.GP4)

# Non-hardware
#pn532 = PN532_I2C(i2c, debug=True)

# With I2C, we recommend connecting RSTPD_N (reset) to a digital pin for manual
# harware reset
reset_pin = DigitalInOut(board.GP6)
# On Raspberry Pi, you must also connect a pin to P32 "H_Request" for hardware
# wakeup! this means we don't need to do the I2C clock-stretch thing
req_pin = DigitalInOut(board.GP7)
pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)

# SPI connection:
# spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
# cs_pin = DigitalInOut(board.D5)
# pn532 = PN532_SPI(spi, cs_pin, debug=False)

# UART connection
# uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=100)
# pn532 = PN532_UART(uart, debug=False)

ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

valid_cards = [
    ['0x63', '0xdd', '0x46', '0x1c'],   # Blue keyfob
    ['0xdd', '0xce', '0x96', '0x38']    # White card
]

last_light = 0
last_card = 0

def found_card(uid):
    global last_light
    print("Found card with UID:", [hex(i) for i in uid])

    # Compare for valid cards
    card_found = [hex(i) for i in uid]
    for valid_card in valid_cards:

        # This is ugly I know
        if (valid_card[0] == card_found[0] and
            valid_card[1] == card_found[1] and
            valid_card[2] == card_found[2] and
            valid_card[3] == card_found[3]):
            print("Valid Card Found ", [hex(i) for i in uid])
            # First time
            if last_light == 0:
                led.value = True
                radio.value = True
                last_light = time.time()
            else:
                led.value = True
                radio.value = True
            # Don't check other cards
            break;
        else:
            print("Invalid Card Found ", [hex(i) for i in uid])


print("Waiting for RFID/NFC card...")
while True:
    # Check if a card is available to read
    uid = pn532.read_passive_target(timeout=0.5)
    print(".", end="")
    # Try again if no card is available.
    if uid is None:
        # Keep LED on for a short time
        diff_time = time.time() - last_light
        if (diff_time >= 2):
            led.value = False
            radio.value = False
        continue
    # Card was found
    if last_card == 0:
        last_card = time.time()
        found_card(uid)
    else:
        diff_card_time = time.time() - last_card
        last_card = time.time()
        if (diff_card_time >= 2):
            found_card(uid)        
    


