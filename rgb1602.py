# This file converted from MicroPython to CircuitPython
# by robjwells. Original copyright Waveshare.

import time

import board
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_struct import UnaryStruct
from busio import I2C

# NOTE: Change these pins to match your circuit.
# On the RPi Pico (eg) there lots of I2C pins.
RGB1602_SDA = board.GP26
RGB1602_SCL = board.GP27

RGB1602_I2C = I2C(sda=RGB1602_SDA, scl=RGB1602_SCL, frequency=400000)

# Device I2C Addresses
LCD_ADDRESS = 0x7C >> 1
RGB_ADDRESS = 0xC0 >> 1

# CGRAM and DDRAM commands but also their memory addresses
LCD_COMMAND_REG = 0x80
LCD_SETDDRAMADDR = 0x80  # 0b1_______    Display Data RAM
LCD_SETCGRAMADDR = 0x40  # 0b_1______    Character Generator RAM
LCD_DATA_REG = 0x40


class LCDControl:
    def __init__(self, i2c: I2CDevice):
        self.i2c_device = i2c  # Required by UnaryStruct

    command_register = UnaryStruct(LCD_COMMAND_REG, "<B")
    data_register = UnaryStruct(LCD_DATA_REG, "<B")


comm_port = RGB1602_I2C

lcd_device = I2CDevice(comm_port, LCD_ADDRESS)
lcd_registers = LCDControl(lcd_device)

# fmt: off

# RGB registers
REG_RED = 0x04      # 0b_1__    pwm2
REG_GREEN = 0x03    # 0b__11    pwm1
REG_BLUE = 0x02     # 0b__1_    pwm0

REG_MODE1 = 0x00    # 0b____
REG_MODE2 = 0x01    # 0b___1
REG_OUTPUT = 0x08   # 0b1___

# fmt: on


class RGBControl:
    def __init__(self, i2c: I2CDevice) -> None:
        self.i2c_device = i2c

    REG_RED = UnaryStruct(REG_RED, "<B")
    REG_GREEN = UnaryStruct(REG_GREEN, "<B")
    REG_BLUE = UnaryStruct(REG_BLUE, "<B")

    REG_MODE1 = UnaryStruct(REG_MODE1, "<B")
    REG_MODE2 = UnaryStruct(REG_MODE2, "<B")
    REG_OUTPUT = UnaryStruct(REG_OUTPUT, "<B")


rgb_device = I2CDevice(comm_port, RGB_ADDRESS)
rgb_registers = RGBControl(rgb_device)


# fmt: off

# Commands -- bits of an 8-bit word
LCD_CLEARDISPLAY = 0x01     # 0b_______1
LCD_RETURNHOME = 0x02       # 0b______1_

LCD_ENTRYMODESET = 0x04     # 0b_____1__
# Used with bits I/D SH:
#   I/D: 0x02 for entry left, 0x00 for entry right
#   SH: 0x01 for shift increment, 0x00 for decrement
# See "flags for display entry mode"

LCD_DISPLAYCONTROL = 0x08   # 0b____1___
# Used with bits DCB:
#   D: display on/off,
#   C: cursor on/off,
#   B: blink cursor on/off
# These are listed below as "flags for display on/off control"

LCD_CURSORSHIFT = 0x10      # 0b___1____
# Cursor or Display Shift
# Uses bits S/C R/L - -:
#   S/C: 0x08 for screen or 0x00 for cursor
#   R/L: 0x04 for right or 0x00 for left

LCD_FUNCTIONSET = 0x20      # 0b__1_____
# Sets number of display lines, and display font type.
# The documentation doesn't mention 8/4 bit mode.

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00           # 0b00
LCD_ENTRYLEFT = 0x02            # 0b10
LCD_ENTRYSHIFTINCREMENT = 0x01  # 0b01
LCD_ENTRYSHIFTDECREMENT = 0x00  # 0b00

# flags for display on/off control
LCD_DISPLAYON = 0x04    # 0b1__
LCD_CURSORON = 0x02     # 0b_1_
LCD_BLINKON = 0x01      # 0b__1

