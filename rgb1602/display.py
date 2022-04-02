# This file converted from MicroPython to CircuitPython
# by robjwells. Original copyright Waveshare.

from time import sleep

from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_struct import UnaryStruct
from busio import I2C
from microcontroller import Pin

from rgb1602.colours import CSS_COLOURS


class Constants:
    # Device I2C Addresses
    LCD_ADDRESS = 0x7C >> 1
    RGB_ADDRESS = 0xC0 >> 1

    # fmt: off
    # CGRAM and DDRAM commands but also their memory addresses
    LCD_COMMAND_REG = 0x80
    LCD_SETDDRAMADDR = 0x80  # 0b1_______    Display Data RAM
    LCD_SETCGRAMADDR = 0x40  # 0b_1______    Character Generator RAM
    LCD_DATA_REG = 0x40

    # RGB registers
    REG_RED = 0x04      # 0b_1__    pwm2
    REG_GREEN = 0x03    # 0b__11    pwm1
    REG_BLUE = 0x02     # 0b__1_    pwm0

    REG_MODE1 = 0x00    # 0b____
    REG_MODE2 = 0x01    # 0b___1
    REG_OUTPUT = 0x08   # 0b1___

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

    # I think the modes relate the to the number of bits
    # sent down the wire at a time, _not_ the colour
    # depth (as I thought originally).
    LCD_8BITMODE = 0x10     # 0b10000
    LCD_4BITMODE = 0x00     # 0b00000

    # Number of lines on the display
    LCD_2LINE = 0x08        # 0b01000
    LCD_1LINE = 0x00        # 0b00000
    LCD_5x8DOTS = 0x00      # 0b00000

    # fmt: on


class LCDControl:
    def __init__(self, i2c: I2CDevice):
        self.i2c_device = i2c  # Required by UnaryStruct

    command_register = UnaryStruct(Constants.LCD_COMMAND_REG, "<B")
    data_register = UnaryStruct(Constants.LCD_DATA_REG, "<B")


class RGBControl:
    def __init__(self, i2c: I2CDevice) -> None:
        self.i2c_device = i2c

    REG_RED = UnaryStruct(Constants.REG_RED, "<B")
    REG_GREEN = UnaryStruct(Constants.REG_GREEN, "<B")
    REG_BLUE = UnaryStruct(Constants.REG_BLUE, "<B")

    REG_MODE1 = UnaryStruct(Constants.REG_MODE1, "<B")
    REG_MODE2 = UnaryStruct(Constants.REG_MODE2, "<B")
    REG_OUTPUT = UnaryStruct(Constants.REG_OUTPUT, "<B")


