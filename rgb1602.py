# This file converted from MicroPython to CircuitPython
# by robjwells. Original copyright Waveshare.

from time import sleep

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

# I think the modes relate the to the number of bits
# sent down the wire at a time, _not_ the colour
# depth (as I thought originally).
LCD_8BITMODE = 0x10     # 0b10000
LCD_4BITMODE = 0x00     # 0b00000
LCD_2LINE = 0x08        # 0b01000
LCD_1LINE = 0x00        # 0b00000
LCD_5x8DOTS = 0x00      # 0b00000

# fmt: on

CSS_COLOURS: dict[str, tuple[int, int, int]] = {
    "aliceblue": (240, 248, 255),
    "antiquewhite": (250, 235, 215),
    "aqua": (0, 255, 255),
    "aquamarine": (127, 255, 212),
    "azure": (240, 255, 255),
    "beige": (245, 245, 220),
    "bisque": (255, 228, 196),
    "black": (0, 0, 0),
    "blanchedalmond": (255, 235, 205),
    "blue": (0, 0, 255),
    "blueviolet": (138, 43, 226),
    "brown": (165, 42, 42),
    "burlywood": (222, 184, 135),
    "cadetblue": (95, 158, 160),
    "chartreuse": (127, 255, 0),
    "chocolate": (210, 105, 30),
    "coral": (255, 127, 80),
    "cornflowerblue": (100, 149, 237),
    "cornsilk": (255, 248, 220),
    "crimson": (220, 20, 60),
    "cyan": (0, 255, 255),
    "darkblue": (0, 0, 139),
    "darkcyan": (0, 139, 139),
    "darkgoldenrod": (184, 134, 11),
    "darkgray": (169, 169, 169),
    "darkgreen": (0, 100, 0),
    "darkgrey": (169, 169, 169),
    "darkkhaki": (189, 183, 107),
    "darkmagenta": (139, 0, 139),
    "darkolivegreen": (85, 107, 47),
    "darkorange": (255, 140, 0),
    "darkorchid": (153, 50, 204),
    "darkred": (139, 0, 0),
    "darksalmon": (233, 150, 122),
    "darkseagreen": (143, 188, 143),
    "darkslateblue": (72, 61, 139),
    "darkslategray": (47, 79, 79),
    "darkslategrey": (47, 79, 79),
    "darkturquoise": (0, 206, 209),
    "darkviolet": (148, 0, 211),
    "deeppink": (255, 20, 147),
    "deepskyblue": (0, 191, 255),
    "dimgray": (105, 105, 105),
    "dimgrey": (105, 105, 105),
    "dodgerblue": (30, 144, 255),
    "firebrick": (178, 34, 34),
    "floralwhite": (255, 250, 240),
    "forestgreen": (34, 139, 34),
    "fuchsia": (255, 0, 255),
    "gainsboro": (220, 220, 220),
    "ghostwhite": (248, 248, 255),
    "gold": (255, 215, 0),
    "goldenrod": (218, 165, 32),
    "gray": (128, 128, 128),
    "green": (0, 128, 0),
    "greenyellow": (173, 255, 47),
    "grey": (128, 128, 128),
    "honeydew": (240, 255, 240),
    "hotpink": (255, 105, 180),
    "indianred": (205, 92, 92),
    "indigo": (75, 0, 130),
    "ivory": (255, 255, 240),
    "khaki": (240, 230, 140),
    "lavender": (230, 230, 250),
    "lavenderblush": (255, 240, 245),
    "lawngreen": (124, 252, 0),
    "lemonchiffon": (255, 250, 205),
    "lightblue": (173, 216, 230),
    "lightcoral": (240, 128, 128),
    "lightcyan": (224, 255, 255),
    "lightgoldenrodyellow": (250, 250, 210),
    "lightgray": (211, 211, 211),
    "lightgreen": (144, 238, 144),
    "lightgrey": (211, 211, 211),
    "lightpink": (255, 182, 193),
    "lightsalmon": (255, 160, 122),
    "lightseagreen": (32, 178, 170),
    "lightskyblue": (135, 206, 250),
    "lightslategray": (119, 136, 153),
    "lightslategrey": (119, 136, 153),
    "lightsteelblue": (176, 196, 222),
    "lightyellow": (255, 255, 224),
    "lime": (0, 255, 0),
    "limegreen": (50, 205, 50),
    "linen": (250, 240, 230),
    "magenta": (255, 0, 255),
    "maroon": (128, 0, 0),
    "mediumaquamarine": (102, 205, 170),
    "mediumblue": (0, 0, 205),
    "mediumorchid": (186, 85, 211),
    "mediumpurple": (147, 112, 219),
    "mediumseagreen": (60, 179, 113),
    "mediumslateblue": (123, 104, 238),
    "mediumspringgreen": (0, 250, 154),
    "mediumturquoise": (72, 209, 204),
    "mediumvioletred": (199, 21, 133),
    "midnightblue": (25, 25, 112),
    "mintcream": (245, 255, 250),
    "mistyrose": (255, 228, 225),
    "moccasin": (255, 228, 181),
    "navajowhite": (255, 222, 173),
    "navy": (0, 0, 128),
    "oldlace": (253, 245, 230),
    "olive": (128, 128, 0),
    "olivedrab": (107, 142, 35),
    "orange": (255, 165, 0),
    "orangered": (255, 69, 0),
    "orchid": (218, 112, 214),
    "palegoldenrod": (238, 232, 170),
    "palegreen": (152, 251, 152),
    "paleturquoise": (175, 238, 238),
    "palevioletred": (219, 112, 147),
    "papayawhip": (255, 239, 213),
    "peachpuff": (255, 218, 185),
    "peru": (205, 133, 63),
    "pink": (255, 192, 203),
    "plum": (221, 160, 221),
    "powderblue": (176, 224, 230),
    "purple": (128, 0, 128),
    "rebeccapurple": (102, 51, 153),
    "red": (255, 0, 0),
    "rosybrown": (188, 143, 143),
    "royalblue": (65, 105, 225),
    "saddlebrown": (139, 69, 19),
    "salmon": (250, 128, 114),
    "sandybrown": (244, 164, 96),
    "seagreen": (46, 139, 87),
    "seashell": (255, 245, 238),
    "sienna": (160, 82, 45),
    "silver": (192, 192, 192),
    "skyblue": (135, 206, 235),
    "slateblue": (106, 90, 205),
    "slategray": (112, 128, 144),
    "slategrey": (112, 128, 144),
    "snow": (255, 250, 250),
    "springgreen": (0, 255, 127),
    "steelblue": (70, 130, 180),
    "tan": (210, 180, 140),
    "teal": (0, 128, 128),
    "thistle": (216, 191, 216),
    "tomato": (255, 99, 71),
    "turquoise": (64, 224, 208),
    "violet": (238, 130, 238),
    "wheat": (245, 222, 179),
    "white": (255, 255, 255),
    "whitesmoke": (245, 245, 245),
    "yellow": (255, 255, 0),
    "yellowgreen": (154, 205, 50),
}
CSS_COLORS = CSS_COLOURS

