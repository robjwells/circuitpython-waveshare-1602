from adafruit_bus_device.i2c_device import I2CDevice
from busio import I2C

class LCDControl:
    def __init__(self, i2c: I2CDevice): ...

class RGBControl:
    def __init__(self, i2c: I2CDevice): ...

class Screen:
    _i2c: I2C
    _lcd: LCDControl
    _rgb: RGBControl

    current_colour: tuple[int, int, int]

    def __init__(self, i2c_bus: I2C): ...
    def _command(self, cmd: int): ...
    def _write_byte(self, data: int): ...
    def _set_rgb_register(self, reg: str, data: int): ...
    def _set_rgb_mode(self, mode: int, value: int): ...
    def set_rgb(self, r: int, g: int, b: int): ...
    def position_cursor(self, *, col: int, row: int): ...
    def write_bytes(self, arg: bytes): ...
    def write_at_position(self, text: str | bytes, *, col: int, row: int): ...
    def update(
        self, first_line: str | bytes, second_line: str | bytes | None = None
    ): ...
    def set_css_colour(self, colour_name: str): ...
    def set_css_color(self, color_name: str): ...
    def set_backlight_power(self, on: bool): ...

    @staticmethod
    def _ensure_bytes(s: str | bytes) -> bytes: ...

    @staticmethod
    def special_char(c: str) -> bytes: ...
