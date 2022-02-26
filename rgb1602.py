# This file converted from MicroPython to CircuitPython
# by robjwells. Original copyright Waveshare.

import time

import board
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_struct import UnaryStruct
from busio import I2C

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

# RGB registers
REG_RED = 0x04      # 0b_1__    pwm2
REG_GREEN = 0x03    # 0b__11    pwm1
REG_BLUE = 0x02     # 0b__1_    pwm0

REG_MODE1 = 0x00    # 0b____
REG_MODE2 = 0x01    # 0b___1
REG_OUTPUT = 0x08   # 0b1___


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

# Commands -- bits of an 8-bit word
LCD_CLEARDISPLAY = 0x01  # 0b_______1
LCD_RETURNHOME = 0x02  # 0b______1_

LCD_ENTRYMODESET = 0x04  # 0b_____1__
# Used with bits I/D SH:
#   I/D: 0x02 for entry left, 0x00 for entry right
#   SH: 0x01 for shift increment, 0x00 for decrement
# See "flags for display entry mode"

LCD_DISPLAYCONTROL = 0x08  # 0b____1___
# Used with bits DCB:
#   D: display on/off,
#   C: cursor on/off,
#   B: blink cursor on/off
# These are listed below as "flags for display on/off control"

LCD_CURSORSHIFT = 0x10  # 0b___1____
# Cursor or Display Shift
# Uses bits S/C R/L - -:
#   S/C: 0x08 for screen or 0x00 for cursor
#   R/L: 0x04 for right or 0x00 for left

LCD_FUNCTIONSET = 0x20  # 0b__1_____
# Sets number of display lines, and display font type.
# The documentation doesn't mention 8/4 bit mode.

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00   # 0b00
LCD_ENTRYLEFT = 0x02    # 0b10
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


class RGB1602:
    def __init__(self, col=16, row=2):
        self._row = row
        self._col = col

        self._showfunction = LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS
        self.begin(self._row, self._col)

    def command(self, cmd: int):
        assert 0 <= cmd <= 255, f"Command {cmd} out of range."
        lcd_registers.command_register = cmd
        # RGB1602_I2C.writeto_mem(LCD_ADDRESS, LCD_SETDDRAMADDR, chr(cmd))

    def write(self, data):
        assert 0 <= data <= 255, f"Command {data} out of range."
        lcd_registers.data_register = data
        # RGB1602_I2C.writeto_mem(LCD_ADDRESS, LCD_SETCGRAMADDR, chr(data))

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
        # RGB1602_I2C.writeto_mem(RGB_ADDRESS, reg, chr(data))

    def setRGB(self, r, g, b):
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
            self.write(x)

    def display(self):
        self._showcontrol |= LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self._showcontrol)

    def begin(self, cols, lines):
        if lines > 1:
            self._showfunction |= LCD_2LINE

        self._numlines = lines
        self._currline = 0

        time.sleep(0.05)

        # Send function set command sequence
        self.command(LCD_FUNCTIONSET | self._showfunction)
        # delayMicroseconds(4500);  # wait more than 4.1ms
        time.sleep(0.005)
        # second try
        self.command(LCD_FUNCTIONSET | self._showfunction)
        # delayMicroseconds(150);
        time.sleep(0.005)
        # third go
        self.command(LCD_FUNCTIONSET | self._showfunction)
        # finally, set # lines, font size, etc.
        self.command(LCD_FUNCTIONSET | self._showfunction)
        # turn the display on with no cursor or blinking default
        self._showcontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.display()
        # clear it off
        self.clear()
        # Initialize to default text direction (for romance languages)
        self._showmode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        # set the entry mode
        self.command(LCD_ENTRYMODESET | self._showmode)
        # backlight init
        self.set_RGB_register("REG_MODE1", 0)
        # set LEDs controllable by both PWM and GRPPWM registers
        self.set_RGB_register("REG_OUTPUT", 0xFF)
        # set MODE2 values
        # 0010 0000 -> 0x20  (DMBLNK to 1, ie blinky mode)
        self.set_RGB_register("REG_MODE2", 0x20)
        self.setColorWhite()

    def set_rgb_mode(self, mode, value: int) -> None:
        assert 0 <= value <= 0xFF, "Value not in range."
        if mode == 1:
            self.set_RGB_register("REG_MODE1", value)
        elif mode == 2:
            self.set_RGB_register("REG_MODE2", value)
        else:
            raise ValueError(f"Unknown mode: {repr(mode)}")

    def setColorWhite(self):
        self.setRGB(255, 255, 255)
