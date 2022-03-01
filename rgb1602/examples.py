from time import sleep

from rgb1602.colours import CSS_COLOURS, WAVESHARE_COLOURS
from rgb1602.display import Screen


def _show_colours(
    screen: Screen,
    delay: int,
    colours: dict[str, tuple[int, int, int]],
    colour_set_name: str,
) -> None:
    original_rgb = screen.current_colour
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
            str(t).encode() + screen.special_char("°") + b"    ", col=10, row=0
        )

        sleep(0.3)