WAVESHARE_COLOURS = {
    "Deep violet": (148, 0, 110),
    "Purple": (255, 0, 255),
    "Blue and white": (144, 249, 15),
    "Light blue": (0, 128, 60),
    "Yellow": (255, 209, 0),
    "Ghost white": (248, 248, 60),
    "Dark blue": (80, 80, 145),
    "Red": (255, 0, 0),
    "Cyan": (0, 255, 0),
}
WAVESHARE_COLORS = WAVESHARE_COLOURS


class Screen:
    # Set dimensions as class variables.
    # Hint is in the module name (LCD1602)!
    COLS = 16
    ROWS = 2

    rgb: tuple[int, int, int]

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
        show_function = LCD_4BITMODE | LCD_2LINE | LCD_5x8DOTS
        self._command(LCD_FUNCTIONSET | show_function)
        sleep(0.05)

        # turn the display on with no cursor or blinking default
        show_control = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self._command(LCD_DISPLAYCONTROL | show_control)

        self.clear()

        # Initialize to default text direction (for romance languages)
        self._showmode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        self._command(LCD_ENTRYMODESET | self._showmode)

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
        lcd_registers.command_register = cmd

    def _write_byte(self, data: int) -> None:
        assert 0 <= data <= 255, f"Command {data} out of range."
        lcd_registers.data_register = data

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
        setattr(rgb_registers, reg, data)

    def _set_rgb_mode(self, mode, value: int) -> None:
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
        self.rgb = (r, g, b)

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

        assert RGB1602_I2C.try_lock(), "Could not lock"
        RGB1602_I2C.writeto(LCD_ADDRESS, bytearray([LCD_SETDDRAMADDR, col]))
        RGB1602_I2C.unlock()

    def clear(self):
        self._command(LCD_CLEARDISPLAY)
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


def _show_colours(
    screen: Screen,
    delay: int,
    colours: dict[str, tuple[int, int, int]],
    colour_set_name: str,
) -> None:
    original_rgb = screen.rgb
    for colour_name, rgb in sorted(colours.items()):
        screen.set_rgb(*rgb)
        screen.update(colour_set_name, colour_name)
        sleep(delay)
    screen.set_rgb(*original_rgb)


def show_css_colours(screen: Screen, delay: int = 2) -> None:
    _show_colours(screen, delay, CSS_COLOURS, "CSS named colour")


def show_waveshare_colours(screen: Screen, delay: int = 2) -> None:
    _show_colours(screen, delay, WAVESHARE_COLOURS, "Waveshare")


def show_discoloration_sample(screen: Screen) -> None:
    from math import sin

    screen.update(f"Waveshare", "Hello, world!")
    t = 0
    while True:
        r = int((abs(sin(3.14 * t / 180))) * 255)
        g = int((abs(sin(3.14 * (t + 60) / 180))) * 255)
        b = int((abs(sin(3.14 * (t + 120) / 180))) * 255)
        t = (t + 3) % 360

        screen.set_rgb(r, g, b)
        screen.write_at_position(
            str(t).encode() + special_char("°") + b"    ", col=10, row=0
        )

        sleep(0.3)