class Screen:
    # Set dimensions as class variables.
    # Hint is in the module name (LCD1602)!
    COLS = 16
    ROWS = 2

    current_colour: tuple[int, int, int]

    _i2c: I2C
    _lcd: LCDControl
    _rgb: RGBControl

    def __init__(self, i2c_bus: I2C):
        self._i2c = i2c_bus
        self._lcd = LCDControl(I2CDevice(self._i2c, Constants.LCD_ADDRESS))
        self._rgb = RGBControl(I2CDevice(self._i2c, Constants.RGB_ADDRESS))
        self._reset_display()

    def _reset_display(self):
        """Initialise the display to its standard settings.

        It is unclear to me (rjw) why some of these are necessary, as
        there seems to be no difference in removing some of the below.
        *However* I have not removed what remains because it wasn't
        *obviously unnecessary*, unlike the now-removed lines.
        """
        # Send function set command sequence
        show_function = (
            Constants.LCD_4BITMODE | Constants.LCD_2LINE | Constants.LCD_5x8DOTS
        )
        self._command(Constants.LCD_FUNCTIONSET | show_function)
        sleep(0.05)

        # turn the display on with no cursor or blinking default
        show_control = (
            Constants.LCD_DISPLAYON | Constants.LCD_CURSOROFF | Constants.LCD_BLINKOFF
        )
        self._command(Constants.LCD_DISPLAYCONTROL | show_control)

        self.clear()

        # Initialize to default text direction (for romance languages)
        self._showmode = Constants.LCD_ENTRYLEFT | Constants.LCD_ENTRYSHIFTDECREMENT
        self._command(Constants.LCD_ENTRYMODESET | self._showmode)

        # backlight init
        self._set_rgb_register("REG_MODE1", 0)
        # set LEDs controllable by both PWM and GRPPWM registers
        self._set_rgb_register("REG_OUTPUT", 0xFF)
        # set MODE2 values
        # 0010 0000 -> 0x20  (DMBLNK to 1, ie blinky mode)
        self._set_rgb_register("REG_MODE2", 0x20)
        self.set_white()

    def _command(self, cmd: int):
        assert 0 <= cmd <= 255, f"Command {cmd} out of range."
        self._lcd.command_register = cmd

    def _write_byte(self, data: int) -> None:
        assert 0 <= data <= 255, f"Command {data} out of range."
        self._lcd.data_register = data

    def _set_rgb_register(self, reg: str, data: int) -> None:
        assert reg in (
            "REG_RED",
            "REG_BLUE",
            "REG_GREEN",
            "REG_MODE1",
            "REG_MODE2",
            "REG_OUTPUT",
        ), f"Register {reg} is not a known register."
        assert 0 <= data <= 255, f"Data {data} is out of range."
        setattr(self._rgb, reg, data)

    def _set_rgb_mode(self, mode: int, value: int) -> None:
        assert 0 <= value <= 0xFF, "Value not in range."
        if mode == 1:
            self._set_rgb_register("REG_MODE1", value)
        elif mode == 2:
            self._set_rgb_register("REG_MODE2", value)
        else:
            raise ValueError(f"Unknown mode: {repr(mode)}")

    def set_rgb(self, r: int, g: int, b: int):
        assert 0 <= r <= 255, f"Red value {r} out of range."
        assert 0 <= g <= 255, f"Green value {g} out of range."
        assert 0 <= b <= 255, f"Blue value {b} out of range."

        self._set_rgb_register("REG_RED", r)
        self._set_rgb_register("REG_GREEN", g)
        self._set_rgb_register("REG_BLUE", b)
        self.current_colour = (r, g, b)

    def position_cursor(self, *, col: int, row: int):
        assert (
            0 <= col < self.COLS
        ), f"Column {col} is out of bounds (max {self.COLS - 1})."
        assert (
            0 <= row < self.ROWS
        ), f"Row {row} is out of bounds (max {self.ROWS - 1})."

        if row == 0:
            col |= 0x80
        else:
            col |= 0xC0

        assert self._i2c.try_lock(), "Could not lock"
        self._i2c.writeto(
            Constants.LCD_ADDRESS, bytearray([Constants.LCD_SETDDRAMADDR, col])
        )
        self._i2c.unlock()

    def clear(self):
        self._command(Constants.LCD_CLEARDISPLAY)
        sleep(0.002)

    def write_bytes(self, arg: bytes):
        for byte in arg:
            self._write_byte(byte)

    def write_at_position(self, text: str | bytes, *, col: int, row: int) -> None:
        self.position_cursor(col=col, row=row)
        self.write_bytes(self._ensure_bytes(text))

    @staticmethod
    def _ensure_bytes(s: str | bytes) -> bytes:
        if isinstance(s, bytes):
            return s
        # Not JIS X 0213 but close enough if you’re careful.
        return bytes(s, "jisx0213")

    def update(
        self, first_line: str | bytes, second_line: str | bytes | None = None
    ) -> None:
        first = self._ensure_bytes(first_line)
        self.clear()
        self.write_bytes(first[: self.COLS])
        if second_line is not None:
            self.position_cursor(col=0, row=1)
            second = self._ensure_bytes(second_line)
            self.write_bytes(second[: self.COLS])

    def set_white(self) -> None:
        self.set_css_colour("white")

    def set_css_colour(self, colour_name: str) -> None:
        self.set_rgb(*CSS_COLOURS[colour_name])

    def set_css_color(self, color_name: str) -> None:
        self.set_css_colour(color_name)

    def set_backlight_power(self, on: bool) -> None:
        data = 0xFF if on else 0x00
        self._set_rgb_register("REG_OUTPUT", data)

    @staticmethod
    def special_char(c: str) -> bytes:
        if c == "\\":
            raise ValueError("\\ (backslash) is not in the character set.")
        elif ord(c) < ord("}"):
            # Everything matches ASCII up to }, except for \ -> ¥.
            return c.encode("ascii")

        chars = {
            "→": b"\x7E",
            "←": b"\x7F",
            "•": b"\xA5",
            "☐": b"\xDB",
            "°": b"\xDF",
            "alpha": b"\xE0",
            "beta": b"\xE2",
            "epsilon": b"\xE3",
            "mu": b"\xE4",
            "sigma": b"\xE5",
            "rho": b"\xE6",
            "√": b"\xE8",
            "theta": b"\xF2",
            "omega": b"\xF4",
            "SIGMA": b"\xF6",
            "pi": b"\xF7",
            "÷": b"\xFD",
            "block": b"\xFF",
        }

        try:
            return chars[c]
        except KeyError:
            raise ValueError(f"Character {repr(c)} is not a registered special character.")