LCD_DISPLAYOFF = 0x00   # 0b000
LCD_CURSOROFF = 0x00    # 0b000
LCD_BLINKOFF = 0x00     # 0b000

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08  # 0b1000
LCD_CURSORMOVE = 0x00   # 0b0000
LCD_MOVERIGHT = 0x04    # 0b0100
LCD_MOVELEFT = 0x00     # 0b0000

# flags for function set
LCD_8BITMODE = 0x10     # 0b10000
LCD_4BITMODE = 0x00     # 0b00000
LCD_2LINE = 0x08        # 0b01000
LCD_1LINE = 0x00        # 0b00000
LCD_5x8DOTS = 0x00      # 0b00000

# fmt: on


class Screen:
    # Set dimensions as class variables.
    # Hint is in the module name (LCD1602)!
    COLS = 16
    ROWS = 2

    WHITE = (0xFF, 0xFF, 0xFF)

    def __init__(self):
        self._reset_display()

    def _reset_display(self):
        """Initialise the display to its standard settings.

        It is unclear to me (rjw) why some of these are necessary, as
        there seems to be no difference in removing some of the below.
        *However* I have not removed what remains because it wasn't
        *obviously unnecessary*, unlike the now-removed lines.
        """
        # Send function set command sequence
        show_function = LCD_8BITMODE | LCD_2LINE | LCD_5x8DOTS
        self.command(LCD_FUNCTIONSET | show_function)
        time.sleep(0.05)

        # turn the display on with no cursor or blinking default
        show_control = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.command(LCD_DISPLAYCONTROL | show_control)

        self.clear()

        # Initialize to default text direction (for romance languages)
        self._showmode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        self.command(LCD_ENTRYMODESET | self._showmode)

        # backlight init
        self.set_RGB_register("REG_MODE1", 0)
        # set LEDs controllable by both PWM and GRPPWM registers
        self.set_RGB_register("REG_OUTPUT", 0xFF)
        # set MODE2 values
        # 0010 0000 -> 0x20  (DMBLNK to 1, ie blinky mode)
        self.set_RGB_register("REG_MODE2", 0x20)
        self.setColorWhite()

    def command(self, cmd: int):
        assert 0 <= cmd <= 255, f"Command {cmd} out of range."
        lcd_registers.command_register = cmd

    def _write_byte(self, data: int) -> None:
        assert 0 <= data <= 255, f"Command {data} out of range."
        lcd_registers.data_register = data

    def set_RGB_register(self, reg: str, data: int) -> None:
        assert reg in (
            "REG_RED",
            "REG_BLUE",
            "REG_GREEN",
            "REG_MODE1",
            "REG_MODE2",
            "REG_OUTPUT",
        ), f"Register {reg} is not a known register."
        assert 0 <= data <= 255, f"Data {data} is out of range."
        setattr(rgb_registers, reg, data)

    def setRGB(self, r: int, g: int, b: int):
        assert 0 <= r <= 255, f"Red value {r} out of range."
        assert 0 <= g <= 255, f"Green value {g} out of range."
        assert 0 <= b <= 255, f"Blue value {b} out of range."

        self.set_RGB_register("REG_RED", r)
        self.set_RGB_register("REG_GREEN", g)
        self.set_RGB_register("REG_BLUE", b)

    def setCursor(self, col, row):
        if row == 0:
            col |= 0x80
        else:
            col |= 0xC0
        assert RGB1602_I2C.try_lock(), "Could not lock"
        RGB1602_I2C.writeto(LCD_ADDRESS, bytearray([LCD_SETDDRAMADDR, col]))
        RGB1602_I2C.unlock()

    def clear(self):
        self.command(LCD_CLEARDISPLAY)
        time.sleep(0.002)

    def printout(self, arg):
        if isinstance(arg, int):
            arg = str(arg)

        for x in bytearray(arg, "utf-8"):
            self._write_byte(x)

    def set_rgb_mode(self, mode, value: int) -> None:
        assert 0 <= value <= 0xFF, "Value not in range."
        if mode == 1:
            self.set_RGB_register("REG_MODE1", value)
        elif mode == 2:
            self.set_RGB_register("REG_MODE2", value)
        else:
            raise ValueError(f"Unknown mode: {repr(mode)}")

    def setColorWhite(self):
        self.setRGB(*self.WHITE)
